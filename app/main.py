from pathlib import Path
from datetime import date,timedelta
import os,uuid,shutil
import pandas as pd
import joblib
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json, urllib.request, urllib.error, sqlite3, io
from contextlib import contextmanager
from fastapi.responses import StreamingResponse
from .engine import CAT,recommend,eligible_products,price_quote,validate_selection,segment_for
from .kyc import applicant_report,batch_report,ocr_file,mask,GST,UDY,gst_checksum
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; STATIC=Path(__file__).parent/'static'; UPLOADS=ROOT/'runtime_uploads'; UPLOADS.mkdir(exist_ok=True)
for _f in UPLOADS.iterdir():
 if _f.is_file() and (date.today()-date.fromtimestamp(_f.stat().st_mtime)).days>180: _f.unlink(missing_ok=True)
app=FastAPI(title='Project Udyam Digital',version='1.0.0')
app.mount('/static',StaticFiles(directory=STATIC),name='static')
leads=pd.read_csv(DATA/'smb_leads.csv').fillna('')
orders={}; consent_audit=[]; esign_audit=[]; handoffs=[]
DB_PATH=ROOT/'runtime_ops.db'
@contextmanager
def db_conn():
 conn=sqlite3.connect(DB_PATH); conn.row_factory=sqlite3.Row
 try: yield conn
 finally: conn.close()
with db_conn() as _db:
 _db.execute("CREATE TABLE IF NOT EXISTS lead_assignments (lead_id TEXT PRIMARY KEY, owner TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Assigned', note TEXT DEFAULT '', updated_at TEXT NOT NULL)")
 _db.execute("CREATE TABLE IF NOT EXISTS assignment_events (event_id INTEGER PRIMARY KEY AUTOINCREMENT, lead_id TEXT NOT NULL, owner TEXT NOT NULL, status TEXT NOT NULL, note TEXT DEFAULT '', event_at TEXT NOT NULL)")
 _db.commit()
try: propensity=joblib.load(ROOT/'analysis'/'propensity_model.joblib')
except Exception: propensity=None

class AdvisorIn(BaseModel): business_type:str='Kirana store'; employees:int=3; sites:int=1; city:str='Nagpur'; city_tier:int=2; gstin_active:bool=False; gstin:str=''; udyam:bool=False; udyam_number:str=''; current_internet:str='Mobile hotspot'; spend:int=1500; pain_point:str='UPI/POS reliability'; language:str='Hindi'
class QuoteIn(BaseModel): profile:dict; product_ids:list[str]; contract_months:int|None=None
class LookupIn(BaseModel): identifier:str
class OrderIn(BaseModel): business_name:str='Demo Business'; profile:dict; product_ids:list[str]; monthly_total:int=0

def optional_llm_explanation(profile, product_names, fallback):
 key=os.getenv('OPENAI_API_KEY')
 if not key: return fallback, 'deterministic-fallback'
 base=os.getenv('OPENAI_BASE_URL','https://api.openai.com/v1/chat/completions')
 model=os.getenv('OPENAI_MODEL','gpt-4o-mini')
 # No name, phone, GSTIN, Udyam ID, uploaded document or exact address is sent.
 safe={'business_type':profile.get('business_type'),'segment':profile.get('segment'),'employees':profile.get('employees'),'sites':profile.get('sites'),'city_tier':profile.get('city_tier'),'language':profile.get('language'),'products':product_names,'pain_point':profile.get('pain_point')}
 payload={'model':model,'temperature':0.2,'messages':[{'role':'system','content':'You are a concise Indian MSME telecom advisor. Explain only the supplied eligible products in plain language. Do not add products, prices, eligibility claims, contract terms or installation promises. Return 2 short sentences in the requested language. Never ask for personal identifiers.'},{'role':'user','content':json.dumps(safe,ensure_ascii=False)}]}
 try:
  req=urllib.request.Request(base,data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},method='POST')
  with urllib.request.urlopen(req,timeout=5) as resp: result=json.loads(resp.read().decode())
  text=result['choices'][0]['message']['content'].strip()
  return (text[:600] if text else fallback), 'configured-llm'
 except Exception:
  return fallback, 'deterministic-fallback'

@app.get('/')
def home(): return FileResponse(STATIC/'index.html')
@app.get('/api/health')
def health(): return {'status':'ok','dataset_leads':len(leads),'products':len(CAT),'demo_date':'2026-07-15'}
@app.get('/api/catalogue')
def catalogue(): return CAT.to_dict(orient='records')
@app.post('/api/advisor')
def advisor(x:AdvisorIn):
 p=x.model_dump(); raw_gstin=p.pop('gstin','').replace(' ','').upper(); p.pop('udyam_number',None)
 gst_row=GST[GST.gstin==raw_gstin] if raw_gstin else GST.iloc[0:0]
 verified=bool(len(gst_row) and str(gst_row.iloc[0].status)=='Active')
 p['gstin_active']=verified
 gst_status=str(gst_row.iloc[0].status) if len(gst_row) else ('not supplied' if not raw_gstin else 'not found')
 ids=recommend(p); eligible=eligible_products(p)
 try:q=price_quote(ids,p)
 except Exception as e: q={'items':[],'monthly_total':0,'setup_total':0,'expected_install_days':0,'error':str(e)}
 name=''; desc=''
 for pid in ids:
  r=CAT[CAT.product_id==pid].iloc[0]; name+=r.product_name+', '
 seg=p.get('segment') or segment_for(x.business_type,x.sites)
 why={'micro':'Keep the entry bundle affordable: reliable fibre plus business calling; POS or WhatsApp can be added as usage grows.','prof':'A stronger office connection with business lines and cloud productivity; security can be added without a site visit.','multi':'Standardise connectivity across branches, add failover and centrally managed Wi-Fi.','mfg':'Prioritise dependable dedicated connectivity, business lines and endpoint protection; schedule an assisted site survey for SLA-grade installation.'}.get(seg,'A right-sized bundle based on your profile.')
 if not verified: why+=' GST-dependent products are not included; completing GST registration can unlock leased lines, managed firewall and selected communication services.'
 if x.language.lower()=='hindi': why={'micro':'कम लागत में भरोसेमंद इंटरनेट और बिज़नेस कॉलिंग। POS या WhatsApp को बाद में जोड़ा जा सकता है।','prof':'ऑफिस के लिए तेज़ इंटरनेट, बिज़नेस लाइन और क्लाउड टूल्स।','multi':'सभी शाखाओं के लिए एक जैसी कनेक्टिविटी, बैकअप और सुरक्षित Wi‑Fi।','mfg':'समर्पित कनेक्टिविटी और सुरक्षा; इंस्टॉलेशन के लिए विशेषज्ञ साइट सर्वे।'}.get(seg,why)
 handoff=not any(i in ids for i in ['P01','P02','P03','P04','P05','P06'])
 if handoff: why='No fixed business-connectivity product is eligible under the current profile. A specialist should confirm registration and site feasibility before proposing a compliant plan.'
 why, explanation_source=optional_llm_explanation({**p,'segment':seg},[CAT[CAT.product_id==i].iloc[0].product_name for i in ids],why)
 if handoff: handoffs.append({'business_type':x.business_type,'city':x.city,'reason':'No catalogue-eligible fixed connectivity product for this profile; assisted feasibility review required.'})
 return {'segment':seg,'recommended_ids':ids,'eligible_ids':eligible,'handoff':handoff,'handoff_reason':'No catalogue-eligible fixed connectivity product for this profile; assisted feasibility review required.' if handoff else None,'recommended_names':[CAT[CAT.product_id==i].iloc[0].product_name for i in ids],'eligible_count':len(eligible),'why':why,'explanation_source':explanation_source,'quote':q,'expected_go_live_days':q.get('expected_install_days',0),'gst_unlock':not verified,'gstin_verification':gst_status,'expected_go_live_date':str(date(2026,7,15)+timedelta(days=q.get('expected_install_days',0))),'gst_upsell':'Active GSTIN unlocks eligible leased-line, firewall and cloud-telephony products.' if not verified else None,'language':x.language}

@app.post('/api/quote')
def quote(x:QuoteIn):
 try:return price_quote(x.product_ids,x.profile,x.contract_months)
 except ValueError as e: raise HTTPException(400,str(e))

@app.post('/api/lookup/gstin')
def gst_lookup(x:LookupIn):
 s=x.identifier.replace(' ','').upper()
 if not gst_checksum(s): return {'found':False,'masked':mask(s),'message':'Invalid GSTIN format/checksum. Verify the 15-character number.'}
 row=GST[GST.gstin==s]
 if row.empty:return {'found':False,'masked':mask(s),'message':'No match in mock GST registry. Check the number or upload the certificate.'}
 r=row.iloc[0].to_dict(); return {'found':True,'masked':mask(s),'legal_name':r['legal_name'],'trade_name':r['trade_name'],'address':r['principal_place_of_business'],'status':r['status'],'state':r['state'],'next_step':'Continue' if r['status']=='Active' else 'GST status must be regularised before onboarding'}
@app.post('/api/lookup/udyam')
def udyam_lookup(x:LookupIn):
 s=x.identifier.replace(' ','').upper(); row=UDY[UDY.udyam_number==s]
 if not __import__('re').fullmatch(r'UDYAM-[A-Z]{2}-00-\d{7}',s): return {'found':False,'masked':mask(s),'message':'Invalid Udyam format. Expected UDYAM-XX-00-NNNNNNN.'}
 if row.empty:return {'found':False,'masked':mask(s),'message':'No match in mock Udyam registry.'}
 r=row.iloc[0].to_dict(); return {'found':True,'masked':mask(s),'enterprise_name':r['enterprise_name'],'enterprise_type':r['enterprise_type'],'activity':r['major_activity'],'city':r['city'],'state':r['state']}

@app.post('/api/consent')
def consent(payload:dict):
 if not payload.get('accepted'): raise HTTPException(400,'Consent is required before document upload')
 rec={'audit_id':str(uuid.uuid4()),'accepted':True,'purpose':'business identity, eligibility and installation onboarding','timestamp':'2026-07-15T10:00:00+05:30','retention_days':180}
 consent_audit.append(rec); return rec
def redact_ocr(text):
 import re
 text=re.sub(r'\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][A-Z0-9]Z[A-Z0-9]\b',lambda m:mask(m.group(0)),text)
 text=re.sub(r'UDYAM-[A-Z]{2}-00-\d{7}',lambda m:mask(m.group(0)),text,flags=re.I)
 text=re.sub(r'SYN-ID-\d{6}', 'SYN-ID-******', text)
 text=re.sub(r'\b\d{10}\b','XXXXXXXXXX',text)
 return text

@app.post('/api/consent/withdraw')
def withdraw_consent():
 import shutil
 for f in UPLOADS.iterdir():
  if f.is_file(): f.unlink(missing_ok=True)
 consent_audit.clear(); esign_audit.clear(); orders.clear()
 return {'withdrawn':True,'message':'Consent withdrawn; uploaded demo documents deleted from local runtime storage.'}
@app.post('/api/esign')
def esign(payload:dict):
 if not consent_audit: raise HTTPException(403,'Consent is required before e-sign')
 if payload.get('otp')!='123456': raise HTTPException(400,'Invalid demo OTP')
 rec={'audit_id':str(uuid.uuid4()),'event':'mock_otp_esign_completed','timestamp':'2026-07-15T10:05:00+05:30','document_hash':'DEMO-HASH-ONLY'}
 esign_audit.append(rec); return rec

@app.post('/api/kyc/upload')
async def kyc_upload(file:UploadFile=File(...),consent:bool=Form(...),doc_type:str=Form('document')):
 if not consent or not consent_audit: raise HTTPException(403,'Explicit consent required before upload')
 for _f in UPLOADS.iterdir():
  if _f.is_file() and (date.today()-date.fromtimestamp(_f.stat().st_mtime)).days>180: _f.unlink(missing_ok=True)
 if file.content_type not in ['image/png','image/jpeg','image/jpg']: raise HTTPException(400,'Upload PNG or JPG only')
 if doc_type not in ['gst_certificate','udyam_certificate','signatory_id','address_proof']: raise HTTPException(400,'Unsupported document type')
 data=await file.read(8*1024*1024+1)
 if len(data)>8*1024*1024: raise HTTPException(413,'Maximum file size is 8 MB')
 try:
  from PIL import Image
  Image.open(io.BytesIO(data)).verify()
 except Exception: raise HTTPException(400,'File content is not a valid PNG/JPEG image')
 dest=UPLOADS/(str(uuid.uuid4())+'.'+('png' if file.content_type=='image/png' else 'jpg'))
 dest.write_bytes(data)
 try: text=ocr_file(dest)
 except Exception as e: text='OCR could not read this file. Please upload a clearer image.'
 import re,datetime
 checks=[]
 if doc_type=='gst_certificate':
  line=next((z for z in text.splitlines() if 'GSTIN' in z.upper()),''); token=re.sub(r'[^A-Z0-9]','',line.split('GSTIN',1)[-1].upper())
  candidates=[token[i:i+15] for i in range(max(1,len(token)-14)) if len(token[i:i+15])==15]
  match=next((z for z in candidates if gst_checksum(z)),None)
  if match:
   row=GST[GST.gstin==match]; checks.append('GSTIN checksum valid' if len(row) else 'GSTIN checksum valid but registry match missing')
   if len(row): checks.append('GST status: '+str(row.iloc[0].status))
  else: checks.append('GSTIN unreadable or checksum invalid; manual review required')
 elif doc_type=='udyam_certificate':
  m=re.search(r'UDYAM\s*-\s*[A-Z]{2}\s*-\s*00\s*-\s*\d{7}',text,re.I); val=re.sub(r'\s+','',m.group(0)).upper() if m else ''
  if val and UDY[UDY.udyam_number==val].shape[0]: checks.append('Udyam format and mock registry match')
  else: checks.append('Udyam number missing, unreadable or not found; manual review required')
 elif doc_type=='address_proof':
  m=re.search(r'Bill date\s*(\d{4}-\d{2}-\d{2})',text,re.I)
  if m:
   age=(date(2026,7,15)-date.fromisoformat(m.group(1))).days; checks.append(f'Address proof age: {age} days' + (' — within 90 days' if 0<=age<=90 else ' — OUTSIDE 90-day rule'))
  else: checks.append('Address proof date unreadable')
 elif doc_type=='signatory_id':
  m=re.search(r'Valid till\s*(\d{4}-\d{2}-\d{2})',text,re.I)
  if m: checks.append('Signatory ID unexpired' if date.fromisoformat(m.group(1))>=date(2026,7,15) else 'Signatory ID expired')
  else: checks.append('Signatory ID expiry not readable')
 return {'filename':file.filename,'doc_type':doc_type,'masked_preview':redact_ocr(text)[:1000],'validation':checks,'extraction_status':'review_required','note':'OCR extraction is a decision-support step; registry and cross-document validation are still required.'}
@app.get('/api/kyc/applicants')
def kyc_applicants():
 return [{k:v for k,v in x.items() if k!='ocr'} for x in batch_report()]
@app.get('/api/kyc/applicants/{applicant_id}')
def kyc_one(applicant_id:str):
 if applicant_id not in [f'K{i:02d}' for i in range(1,13)]: raise HTTPException(404,'Unknown specimen applicant')
 r=applicant_report(applicant_id); return {k:r[k] for k in ['applicant','checks_passed','passed','failures','decision','masked_gstin','masked_udyam']}

@app.post('/api/orders')
def create_order(x:OrderIn):
 if not consent_audit or not esign_audit: raise HTTPException(403,'Consent and mock e-sign are required before order creation')
 try:q=price_quote(x.product_ids,x.profile)
 except ValueError as e: raise HTTPException(400,str(e))
 oid='UD-'+uuid.uuid4().hex[:8].upper(); start=date(2026,7,15); rows=[]
 for item in q['items']:
  days=item['install_days']; rows.append({'product':item['name'],'install_days':days,'expected_date':str(start+timedelta(days=days)),'status':'Scheduled' if days>2 else 'Ready'})
 critical=q['expected_install_days']; order={'order_id':oid,'business_name':x.business_name,'status':'Quote accepted','created':'2026-07-15','expected_activation':str(start+timedelta(days=critical)),'critical_path_days':critical,'items':rows,'timeline':[{'name':'Quote accepted','status':'done','date':'2026-07-15'},{'name':'KYC verified','status':'in progress','date':'Pending'},{'name':'Site survey','status':'up next','date':'Pending'},{'name':'Installation','status':'up next','date':str(start+timedelta(days=max(1,critical-2)))},{'name':'Activated','status':'up next','date':str(start+timedelta(days=critical))}],'next_action':'Complete consent-led KYC and OTP e-sign.','notifications':['Mock SMS: Quote created. Complete KYC to reserve your installation slot.']}
 orders[oid]=order; return order
@app.get('/api/orders/{order_id}')
def get_order(order_id:str):
 if order_id not in orders: raise HTTPException(404,'Order not found in this demo session')
 return orders[order_id]
@app.post('/api/orders/{order_id}/advance')
def advance_order(order_id:str):
 if order_id not in orders: raise HTTPException(404,'Order not found')
 o=orders[order_id]; stages=['Quote accepted','KYC verified','Site survey','Installation','Activated']; idx=stages.index(o['status']); idx=min(idx+1,4); o['status']=stages[idx]; o['timeline'][idx]['status']='done'; o['timeline'][idx]['date']='2026-07-16'; o['next_action']='No action required. We will notify you when the next milestone changes.' if idx==4 else 'Our team will complete the next milestone; track progress here.'; o['notifications'].append('Mock WhatsApp: '+o['status']+' update for '+order_id); return o

@app.get('/api/analytics/overview')
def analytics_overview():
 d=leads.copy(); act=d[d.outcome=='Activated']
 stage_order=['Lead','Contacted','Needs assessed','Quote accepted','KYC complete','Activated']
 stage_counts={stage:int((d.stage_reached.map({x:i for i,x in enumerate(stage_order)})>=i).sum()) for i,stage in enumerate(stage_order)}
 def grouped(col):
  g=d.groupby(col,dropna=False).agg(leads=('lead_id','count'),activations=('outcome',lambda x:(x=='Activated').sum()),cac_total=('acquisition_cost_inr','sum')).reset_index()
  g['conversion']=g.activations/g.leads; g['cac_per_activation']=g.cac_total/g.activations.replace(0,float('nan'))
  return g.replace({float('nan'):None}).to_dict(orient='records')
 reasons=d[d.outcome!='Activated'].dropna(subset=['drop_reason']).groupby('drop_reason').size().sort_values(ascending=False).head(8)
 return {'leads':len(d),'activations':len(act),'conversion':len(act)/len(d),'avg_days':round(act.days_lead_to_activation.mean(),1),'avg_chase_calls':round(act.customer_follow_up_calls.mean(),1),'blended_cac':round(d.acquisition_cost_inr.sum()/len(act)),'six_month_churn':round((act.churned_within_6_months=='Y').mean(),3),'median_monthly_value':round(act.monthly_bundle_value_inr.median()),'stage_counts':stage_counts,'segments':grouped('segment'),'sources':grouped('lead_source'),'drop_reasons':[{'reason':str(k),'count':int(v)} for k,v in reasons.items()]}

@app.get('/api/backoffice/leads')
def backoffice(search:str='',segment:str='',source:str='',tier:str='',stage:str='',score_min:float=0,sort:str='score',limit:int=100,offset:int=0):
 d=leads.copy(); feats=['lead_source','business_type','segment','city_tier','state','preferred_language','employee_count','num_sites','annual_turnover_band','has_gstin','has_udyam','current_internet','current_provider','monthly_telecom_spend_inr']
 if propensity:
  d['propensity']=propensity.predict_proba(d[feats])[:,1]
 else:d['propensity']=.5
 d['masked_contact']=d.contact_name.astype(str).str[:1]+'***'
 d=d[d.outcome!='Activated'].copy()
 if search:
  q=search.lower(); d=d[d.apply(lambda r:q in ' '.join(str(r.get(c,'')) for c in ['lead_id','business_name','city','contact_name','drop_reason']).lower(),axis=1)]
 if segment: d=d[d.segment==segment]
 if source: d=d[d.lead_source==source]
 if tier: d=d[d.city_tier.astype(str)==str(tier)]
 if stage: d=d[d.stage_reached==stage]
 d=d[d.propensity>=score_min]
 if sort=='cac': d=d.sort_values('acquisition_cost_inr',ascending=False)
 elif sort=='recent': d=d.sort_values('created_date',ascending=False)
 else: d=d.sort_values('propensity',ascending=False)
 total=len(d); d=d.iloc[max(0,offset):max(0,offset)+max(1,min(limit,500))]
 with db_conn() as conn: assigned={r['lead_id']:dict(r) for r in conn.execute('SELECT * FROM lead_assignments').fetchall()}
 rows=d[['lead_id','business_name','segment','business_type','city','city_tier','lead_source','stage_reached','drop_reason','propensity','masked_contact','has_gstin','acquisition_cost_inr','created_date']].to_dict(orient='records')
 for r in rows:
  r['assignment']=assigned.get(r['lead_id'])
 return {'count':total,'leads':rows,'model_auc':.660,'limit':limit,'offset':offset,'note':'Scores are triage signals from lead-creation fields only; humans decide outreach.'}

class AssignmentIn(BaseModel): lead_id:str; owner:str; status:str='Assigned'; note:str=''
@app.post('/api/backoffice/assign')
def assign_lead(x:AssignmentIn):
 if x.lead_id not in set(leads.lead_id.astype(str)): raise HTTPException(404,'Lead not found')
 allowed=['Inside Sales','Channel Partner','Field Sales','Installation Desk','KYC Desk']
 if x.owner not in allowed: raise HTTPException(400,'Choose a valid assignment team')
 if x.status not in ['Assigned','Contacted','In progress','Closed - won','Closed - lost']: raise HTTPException(400,'Invalid assignment status')
 now=str(pd.Timestamp.now(tz='Asia/Kolkata'))
 with db_conn() as conn:
  conn.execute('INSERT INTO lead_assignments(lead_id,owner,status,note,updated_at) VALUES(?,?,?,?,?) ON CONFLICT(lead_id) DO UPDATE SET owner=excluded.owner,status=excluded.status,note=excluded.note,updated_at=excluded.updated_at',(x.lead_id,x.owner,x.status,x.note[:500],now))
  conn.execute('INSERT INTO assignment_events(lead_id,owner,status,note,event_at) VALUES(?,?,?,?,?)',(x.lead_id,x.owner,x.status,x.note[:500],now))
  conn.commit()
 return {'saved':True,'lead_id':x.lead_id,'owner':x.owner,'status':x.status,'updated_at':now}

@app.get('/api/backoffice/lead/{lead_id}')
def backoffice_lead_detail(lead_id:str):
 rows=leads[leads.lead_id.astype(str)==lead_id]
 if rows.empty: raise HTTPException(404,'Lead not found')
 r=rows.iloc[0].to_dict()
 # Never return raw GSTIN/Udyam identifiers or full contact names from this operational endpoint.
 detail={k:(None if pd.isna(v) else v) for k,v in r.items() if k not in ['gstin','udyam_number','contact_name','contacted_date','needs_assessed_date','quote_accepted_date','kyc_complete_date','activated_date']}
 detail['masked_contact']=str(r.get('contact_name',''))[:1]+'***'
 feats=['lead_source','business_type','segment','city_tier','state','preferred_language','employee_count','num_sites','annual_turnover_band','has_gstin','has_udyam','current_internet','current_provider','monthly_telecom_spend_inr']
 detail['propensity']=float(propensity.predict_proba(pd.DataFrame([{k:r.get(k) for k in feats}]))[:,1][0]) if propensity else 0.5
 with db_conn() as conn:
  a=conn.execute('SELECT * FROM lead_assignments WHERE lead_id=?',(lead_id,)).fetchone()
  events=conn.execute('SELECT owner,status,note,event_at FROM assignment_events WHERE lead_id=? ORDER BY event_id DESC LIMIT 20',(lead_id,)).fetchall()
 detail['assignment']=dict(a) if a else None
 detail['activity']=[dict(e) for e in events]
 return detail

@app.get('/api/backoffice/assignments')
def assignments():
 with db_conn() as conn: rows=[dict(r) for r in conn.execute('SELECT * FROM lead_assignments ORDER BY updated_at DESC').fetchall()]
 return {'count':len(rows),'assignments':rows}

@app.get('/api/backoffice/export.csv')
def export_leads(search:str='',segment:str='',source:str='',tier:str='',stage:str='',score_min:float=0):
 # Export every matching record, not just the first dashboard page.
 first=backoffice(search,segment,source,tier,stage,score_min,'score',500,0)
 rows=list(first['leads'])
 for offset in range(500,first['count'],500):
  rows.extend(backoffice(search,segment,source,tier,stage,score_min,'score',500,offset)['leads'])
 frame=pd.DataFrame(rows)
 stream=io.StringIO(); frame.to_csv(stream,index=False)
 return StreamingResponse(iter([stream.getvalue()]),media_type='text/csv',headers={'Content-Disposition':'attachment; filename=udyam_priority_leads.csv'})

@app.get('/api/backoffice/handoffs')
def get_handoffs(): return {'count':len(handoffs),'handoffs':handoffs}

@app.get('/api/metrics')
def metrics():
 d=leads; act=d[d.outcome=='Activated']; return {'leads':len(d),'activations':len(act),'conversion':len(act)/len(d),'avg_days':round(act.days_lead_to_activation.mean(),1),'avg_chase_calls':round(act.customer_follow_up_calls.mean(),1),'blended_cac':round(d.acquisition_cost_inr.sum()/len(act)),'six_month_churn':round((act.churned_within_6_months=='Y').mean(),3),'median_monthly_value':round(act.monthly_bundle_value_inr.median())}

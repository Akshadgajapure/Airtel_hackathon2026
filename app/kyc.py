from pathlib import Path
import re,datetime,os
from functools import lru_cache
import pandas as pd
from PIL import Image,ImageOps,ImageEnhance,ImageFilter
import pytesseract
DATA=Path(__file__).resolve().parents[1]/'data'; DOCS=DATA/'kyc_documents'; TODAY=datetime.date(2026,7,15)
GST=pd.read_csv(DATA/'mock_gstin_registry.csv').fillna(''); UDY=pd.read_csv(DATA/'mock_udyam_registry.csv').fillna('')
CHARS='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
def gst_checksum(s):
 try:
  if len(s)!=15 or not re.fullmatch(r'[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][A-Z0-9]Z[A-Z0-9]',s) or s[5]!='X': return False
  total=0; factor=2
  for ch in s[:14][::-1]:
   prod=CHARS.index(ch)*factor; total+=prod//36+prod%36; factor=1 if factor==2 else 2
  return CHARS[(36-total%36)%36]==s[-1]
 except Exception: return False

def mask(s):
 if not s:return ''
 s=str(s); return s[:2]+'X'*(max(0,len(s)-5))+s[-3:]
@lru_cache(maxsize=96)
def ocr_file(path):
 im=Image.open(path).convert('L'); im=ImageOps.autocontrast(im); im=im.resize((im.width*2,im.height*2));
 return pytesseract.image_to_string(im,config='--psm 6')
def _clean(s): return re.sub(r'[^A-Z0-9]','',str(s).upper())
def _distance(a,b):
 # Levenshtein distance without an optional dependency
 prev=list(range(len(b)+1))
 for i,ca in enumerate(a,1):
  cur=[i]
  for j,cb in enumerate(b,1): cur.append(min(cur[-1]+1,prev[j]+1,prev[j-1]+(ca!=cb)))
  prev=cur
 return prev[-1]
@lru_cache(maxsize=12)
def applicant_report(k):
 files={typ:DOCS/f'{k}_{typ}.png' for typ in ['gst_certificate','udyam_certificate','signatory_id','address_proof']}
 texts={t:(ocr_file(p) if p.exists() else '') for t,p in files.items()}
 issues=[]; passed=[]; manual=False
 # Find GSTIN OCR token, then reconcile only against registry records whose trade name matches the certificate.
 line=next((z for z in texts['gst_certificate'].splitlines() if 'GSTIN' in z.upper()),'')
 raw=line.split('GSTIN',1)[-1] if 'GSTIN' in line.upper() else ''
 token=_clean(raw)
 trade_m=re.search(r'Trade name\s+(.+)',texts['gst_certificate'],re.I)
 trade=trade_m.group(1).splitlines()[0].strip() if trade_m else ''
 candidates=[]
 for _,rr in GST.iterrows():
  sim=__import__('difflib').SequenceMatcher(None,_clean(trade),_clean(rr.trade_name)).ratio() if trade else 0
  if sim>=.78: candidates.append((rr,sim))
 gstin=''; reg=None; corrected=False
 if token and candidates:
  scored=sorted([(_distance(token,str(rr.gstin)), -sim, rr) for rr,sim in candidates],key=lambda z:(z[0],z[1]))
  if scored and scored[0][0]<=5:
   gstin=str(scored[0][2].gstin); reg=scored[0][2]; corrected=(token!=gstin)
 elif len(token)==15 and gst_checksum(token):
  m=GST[GST.gstin==token]
  if len(m): gstin=token; reg=m.iloc[0]
 if gstin and len(gstin)==15 and gst_checksum(gstin):
  passed.append('GSTIN format + checksum')
  if corrected: passed.append('OCR number reconciled to matching trade-name registry record (human confirmation advised)'); issues.append('OCR corrected GSTIN; reviewer must confirm against the original certificate'); manual=True
 else: issues.append('GSTIN unreadable or checksum/format invalid; re-upload a clear GST certificate')
 if reg is not None:
  if str(reg.status)=='Active': passed.append('GST registry status: Active')
  else: issues.append(f'GST registration is {reg.status}; resolve with tax authority before onboarding')
 else: issues.append('GSTIN does not match mock GST registry')
 # Udyam number; allow OCR whitespace/hyphen noise but not invent a missing identifier.
 uline=next((z for z in texts['udyam_certificate'].splitlines() if re.search(r'UDYAM\s*-\s*[A-Z]{2}',z,re.I)), '')
 um=re.search(r'UDYAM[\s-]*[A-Z]{2}[\s-]*00[\s-]*\d{7}',uline,re.I)
 udyam=re.sub(r'[^A-Z0-9]','',um.group(0)).upper() if um else ''
 if udyam and re.fullmatch(r'UDYAM[A-Z]{2}00\d{7}',udyam):
  # restore canonical hyphens
  udyam=f'UDYAM-{udyam[5:7]}-{udyam[7:9]}-{udyam[9:]}'
  passed.append('Udyam format')
 else: issues.append('Udyam number missing or unreadable; provide a clear Udyam certificate')
 ureg=UDY[UDY.udyam_number==udyam] if udyam else UDY.iloc[0:0]
 if len(ureg): passed.append('Udyam registry match')
 elif udyam: issues.append('Udyam number not found in mock registry')
 # Cross-document name check uses GST legal name and Udyam enterprise name.
 gname=''
 m=re.search(r'Legal name\s+(.+)',texts['gst_certificate'],re.I); gname=m.group(1).splitlines()[0].strip() if m else ''
 uname=''; m=re.search(r'Enterprise name\s+(.+)',texts['udyam_certificate'],re.I); uname=m.group(1).splitlines()[0].strip() if m else ''
 def norm(s): return re.sub(r'[^a-z0-9]','',str(s).lower())
 registry_trade=str(reg.trade_name) if reg is not None else trade
 name_candidates=[z for z in [gname,trade,registry_trade] if z and uname]
 name_scores=[(__import__('difflib').SequenceMatcher(None,norm(z),norm(uname)).ratio(),z) for z in name_candidates]
 name_match_score=round(max([z[0] for z in name_scores],default=0.0),3)
 if uname and name_match_score>=0.78:
  passed.append(f'GST–Udyam business-name consistency (similarity {name_match_score:.3f})')
 elif gname and uname: issues.append(f'GST and Udyam enterprise names differ (best similarity {name_match_score:.3f}); manual review required'); manual=True
 else: issues.append('Could not confidently compare GST and Udyam names'); manual=True
 # Address proof freshness, evaluated against fixed case date.
 dm=re.search(r'Bill date\s*(\d{4}-\d{2}-\d{2})',texts['address_proof'],re.I)
 if dm:
  dt=datetime.date.fromisoformat(dm.group(1)); age=(TODAY-dt).days
  if 0<=age<=90: passed.append(f'Address proof age: {age} days (within 90-day rule)')
  else: issues.append(f'Address proof is {age} days old; must be within 90 days of 2026-07-15')
 else: issues.append('Address proof date not readable')
 # Compare the address proof location with the Udyam/GST registry where available.
 expected_state=str(ureg.iloc[0].state) if len(ureg) else (str(reg.state) if reg is not None else '')
 expected_city=str(ureg.iloc[0].city) if len(ureg) else ''
 addr_compact=re.sub(r'\s+','',texts['address_proof']).lower()
 if expected_state and expected_state.replace(' ','').lower() in addr_compact: passed.append('Address state matches registry')
 elif expected_state: issues.append(f'Address state does not match registry state ({expected_state}); manual review required'); manual=True
 if expected_city and expected_city.replace(' ','').lower() in addr_compact: passed.append('Address city matches Udyam registry')
 elif expected_city: issues.append(f'Address city does not match Udyam registry city ({expected_city}); manual review required'); manual=True
 # Signatory presence, expiry and entity consistency.
 idtxt=texts['signatory_id']; nm=re.search(r'Name\s+([A-Za-z ]+)',idtxt,re.I); signatory=nm.group(1).strip() if nm else ''
 em=re.search(r'Valid till\s*(\d{4}-\d{2}-\d{2})',idtxt,re.I)
 if 'SYN-ID-' in idtxt and em and datetime.date.fromisoformat(em.group(1))>=TODAY:
  passed.append('Signatory ID present and unexpired')
 else: issues.append('Signatory ID missing, illegible or expired')
 designation_m=re.search(r'Designation\s+([A-Za-z ]+)',idtxt,re.I); designation=designation_m.group(1).strip().lower() if designation_m else ''
 business=trade or uname
 if signatory and business and norm(business) in norm(idtxt):
  if any(term in (gname+' '+trade).lower() for term in [' llp',' pvt','private limited','limited liability',' limited']):
   if designation in ['partner','director','authorised signatory','authorized signatory'] or (gname and norm(signatory) in norm(gname)): passed.append('Entity signatory role evidenced')
   else: issues.append('Non-proprietor entity signatory authority not evidenced; obtain partner/director authorisation'); manual=True
  else: passed.append('Signatory ID references the business')
 elif signatory and gname and norm(signatory) in norm(gname): passed.append('Signatory name consistent with legal proprietor')
 elif signatory: issues.append('Signatory-to-entity authority is not evidenced; obtain authorisation/board resolution'); manual=True
 if not issues and not manual: decision='AUTO-APPROVE'
 elif manual and not any(x.startswith(('GST registration is','Address proof is','GSTIN unreadable','GSTIN does not','Udyam number missing','Udyam number not found')) for x in issues): decision='MANUAL REVIEW'
 elif any(x.startswith(('GST registration is','Address proof is','GSTIN unreadable','GSTIN does not','Udyam number missing','Udyam number not found')) for x in issues): decision='NEEDS FIX'
 else: decision='MANUAL REVIEW'
 return {'applicant':k,'checks_passed':len(passed),'passed':passed,'failures':issues,'decision':decision,'masked_gstin':mask(gstin),'masked_udyam':mask(udyam),'name_match_score':name_match_score,'ocr':texts}

@lru_cache(maxsize=1)
def batch_report(): return [applicant_report(f'K{i:02d}') for i in range(1,13)]

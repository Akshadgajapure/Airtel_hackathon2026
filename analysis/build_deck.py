from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN,MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.dml import MSO_THEME_COLOR
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'business_case.pptx'
prs=Presentation(str(ROOT/'Submission Template_Sync.pptx'))
# Remove blank placeholder slides while retaining the supplied template's theme/master.
ids=prs.slides._sldIdLst
for sid in list(ids):
 prs.part.drop_rel(sid.rId); ids.remove(sid)
prs.slide_width=Inches(13.333); prs.slide_height=Inches(7.5)
NAVY=RGBColor(10,49,57); TEAL=RGBColor(8,126,121); MINT=RGBColor(225,244,239); TEXT=RGBColor(32,53,61); GREY=RGBColor(105,122,129); LIGHT=RGBColor(245,249,248); WHITE=RGBColor(255,255,255); ORANGE=RGBColor(229,145,67); RED=RGBColor(190,87,72)
blank=prs.slide_layouts[6]
def textbox(slide,x,y,w,h,text,size=14,color=TEXT,bold=False,font='Aptos',align=None):
 sh=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)); tf=sh.text_frame; tf.clear(); tf.word_wrap=True
 p=tf.paragraphs[0]; p.text=str(text); p.font.name=font;p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=color
 if align is not None:p.alignment=align
 return sh
def rect(slide,x,y,w,h,fill, radius=False,line=None):
 shape=slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h)); shape.fill.solid();shape.fill.fore_color.rgb=fill;shape.line.fill.background() if line is None else None
 if line: shape.line.color.rgb=line
 return shape
def header(slide,kicker,title,sub=None):
 rect(slide,0,0,13.333,.16,TEAL);textbox(slide,.55,.34,12,.25,kicker.upper(),9,TEAL,True)
 textbox(slide,.55,.66,12, .55,title,24,NAVY,True,'Aptos Display')
 if sub:textbox(slide,.57,1.22,12,.32,sub,10,GREY)
def footer(slide,n):
 textbox(slide,.55,7.17,10,.16,'PROJECT UDYAM DIGITAL  ·  YTL HACKATHON 2026  ·  SYNTHETIC DATA',7,GREY,True)
 textbox(slide,12.35,7.14,.4,.2,f'{n:02d}',8,TEAL,True,align=PP_ALIGN.RIGHT)
def bullet_list(slide,x,y,w,items,size=12,gap=.5,color=TEXT):
 for i,t in enumerate(items):
  yy=y+i*gap; textbox(slide,x,yy,.22,.28,'•',15,TEAL,True); textbox(slide,x+.25,yy,w-.25,gap-.03,t,size,color)
def metric(slide,x,y,w,label,value,detail=''):
 rect(slide,x,y,w,.95,LIGHT,True);textbox(slide,x+.15,y+.12,w-.3,.18,label.upper(),8,GREY,True);textbox(slide,x+.15,y+.34,w-.3,.35,value,21,TEAL,True,'Aptos Display');
 if detail:textbox(slide,x+.15,y+.72,w-.3,.16,detail,7,GREY)
def add_table(slide,x,y,w,h,headers,rows,widths=None,fs=9):
 sh=slide.shapes.add_table(len(rows)+1,len(headers),Inches(x),Inches(y),Inches(w),Inches(h));t=sh.table
 if widths:
  for c,ww in enumerate(widths):t.columns[c].width=Inches(ww)
 for ri,row in enumerate([headers]+rows):
  for ci,val in enumerate(row):
   cell=t.cell(ri,ci);cell.text=str(val);cell.margin_left=Inches(.06);cell.margin_right=Inches(.05);cell.margin_top=Inches(.03);cell.margin_bottom=Inches(.03);cell.vertical_anchor=MSO_ANCHOR.MIDDLE
   cell.fill.solid();cell.fill.fore_color.rgb=NAVY if ri==0 else (LIGHT if ri%2 else WHITE)
   for p in cell.text_frame.paragraphs:
    p.font.name='Aptos';p.font.size=Pt(fs);p.font.bold=(ri==0 or ci==0);p.font.color.rgb=WHITE if ri==0 else TEXT
 return sh
# Slide 1 cover
s=prs.slides.add_slide(blank);rect(s,0,0,13.333,7.5,NAVY);rect(s,0,0,.18,7.5,TEAL)
textbox(s,.85,.72,7,.28,'YTL HACKATHON 2026  /  ENTERPRISE TRACK A',10,RGBColor(154,222,210),True)
textbox(s,.85,1.55,7.7,1.3,'PROJECT\nUDYAM DIGITAL',34,WHITE,True,'Aptos Display')
textbox(s,.9,3.12,6.7,.8,'Making small businesses go digital\nin one sitting.',20,RGBColor(204,230,225),False,'Aptos Display')
rect(s,9.1,1.35,3.1,4.55,TEAL,True);textbox(s,9.48,1.82,2.3,.3,'THE PROMISE',9,RGBColor(195,235,226),True)
for i,(a,b) in enumerate([('01','Discover'),('02','Quote'),('03','Verify'),('04','Activate')]):
 y=2.42+i*.82;textbox(s,9.5,y,.45,.3,a,10,RGBColor(170,229,216),True);textbox(s,10.12,y-.02,1.7,.34,b,17,WHITE,True,'Aptos Display')
textbox(s,.9,6.35,7,.3,'ACCEL BUSINESS  ·  PRODUCT + ENGINEERING + UNIT ECONOMICS',9,RGBColor(166,194,192),True)
textbox(s,.9,6.78,8,.2,'Prototype and business case  |  15 July 2026 reference date',8,RGBColor(166,194,192))
# Slide 2 baseline
s=prs.slides.add_slide(blank);header(s,'01 · The problem','The leak is in the journey — not just the product','5,000 synthetic leads, Apr–Jun 2026. Only 368 reached activation (7.36%).')
for i,(lab,val,det) in enumerate([('LEADS','5,000','100%'),('ACTIVATED','368','7.36% of leads'),('AVG. ACTIVATION','17.6 days','Lead to go-live'),('CAC / ACTIVATION','₹15,053','₹55.40L total cost / 368')]):metric(s,.58+i*3.12,1.78,2.82,lab,val,det)
# funnel chart
s.shapes.add_picture(str(ROOT/'analysis'/'funnel.png'),Inches(.55),Inches(3.0),width=Inches(6.2),height=Inches(3.35))
bullet_list(s,7.05,3.15,5.55,['805 unreachable after 3 attempts; 531 owners had no time for a visit.','1,113 assessed leads did not accept a quote — largest mid-funnel leak.','Quote clarity, self-serve discovery, KYC pre-check and install visibility address distinct failure modes.'],12,.9)
footer(s,2)
# Slide 3 segment economics
s=prs.slides.add_slide(blank);header(s,'02 · Where to play','Lead with professional offices; serve micro through low-touch channels','CAC uses total acquisition cost across all leads in the segment divided by activated customers.')
seg=pd.read_csv(ROOT/'analysis'/'segment_economics.csv')
rows=[]
for _,r in seg.iterrows():rows.append([r.segment.replace(' & services','').replace(' businesses',''),f"{r.conversion:.1%}",f"₹{r.cac_per_activation:,.0f}",f"₹{r.activated_value:,.0f}",f"{r.churn:.1%}",f"{r.nps:.1f}"])
add_table(s,.55,1.85,12.2,2.5,['SEGMENT','ACTIVATION','CAC / WIN','MEDIAN MRR','6M CHURN','NPS'],rows,[3.4,1.5,1.8,1.8,1.5,1.5],9)
s.shapes.add_picture(str(ROOT/'analysis'/'segment_conversion.png'),Inches(.65),Inches(4.55),width=Inches(5.6),height=Inches(2.25))
bullet_list(s,6.65,4.62,6.0,['Professional offices: 11.1% conversion, ₹10.7k CAC, ₹6.6k median monthly billings. Best initial digital wedge.','Micro: 4.1% conversion, ₹20.0k CAC, ₹2.47k monthly billings and 22.7% 6m churn. WhatsApp/partner-assisted, entry-priced.','Multi-site + manufacturing: high monthly value, but assisted survey / SLA sales and install orchestration required.'],10,.68)
footer(s,3)
# Slide 4 bundles
s=prs.slides.add_slide(blank);header(s,'03 · What to sell','Four catalogue-backed bundles — simple entry, expandable value','Illustrative monthly prices use catalogue midpoints, indicative quantities and 5% discount for 3+ distinct products; GST extra.')
bundles=[['MICRO START','Biz Fibre 100 + Business Postpaid 299','₹1,448','12 mo','Self-serve / WhatsApp'],['OFFICE PRO','Fibre 300 + 2 business lines + 8 email seats + endpoint security','₹3.9k','12 mo','Digital; human exception'],['MULTI-SITE CONTROL','Fibre 300 × sites + failover + secure Wi-Fi + cloud email','₹20.8k*','12–24 mo','Partner + field seller'],['MANUFACTURING SLA','Leased Line 20 + 20 mobile lines + 20 email + endpoint + firewall','₹30.1k*','24 mo','Named seller + site survey']]
for i,b in enumerate(bundles):
 x=.58+(i%2)*6.15;y=1.85+(i//2)*2.22;rect(s,x,y,5.85,1.9,LIGHT,True);textbox(s,x+.2,y+.17,5.4,.2,b[0],9,TEAL,True);textbox(s,x+.2,y+.48,5.35,.48,b[1],12,TEXT,True);textbox(s,x+.2,y+1.07,1.5,.4,b[2],21,NAVY,True,'Aptos Display');textbox(s,x+1.85,y+1.16,1.0,.2,b[3],9,GREY);textbox(s,x+3.05,y+1.16,2.4,.2,b[4],9,GREY)
textbox(s,.75,6.48,11.9,.28,'*Multi-site example assumes 5 sites / 10 employees; manufacturing example assumes 1 site / 20 employees. All prices before GST; actual quote is quantity- and eligibility-aware.',8,GREY)
footer(s,4)
# Slide 5 architecture
s=prs.slides.add_slide(blank);header(s,'04 · Product & engineering','LLM explains. Rules decide. KYC evidence gates activation.','A hard boundary between conversational AI and deterministic commercial / compliance decisions.')
blocks=[('OWNER UI','Mobile-first · Hindi / English','01'),('ADVISOR','6-question discovery\nLLM-ready dialogue','02'),('RULES ENGINE','Catalogue eligibility\nDependencies + install days','03'),('QUOTE','Midpoint price bands\nContract + GST + add-ons','04'),('SMART KYC','Consent → OCR → registry\nName / date / signatory checks','05'),('ORDER TRACKER','Critical-path ETA\nPer-product status + alerts','06')]
for i,(a,b,n) in enumerate(blocks):
 x=.55+i*2.12;rect(s,x,2.05,1.92,1.48,LIGHT,True);textbox(s,x+.12,2.2,.4,.2,n,9,TEAL,True);textbox(s,x+.12,2.52,1.7,.28,a,10,NAVY,True);textbox(s,x+.12,2.9,1.68,.5,b,9,GREY)
 if i<5:textbox(s,x+1.93,2.62,.2,.25,'→',16,TEAL,True)
rect(s,.75,4.05,5.7,1.35,MINT,True);textbox(s,1.0,4.28,5.1,.22,'MOCK REGISTRIES + OCR',10,TEAL,True);textbox(s,1.0,4.65,5.0,.45,'GSTIN / Udyam CSV lookups · Tesseract OCR · checksum · 90-day address rule · manual review queue',10,TEXT)
rect(s,6.85,4.05,5.7,1.35,LIGHT,True);textbox(s,7.1,4.28,5.1,.22,'BACK OFFICE',10,TEAL,True);textbox(s,7.1,4.65,5.0,.45,'Logistic propensity score · reason codes · partner attribution · assisted follow-up',10,TEXT)
textbox(s,.8,5.95,11.7,.45,'Safety boundary: no raw PII in prompts. LLM is not allowed to alter eligibility, pricing, KYC decisions or installation promises.',11,RED,True)
footer(s,5)
# Slide 6 funnel targets
s=prs.slides.add_slide(blank);header(s,'05 · Conversion model','A 12% activation target is built from explicit stage improvements','Scenario for 5,000 leads; each conversion is conditional on the immediately previous stage.')
rows=[['Lead → contacted','68.1%','75.0%','3,750'],['Contacted → assessed','58.0%','60.0%','2,250'],['Assessed → quote accepted','43.6%','50.0%','1,125'],['Quote → KYC complete','68.3%','75.0%','844'],['KYC → activated','62.6%','71.1%','600']]
add_table(s,.65,1.9,8.0,3.1,['STAGE','BASELINE','PILOT TARGET','TARGET LEADS'],rows,[3.5,1.4,1.5,1.6],10)
metric(s,9.05,2.05,3.4,'TARGET ACTIVATIONS','600','12.0% of 5,000 leads')
metric(s,9.05,3.25,3.4,'CAC AT FLAT SPEND','₹9,233','₹55.40L / 600 activations')
textbox(s,.85,5.55,11.6,.8,'Leak closure levers: self-serve + verified contact links improve reach; asynchronous needs discovery removes visit friction; instant plain-language quotes improve acceptance; OCR / registry pre-checks reduce KYC rework; install-day-aware routing protects final activation.',11,TEXT)
footer(s,6)
# Slide 7 channel strategy + rollout
s=prs.slides.add_slide(blank);header(s,'06 · Go-to-market','Digital should make partners more productive — not disintermediate them','Observed source economics: referral and inbound are the most efficient acquisition channels in this sample.')
src=pd.read_csv(ROOT/'analysis'/'source_economics.csv')
rows=[]
for _,r in src.iterrows():rows.append([r.lead_source,f"{r.conversion:.1%}",f"₹{r.cac_per_activation:,.0f}",r.decision])
add_table(s,.55,1.8,6.2,3.55,['SOURCE','CONVERSION','CAC / WIN','ACTION'],rows,[1.8,1.2,1.5,1.7],8)
bullet_list(s,7.05,1.95,5.55,['Referral + inbound: scale; use referral IDs and a fast callback SLA.','Partner + field: shared lead ID, attribution lock and commission protection; redeploy field sellers to multi-site / manufacturing and installation.','Website: improve qualification and quote UX. WhatsApp: controlled test; 2.8% observed conversion is low despite low CAC.'],10,.72)
rect(s,7.1,4.75,5.3,1.15,MINT,True);textbox(s,7.35,4.95,4.8,.2,'ROLLOUT',9,TEAL,True);textbox(s,7.35,5.28,4.8,.43,'Pilot: Tier 1–2 cities · professional offices + micro. Then expand multi-site and manufacturing with assisted delivery.',10,TEXT)
footer(s,7)
# Slide 8 privacy risks
s=prs.slides.add_slide(blank);header(s,'07 · Trust & delivery risk','Fast onboarding only works when trust and operations are designed in','Production launch requires telecom/KYC legal review and real provider contracts; this prototype uses mock services.')
risks=[['GST / KYC fraud','Registry + checksum + OCR cross-check; ambiguous OCR → manual review; cancelled/suspended GSTIN blocked.'],['LLM hallucination','LLM explains only; server-side rules own eligibility, price, dependency and ETA.'],['DPDP / data misuse','Purpose notice + explicit consent before upload; minimise, mask, encrypt, retain 180 days then delete subject to legal holds.'],['Partner conflict','Shared lead ID, source attribution, commission protection and transparent ownership.'],['Install SLA failure','Catalogue install-day critical path, per-product status, exception alerts and honest ETA.']]
for i,(a,b) in enumerate(risks):
 y=1.8+i*.91;rect(s,.65,y,2.25,.68,NAVY,True);textbox(s,.82,y+.2,1.95,.25,a,10,WHITE,True);textbox(s,3.15,y+.08,9.3,.52,b,10,TEXT)
textbox(s,.8,6.48,11.7,.3,'Privacy contact in prototype is a fictional placeholder. Production needs named grievance owner, access controls, breach response and processor / cross-border assessment.',8,GREY)
footer(s,8)
# Slide 9 scorecard
s=prs.slides.add_slide(blank);header(s,'08 · Scorecard','Pilot targets — measured as outcomes, not demo claims','Targets are hypotheses for a controlled pilot, anchored to observed funnel arithmetic and current synthetic baseline.')
rows=[['Lead → activation','7.36%','12.0%','5,000 × 75% × 60% × 50% × 75% × 71.1% ≈ 600'],['Lead → activation time','17.6 days avg','≤12 days avg','Instant quote + progressive KYC + install critical-path visibility'],['CAC / activation','₹15,053','≤₹9,233','Flat ₹55.40L acquisition spend / 600 activations'],['Status-chase calls','3.0 avg','≤1.0','Owner-visible tracker + proactive milestone notifications'],['6-month churn','15.2%','≤12.0%','Right-fit bundles + early service-risk outreach; pilot hypothesis']]
add_table(s,.55,1.9,12.2,3.9,['METRIC','BASELINE','PILOT TARGET','WHY IT IS PLAUSIBLE'],rows,[2.3,1.5,1.6,6.8],9)
textbox(s,.8,6.05,11.8,.48,'Decision ask: approve a 6–8 week pilot in 2 cities, start with professional offices + micro, randomise eligible leads into digital vs current journey, and review activation, CAC, time-to-go-live, calls and churn weekly.',11,TEAL,True)
footer(s,9)
prs.save(OUT)
print(OUT)

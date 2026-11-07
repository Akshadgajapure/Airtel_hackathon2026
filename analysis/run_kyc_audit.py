"""Re-run the supplied synthetic KYC specimen audit using local Tesseract OCR."""
from pathlib import Path
import sys
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app.kyc import batch_report
OUT=ROOT/'analysis'
rows=batch_report()
summary=[]
transcripts=['# KYC OCR inspection transcripts','', 'All supplied specimen images are synthetic. Missing files are reported as missing; no identifiers are invented.','']
for item in rows:
    summary.append({k:item.get(k) for k in ['applicant','checks_passed','decision','masked_gstin','masked_udyam','name_match_score','passed','failures']})
    transcripts += [f"## {item['applicant']} — {item['decision']}", '']
    for doc,text in item['ocr'].items():
        transcripts += [f'### {doc}', '```text', text if text else '[DOCUMENT NOT PROVIDED OR OCR EMPTY]', '```', '']
pd.DataFrame(summary).to_csv(OUT/'kyc_validation_results.csv',index=False)
(OUT/'kyc_ocr_transcripts.md').write_text('\n'.join(transcripts),encoding='utf-8')
print(f"Audited {sum(1 for p in (ROOT/'data'/'kyc_documents').glob('*') if p.is_file())} supplied images across {len(rows)} applicants")
for r in rows: print(r['applicant'],r['decision'],'name_similarity=',r.get('name_match_score'))

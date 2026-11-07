from pathlib import Path
import json, warnings
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report
from sklearn.inspection import permutation_importance
warnings.filterwarnings('ignore')
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; OUT=ROOT/'analysis'; OUT.mkdir(exist_ok=True)
df=pd.read_csv(DATA/'smb_leads.csv')
df['activated']=(df.outcome=='Activated').astype(int)
# funnel: stages are cumulative via dates, not mutually exclusive last-stage labels
stage_cols=['contacted_date','needs_assessed_date','quote_accepted_date','kyc_complete_date','activated_date']
stages={'Lead':df.lead_id.notna().sum()}
for label,col in zip(['Contacted','Needs assessed','Quote accepted','KYC complete','Activated'],stage_cols): stages[label]=df[col].notna().sum()
# group funnel by dimension: lead count, activation count, conversion
segments=df.groupby('segment').agg(leads=('lead_id','size'),activated=('activated','sum'),total_acq_cost=('acquisition_cost_inr','sum'),activated_value=('monthly_bundle_value_inr','median'),churn=('churned_within_6_months',lambda s:(s.dropna()=='Y').mean()),nps=('nps_score','mean'),activation_days=('days_lead_to_activation','mean')).reset_index()
segments['conversion']=segments.activated/segments.leads
segments['cac_per_activation']=segments.total_acq_cost/segments.activated
segments['payback_months_gross_revenue_proxy']=segments.cac_per_activation/segments.activated_value

def group_report(col):
 g=df.groupby(col,dropna=False).agg(leads=('lead_id','size'),contacted=('contacted_date',lambda s:s.notna().sum()),needs_assessed=('needs_assessed_date',lambda s:s.notna().sum()),quote_accepted=('quote_accepted_date',lambda s:s.notna().sum()),kyc_complete=('kyc_complete_date',lambda s:s.notna().sum()),activated=('activated','sum'),cost=('acquisition_cost_inr','sum')).reset_index()
 g['conversion']=g.activated/g.leads; g['cac_per_activation']=g.cost/g.activated.replace(0,np.nan)
 for stage in ['contacted','needs_assessed','quote_accepted','kyc_complete','activated']:
  g[stage+'_rate']=g[stage]/g.leads
 return g.sort_values('conversion',ascending=False)
reports={c:group_report(c) for c in ['segment','lead_source','city_tier','preferred_language','has_gstin']}
drops=df[df.outcome!='Activated'].drop_reason.value_counts().rename_axis('drop_reason').reset_index(name='count')
# Bundle patterns: summarize exact bundles with at least 3 activations per segment
act=df[df.activated==1].copy(); bundle=act.groupby(['segment','bundle_products']).agg(activations=('lead_id','size'),monthly_value=('monthly_bundle_value_inr','median'),churn_rate=('churned_within_6_months',lambda s:(s=='Y').mean()),nps=('nps_score','mean')).reset_index()
bundle=bundle[bundle.activations>=2].sort_values(['segment','activations'],ascending=[True,False])
# Source recommendation economics
sources=reports['lead_source'].copy(); sources['decision']=np.where((sources.conversion>=.08)&(sources.cac_per_activation<10000),'Scale',np.where(sources.conversion<.04,'Fix / controlled test','Optimise attribution & targeting'))
# propensity model - only fields available at lead creation
features=['lead_source','business_type','segment','city_tier','state','preferred_language','employee_count','num_sites','annual_turnover_band','has_gstin','has_udyam','current_internet','current_provider','monthly_telecom_spend_inr']
X=df[features].copy(); y=df.activated
cat=[c for c in features if X[c].dtype=='object']; num=[c for c in features if c not in cat]
pre=ColumnTransformer([('cat',Pipeline([('impute',SimpleImputer(strategy='most_frequent')),('oh',OneHotEncoder(handle_unknown='ignore'))]),cat),('num',Pipeline([('impute',SimpleImputer(strategy='median')),('scale',StandardScaler())]),num)])
model=Pipeline([('prep',pre),('clf',LogisticRegression(max_iter=1500,class_weight='balanced',C=.5))])
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.25,random_state=42,stratify=y)
model.fit(Xtr,ytr); prob=model.predict_proba(Xte)[:,1]; auc=roc_auc_score(yte,prob)
test=pd.DataFrame({'actual':yte.values,'score':prob}); test['decile']=pd.qcut(test.score.rank(method='first',ascending=False),10,labels=False)+1
lift=test.groupby('decile').agg(leads=('actual','size'),activations=('actual','sum'),rate=('actual','mean')).reset_index().sort_values('decile')
base=yte.mean(); lift['lift_vs_test_average']=lift.rate/base
# coefficient drivers mapped back to transformed names
names=model.named_steps['prep'].get_feature_names_out(); coefs=model.named_steps['clf'].coef_[0]
coef=pd.DataFrame({'feature':names,'coefficient':coefs}); coef['abs']=coef.coefficient.abs(); drivers=coef.sort_values('abs',ascending=False).head(15)
# export
for name,g in reports.items(): g.to_csv(OUT/f'funnel_by_{name}.csv',index=False)
segments.to_csv(OUT/'segment_economics.csv',index=False); drops.to_csv(OUT/'drop_reasons.csv',index=False); bundle.to_csv(OUT/'bundle_patterns.csv',index=False); sources.to_csv(OUT/'source_economics.csv',index=False); lift.to_csv(OUT/'propensity_top_decile_lift.csv',index=False); drivers.to_csv(OUT/'propensity_drivers.csv',index=False)
import joblib; joblib.dump(model,OUT/'propensity_model.joblib')
# charts
plt.figure(figsize=(8,4.5)); plt.bar(list(stages.keys()),list(stages.values())); plt.title('SMB acquisition funnel (cumulative stage reach)'); plt.ylabel('Leads'); plt.xticks(rotation=20,ha='right'); plt.tight_layout(); plt.savefig(OUT/'funnel.png',dpi=160); plt.close()
plt.figure(figsize=(8,4.5)); s=segments.sort_values('conversion'); plt.barh(s.segment,s.conversion*100); plt.title('Lead-to-activation conversion by segment'); plt.xlabel('Conversion (%)'); plt.tight_layout(); plt.savefig(OUT/'segment_conversion.png',dpi=160); plt.close()
plt.figure(figsize=(8,4.5)); d=drops.head(10).sort_values('count'); plt.barh(d.drop_reason,d['count']); plt.title('Top 10 drop reasons'); plt.xlabel('Dropped leads'); plt.tight_layout(); plt.savefig(OUT/'drop_reasons.png',dpi=160); plt.close()
plt.figure(figsize=(8,4.5)); q=sources.sort_values('conversion'); plt.barh(q.lead_source,q.conversion*100); plt.title('Lead source conversion'); plt.xlabel('Conversion (%)'); plt.tight_layout(); plt.savefig(OUT/'source_conversion.png',dpi=160); plt.close()
# Markdown findings
fmt=lambda x: f'{x:,.1f}'
lines=['# Project Udyam Digital — Data findings','',f'**Dataset:** {len(df):,} synthetic leads, Apr–Jun 2026. **Outcome:** {int(y.sum()):,} activations ({y.mean():.2%}).','', '## Funnel (cumulative stage reach)','', '| Stage | Leads | Stage-to-stage conversion |','|---|---:|---:|']
prev=None
for k,v in stages.items(): lines.append(f'| {k} | {v:,} | {"—" if prev is None else f"{v/prev:.1%}"} |'); prev=v
overall_cac=df.acquisition_cost_inr.sum()/act.shape[0]
overall_churn=(act.churned_within_6_months=='Y').mean(); overall_nps=act.nps_score.mean()
lines += ['', '## Overall operating baseline','', f'- Total acquisition spend: ₹{df.acquisition_cost_inr.sum():,.0f}; CAC per activation: ₹{overall_cac:,.0f} (total cohort acquisition cost / 368 activations).',f'- Activated-customer average lead-to-activation time: {act.days_lead_to_activation.mean():.1f} days; average status chases: {act.customer_follow_up_calls.mean():.1f}.',f'- Six-month churn among activated customers: {overall_churn:.1%}; mean NPS score: {overall_nps:.2f}.', '', '## Segment economics','', 'CAC = **total acquisition cost for every lead in segment / activated customers**, not cost only among winners. Payback shown as CAC divided by median monthly billings; it is a revenue proxy, not contribution-margin payback because gross margin is not supplied.','', '| Segment | Leads | Activation | CAC / activation | Median monthly value | Gross-billing payback | 6m churn | NPS |','|---|---:|---:|---:|---:|---:|---:|---:|']
for _,r in segments.iterrows(): lines.append(f"| {r.segment} | {r.leads:,} | {r.conversion:.1%} | ₹{r.cac_per_activation:,.0f} | ₹{r.activated_value:,.0f} | {r.payback_months_gross_revenue_proxy:.1f} mo | {r.churn:.1%} | {r.nps:.2f} |")
lines += ['', '## Stage reach by segment, source, city tier, language and GSTIN', '', 'Counts are cumulative: a lead is counted at every stage whose timestamp is present. Full CSVs are saved as `funnel_by_*.csv`.']
for dim,label in [('segment','Segment'),('lead_source','Lead source'),('city_tier','City tier'),('preferred_language','Preferred language'),('has_gstin','Has GSTIN')]:
 g=reports[dim]
 lines += ['', f'### {label}', '', '| Group | Leads | Contacted | Needs assessed | Quote accepted | KYC complete | Activated | Activation rate |','|---|---:|---:|---:|---:|---:|---:|---:|']
 for _,r in g.iterrows(): lines.append(f"| {r[dim]} | {int(r.leads):,} | {int(r.contacted):,} | {int(r.needs_assessed):,} | {int(r.quote_accepted):,} | {int(r.kyc_complete):,} | {int(r.activated):,} | {r.conversion:.1%} |")
lines += ['', '## Biggest drop reasons and product response','', '| Drop reason | Leads | Product / process response |','|---|---:|---|']
mapr={'Unreachable after 3 attempts':'Self-serve advisor + WhatsApp resume link','Owner had no time for a visit':'Asynchronous mobile-first onboarding','Not interested on first call':'Need-led discovery; suppress irrelevant pitch','Price too high':'Good/better/best bundles; transparent total and spend comparison','Locked in with current provider':'Switching-cost assessment; migration / backup proposition','Wrong or invalid number':'Contact validation and channel preference','Visit not scheduled by sales':'Self-serve quote and partner-assisted appointment','Only wanted a mobile plan':'Right-size entry offer; avoid forcing broadband','Competitor offered cheaper plan':'Comparable feature / SLA quote, not blanket discount','Quote too complex to understand':'Plain-language line-item quote','Quote took too long to arrive':'Instant rules-priced quote','Installation delayed beyond 21 days':'Install-day-aware promise + tracker','Missing GST or Udyam document':'Registry lookup + OCR pre-validation','Found paperwork too long':'Consent-led progressive KYC','Document details did not match':'Cross-document fuzzy match + manual review','Site not feasible for fibre':'AirFiber alternative / feasibility check','First payment failed':'UPI / card retry, payment link and clear failure recovery','Customer cancelled before install':'Proactive install-slot confirmation and cancellation save desk','Authorised signatory not available':'Remote e-sign / delegated authority workflow'}
for _,r in drops.iterrows(): lines.append(f"| {r.drop_reason} | {r['count']:,} | {mapr.get(r.drop_reason,'Targeted reason-code workflow / human escalation')} |")
lines += ['', '## Lead source economics','', '| Source | Leads | Activations | Conversion | CAC / activation | Decision |','|---|---:|---:|---:|---:|---|']
for _,r in sources.iterrows(): lines.append(f"| {r.lead_source} | {r.leads:,} | {r.activated:,} | {r.conversion:.1%} | ₹{r.cac_per_activation:,.0f} | {r.decision} |")
lines += ['', '## Propensity model','', f'- Logistic regression with class weighting; stratified 75/25 split, random_state=42. Test ROC-AUC: **{auc:.3f}**.','- Features are strictly lead-creation attributes: source, business profile, city tier/state/language, employee/site counts, turnover band, GST/Udyam availability, current connectivity/provider and spend. Excluded: stage dates, stage reached, drop reason, outcome, bundle, activation time, churn, NPS, CAC.','- Top decile lift table is in `propensity_top_decile_lift.csv`; coefficients in `propensity_drivers.csv`. Model is prioritisation support, not automated credit/eligibility.','', '| Score decile (1=highest) | Leads | Activations | Rate | Lift vs test average |','|---:|---:|---:|---:|---:|']
for _,r in lift.iterrows(): lines.append(f"| {int(r.decile)} | {int(r.leads)} | {int(r.activations)} | {r.rate:.1%} | {r.lift_vs_test_average:.2f}x |")
lines += ['', '## Strategic recommendation','', '1. **Professional offices** are the best first self-serve wedge: material volume, high conversion/value and 6-month retention better than micro. Use guided bundles and assisted exception handling.','2. **Micro retail & services** need WhatsApp/partner-assisted low-ticket offers; high price sensitivity and lower monthly value make expensive field acquisition uneconomic.','3. **Small multi-site businesses and manufacturers** are high-value but low-volume/longer-install segments; route qualified leads to named field sellers and installation specialists rather than forcing pure self-serve.','4. Scale referral and inbound-call motions; redesign partner/field economics and targeting before scaling them. Website conversion needs stronger qualification; WhatsApp campaign needs a controlled experiment before scaling based on observed conversion.','5. Pilot target scenario: 12.0% activation, ≤10-day average activation, ≤₹9,250 CAC at unchanged cohort acquisition spend, ≤1 status chase and ≤12% six-month churn. Funnel arithmetic and assumptions are documented in `target_scenario.md`; targets are hypotheses, not measured impact.','', '## Limitations','', '- Synthetic one-quarter data; segment samples, especially manufacturing, are small.','- Payback uses monthly billings as a proxy because contribution margin and gross margin are absent.','- Historical churn/NPS only exist for activated leads; non-activated leads are excluded.','- Model AUC is a holdout estimate and should be recalibrated on a time-based split before production.']
(OUT/'findings.md').write_text('\n'.join(lines),encoding='utf-8')
(OUT/'model_metrics.json').write_text(json.dumps({'test_roc_auc':auc,'test_size':len(yte),'test_activation_rate':base,'features':features},indent=2))
print('AUC',auc,'stages',stages); print(segments.to_string(index=False)); print(sources.to_string(index=False)); print('drops',drops.head(10).to_dict('records'))

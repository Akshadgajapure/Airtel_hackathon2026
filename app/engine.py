from pathlib import Path
import pandas as pd
DATA=Path(__file__).resolve().parents[1]/'data'
CAT=pd.read_csv(DATA/'product_catalogue.csv').fillna('')

def segment_for(t, sites=1):
 t=(t or '').lower()
 if any(x in t for x in ['factory','manufactur','textile','auto-parts','unit','plant']): return 'mfg'
 if int(sites or 1)>=2 or any(x in t for x in ['chain','multi-site','multi site']): return 'multi'
 if any(x in t for x in ['kirana','retail','salon','pharmacy','restaurant','bakery','shop']): return 'micro'
 if any(x in t for x in ['clinic','doctor','ca','coaching','office','legal','diagnostic','consult']): return 'prof'
 return 'micro'

def eligible_products(profile):
 seg=profile.get('segment') or segment_for(profile.get('business_type'), profile.get('sites',1))
 tier=int(profile.get('city_tier',2)); employees=int(profile.get('employees',1)); sites=int(profile.get('sites',1)); gst=bool(profile.get('gstin_active',False))
 base=[]
 for _,r in CAT.iterrows():
  reasons=[]
  if seg not in str(r.target_segments).split(';'): reasons.append('not targeted to this business segment')
  if str(tier) not in str(r.available_city_tiers).split(';'): reasons.append(f'not available in city tier {tier}')
  if employees<int(r.min_employees): reasons.append(f'requires at least {int(r.min_employees)} employees')
  if sites<int(r.min_sites): reasons.append(f'requires at least {int(r.min_sites)} sites')
  if r.requires_gstin=='Y' and not gst: reasons.append('requires an active GSTIN')
  if not reasons: base.append(r.product_id)
 # A dependent item may be offered only when at least one eligible parent can be included in the same quote.
 out=[]
 for pid in base:
  row=CAT[CAT.product_id==pid].iloc[0]; deps=str(row.requires_one_of).strip()
  if not deps or (set(deps.split('|')) & set(base)): out.append(pid)
 return out

def validate_selection(ids,profile):
 ids=list(dict.fromkeys(ids)); eligible=set(eligible_products(profile)); errors=[]
 for pid in ids:
  if pid not in eligible: errors.append(f'{pid} is not eligible for this business profile')
  row=CAT[CAT.product_id==pid]
  if row.empty: errors.append(f'Unknown product {pid}'); continue
  deps=str(row.iloc[0].requires_one_of).strip()
  if deps and not (set(deps.split('|')) & set(ids)): errors.append(f'{pid} requires one of: {deps}')
 return errors

def recommend(profile):
 seg=profile.get('segment') or segment_for(profile.get('business_type'), profile.get('sites',1)); gst=bool(profile.get('gstin_active',False))
 if seg=='micro': ids=['P01','P07']
 elif seg=='prof': ids=['P02','P07','P16','P20']
 elif seg=='multi': ids=['P02','P08','P16','P09','P22']
 else: ids=['P05','P08','P16','P20','P21']
 # remove non-eligible items; retain only catalogue-allowed products
 eligible=set(eligible_products({**profile,'segment':seg}))
 ids=[x for x in ids if x in eligible]
 # Add core fibre if leased line unavailable and a suitable fibre plan exists
 if not any(x in ids for x in ['P01','P02','P03','P04','P05','P06']):
  for x in ['P01','P02','P04']:
   if x in eligible: ids.insert(0,x); break
 errors=validate_selection(ids,{**profile,'segment':seg})
 # Dependencies are always resolved in recommendations; strip dependent product if parent absent.
 if errors:
  ids=[x for x in ids if x not in ['P09','P10','P12','P21','P22','P23'] or not validate_selection([x],{**profile,'segment':seg})]
 return ids

def price_quote(ids,profile,contract_months=None):
 seg=profile.get('segment') or segment_for(profile.get('business_type'), profile.get('sites',1))
 errors=validate_selection(ids,profile)
 if errors: raise ValueError('; '.join(errors))
 rows=[]; monthly=0; setup=0
 for pid in ids:
  r=CAT[CAT.product_id==pid].iloc[0]
  if r.unit=='per site': qty=max(1,int(profile.get('sites',1)))
  elif r.unit=='per user': qty=max(1,int(profile.get('employees',1)))
  elif r.unit=='per device': qty=max(1,int(profile.get('employees',1)))
  elif r.unit=='per line': qty=max(1,int(profile.get('mobile_lines', 1 if seg=='micro' else (2 if seg=='prof' else min(int(profile.get('employees',1)),20)))))
  else: qty=1
  # midpoint price with 5% bundle discount when 3+ distinct items
  unit=(int(r.price_min_inr_per_month)+int(r.price_max_inr_per_month))/2
  monthly+=unit*qty; setup+=int(r.one_time_setup_inr)*qty
  rows.append({'product_id':pid,'name':r.product_name,'qty':qty,'unit':r.unit,'unit_monthly':round(unit),'monthly':round(unit*qty),'setup':int(r.one_time_setup_inr)*qty,'install_days':int(r.typical_install_days),'min_contract':int(r.min_contract_months)})
 catalogue_monthly=round(monthly)
 discount=.05 if len(ids)>=3 else 0
 after_bundle=round(catalogue_monthly*(1-discount)); contract=max([int(CAT[CAT.product_id==p].iloc[0].min_contract_months) for p in ids] or [1])
 chosen=int(contract_months or contract)
 if chosen<contract: chosen=contract
 contract_discount=.05 if chosen>=24 else (.02 if chosen>=12 else 0)
 monthly=round(after_bundle*(1-contract_discount)); gst=round(monthly*.18)
 current_spend=int(profile.get('spend',0) or 0)
 return {'items':rows,'catalogue_monthly':catalogue_monthly,'monthly_subtotal':monthly,'monthly_gst':gst,'monthly_total':monthly+gst,'setup_total':setup,'setup_gst':round(setup*.18),'setup_total_with_gst':round(setup*1.18),'contract_months':chosen,'minimum_contract_months':contract,'bundle_discount_pct':int(discount*100),'contract_discount_pct':int(contract_discount*100),'discount_total_monthly':catalogue_monthly-monthly,'savings_vs_current_spend':current_spend-monthly if current_spend else None,'expected_install_days':max([x['install_days'] for x in rows] or [1]),'savings_note':f'{int(discount*100)}% bundle discount + {int(contract_discount*100)}% contract discount applied before GST' if discount or contract_discount else 'Catalogue midpoint pricing; no discount applied'}

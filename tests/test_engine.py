import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.engine import eligible_products, recommend, validate_selection, price_quote
from app.kyc import gst_checksum

def p(**kw):
 d={'business_type':'Kirana store','employees':3,'sites':1,'city':'Nagpur','city_tier':2,'gstin_active':False,'segment':'micro'};d.update(kw);return d

def test_micro_tier2_without_gstin_core_bundle():
 e=eligible_products(p()); assert 'P01' in e and 'P07' in e and 'P03' not in e

def test_micro_without_gstin_never_gets_gstin_only_products():
 e=eligible_products(p()); assert not {'P03','P05','P06','P10','P12','P13','P21','P24'} & set(e)

def test_micro_advisor_recommendation_is_eligible():
 x=p(); assert not validate_selection(recommend(x),x)

def test_clinic_8_staff_tier2():
 x=p(business_type='Clinic',segment='prof',employees=8); e=eligible_products(x); assert {'P02','P07','P16','P20'} <= set(e); assert 'P03' not in e

def test_clinic_8_staff_tier1_active_gst_can_get_gigabit():
 x=p(business_type='Clinic',segment='prof',employees=8,city_tier=1,gstin_active=True); assert 'P03' in eligible_products(x)

def test_five_store_chain_gets_failover_with_core_link():
 x=p(business_type='Restaurant chain',segment='multi',employees=20,sites=5,gstin_active=True); e=eligible_products(x); assert {'P02','P09','P22'} <= set(e)

def test_sdwan_requires_three_sites_and_ten_staff():
 x=p(segment='multi',employees=10,sites=2,gstin_active=True); assert 'P10' not in eligible_products(x)
 x['sites']=3; assert 'P10' in eligible_products(x)

def test_textile_40_staff_tier2():
 x=p(business_type='Textile unit',segment='mfg',employees=40,sites=1,gstin_active=True); e=eligible_products(x); assert {'P05','P06','P21','P24'} <= set(e)

def test_manufacturer_without_gst_excludes_leased_line_firewall_iot():
 x=p(business_type='Textile unit',segment='mfg',employees=40,sites=1,gstin_active=False); e=eligible_products(x); assert not {'P05','P06','P21','P24'} & set(e)

def test_tier2_cannot_get_fibre_1g():
 x=p(segment='prof',employees=8,city_tier=2,gstin_active=True); assert 'P03' not in eligible_products(x)

def test_static_ip_requires_connectivity_parent():
 x=p(segment='prof',employees=5,gstin_active=True); assert validate_selection(['P11'],x)
 assert not validate_selection(['P01','P11'],x)

def test_cctv_requires_connectivity_parent():
 x=p(segment='micro',employees=4,gstin_active=False); assert validate_selection(['P23'],x)
 assert not validate_selection(['P01','P23'],x)

def test_cloud_telephony_requires_internet_parent():
 x=p(segment='prof',employees=4,gstin_active=True); assert validate_selection(['P12'],x)
 assert not validate_selection(['P02','P12'],x)

def test_managed_firewall_requires_link_and_gst():
 x=p(segment='mfg',employees=15,gstin_active=False); assert 'P21' not in eligible_products(x)
 x['gstin_active']=True; assert validate_selection(['P21'],x); assert not validate_selection(['P05','P21'],x)

def test_product_min_employees_enforced():
 x=p(segment='mfg',business_type='Textile unit',employees=9,gstin_active=True); assert 'P24' not in eligible_products(x)
 x['employees']=10; assert 'P24' in eligible_products(x)

def test_product_min_sites_enforced():
 x=p(segment='multi',employees=15,sites=2,gstin_active=True); assert 'P10' not in eligible_products(x)

def test_quote_calculates_gst_and_setup():
 x=p(segment='multi',employees=12,sites=3,gstin_active=True); q=price_quote(['P02','P09'],x); assert q['monthly_gst']==round(q['monthly_subtotal']*.18); assert q['setup_total']==4500

def test_bundle_discount_applies_three_products():
 x=p(segment='prof',employees=4,gstin_active=True); q=price_quote(['P02','P07','P16'],x); assert q['bundle_discount_pct']==5

def test_quote_rejects_ineligible_product():
 x=p();
 try: price_quote(['P03'],x)
 except ValueError: assert True
 else: assert False

def test_gstin_checksum_known_registry_sample():
 assert gst_checksum('32TTNXB7384T1ZW')

def test_gstin_checksum_rejects_tampered_last_char():
 assert not gst_checksum('32TTNXB7384T1ZA')

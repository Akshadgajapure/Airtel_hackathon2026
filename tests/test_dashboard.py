from fastapi.testclient import TestClient
import sqlite3
import app.main as main


def client_with_temp_db(tmp_path, monkeypatch):
    db_path = tmp_path / 'ops_test.db'
    monkeypatch.setattr(main, 'DB_PATH', db_path)
    main.consent_audit.clear()
    main.esign_audit.clear()
    main.orders.clear()
    main.handoffs.clear()
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE lead_assignments (lead_id TEXT PRIMARY KEY, owner TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Assigned', note TEXT DEFAULT '', updated_at TEXT NOT NULL)")
        conn.execute("CREATE TABLE assignment_events (event_id INTEGER PRIMARY KEY AUTOINCREMENT, lead_id TEXT NOT NULL, owner TEXT NOT NULL, status TEXT NOT NULL, note TEXT DEFAULT '', event_at TEXT NOT NULL)")
    return TestClient(main.app)


def test_analytics_overview_uses_dataset(tmp_path, monkeypatch):
    c = client_with_temp_db(tmp_path, monkeypatch)
    r = c.get('/api/analytics/overview')
    assert r.status_code == 200
    body = r.json()
    assert body['leads'] == 5000
    assert body['activations'] == 368
    assert round(body['conversion'] * 100, 2) == 7.36
    assert body['stage_counts']['Contacted'] == 3406
    assert body['segments'] and body['sources'] and body['drop_reasons']


def test_backoffice_filters_and_pagination(tmp_path, monkeypatch):
    c = client_with_temp_db(tmp_path, monkeypatch)
    r = c.get('/api/backoffice/leads', params={'segment': 'Professional offices', 'limit': 7, 'offset': 0})
    assert r.status_code == 200
    body = r.json()
    assert body['count'] > 0
    assert len(body['leads']) <= 7
    assert all(x['segment'] == 'Professional offices' for x in body['leads'])


def test_assignment_is_saved_and_returned(tmp_path, monkeypatch):
    c = client_with_temp_db(tmp_path, monkeypatch)
    lead = c.get('/api/backoffice/leads', params={'limit': 1}).json()['leads'][0]['lead_id']
    r = c.post('/api/backoffice/assign', json={'lead_id': lead, 'owner': 'Channel Partner', 'status': 'In progress', 'note': 'Test assignment'})
    assert r.status_code == 200 and r.json()['saved'] is True
    saved = c.get('/api/backoffice/assignments').json()
    assert saved['count'] == 1
    assert saved['assignments'][0]['lead_id'] == lead
    assert saved['assignments'][0]['status'] == 'In progress'
    detail = c.get(f'/api/backoffice/lead/{lead}').json()
    assert detail['assignment']['owner'] == 'Channel Partner'
    assert len(detail['activity']) == 1
    assert 'gstin' not in detail and 'udyam_number' not in detail


def test_assignment_rejects_unknown_lead(tmp_path, monkeypatch):
    c = client_with_temp_db(tmp_path, monkeypatch)
    r = c.post('/api/backoffice/assign', json={'lead_id': 'NOT-A-LEAD', 'owner': 'Field Sales'})
    assert r.status_code == 404


def test_csv_export_returns_filtered_lead_records(tmp_path, monkeypatch):
    c = client_with_temp_db(tmp_path, monkeypatch)
    r = c.get('/api/backoffice/export.csv', params={'tier': '1'})
    assert r.status_code == 200
    assert 'text/csv' in r.headers['content-type']
    assert 'lead_id' in r.text and 'propensity' in r.text


def test_lead_detail_rejects_unknown_id(tmp_path, monkeypatch):
    c = client_with_temp_db(tmp_path, monkeypatch)
    assert c.get('/api/backoffice/lead/NOT-A-LEAD').status_code == 404


def test_kyc_upload_requires_consent(tmp_path, monkeypatch):
    c = client_with_temp_db(tmp_path, monkeypatch)
    r = c.post('/api/kyc/upload', data={'consent':'true','doc_type':'gst_certificate'}, files={'file':('test.png', b'not-an-image', 'image/png')})
    assert r.status_code == 403


def test_advisor_returns_catalogue_backed_recommendation(tmp_path, monkeypatch):
    c = client_with_temp_db(tmp_path, monkeypatch)
    r = c.post('/api/advisor', json={'business_type':'Kirana store','employees':3,'sites':1,'city':'Nagpur','city_tier':2,'gstin_active':False,'language':'Hindi'})
    assert r.status_code == 200
    body = r.json()
    assert body['recommended_ids']
    assert body['quote']['monthly_total'] > 0
    assert body['language'] == 'Hindi'


def test_kyc_upload_rejects_non_image_payload_after_consent(tmp_path, monkeypatch):
    c = client_with_temp_db(tmp_path, monkeypatch)
    monkeypatch.setattr(main, 'UPLOADS', tmp_path / 'uploads')
    main.UPLOADS.mkdir(exist_ok=True)
    assert c.post('/api/consent', json={'accepted': True}).status_code == 200
    r = c.post('/api/kyc/upload', data={'consent': 'true', 'doc_type': 'gst_certificate'}, files={'file': ('fake.png', b'not an image', 'image/png')})
    assert r.status_code == 400


def test_kyc_upload_masks_identifiers_and_returns_review_required(tmp_path, monkeypatch):
    from pathlib import Path
    c = client_with_temp_db(tmp_path, monkeypatch)
    upload_dir = tmp_path / 'uploads'
    upload_dir.mkdir()
    monkeypatch.setattr(main, 'UPLOADS', upload_dir)
    monkeypatch.setattr(main, 'ocr_file', lambda path: 'GSTIN 27ABCDE1234X1Z5\nPhone 9876543210')
    assert c.post('/api/consent', json={'accepted': True}).status_code == 200
    sample = Path(main.DATA / 'kyc_documents' / 'K12_gst_certificate.png').read_bytes()
    r = c.post('/api/kyc/upload', data={'consent': 'true', 'doc_type': 'gst_certificate'}, files={'file': ('specimen.png', sample, 'image/png')})
    assert r.status_code == 200
    body = r.json()
    assert body['extraction_status'] == 'review_required'
    assert '9876543210' not in body['masked_preview']
    assert 'XXXXXXXXXX' in body['masked_preview']


def test_csv_export_includes_all_filtered_pages(tmp_path, monkeypatch):
    c = client_with_temp_db(tmp_path, monkeypatch)
    expected = c.get('/api/backoffice/leads', params={'tier': '1', 'limit': 1}).json()['count']
    r = c.get('/api/backoffice/export.csv', params={'tier': '1'})
    assert r.status_code == 200
    assert len(r.text.strip().splitlines()) - 1 == expected


def test_end_to_end_advisor_quote_consent_esign_order_tracker(tmp_path, monkeypatch):
    c = client_with_temp_db(tmp_path, monkeypatch)
    profile = {'business_type':'Kirana store','employees':3,'sites':1,'city':'Nagpur','city_tier':2,'gstin_active':False,'language':'Hindi','spend':1500}
    advisor = c.post('/api/advisor', json=profile)
    assert advisor.status_code == 200
    rec = advisor.json()
    quote = c.post('/api/quote', json={'profile':{**profile,'segment':rec['segment']},'product_ids':rec['recommended_ids']})
    assert quote.status_code == 200 and quote.json()['monthly_total'] > 0
    assert c.post('/api/consent', json={'accepted':True}).status_code == 200
    assert c.post('/api/esign', json={'otp':'123456'}).status_code == 200
    order = c.post('/api/orders', json={'business_name':'Demo Kirana','profile':{**profile,'segment':rec['segment']},'product_ids':rec['recommended_ids']})
    assert order.status_code == 200
    oid = order.json()['order_id']
    for expected in ['KYC verified','Site survey','Installation','Activated']:
        step = c.post(f'/api/orders/{oid}/advance')
        assert step.status_code == 200 and step.json()['status'] == expected
    assert c.get(f'/api/orders/{oid}').json()['status'] == 'Activated'


def test_specimen_kyc_audit_has_expected_exception_cases():
    from app.kyc import batch_report
    rows = {x['applicant']: x for x in batch_report()}
    assert len(rows) == 12
    assert rows['K01']['decision'] == 'NEEDS FIX'
    assert any('Cancelled' in reason for reason in rows['K01']['failures'])
    assert rows['K04']['decision'] == 'NEEDS FIX'
    assert rows['K05']['decision'] == 'NEEDS FIX'
    assert rows['K11']['decision'] == 'NEEDS FIX'
    assert rows['K12']['decision'] == 'AUTO-APPROVE'
    assert rows['K12']['name_match_score'] >= 0.78

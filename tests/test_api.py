from fastapi.testclient import TestClient
from app.main import app
from app.seed import load

def test_fit_check_submission(tmp_path, monkeypatch):
    monkeypatch.setenv('DATABASE_URL', f'sqlite+pysqlite:///{tmp_path}/t.db')
    load('seeds/development_seed.json')
    c=TestClient(app)
    schema=c.get('/api/v1/public/assessments/fit-check').json()
    assert schema['key']=='fit-check'
    payload={'answers':{'name':'A Owner','email':'a@example.com','ownership_status':'active_owner','destination':'los_cabos','rental_restrictions':False,'nights_available':8,'consent':True}}
    r=c.post('/api/v1/public/assessments/fit-check/submissions', json=payload, headers={'Idempotency-Key':'abc'})
    assert r.status_code==200
    token=r.json()['public_token']
    assert c.get(f'/api/v1/public/submissions/{token}/result').json()['outcome']=='qualified_for_paid_audit'
    r2=c.post('/api/v1/public/assessments/fit-check/submissions', json=payload, headers={'Idempotency-Key':'abc'})
    assert r2.json()['idempotent'] is True

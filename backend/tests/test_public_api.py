import os, uuid, requests

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")

def test_root_and_inquiry_crud_contract():
    s=requests.Session()
    r=s.get(BASE_URL+"/api/",timeout=20)
    assert r.status_code == 200 and r.json()["message"] == "AR ELECTRO Projects API"
    payload={"name":"TEST_"+uuid.uuid4().hex[:8],"email":"tester@example.com","phone":"+919998525347","requirement":"Need an embedded project with documentation."}
    r=s.post(BASE_URL+"/api/inquiries",json=payload,timeout=20)
    assert r.status_code == 200
    data=r.json()
    assert data["name"]==payload["name"] and data["email"]==payload["email"] and data["requirement"]==payload["requirement"]
    assert isinstance(data["id"],str) and data["created_at"]

def test_inquiry_validation():
    r=requests.post(BASE_URL+"/api/inquiries",json={"name":"x","email":"bad","phone":"1","requirement":"short"},timeout=20)
    assert r.status_code == 422

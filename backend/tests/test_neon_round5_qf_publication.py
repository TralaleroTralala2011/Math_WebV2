"""Verify QF2 staging is isolated, auth-controlled, and published atomically."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import admin_routes
from app.auth.routes import create_admin_token
from app.roadmap_v2_routes import _data, pool
from database import database as db

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(db,'DATABASE_PATH',tmp_path/'factory.db')
    db.init_database()
    admin_routes.ensure_admin_schema_and_account()
    with TestClient(app) as c:yield c

def admin_headers():
    c=db.get_connection()
    try:
        row=c.execute("SELECT id,username,auth_version FROM admin_accounts LIMIT 1").fetchone()
    finally:c.close()
    token=create_admin_token(row['id'],row['username'],row['auth_version'])
    return {'Authorization':'Bearer '+token}

def test_reviewed_questions_publish_and_appear_in_roadmap(client):
    topic=next(t for t in _data()[0] if t['grade']==10)
    before=len(pool(topic))
    words=['đầu','thứ hai','thứ ba','thứ tư','thứ năm','thứ sáu','thứ bảy','thứ tám','thứ chín','thứ mười']
    candidate={
      'grade':10, 'topic_id':topic['id'],
      'title':'Ứng viên phép cộng cơ bản trong kiểm thử',
      'concept':'Kiểm tra phép cộng số tự nhiên',
      'method':'Tổng hai số nhỏ bằng cách cộng từng đơn vị',
      'conditions':'Số tự nhiên không âm',
      'distinguishing':'Kiểm thử hệ thống xét duyệt, không chứng nhận loại toán mới',
      'questions':[{'question':f'Trong bài kiểm tra lần {name}, một cộng một có kết quả là mấy?',
        'question_type':'multiple_choice', 'difficulty':'nền tảng',
        'choices':['2','3','4','5'],'correct_index':0,'answer':'2',
        'explanation':'Một đơn vị cộng với một đơn vị nữa thì kết quả bằng hai đơn vị.'}
        for name in words]
    }
    auth=admin_headers()
    response=client.post('/api/admin/qf2/candidates',headers=auth,json=candidate)
    assert response.status_code==200,response.text
    form_id=response.json()['id']
    assert len(pool(topic))==before
    assert client.get(f'/api/admin/qf2/candidates/{form_id}').status_code in (401,403)
    details=client.get(f'/api/admin/qf2/candidates/{form_id}',headers=auth)
    assert details.status_code==200 and len(details.json()['questions'])==10
    premature=client.post(f'/api/admin/qf2/candidates/{form_id}/review',headers=auth,
       json={'approved':True,'notes':'Chưa kiểm tra độc lập toàn bộ câu.', 'independently_checked':False})
    assert premature.status_code==409
    reviewed=client.post(f'/api/admin/qf2/candidates/{form_id}/review',headers=auth,
       json={'approved':True,'notes':'Đã đối chiếu từng câu trong môi trường kiểm thử riêng.', 'independently_checked':True})
    assert reviewed.status_code==200,reviewed.text
    assert reviewed.json()['published_questions']==10
    assert len(pool(topic))==before+10
    assert any(q['source']=='qf2-approved' for q in pool(topic))
    repeated=client.post(f'/api/admin/qf2/candidates/{form_id}/review',headers=auth,
       json={'approved':True,'notes':'Đã kiểm tra lại đầy đủ các đáp án.', 'independently_checked':True})
    assert repeated.status_code==409

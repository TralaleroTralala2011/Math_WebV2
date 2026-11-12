"""Mountable FastAPI router. Write operations are disabled without an admin token."""
import hmac
import os
from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field
from . import storage

class AnswerRequest(BaseModel):
    session_id: str=Field(min_length=20,max_length=128)
    answer: str=Field(min_length=1,max_length=500)

class EnqueueRequest(BaseModel):
    per_type: int=Field(10,ge=1,le=10)

class ReviewRequest(BaseModel):
    reviewer: str=Field(min_length=2,max_length=80)

class LimitRequest(BaseModel):
    max_verified: int=Field(ge=0)

class CostCeilingRequest(BaseModel):
    cost_limit_cents: int=Field(ge=0)


def make_router(db_path, admin_token=None):
    router=APIRouter(prefix='/api/factory',tags=['Question Factory'])
    token=admin_token if admin_token is not None else os.environ.get('QF_ADMIN_TOKEN','')

    def admin_guard(x_admin_token: str|None=Header(default=None)):
        if not token:
            raise HTTPException(503,'Admin API disabled: configure QF_ADMIN_TOKEN')
        if not x_admin_token or not hmac.compare_digest(x_admin_token,token):
            raise HTTPException(403,'Admin token required')

    @router.get('/health')
    def health():
        return {'ok':True,'storage':'sqlite-pilot'}

    @router.get('/catalog')
    def topic_catalog():
        summary=storage.progress(db_path)
        topics=storage.list_topics(db_path)
        return {
            'items': topics,
            # This flag is a statement about the entire catalog, not the presence
            # of an approval: only full coverage of all 150*2000 types qualifies.
            'method_independence_certified': len(topics)==150 and all(
                row['certified_independent_types']>=2000 for row in topics),
            'independent_types_certified': summary['certified_independent_types'],
            'quality_gate': 'independence_certifications_are_separate_from_generation_approvals',
        }

    @router.get('/progress')
    def progress():
        return storage.progress(db_path)

    @router.get('/topics/{topic_id}/questions')
    def questions(topic_id: str,limit: int=Query(20,ge=1,le=100),after_id: str=''):
        return {'items':storage.read_questions(db_path,topic_id,limit,after_id)}

    @router.get('/next')
    def next_question(topic_id: str=Query(min_length=1, max_length=100),
                      surface: str=Query('practice', pattern='^(practice|learning|roadmap|battle)$'),
                      sequence_key: str | None=Query(None, min_length=12, max_length=128,
                         pattern='^[A-Za-z0-9_-]+$')):
        # Every surface accesses the same approved question store; integration into existing
        # gameplay engines requires separate regression tests and is not enabled implicitly.
        try:
            found=storage.create_answer_session(db_path,topic_id,sequence_key=sequence_key)
        except storage.LimitReached as e:
            raise HTTPException(429,str(e)) from e
        if found is None:
            raise HTTPException(404,'No approved and verified question for this topic')
        found['surface']=surface
        return found

    @router.post('/answer')
    def answer(body:AnswerRequest):
        graded=storage.submit_answer_session(db_path,body.session_id,body.answer)
        if graded is None:
            raise HTTPException(404,'Session missing, expired or already graded')
        return graded

    @router.post('/admin/types/{archetype_id}/approve',dependencies=[Depends(admin_guard)])
    def approve(archetype_id: str, body:ReviewRequest):
        try: storage.approve(db_path,archetype_id,body.reviewer)
        except ValueError as e: raise HTTPException(400,str(e)) from e
        return {'ok':True}

    @router.get('/admin/topics/{topic_id}/questions',dependencies=[Depends(admin_guard)])
    def admin_questions(topic_id: str,limit:int=Query(20,ge=1,le=100),after_id:str=''):
        return {'items':storage.read_questions(db_path,topic_id,limit,after_id,include_answers=True)}

    @router.post('/admin/enqueue',dependencies=[Depends(admin_guard)])
    def enqueue(body:EnqueueRequest):
        return {'jobs_enqueued':storage.enqueue(db_path,body.per_type)}

    @router.post('/admin/pause',dependencies=[Depends(admin_guard)])
    def pause():
        storage.set_paused(db_path,True)
        return {'paused':True}

    @router.post('/admin/resume',dependencies=[Depends(admin_guard)])
    def resume():
        storage.set_paused(db_path,False)
        return {'paused':False}

    @router.post('/admin/limit',dependencies=[Depends(admin_guard)])
    def set_limit(body:LimitRequest):
        storage.set_limit(db_path,body.max_verified)
        return {'max_verified':body.max_verified}

    @router.post('/admin/cost-ceiling',dependencies=[Depends(admin_guard)])
    def set_cost_ceiling(body:CostCeilingRequest):
        try: storage.set_cost_limit(db_path,body.cost_limit_cents)
        except ValueError as e: raise HTTPException(400,str(e)) from e
        return {'cost_limit_cents':body.cost_limit_cents}

    return router


def create_app(db_path=None,admin_token=None):
    if db_path is None:
        from .bootstrap import database_path as default_database_path
        db_path = default_database_path()
    storage.initialize(db_path)
    app=FastAPI(title='Question Factory Pilot')
    app.include_router(make_router(db_path,admin_token))
    return app

# Import-safe router. Standalone API is in question_factory.standalone.


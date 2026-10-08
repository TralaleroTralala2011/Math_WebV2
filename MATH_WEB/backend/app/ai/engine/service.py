import time, random, uuid
from ..config import MAX_COUNT, MAX_TOPICS, QUESTION_TTL_SECONDS
from .knowledge_service import KnowledgeService
from .generator import QuestionGenerator
from .validator import validate, ValidationError, fingerprint
from .difficulty import normalize
from .adaptive import next_difficulty
from .feedback import feedback

class QuestionStore:
    def __init__(self): self.items={}
    def put(self,q):
        self.items[q["id"]]=(time.time(),q)
    def get(self,qid):
        item=self.items.get(qid)
        if not item: return None
        if time.time()-item[0] > QUESTION_TTL_SECONDS:
            self.items.pop(qid,None); return None
        return item[1]
    def cleanup(self):
        now=time.time()
        for k,(t,_) in list(self.items.items()):
            if now-t>QUESTION_TTL_SECONDS: self.items.pop(k,None)

class AIQuestionService:
    def __init__(self):
        self.knowledge=KnowledgeService()
        self.generator=QuestionGenerator(self.knowledge)
        self.store=QuestionStore()

    def topics(self,grade=None): return self.knowledge.list_topics(grade)

    def generate_one(self,grade,topic_id,difficulty="medium",question_type="multiple_choice",seen=None,game_id=None):
        if self.knowledge.get(topic_id) is None: raise ValueError("Unknown topic")
        seen=seen or set()
        last=None
        for _ in range(20):
            q=self.generator.generate(grade,topic_id,normalize(difficulty),question_type,game_id)
            try: validate(q)
            except ValidationError as e: last=e; continue
            if q["fingerprint"] in seen: continue
            self.store.put(q)
            return q
        raise RuntimeError(f"Could not generate a valid unique question: {last}")

    def generate_set(self,grade,topics,count,difficulty="medium",question_type="multiple_choice",history=None,game_id=None):
        if count<1 or count>MAX_COUNT: raise ValueError("count out of range")
        topics=self.knowledge.normalize_topics(grade,topics)
        if not topics: raise ValueError("No valid topics")
        current=next_difficulty(history,normalize(difficulty)) if history else normalize(difficulty)
        out=[]; seen=set()
        for i in range(count):
            topic=topics[i%len(topics)] if len(topics)>1 else topics[0]
            # A set mixes difficulty around requested level while preserving control.
            level=current
            if count>=8 and i>=count*0.65: level={"easy":"medium","medium":"hard","hard":"expert","expert":"expert"}[current]
            q=self.generate_one(grade,topic,level,question_type,seen,game_id)
            seen.add(q["fingerprint"]); out.append(q)
        return {"set_id":uuid.uuid4().hex,"grade":grade,"topics":topics,"difficulty":current,"count":len(out),"game_id":game_id,"questions":out}

    def answer(self,qid,user_answer):
        q=self.store.get(qid)
        if not q: raise KeyError("question_expired_or_not_found")
        correct=self._check(q,user_answer)
        return {"question_id":qid,"correct":correct,"feedback":feedback(correct),"correct_answer":q["answer"] if not correct else None,"solution":q["solution"] if not correct else None}

    def _check(self,q,user_answer):
        t=q["question_type"]
        if t=="multiple_choice": return str(user_answer).strip()==str(q["answer"]).strip()
        if t=="short_answer":
            from .solver import equivalent
            return equivalent(user_answer,q["answer"])
        if t=="true_false":
            vals=user_answer if isinstance(user_answer,list) else []
            return [bool(x) for x in vals]==q["statement_answers"]
        return False

    def battle_topics(self,a,b):
        a=[x for x in a if self.knowledge.get(x)]
        b=[x for x in b if self.knowledge.get(x)]
        common=[]
        for x in a:
            if x in b and x not in common: common.append(x)
        return common[:MAX_TOPICS]

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
        self.recent_families={}

    def topics(self,grade=None): return self.knowledge.list_topics(grade)

    def generate_one(self,grade,topic_id,difficulty="medium",question_type="multiple_choice",seen=None,game_id=None,recent_families=None,seen_structures=None,seen_variations=None):
        if self.knowledge.get(topic_id) is None: raise ValueError("Unknown topic")
        seen=set(seen or set())
        seen_structures=set(seen_structures or set())
        seen_variations=set(seen_variations or set())
        last=None
        recent_families = list(recent_families or self.recent_families.get(game_id, []))

        # Phase 1: strict diversity. A question must not repeat the same
        # mathematical structure or the same bank variation already used.
        for strict in (True, False):
            for _ in range(150):
                q=self.generator.generate(grade,topic_id,normalize(difficulty),question_type,game_id,recent_families)
                try: validate(q)
                except ValidationError as e: last=e; continue

                variation = self._variation_key(q)
                if q["fingerprint"] in seen:
                    continue
                if strict and q.get("structure_fingerprint") in seen_structures:
                    continue
                if strict and variation in seen_variations:
                    continue

                self.store.put(q)
                if game_id:
                    bucket=self.recent_families.setdefault(game_id, [])
                    family=q.get("template_family")
                    if family:
                        bucket.append(family)
                        del bucket[:-12]
                return q

        raise RuntimeError(f"Could not generate a valid unique question: {last}")

    @staticmethod
    def _variation_key(q):
        # This key represents the visible bank variation, not just the random
        # numbers. It makes repeated "same question, different numbers" much
        # harder to slip into one practice set.
        return "|".join(str(q.get(k, "")) for k in (
            "game_id", "template_family", "generation_style", "reasoning_mode", "context", "diversity_key"
        ))

    def generate_set(self,grade,topics,count,difficulty="medium",question_type="multiple_choice",history=None,game_id=None):
        if count<1 or count>MAX_COUNT: raise ValueError("count out of range")
        topics=self.knowledge.normalize_topics(grade,topics)
        if not topics: raise ValueError("No valid topics")
        current=next_difficulty(history,normalize(difficulty)) if history else normalize(difficulty)
        out=[]; seen=set()
        seen_structures=set()
        seen_variations=set()
        recent_families=[]
        for item in (history or []):
            if isinstance(item, dict):
                if item.get("structure_fingerprint"): seen_structures.add(item["structure_fingerprint"])
                if item.get("fingerprint"): seen.add(item["fingerprint"])
                if item.get("template_family"): recent_families.append(item["template_family"])
                if item.get("variation_key"): seen_variations.add(item["variation_key"])
        for i in range(count):
            # Shuffle topic order once so selected topics do not always appear
            # in the exact same repeating sequence.
            if i == 0:
                topic_order=list(topics); random.shuffle(topic_order)
            topic=topic_order[i%len(topic_order)] if len(topic_order)>1 else topic_order[0]
            level=current
            if count>=8 and i>=count*0.65: level={"easy":"medium","medium":"hard","hard":"expert","expert":"expert"}[current]
            q=self.generate_one(grade,topic,level,question_type,seen,game_id,recent_families[-10:],seen_structures,seen_variations)
            q["variation_key"]=self._variation_key(q)
            seen.add(q["fingerprint"]); seen_structures.add(q.get("structure_fingerprint")); seen_variations.add(q["variation_key"]); out.append(q)
            if q.get("template_family"): recent_families.append(q["template_family"])
        return {"set_id":uuid.uuid4().hex,"grade":grade,"topics":topics,"difficulty":current,"count":len(out),"game_id":game_id,"questions":out}

    def answer(self,qid,user_answer):
        q=self.store.get(qid)
        if not q: raise KeyError("question_expired_or_not_found")
        correct=self._check(q,user_answer)
        return {
            "question_id": qid,
            "correct": correct,
            "feedback": feedback(correct),
            # Always return the solution, including when the student is correct.
            "correct_answer": q["answer"],
            "solution": q.get("solution", q.get("explanation", "")),
            "explanation": q.get("explanation", q.get("solution", "")),
        }

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

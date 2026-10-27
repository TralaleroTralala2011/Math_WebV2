import time, random, uuid, json, re
from database.database import get_connection
from ..config import MAX_COUNT, MAX_TOPICS, QUESTION_TTL_SECONDS
from .knowledge_service import KnowledgeService
from .generator import QuestionGenerator
from .problem_generator import ProblemGenerator
from .validator import validate, ValidationError, fingerprint
from .difficulty import normalize
from .adaptive import next_difficulty
from .feedback import feedback
from .explanation import build_detailed_solution
from .topic_expansion import geometry_diagram
from .question_history import QuestionHistory

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
        # Additive multi-part problem layer. The legacy/super-bank engine remains the source for normal questions.
        self.problem_generator=ProblemGenerator(self.knowledge, self.generator)
        self.store=QuestionStore()
        self.recent_families={}
        # Persistent ledger prevents exact repeats across separate practice sets and restarts.
        self.question_history = QuestionHistory()

    def topics(self,grade=None): return self.knowledge.list_topics(grade)

    def _curated_admin_candidates(self, grade, topic_id, difficulty, question_type, game_id=None):
        """Load reviewed admin-authored items for the exact knowledge topic, if any."""
        type_aliases = {"short_answer": {"short_answer", "written"}, "multiple_choice": {"multiple_choice"}, "true_false": {"true_false"}}
        allowed_types = type_aliases.get(question_type, {question_type})
        topic_info = self.knowledge.get(topic_id) or {}
        topic_name = str(topic_info.get("name", "")).strip().casefold()
        wanted = str(topic_id).strip().casefold()
        level_aliases = {"easy": {"easy", "foundation", "nền tảng", "sơ cấp"},
                         "medium": {"medium", "intermediate", "trung cấp"},
                         "hard": {"hard", "advanced", "nâng cao", "expert", "hell"}}
        accepted_levels = level_aliases.get(normalize(difficulty), {str(difficulty).casefold()})
        conn = get_connection()
        try:
            rows = conn.execute("SELECT * FROM admin_question_bank WHERE grade=? ORDER BY id DESC LIMIT 500", (grade,)).fetchall()
        finally:
            conn.close()
        matched = []
        for row in rows:
            item = dict(row)
            stored_topic = str(item.get("topic", "")).strip().casefold()
            stored_type = str(item.get("question_type", "")).strip().casefold()
            stored_level = str(item.get("difficulty", "")).strip().casefold()
            if stored_topic not in {wanted, topic_name}:
                continue
            stored_game_id = str(item.get("game_id", "") or "").strip()
            requested_game_id = str(game_id or "").strip()
            # An empty game_id marks a general bank question usable by practice and games.
            # A non-empty game_id remains restricted to that exact game.
            if stored_game_id and stored_game_id != requested_game_id:
                continue
            if stored_type not in allowed_types:
                continue
            if stored_level and stored_level not in accepted_levels:
                continue
            try:
                choices = json.loads(item.get("choices_json") or "[]")
            except Exception:
                choices = []
            item["choices"] = choices if isinstance(choices, list) else []
            matched.append(item)
        random.shuffle(matched)
        return matched

    def _build_curated_question(self, item, grade, topic_id, difficulty, question_type):
        stored_type = str(item.get("question_type", ""))
        choices = [str(x).strip() for x in item.get("choices", []) if str(x).strip()]
        answer = str(item.get("correct_answer", "")).strip()
        if question_type == "multiple_choice":
            if len(choices) != 4 or len(set(choices)) != 4:
                return None
            if answer not in choices:
                match = re.match(r"^([A-D])(?:\.|\)|\s|$)", answer, re.I)
                if match:
                    idx = ord(match.group(1).upper()) - ord("A")
                    if 0 <= idx < len(choices): answer = choices[idx]
            if answer not in choices:
                return None
            options = choices
        elif question_type == "true_false":
            if len(choices) != 4:
                return None
            tokens = [x.strip().casefold() for x in re.split(r"[,;|]", answer) if x.strip()]
            truth_map = {"true": True, "t": True, "đ": True, "đúng": True, "1": True,
                         "false": False, "f": False, "s": False, "sai": False, "0": False}
            if len(tokens) != 4 or any(t not in truth_map for t in tokens):
                return None
            statement_answers = [truth_map[t] for t in tokens]
            options = []
        else:
            options = []
        q = {
            "id": uuid.uuid4().hex, "grade": grade, "topic": topic_id,
            "difficulty": normalize(difficulty), "question_type": question_type,
            "question": str(item.get("question", "")).strip(),
            "answer": answer, "solution": str(item.get("explanation", "")).strip() or "Lời giải đang được bổ sung.",
            "explanation": str(item.get("explanation", "")).strip(), "options": options,
            "archetype": f"admin_bank_{item['id']}", "template_family": f"admin_bank_{item['id']}",
            "generation_style": "admin_curated", "source": item.get("source", "Admin MATH_WEB"),
            "knowledge_name": (self.knowledge.get(topic_id) or {}).get("name", topic_id),
            "game_id": str(item.get("game_id", "") or ""), "admin_question_id": item["id"]
        }
        if question_type == "true_false":
            q["statements"] = choices
            q["statement_answers"] = statement_answers
            q["answer"] = ",".join("Đúng" if x else "Sai" for x in statement_answers)
        return q

    def generate_one(self,grade,topic_id,difficulty="medium",question_type="multiple_choice",seen=None,game_id=None,recent_families=None,seen_structures=None,seen_variations=None,seen_archetypes=None):
        if self.knowledge.get(topic_id) is None: raise ValueError("Unknown topic")
        seen=set(seen or set())
        seen_structures=set(seen_structures or set())
        seen_variations=set(seen_variations or set())
        seen_archetypes=set(seen_archetypes or set())
        # Recent archetypes are avoided first, while exact fingerprints are blocked
        # across sessions by the persistent ledger.
        seen_archetypes.update(self.question_history.recent_archetypes(topic_id, limit=8))
        seen_structures.update(self.question_history.recent_structures(topic_id, limit=10))
        seen_variations.update(self.question_history.recent_variations(topic_id, limit=10))
        last=None
        recent_families = list(recent_families or self.recent_families.get(game_id, []))

        # Admin-reviewed questions are a first-class source for the matching topic.
        # They pass the same validation and duplicate gates as generated questions.
        for item in self._curated_admin_candidates(grade, topic_id, difficulty, question_type, game_id):
            q = self._build_curated_question(item, grade, topic_id, difficulty, question_type)
            if not q:
                continue
            try:
                validate(q)
            except ValidationError:
                continue
            variation = self._variation_key(q)
            if q["fingerprint"] in seen or self.question_history.question_seen(q.get("question", "")):
                continue
            if q.get("structure_fingerprint") in seen_structures or variation in seen_variations:
                continue
            if q.get("archetype") in seen_archetypes:
                continue
            self.store.put(q)
            self.question_history.record_question(q)
            if game_id:
                bucket = self.recent_families.setdefault(game_id, [])
                bucket.append(q.get("template_family"))
                del bucket[:-12]
            return q

        # Phase 1: strict diversity. A question must not repeat the same
        # mathematical structure or the same bank variation already used.
        for strict in (True, False):
            for _ in range(150):
                q=self.generator.generate(grade,topic_id,normalize(difficulty),question_type,game_id,recent_families)
                try: validate(q)
                except ValidationError as e: last=e; continue

                variation = self._variation_key(q)
                if q["fingerprint"] in seen or self.question_history.question_seen(q.get("question", "")):
                    continue
                if strict and q.get("structure_fingerprint") in seen_structures:
                    continue
                if strict and variation in seen_variations:
                    continue
                # Within one generated set, avoid repeating the same named
                # mathematical archetype whenever enough alternatives exist.
                if strict and q.get("archetype") and q.get("archetype") in seen_archetypes:
                    continue

                q["variation_key"] = variation
                self.store.put(q)
                self.question_history.record_question(q)
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
            "game_id", "template_family", "generation_style", "context", "archetype", "topic_group"
        ))

    def generate_set(self,grade,topics,count,difficulty="medium",question_type="multiple_choice",history=None,game_id=None):
        if count<1 or count>MAX_COUNT: raise ValueError("count out of range")
        if question_type not in {"multiple_choice", "short_answer", "true_false", "mixed"}:
            raise ValueError("Unsupported question type")
        topics=self.knowledge.normalize_topics(grade,topics)
        if not topics: raise ValueError("No valid topics")
        current=normalize(difficulty)
        out=[]; seen=set()
        seen_structures=set()
        seen_variations=set()
        seen_archetypes=set()
        recent_families=[]
        mixed_types=["multiple_choice", "short_answer", "true_false"]
        random.shuffle(mixed_types)
        for item in (history or []):
            if isinstance(item, dict):
                if item.get("structure_fingerprint"): seen_structures.add(item["structure_fingerprint"])
                if item.get("fingerprint"): seen.add(item["fingerprint"])
                if item.get("template_family"): recent_families.append(item["template_family"])
                if item.get("variation_key"): seen_variations.add(item["variation_key"])
                if item.get("archetype"): seen_archetypes.add(item["archetype"])
        for i in range(count):
            # Shuffle topic order once so selected topics do not always appear
            # in the exact same repeating sequence.
            if i == 0:
                topic_order=list(topics); random.shuffle(topic_order)
            topic=topic_order[i%len(topic_order)] if len(topic_order)>1 else topic_order[0]
            # Keep the selected level stable across a question set. Adaptive
            # difficulty can still react to learner history above, but a user
            # who selected Nền tảng should not silently receive nâng cao items
            # just because the set contains ten questions.
            level=current
            item_type = mixed_types[i % len(mixed_types)] if question_type == "mixed" else question_type
            q=self.generate_one(grade,topic,level,item_type,seen,game_id,recent_families[-10:],seen_structures,seen_variations,seen_archetypes)
            q["variation_key"]=self._variation_key(q)
            # Prefer a diagram reconstructed from this exact question whenever
            # its wording contains coordinate, slope, graph, or geometric data.
            # A stale template illustration must never override the actual prompt.
            question_text = q.get("question", "")
            generated_diagram = geometry_diagram(topic, question_text, q.get("answer", ""))
            explicit_figure = any(token in str(question_text).lower() for token in (
                "tọa độ", "toa do", "hệ số góc", "he so goc", "đồ thị", "do thi",
                "đường thẳng", "duong thang", "đường tròn", "duong tron", "tam giác",
                "tam giac", "hình chóp", "hinh chop", "oxyz", "mặt phẳng", "mat phang",
            ))
            diagram = generated_diagram if (generated_diagram and explicit_figure) else (q.get("diagram") or generated_diagram)
            if diagram:
                q["diagram"] = diagram
            seen.add(q["fingerprint"]); seen_structures.add(q.get("structure_fingerprint")); seen_variations.add(q["variation_key"]);
            if q.get("archetype"): seen_archetypes.add(q["archetype"])
            out.append(q)
            if q.get("template_family"): recent_families.append(q["template_family"])
        return {"set_id":uuid.uuid4().hex,"grade":grade,"topics":topics,"difficulty":current,"count":len(out),"game_id":game_id,"questions":out}


    def generate_problem_set(self,grade,topics,count,difficulty="medium",problem_parts=4,history=None,game_id=None):
        if count<1 or count>MAX_COUNT: raise ValueError("count out of range")
        topics=self.knowledge.normalize_topics(grade,topics)
        if not topics: raise ValueError("No valid topics")
        current=normalize(difficulty)
        problems=[]
        flat=[]
        seen_titles=set()
        for i in range(count):
            topic=topics[i % len(topics)]
            problem=None
            for _ in range(40):
                candidate=self.problem_generator.generate(grade,topic,current,problem_parts,"mixed",game_id)
                signature=(candidate.get("archetype"),candidate.get("title"),candidate.get("context"))
                persistent_signature = " | ".join(str(x or "") for x in signature)
                if signature not in seen_titles and not self.question_history.problem_seen(persistent_signature):
                    problem=candidate
                    seen_titles.add(signature)
                    break
            if problem is None:
                # Never silently return a repeated scenario after exhausting retries.
                raise RuntimeError("Could not generate a new unique problem after repeated attempts; try another topic or difficulty.")
            self.question_history.record_problem(topic, grade, current, str(problem.get("archetype", "")), " | ".join(str(problem.get(k, "") or "") for k in ("archetype", "title", "context")))
            problem_id=problem["id"]
            stored_parts=[]
            for part in problem.get("parts",[]):
                q=dict(part)
                q["problem_id"]=problem_id
                q["problem_title"]=problem.get("title","")
                q["problem_context"]=problem.get("context","")
                q["problem_data"]=problem.get("data",{})
                q["problem_archetype"]=problem.get("archetype","")
                q["knowledge_name"]=self.knowledge.get(topic)["name"]
                q["grade"]=grade
                q["topic"]=topic
                q["difficulty"]=current
                q["game_id"]=game_id or ""
                q["fingerprint"]=fingerprint(str(q.get("problem_context", "")) + " | " + str(q.get("question", "")))
                q["structure_fingerprint"]=fingerprint(str(q.get("problem_archetype", "")) + " | " + str(q.get("part", "")) + " | " + str(q.get("question", "")))
                self.store.put(q)
                stored_parts.append(q)
                flat.append(q)
            problem["parts"]=stored_parts
            problems.append(problem)
        return {
            "set_id":uuid.uuid4().hex,
            "mode":"problem",
            "problem_mode":True,
            "grade":grade,
            "topics":topics,
            "difficulty":current,
            "count":len(problems),
            "problem_count":len(problems),
            "question_count":len(flat),
            "game_id":game_id,
            "problems":problems,
            "questions":flat,
        }

    def answer(self,qid,user_answer):
        q=self.store.get(qid)
        if not q: raise KeyError("question_expired_or_not_found")
        correct=self._check(q,user_answer)
        raw_solution = q.get("solution", q.get("explanation", ""))
        detailed_solution = build_detailed_solution(
            q.get("question", ""), raw_solution, q.get("answer"),
            q.get("topic", ""), q.get("game_id")
        )
        return {
            "question_id": qid,
            "correct": correct,
            "feedback": feedback(correct),
            # Always return a student-friendly, stepwise solution after answering.
            "correct_answer": q["answer"],
            "solution": detailed_solution,
            "explanation": detailed_solution,
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

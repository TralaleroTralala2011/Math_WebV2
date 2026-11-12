"""Durable SQLite pilot queue with short atomic transactions.

For large-scale/multi-host deployments, migrate this interface to PostgreSQL
with SELECT ... FOR UPDATE SKIP LOCKED; do not claim SQLite is a 24/7 cluster.
"""
from __future__ import annotations
import json
import sqlite3
import time
import uuid
from pathlib import Path
from contextlib import contextmanager, closing


def connect(path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, isolation_level=None, timeout=30, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA busy_timeout=30000")
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA foreign_keys=ON")
    return con


@contextmanager
def transaction(con):
    con.execute("BEGIN IMMEDIATE")
    try:
        yield
        con.execute("COMMIT")
    except BaseException:
        con.execute("ROLLBACK")
        raise


def initialize(path):
    with closing(connect(path)) as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS topics (
            id TEXT PRIMARY KEY, grade INTEGER NOT NULL CHECK(grade IN (10,11,12)),
            name TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS archetypes (
            id TEXT PRIMARY KEY, topic_id TEXT NOT NULL REFERENCES topics(id),
            family TEXT NOT NULL, name TEXT NOT NULL,
            method_signature TEXT NOT NULL, difficulty TEXT NOT NULL,
            review_status TEXT NOT NULL DEFAULT 'pending'
              CHECK(review_status IN ('pending','approved','rejected')),
            reviewer TEXT, reviewed_at REAL,
            UNIQUE(topic_id,method_signature)
        );
        -- Mathematical independence requires evidence separate from approval
        -- to generate questions. No candidate is certified by seed/approve.
        CREATE TABLE IF NOT EXISTS independence_certifications (
            archetype_id TEXT PRIMARY KEY REFERENCES archetypes(id),
            reviewer TEXT NOT NULL,
            evidence_json TEXT NOT NULL,
            certified_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY, archetype_id TEXT NOT NULL UNIQUE REFERENCES archetypes(id),
            desired INTEGER NOT NULL CHECK(desired BETWEEN 1 AND 10),
            status TEXT NOT NULL DEFAULT 'pending'
              CHECK(status IN ('pending','leased','done','failed')),
            attempts INTEGER NOT NULL DEFAULT 0,
            max_attempts INTEGER NOT NULL DEFAULT 3,
            lease_owner TEXT, lease_until REAL, next_attempt_at REAL NOT NULL DEFAULT 0,
            last_error TEXT, updated_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS questions (
            id TEXT PRIMARY KEY,
            archetype_id TEXT NOT NULL REFERENCES archetypes(id),
            ordinal INTEGER NOT NULL, fingerprint TEXT NOT NULL UNIQUE,
            stem TEXT NOT NULL, answer TEXT NOT NULL, solution TEXT NOT NULL,
            params_json TEXT NOT NULL, difficulty TEXT NOT NULL,
            validation_json TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('verified','rejected')),
            verified_at REAL NOT NULL,
            UNIQUE(archetype_id,ordinal)
        );
        CREATE TABLE IF NOT EXISTS control (
            id INTEGER PRIMARY KEY CHECK(id=1), paused INTEGER NOT NULL DEFAULT 0,
            max_verified INTEGER NOT NULL DEFAULT 0,
            cost_limit_cents INTEGER NOT NULL DEFAULT 0,
            cost_used_cents INTEGER NOT NULL DEFAULT 0,
            cost_reserved_cents INTEGER NOT NULL DEFAULT 0
        );
        INSERT OR IGNORE INTO control(id,paused,max_verified,cost_limit_cents,cost_used_cents)
            VALUES(1,0,0,0,0);
        CREATE TABLE IF NOT EXISTS answer_sessions (
            session_id TEXT PRIMARY KEY, question_id TEXT NOT NULL REFERENCES questions(id),
            expires_at REAL NOT NULL, used_at REAL
        );
        CREATE INDEX IF NOT EXISTS answer_sessions_expire ON answer_sessions(expires_at);
        CREATE TABLE IF NOT EXISTS budget_reservations (
            request_id TEXT PRIMARY KEY, reserved_cents INTEGER NOT NULL CHECK(reserved_cents>=0),
            actual_cents INTEGER, status TEXT NOT NULL CHECK(status IN ('reserved','settled','released')),
            created_at REAL NOT NULL, updated_at REAL NOT NULL
        );
        CREATE INDEX IF NOT EXISTS jobs_next ON jobs(status,next_attempt_at,lease_until);
        CREATE INDEX IF NOT EXISTS q_topic ON questions(archetype_id,status,id);
        """)
        # Non-destructive schema migration: older pilot DBs have neither field.
        cols = {row['name'] for row in con.execute('PRAGMA table_info(answer_sessions)')}
        if 'sequence_hash' not in cols:
            con.execute('ALTER TABLE answer_sessions ADD COLUMN sequence_hash TEXT')
        if 'created_at' not in cols:
            con.execute('ALTER TABLE answer_sessions ADD COLUMN created_at REAL')
        con.execute('CREATE INDEX IF NOT EXISTS answer_sessions_sequence_recent '
                    'ON answer_sessions(sequence_hash,created_at DESC)')


def seed_samples(path):
    """Nine REVIEW-PENDING teaching examples. No artificial type-count inflation.

    Import into the official catalog when present; standalone pilot tests still
    support an empty, seven-topic sandbox database.
    """
    from .catalog import SAMPLES
    canonical = {
        "10-menh-de-tap-hop": "menh_de_tap_hop",
        "10-phuong-trinh": "phuong_trinh",
        "10-hinh-hoc": "hinh_hoc_co_ban_10",
        "11-day-so": "day_so",
        "11-dao-ham": "dao_ham",
        "12-nguyen-ham-tich-phan": "nguyen_ham_tich_phan",
        "12-toa-do-khong-gian": "toa_do_khong_gian",
    }
    with closing(connect(path)) as con, transaction(con):
        is_canonical=con.execute('SELECT COUNT(*) FROM topics').fetchone()[0]>=150
        for topic, grade, name, types in SAMPLES:
            linked_id = canonical[topic] if is_canonical else topic
            if is_canonical:
                exists=con.execute('SELECT 1 FROM topics WHERE id=? AND grade=?',
                                   (linked_id,grade)).fetchone()
                if not exists:
                    raise ValueError(f'catalog missing required topic {linked_id}')
            else:
                con.execute("INSERT OR IGNORE INTO topics VALUES(?,?,?)", (linked_id,grade,name))
            for slug, family, title, signature, difficulty in types:
                con.execute("""INSERT OR IGNORE INTO archetypes
                    (id,topic_id,family,name,method_signature,difficulty)
                    VALUES(?,?,?,?,?,?)""", (slug,linked_id,family,title,signature,difficulty))


def seed_curated(path):
    # Register implemented candidate methods, pending explicit review.
    from .expanded_catalog import BLUEPRINTS
    with closing(connect(path)) as con, transaction(con):
        for family, topic_id, name, signature, difficulty in BLUEPRINTS:
            if con.execute('SELECT 1 FROM topics WHERE id=?',(topic_id,)).fetchone() is None:
                raise ValueError(f'150-topic catalog missing {topic_id}')
            con.execute('''INSERT OR IGNORE INTO archetypes
                 (id,topic_id,family,name,method_signature,difficulty)
                 VALUES(?,?,?,?,?,?)''',
                 (f'v113-{family}',topic_id,family,name,signature,difficulty))
    return len(BLUEPRINTS)



def seed_v114(path):
    # Register V114 candidate methods under a review lock. Never auto-approve.
    from .v114_catalog import BLUEPRINTS
    with closing(connect(path)) as con, transaction(con):
        for family, topic_id, name, signature, difficulty in BLUEPRINTS:
            if con.execute('SELECT 1 FROM topics WHERE id=?',(topic_id,)).fetchone() is None:
                raise ValueError(f'catalog missing {topic_id}')
            con.execute("""INSERT OR IGNORE INTO archetypes
                 (id,topic_id,family,name,method_signature,difficulty)
                 VALUES(?,?,?,?,?,?)""",
                 (f'v114-{family}',topic_id,family,name,signature,difficulty))
    return len(BLUEPRINTS)


def seed_v116(path):
    # Research candidates remain pending independent-method/expert review.
    from .v116_research import METHODS
    with closing(connect(path)) as con, transaction(con):
        for item in METHODS:
            if con.execute('SELECT 1 FROM topics WHERE id=?', (item.topic,)).fetchone() is None:
                raise ValueError(f'catalog missing {item.topic}')
            con.execute('''INSERT OR IGNORE INTO archetypes
                 (id,topic_id,family,name,method_signature,difficulty)
                 VALUES(?,?,?,?,?,?)''',
                 (item.family,item.topic,item.family,item.title,item.signature,item.difficulty))
    return len(METHODS)


def seed_v117(path):
    # Register V117 candidates, pending human review, never publish automatically.
    from .v117_research import METHODS
    with closing(connect(path)) as con, transaction(con):
        for item in METHODS:
            if con.execute('SELECT 1 FROM topics WHERE id=?',(item.topic,)).fetchone() is None:
                raise ValueError(f'catalog missing {item.topic}')
            con.execute('''INSERT OR IGNORE INTO archetypes
                 (id,topic_id,family,name,method_signature,difficulty)
                 VALUES(?,?,?,?,?,?)''',
                 (item.family,item.topic,item.family,item.title,item.signature,item.difficulty))
    return len(METHODS)

def seed_v118(path):
    # Register research candidates without automatic expert approval or publication.
    from .v118_research import METHODS
    with closing(connect(path)) as con, transaction(con):
        for m in METHODS:
            if con.execute('SELECT 1 FROM topics WHERE id=? AND grade=?',
                           (m.topic,m.grade)).fetchone() is None:
                raise ValueError('catalog missing requested V118 topic: '+m.topic)
            con.execute('''INSERT OR IGNORE INTO archetypes
                (id,topic_id,family,name,method_signature,difficulty)
                VALUES(?,?,?,?,?,?)''',
                (m.family,m.topic,m.family,m.title,m.signature,m.difficulty))
    return len(METHODS)


def seed_v119(path):
    """Register V119 candidates strictly pending approval, never auto-publish."""
    from .v119_research import METHODS
    with closing(connect(path)) as con, transaction(con):
        for m in METHODS:
            if con.execute('SELECT 1 FROM topics WHERE id=? AND grade=?',
                           (m.topic,m.grade)).fetchone() is None:
                raise ValueError('catalog missing V119 topic: '+m.topic)
            con.execute('''INSERT OR IGNORE INTO archetypes
                (id,topic_id,family,name,method_signature,difficulty)
                VALUES(?,?,?,?,?,?)''',
                (m.family,m.topic,m.family,m.title,m.signature,m.difficulty))
    return len(METHODS)

def seed_v120(path):
    """Register 150 V120 topic-specific candidate methods, all pending review."""
    from .v120_research import METHODS
    with closing(connect(path)) as con, transaction(con):
        for m in METHODS:
            if con.execute('SELECT 1 FROM topics WHERE id=? AND grade=?',
                           (m.topic,m.grade)).fetchone() is None:
                raise ValueError('catalog missing V120 topic: '+m.topic)
            con.execute('''INSERT OR IGNORE INTO archetypes
                (id,topic_id,family,name,method_signature,difficulty)
                VALUES(?,?,?,?,?,?)''',
                (m.family,m.topic,m.family,m.title,m.signature,m.difficulty))
    return len(METHODS)


def seed_v121(path):
    """Register V121 300 candidate objectives. Publication requires a reviewer."""
    from .v121_research import METHODS
    with closing(connect(path)) as con, transaction(con):
        for m in METHODS:
            if con.execute('SELECT 1 FROM topics WHERE id=? AND grade=?',
                           (m.topic,m.grade)).fetchone() is None:
                raise ValueError('catalog missing V121 topic: '+m.topic)
            con.execute('''INSERT OR IGNORE INTO archetypes
                (id,topic_id,family,name,method_signature,difficulty)
                VALUES(?,?,?,?,?,?)''',
                (m.family,m.topic,m.family,m.title,m.signature,m.difficulty))
    return len(METHODS)


def seed_v122(path):
    '''Explicitly register V122 if its optional source exists; never approve.'''
    from importlib.util import find_spec
    if find_spec('question_factory.v122_research') is None:
        # V122 distributed as an audit in some releases: no source module.
        # Return an honest zero, not an import error or invented candidates.
        return 0
    from .v122_research import METHODS
    with closing(connect(path)) as con, transaction(con):
        for m in METHODS:
            if con.execute('SELECT 1 FROM topics WHERE id=? AND grade=?',
                           (m.topic,m.grade)).fetchone() is None:
                raise ValueError('catalog missing V122 topic: '+m.topic)
            con.execute('''INSERT OR IGNORE INTO archetypes
                (id,topic_id,family,name,method_signature,difficulty)
                VALUES(?,?,?,?,?,?)''',
                (m.family,m.topic,m.family,m.title,m.signature,m.difficulty))
    return len(METHODS)


def seed_v123(path):
    """Opt-in registration of composite candidate objectives for manual review."""
    from .v123_research import METHODS
    with closing(connect(path)) as con, transaction(con):
        for m in METHODS:
            if con.execute('SELECT 1 FROM topics WHERE id=? AND grade=?',
                           (m.topic, m.grade)).fetchone() is None:
                raise ValueError('catalog missing V123 topic: '+m.topic)
            con.execute("""INSERT OR IGNORE INTO archetypes
                (id, topic_id, family, name, method_signature, difficulty)
                VALUES(?,?,?,?,?,?)""",
                (m.family,m.topic,m.family,m.title,m.signature,m.difficulty))
    return len(METHODS)

def approve(path, archetype_id, reviewer):
    if not reviewer.strip():
        raise ValueError("reviewer must be specified")
    with closing(connect(path)) as con, transaction(con):
        result = con.execute("""UPDATE archetypes SET review_status='approved',
            reviewer=?, reviewed_at=? WHERE id=? AND review_status!='rejected'""",
            (reviewer, time.time(), archetype_id))
        if result.rowcount != 1:
            raise ValueError("unknown or rejected archetype")


def enqueue(path, per_type=10, max_attempts=3):
    if not 1 <= per_type <= 10 or not 1 <= max_attempts <= 10:
        raise ValueError("per_type must be 1..10 and max_attempts 1..10")
    count = 0
    with closing(connect(path)) as con, transaction(con):
        ids = con.execute("SELECT id FROM archetypes WHERE review_status='approved'").fetchall()
        for row in ids:
            result = con.execute("""INSERT OR IGNORE INTO jobs
                  (id, archetype_id,desired,max_attempts,updated_at)
                  VALUES(?,?,?,?,?)""", (str(uuid.uuid4()),row['id'],per_type,max_attempts,time.time()))
            count += result.rowcount
    return count


def set_paused(path, paused):
    with closing(connect(path)) as con, transaction(con):
        con.execute("UPDATE control SET paused=? WHERE id=1", (int(paused),))


def set_limit(path, max_verified):
    if max_verified < 0:
        raise ValueError("max_verified must be >= 0; 0 means unlimited")
    with closing(connect(path)) as con, transaction(con):
        con.execute("UPDATE control SET max_verified=? WHERE id=1", (max_verified,))


def claim(con, owner, lease_sec=120):
    now = time.time()
    with transaction(con):
        # A worker can die after consuming its final attempt. Terminalize
        # expired leases so the queue doesn't appear stuck indefinitely.
        con.execute("""UPDATE jobs SET status='failed',lease_owner=NULL,lease_until=NULL,
            last_error=COALESCE(last_error,'lease expired after max attempts'),updated_at=?
            WHERE status='leased' AND lease_until<? AND attempts>=max_attempts""",(now,now))
        control = con.execute("SELECT * FROM control WHERE id=1").fetchone()
        if control['paused']:
            return None
        if control['max_verified']:
            count = con.execute("SELECT COUNT(*) FROM questions WHERE status='verified'").fetchone()[0]
            if count >= control['max_verified']:
                return None
        job = con.execute("""SELECT j.* FROM jobs j
          JOIN archetypes a ON a.id=j.archetype_id
          WHERE a.review_status='approved' AND
          ((j.status='pending' AND j.next_attempt_at<=?) OR
           (j.status='leased' AND j.lease_until<?)) AND
          j.attempts<j.max_attempts ORDER BY j.updated_at,j.id LIMIT 1""",
          (now,now)).fetchone()
        if job is None:
            return None
        con.execute("""UPDATE jobs SET status='leased',attempts=attempts+1,
                    lease_owner=?,lease_until=?,updated_at=? WHERE id=?""",
                    (owner, now+lease_sec, now, job['id']))
        return dict(job)


def heartbeat(con, job_id, owner, lease_sec=120):
    with transaction(con):
        res=con.execute("""UPDATE jobs SET lease_until=?, updated_at=? WHERE id=?
          AND lease_owner=? AND status='leased'""",
          (time.time()+lease_sec,time.time(),job_id,owner))
        return res.rowcount==1


class LimitReached(RuntimeError):
    pass


def store_question(con, job_id, owner, data, is_valid, details):
    with transaction(con):
        job=con.execute("SELECT * FROM jobs WHERE id=?",(job_id,)).fetchone()
        if not job or job['status']!='leased' or job['lease_owner']!=owner or job['lease_until']<=time.time():
            raise RuntimeError("job lease lost")
        ctrl=con.execute("SELECT * FROM control WHERE id=1").fetchone()
        row=con.execute("SELECT id,fingerprint,status,validation_json FROM questions WHERE archetype_id=? AND ordinal=?",
                        (job['archetype_id'],data['ordinal'])).fetchone()
        if row is not None:
            if row['fingerprint']!=data['fingerprint']:
                raise RuntimeError("non-deterministic regeneration")
            if row['status']=='verified' or not is_valid:
                return
            # A rejected result may become valid after a verifier bug is fixed.
            # Previous behavior kept it rejected forever, so retries could
            # never finish despite successful independent verification.
            if ctrl['max_verified']:
                count=con.execute("SELECT COUNT(*) FROM questions WHERE status='verified'").fetchone()[0]
                if count>=ctrl['max_verified']:
                    raise LimitReached("verified-question limit reached")
            history = {'previous_rejected_validation': json.loads(row['validation_json']),
                       'latest_validation': details,
                       'reverified_after_rejection': True}
            con.execute('''UPDATE questions SET stem=?,answer=?,solution=?,params_json=?,
                difficulty=?,validation_json=?,status='verified',verified_at=? WHERE id=?''',
                (data['stem'],data['answer'],data['solution'],
                 json.dumps(data['params'],sort_keys=True),data['difficulty'],
                 json.dumps(history,sort_keys=True),time.time(),row['id']))
            return
        if is_valid and ctrl['max_verified']:
            count=con.execute("SELECT COUNT(*) FROM questions WHERE status='verified'").fetchone()[0]
            if count>=ctrl['max_verified']:
                raise LimitReached("verified-question limit reached")
        con.execute("""INSERT INTO questions(id,archetype_id,ordinal,fingerprint,stem,answer,
         solution,params_json,difficulty,validation_json,status,verified_at)
         VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",(
            str(uuid.uuid4()), job['archetype_id'],data['ordinal'],data['fingerprint'],
            data['stem'],data['answer'],data['solution'],json.dumps(data['params'],sort_keys=True),
            data['difficulty'],json.dumps(details,sort_keys=True),
            'verified' if is_valid else 'rejected',time.time()))


def finish(con, job_id, owner):
    with transaction(con):
        job=con.execute("SELECT * FROM jobs WHERE id=?",(job_id,)).fetchone()
        if not job or job['lease_owner']!=owner or job['status']!='leased':
            raise RuntimeError('job lease lost')
        done=con.execute("""SELECT COUNT(*) FROM questions WHERE archetype_id=? AND status='verified'""",
                         (job['archetype_id'],)).fetchone()[0]
        if done != job['desired']:
            raise RuntimeError(f"not all questions validated ({done}/{job['desired']})")
        con.execute("UPDATE jobs SET status='done',lease_owner=NULL,lease_until=NULL,updated_at=? WHERE id=?",
                    (time.time(),job_id))


def defer(con, job_id, owner, reason):
    """Defer on pause/hard cap without spending an attempt."""
    with transaction(con):
        con.execute("""UPDATE jobs SET status='pending',attempts=MAX(0,attempts-1),
                     lease_owner=NULL,lease_until=NULL,next_attempt_at=0,
                     last_error=?,updated_at=? WHERE id=?
                     AND status='leased' AND lease_owner=?""",
                    (str(reason)[:200],time.time(),job_id,owner))


def is_paused(con):
    return bool(con.execute('SELECT paused FROM control WHERE id=1').fetchone()[0])


def fail(con, job_id, owner, error):
    with transaction(con):
        job=con.execute("SELECT * FROM jobs WHERE id=?",(job_id,)).fetchone()
        if not job or job['lease_owner']!=owner or job['status']!='leased':
            return
        terminal = job['attempts']>=job['max_attempts']
        delay = min(60,2**job['attempts'])
        con.execute("""UPDATE jobs SET status=?,lease_owner=NULL,lease_until=NULL,
                     next_attempt_at=?,last_error=?,updated_at=? WHERE id=?""",
                    ('failed' if terminal else 'pending', time.time()+delay,
                     str(error)[:200],time.time(),job_id))


def progress(path):
    with closing(connect(path)) as con:
        out={}
        for table in ['topics','archetypes','jobs','questions']:
            out[table]=con.execute('SELECT COUNT(*) FROM '+table).fetchone()[0]
        out['approved_archetypes']=con.execute("SELECT COUNT(*) FROM archetypes WHERE review_status='approved'").fetchone()[0]
        # Approved for generation != independently certified mathematical type.
        # A certification requires a separately reviewed, evidence-backed record.
        out['certificate_records_total']=con.execute('SELECT COUNT(*) FROM independence_certifications').fetchone()[0]
        # Basic eligibility is NOT proof of mathematical independence. Exclude
        # revoked/unapproved or malformed evidence from milestone counters.
        eligibility = "a.review_status='approved' AND trim(c.reviewer)!='' AND CASE WHEN json_valid(c.evidence_json)=1 THEN json_type(c.evidence_json)='object' AND json(c.evidence_json)!='{}' AND json_type(c.evidence_json,'$.compared_method_ids')='array' AND json_type(c.evidence_json,'$.independence_reason')='text' AND length(trim(coalesce(json_extract(c.evidence_json,'$.independence_reason'),'')))>=20 ELSE 0 END"
        out['certified_independent_types']=con.execute('SELECT COUNT(*) FROM independence_certifications c JOIN archetypes a ON a.id=c.archetype_id WHERE '+eligibility).fetchone()[0]
        # Integrity diagnostics: a certificate row alone is not proof of quality.
        # Keep legacy counters intact, but expose suspicious records explicitly.
        out['certifications_without_approval']=con.execute('''
            SELECT COUNT(*) FROM independence_certifications c
            JOIN archetypes a ON a.id=c.archetype_id
            WHERE a.review_status!='approved'
        ''').fetchone()[0]
        out['certifications_with_empty_evidence']=con.execute('''
            SELECT COUNT(*) FROM independence_certifications
            WHERE trim(reviewer)='' OR json_valid(evidence_json)=0 OR CASE WHEN json_valid(evidence_json)=1 THEN json_type(evidence_json)!='object' OR json(evidence_json)='{}' ELSE 1 END
        ''').fetchone()[0]
        # JSON-shaped evidence is not necessarily a documented comparison.
        # Diagnostic only: human mathematical review remains essential.
        out['certifications_without_method_comparison']=con.execute('''
            SELECT COUNT(*) FROM independence_certifications
            WHERE json_valid(evidence_json)=0 OR CASE WHEN json_valid(evidence_json)=1 THEN
                json_type(evidence_json)!='object'
                OR json_type(evidence_json,'$.compared_method_ids')!='array'
                OR json_type(evidence_json,'$.independence_reason')!='text'
                OR length(trim(coalesce(json_extract(evidence_json,'$.independence_reason'),'')))<20
                ELSE 1 END
        ''').fetchone()[0]
        out['verified_questions_on_unapproved_certified_methods']=con.execute('''
            SELECT COUNT(*) FROM questions q
            JOIN independence_certifications c ON c.archetype_id=q.archetype_id
            JOIN archetypes a ON a.id=q.archetype_id
            WHERE q.status='verified' AND a.review_status!='approved'
        ''').fetchone()[0]
        out['certification_integrity_warnings']=(
            out['certifications_without_approval'] + out['certifications_with_empty_evidence']
            + out['verified_questions_on_unapproved_certified_methods'])
        out['pending_review_archetypes']=con.execute("SELECT COUNT(*) FROM archetypes WHERE review_status='pending'").fetchone()[0]
        out['verified_questions']=con.execute("SELECT COUNT(*) FROM questions WHERE status='verified'").fetchone()[0]
        # Only verified questions attached to a separately certified method count
        # toward the final 3M-question quality target. No implicit certification.
        out['certified_method_verified_questions']=con.execute(f'''
            SELECT COUNT(*) FROM questions q JOIN independence_certifications c
            ON c.archetype_id=q.archetype_id JOIN archetypes a ON a.id=q.archetype_id WHERE q.status='verified' AND {eligibility}
        ''').fetchone()[0]
        out['rejected_questions']=con.execute("SELECT COUNT(*) FROM questions WHERE status='rejected'").fetchone()[0]
        out['job_status']={r[0]:r[1] for r in con.execute("SELECT status,COUNT(*) FROM jobs GROUP BY status")}
        out['paused']=bool(con.execute('SELECT paused FROM control WHERE id=1').fetchone()[0])
        ctrl=con.execute('SELECT * FROM control WHERE id=1').fetchone()
        out['max_verified']=ctrl['max_verified']
        out['cost_limit_cents']=ctrl['cost_limit_cents']
        out['cost_used_cents']=ctrl['cost_used_cents']
        out['cost_reserved_cents']=ctrl['cost_reserved_cents']
        out['type_records_with_approval']=out['approved_archetypes']
        # The user's interim research milestone is 500 types/topic; the original
        # 2,000 types/topic remains the long-term target. Do not count candidate
        # registrations as certified progress.
        out['interim_target_types']=75_000
        out['interim_target_questions']=750_000
        out['interim_types_remaining_uncertified']=max(0,75_000-out['certified_independent_types'])
        out['target_types']=300_000
        out['target_questions']=3_000_000
        # Targets are PER TOPIC: excess types in one topic cannot substitute
        # for missing independent types in another topic.
        counts=con.execute(f'''SELECT t.id,
            (SELECT COUNT(*) FROM independence_certifications ic
               JOIN archetypes a ON a.id=ic.archetype_id WHERE a.topic_id=t.id AND {eligibility.replace("c.", "ic.")}) as certified,
            (SELECT COUNT(*) FROM questions q
               JOIN archetypes a ON a.id=q.archetype_id
               JOIN independence_certifications ic ON ic.archetype_id=a.id
               WHERE a.topic_id=t.id AND q.status='verified' AND {eligibility.replace('c.', 'ic.')}) as qualified
            FROM topics t''').fetchall()
        missing_topics=max(0,150-len(counts))
        out['interim_types_remaining_uncertified']=500*missing_topics + sum(
            max(0,500-r['certified']) for r in counts)
        out['topics_meeting_type_target']=sum(r['certified']>=2000 for r in counts)
        out['topics_meeting_question_target']=sum(r['qualified']>=20000 for r in counts)
        out['topics_meeting_both_targets']=sum(r['certified']>=2000 and r['qualified']>=20000 for r in counts)
        out['methods_remaining_uncertified']=2000*missing_topics + sum(max(0,2000-r['certified']) for r in counts)
        out['questions_remaining_unverified']=max(0,3_000_000-out['verified_questions'])
        out['target_ready_questions']=out['certified_method_verified_questions']
        out['target_questions_remaining_qualified']=20_000*missing_topics + sum(max(0,20_000-r['qualified']) for r in counts)
        return out


def read_questions(path, topic_id, limit=20, after_id='', include_answers=False):
    limit=min(max(int(limit),1),100)
    with closing(connect(path)) as con:
        public_columns="q.id,q.stem,q.difficulty,a.id archetype_id,a.topic_id"
        private_columns=",q.answer,q.solution,q.validation_json" if include_answers else ""
        rows=con.execute(f"""SELECT {public_columns}{private_columns} FROM questions q
           JOIN archetypes a ON a.id=q.archetype_id WHERE q.status='verified'
           AND a.review_status='approved' AND a.topic_id=? AND q.id>? ORDER BY q.id LIMIT ?""",
           (topic_id,after_id,limit)).fetchall()
        return [dict(r) for r in rows]


def set_cost_limit(path, limit_cents):
    """0 means no paid requests permitted until configured (fail closed)."""
    if limit_cents < 0:
        raise ValueError('negative cost ceiling')
    with closing(connect(path)) as con, transaction(con):
        ctrl=con.execute('SELECT cost_used_cents,cost_reserved_cents FROM control WHERE id=1').fetchone()
        if ctrl['cost_used_cents']+ctrl['cost_reserved_cents']>limit_cents:
            raise ValueError('ceiling cannot be lower than spent plus reserved')
        con.execute('UPDATE control SET cost_limit_cents=? WHERE id=1',(limit_cents,))


def reserve_cost(path, request_id, estimate_cents):
    """Call BEFORE any paid operation; idempotent by request ID."""
    if not request_id or estimate_cents <= 0:
        raise ValueError('request ID and positive estimated cost required')
    with closing(connect(path)) as con, transaction(con):
        existing=con.execute('SELECT * FROM budget_reservations WHERE request_id=?',
                            (request_id,)).fetchone()
        if existing:
            if existing['reserved_cents']!=estimate_cents:
                raise ValueError('request ID was reused with different estimate')
            return existing['status']=='reserved'
        ctrl=con.execute('SELECT * FROM control WHERE id=1').fetchone()
        if (ctrl['cost_limit_cents']==0 or
            ctrl['cost_used_cents']+ctrl['cost_reserved_cents']+estimate_cents>ctrl['cost_limit_cents']):
            return False
        con.execute('UPDATE control SET cost_reserved_cents=cost_reserved_cents+? WHERE id=1',
                    (estimate_cents,))
        now=time.time()
        con.execute("""INSERT INTO budget_reservations
                    (request_id,reserved_cents,actual_cents,status,created_at,updated_at)
                    VALUES(?, ?, NULL,'reserved',?,?)""",
                    (request_id,estimate_cents,now,now))
        return True


def settle_cost(path, request_id, actual_cents):
    """Settle after response. Over-estimate is rejected, not silently charged."""
    if actual_cents<0: raise ValueError('negative actual spend')
    with closing(connect(path)) as con, transaction(con):
        entry=con.execute('SELECT * FROM budget_reservations WHERE request_id=?',
                          (request_id,)).fetchone()
        if not entry or entry['status']!='reserved':
            raise ValueError('unknown or already closed reservation')
        if actual_cents>entry['reserved_cents']:
            raise ValueError('actual cost exceeds reserved amount')
        con.execute('''UPDATE control SET cost_reserved_cents=cost_reserved_cents-?,
                       cost_used_cents=cost_used_cents+? WHERE id=1''',
                    (entry['reserved_cents'],actual_cents))
        con.execute("""UPDATE budget_reservations SET status='settled',actual_cents=?,updated_at=?
                     WHERE request_id=?""",(actual_cents,time.time(),request_id))


def release_cost(path, request_id):
    """Release only if provider wasn't billed; not automatic after a crash."""
    with closing(connect(path)) as con, transaction(con):
        entry=con.execute('SELECT * FROM budget_reservations WHERE request_id=?',
                          (request_id,)).fetchone()
        if not entry or entry['status']!='reserved':
            raise ValueError('unknown or already closed reservation')
        con.execute('UPDATE control SET cost_reserved_cents=cost_reserved_cents-? WHERE id=1',
                    (entry['reserved_cents'],))
        con.execute("UPDATE budget_reservations SET status='released',updated_at=? WHERE request_id=?",
                    (time.time(),request_id))


def list_topics(path):
    """Catalog coverage is distinct from approved type and validated question counts."""
    with closing(connect(path)) as con:
        eligibility = "a.review_status='approved' AND trim(c.reviewer)!='' AND CASE WHEN json_valid(c.evidence_json)=1 THEN json_type(c.evidence_json)='object' AND json(c.evidence_json)!='{}' AND json_type(c.evidence_json,'$.compared_method_ids')='array' AND json_type(c.evidence_json,'$.independence_reason')='text' AND length(trim(coalesce(json_extract(c.evidence_json,'$.independence_reason'),'')))>=20 ELSE 0 END"
        rows = con.execute(f'''SELECT t.id,t.grade,t.name,
            (SELECT COUNT(*) FROM archetypes a WHERE a.topic_id=t.id AND a.review_status='approved') approved_types,
            (SELECT COUNT(*) FROM independence_certifications c
                JOIN archetypes a ON a.id=c.archetype_id WHERE a.topic_id=t.id AND {eligibility}) certified_independent_types,
            (SELECT COUNT(*) FROM questions q JOIN archetypes a ON a.id=q.archetype_id
             WHERE a.topic_id=t.id AND a.review_status='approved' AND q.status='verified') verified_questions,
            (SELECT COUNT(*) FROM questions q JOIN archetypes a ON a.id=q.archetype_id
                JOIN independence_certifications c ON c.archetype_id=a.id
             WHERE a.topic_id=t.id AND q.status='verified' AND {eligibility}) certified_method_verified_questions
            FROM topics t ORDER BY t.grade,t.name''').fetchall()
        return [dict(x, interim_target_types=500, interim_target_questions=5000,
                     interim_type_shortfall=max(0,500-x['certified_independent_types']),
                     interim_question_shortfall=max(0,5000-x['certified_method_verified_questions']),
                     target_types=2000, target_questions=20000,
                     type_shortfall=max(0,2000-x['certified_independent_types']),
                     question_shortfall=max(0,20000-x['certified_method_verified_questions'])) for x in rows]


def create_answer_session(path, topic_id, ttl_seconds=900, max_active_sessions=10000,
                          sequence_key=None):
    '''Choose an approved question; avoid consecutive method and literal repeats.

    An opaque client-generated sequence key enables per-learner history across
    requests. No key means stateless legacy behavior (no anti-repeat guarantee).
    Selection is transactional; on exhausted pools, a repeat is unavoidable.
    The key is hashed before persistence and must NOT contain personal data.
    '''
    import hashlib
    import secrets
    if not 1 <= ttl_seconds <= 3600 or max_active_sessions < 1:
        raise ValueError('invalid session limits')
    if sequence_key is not None:
        if not isinstance(sequence_key, str) or not 12 <= len(sequence_key) <= 128 or \
           not all(c.isascii() and (c.isalnum() or c in '_-') for c in sequence_key):
            raise ValueError('sequence_key must be an opaque 12..128 character token')
        sequence_hash = hashlib.sha256(sequence_key.encode('ascii')).hexdigest()
    else:
        sequence_hash = None
    with closing(connect(path)) as con, transaction(con):
        # Timestamp must be assigned INSIDE the write lock. Concurrent callers
        # otherwise record request-start order rather than committed order.
        now = time.time()
        # Keep one day of expired sessions for repeat prevention, not grading.
        con.execute('DELETE FROM answer_sessions WHERE expires_at<?', (now-86400,))
        active = con.execute('SELECT COUNT(*) FROM answer_sessions WHERE used_at IS NULL AND expires_at>?', (now,)).fetchone()[0]
        if active >= max_active_sessions:
            raise LimitReached('too many active sessions; retry after expiry')
        # Read only this sequence's history.  Other users have independent pools.
        recent_qids = set()
        last_method = None
        if sequence_hash:
            rows = con.execute('''SELECT s.question_id,q.archetype_id
                FROM answer_sessions s JOIN questions q ON q.id=s.question_id
                JOIN archetypes a ON a.id=q.archetype_id
                WHERE s.sequence_hash=? AND a.topic_id=?
                  AND s.created_at>=?
                ORDER BY s.created_at DESC, s.rowid DESC LIMIT 200''',
                (sequence_hash,topic_id,now-86400)).fetchall()
            recent_qids = {r['question_id'] for r in rows}
            if rows:
                last_method = rows[0]['archetype_id']
        if last_method is None:
            row = con.execute('''SELECT q.id,q.stem,q.difficulty,
                a.id archetype_id,a.topic_id
                FROM questions q JOIN archetypes a ON a.id=q.archetype_id
                WHERE a.topic_id=? AND a.review_status='approved'
                  AND q.status='verified'
                ORDER BY RANDOM() LIMIT 1''',(topic_id,)).fetchone()
        else:
            # Index-friendly one-row selection: never repeat a recent literal
            # question while any unseen one exists. Among unseen questions,
            # prefer a different method. All values are SQL parameters.
            seen = sorted(recent_qids)
            seen_expr = ('q.id IN (' + ','.join('?' for _ in seen) + ')') if seen else '0'
            row = con.execute(f'''SELECT q.id,q.stem,q.difficulty,
                a.id archetype_id,a.topic_id
                FROM questions q JOIN archetypes a ON a.id=q.archetype_id
                WHERE a.topic_id=? AND a.review_status='approved'
                  AND q.status='verified'
                ORDER BY CASE WHEN {seen_expr} THEN 1 ELSE 0 END,
                         CASE WHEN a.id=? THEN 1 ELSE 0 END,
                         RANDOM() LIMIT 1''',
                (topic_id,*seen,last_method)).fetchone()
        if not row:
            return None
        session_id = secrets.token_urlsafe(32)
        con.execute('''INSERT INTO answer_sessions
            (session_id,question_id,expires_at,sequence_hash,created_at)
            VALUES(?,?,?,?,?)''',
            (session_id,row['id'],now+ttl_seconds,sequence_hash,now))
        result = dict(row)
        result['session_id'] = session_id
        result['expires_in_seconds'] = ttl_seconds
        return result


def submit_answer_session(path, session_id, user_answer):
    """Consume session before grading to block replay, even on invalid answers."""
    from .grading import answers_equivalent
    with closing(connect(path)) as con, transaction(con):
        session=con.execute('''SELECT s.session_id,s.expires_at,s.used_at,q.answer,q.solution,q.difficulty
         FROM answer_sessions s JOIN questions q ON q.id=s.question_id
         JOIN archetypes a ON a.id=q.archetype_id
         WHERE s.session_id=? AND q.status='verified' AND a.review_status='approved' ''',
                            (session_id,)).fetchone()
        if not session or session['used_at'] is not None or session['expires_at']<=time.time():
            return None
        con.execute('UPDATE answer_sessions SET used_at=? WHERE session_id=?',(time.time(),session_id))
        expected=session['answer'].strip()
        supplied=user_answer.strip()
        correct,grading_scope=answers_equivalent(expected,supplied)
        return {'is_correct':correct,'correct_answer':expected,'solution':session['solution'],
                'difficulty':session['difficulty'], 'grading_scope':grading_scope}

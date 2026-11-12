"""Privacy-preserving, per-student *trained* predictor for verified math responses.

Unlike fixed-parameter BKT, this logistic model updates its coefficients from
observed server-graded answers using online SGD. It predicts correctness for
NEW practice items and never grants curriculum unlocks or certifies ability.
Data isolation is by (user_id, grade); no raw question, answer, or identity is
stored in the coefficient table. Rebuild from verified evidence is deterministic.
"""
import json
import math
from datetime import datetime, timezone

TIERS = ('nền tảng', 'trung cấp', 'nâng cao')
SOURCES = ('lesson-reviewed', 'qf2-approved')
INITIAL = [-0.1, -0.28, -0.62, 0.48, 0.32]
VERSION = 'online_personal_logistic_v2_evidence_guard'


def create_table(c):
    c.execute('''CREATE TABLE IF NOT EXISTS roadmap_v2_personal_predictors (
        user_id INTEGER NOT NULL, grade INTEGER NOT NULL,
        version TEXT NOT NULL, state_json TEXT NOT NULL,
        trained_count INTEGER NOT NULL, updated_at TEXT NOT NULL,
        PRIMARY KEY(user_id,grade))''')


def empty_state():
    return {'version': VERSION, 'weights': INITIAL.copy(), 'n': 0, 'right': 0,
            'brier_sum': 0.0, 'topic_stats': {}, 'tier_stats': {},
            'topic_tier_stats': {}, 'evaluated_count': 0,
            'evaluated_model_brier': 0.0, 'evaluated_baseline_brier': 0.0}


def _rate(stats, key):
    r, n = stats.get(key, [0, 0])
    return (float(r) + 1) / (float(n) + 2)


def features(state, topic_id, tier):
    # Smoothed history is measured BEFORE the current answer is observed.
    topic_rate = _rate(state['topic_stats'], topic_id)
    tier_rate = _rate(state['tier_stats'], tier)
    return [1., float(tier == 'trung cấp'), float(tier == 'nâng cao'),
            2 * topic_rate - 1, 2 * tier_rate - 1]


def probability(state, topic_id, tier):
    if tier not in TIERS:
        raise ValueError('Mức độ không hợp lệ')
    z = sum(w * x for w, x in zip(state['weights'], features(state, topic_id, tier)))
    z = max(-12., min(12., z))
    return 1 / (1 + math.exp(-z))


def learn(state, topic_id, tier, verdict):
    """Exactly one verified *first answered* question contributes one update."""
    if (tier not in TIERS or verdict not in ('correct', 'wrong')
            or not isinstance(topic_id, str) or not topic_id.strip()):
        return False
    x = features(state, topic_id, tier)
    target = 1.0 if verdict == 'correct' else 0.0
    pred = probability(state, topic_id, tier)
    # Chronological prequential evaluation: neither model nor baseline sees
    # the label until AFTER the prediction. Ignore the initial warm-up window.
    baseline_pred = (state['right'] + 1) / (state['n'] + 2)
    if state['n'] >= 10:
        state['evaluated_count'] += 1
        state['evaluated_model_brier'] += (pred - target) ** 2
        state['evaluated_baseline_brier'] += (baseline_pred - target) ** 2
    rate = .14 / math.sqrt(1 + state['n'] / 40)
    # Weak shrinkage towards a neutral prior limits drift on few observations.
    state['weights'] = [max(-3., min(3., w + rate * ((target-pred)*v - .002*(w-p))))
                        for w, p, v in zip(state['weights'], INITIAL, x)]
    for group, key in ((state['topic_stats'], topic_id), (state['tier_stats'], tier)):
        previous = group.setdefault(key, [0, 0])
        previous[0] += int(target)
        previous[1] += 1
    by_tier = state['topic_tier_stats'].setdefault(topic_id, {})
    previous_topic_tier = by_tier.setdefault(tier, [0, 0])
    previous_topic_tier[0] += int(target)
    previous_topic_tier[1] += 1
    state['n'] += 1
    state['right'] += int(target)
    state['brier_sum'] += (pred - target) ** 2
    return True


def replay_events(events):
    """First actual verified answer per qid wins; skips never train.

    Caller MUST supply chronological server-graded rows and scope user/grade.
    """
    state = empty_state()
    seen = set()
    for e in events:
        qid = e['qid']
        if qid in seen or e['source'] not in SOURCES:
            continue
        if e['verdict'] not in ('correct', 'wrong'):
            continue
        if learn(state, e['topic_id'], e['tier'], e['verdict']):
            seen.add(qid)
    return state


def load(c, user_id, grade):
    create_table(c)
    row = c.execute('SELECT state_json FROM roadmap_v2_personal_predictors '
                    'WHERE user_id=? AND grade=?', (user_id, grade)).fetchone()
    if not row:
        return None
    try:
        state = json.loads(row['state_json'])
        required = ('topic_stats','tier_stats','topic_tier_stats','evaluated_count',
                    'evaluated_model_brier','evaluated_baseline_brier','brier_sum','right','n')
        if (state.get('version') == VERSION
                and all(key in state for key in required)
                and isinstance(state['topic_stats'],dict)
                and isinstance(state['tier_stats'],dict)
                and isinstance(state['topic_tier_stats'],dict)
                and isinstance(state.get('weights'),list)
                and len(state['weights']) == len(INITIAL)
                and all(isinstance(w,(int,float)) and math.isfinite(w) for w in state['weights'])
                and isinstance(state['n'],int) and state['n']>=0
                and isinstance(state['right'],int) and 0<=state['right']<=state['n']
                and isinstance(state['evaluated_count'],int)
                and 0<=state['evaluated_count']<=state['n']
                and all(isinstance(state[k],(int,float)) and math.isfinite(state[k]) and state[k]>=0
                        for k in ('brier_sum','evaluated_model_brier','evaluated_baseline_brier'))):
            return state
    except (ValueError, TypeError, KeyError):
        pass
    return None


def rebuild(c, user_id, grade):
    """Train/retrain from authoritative evidence only, avoiding overcounting."""
    create_table(c)
    rows = c.execute('''SELECT qid,topic_id,tier,verdict,source FROM roadmap_v2_learning_events
        WHERE user_id=? AND grade=? ORDER BY created_at ASC, rowid ASC''', (user_id, grade)).fetchall()
    state = replay_events(rows)
    c.execute('''INSERT INTO roadmap_v2_personal_predictors
       (user_id,grade,version,state_json,trained_count,updated_at)
       VALUES (?,?,?,?,?,?)
       ON CONFLICT(user_id,grade) DO UPDATE SET version=excluded.version,
          state_json=excluded.state_json,trained_count=excluded.trained_count,
          updated_at=excluded.updated_at''',
       (user_id, grade, VERSION, json.dumps(state, ensure_ascii=False, separators=(',', ':')),
        state['n'], datetime.now(timezone.utc).isoformat()))
    return state


def ensure(c, user_id, grade):
    """Migrate existing V23 training evidence on demand, without raw answers."""
    return load(c, user_id, grade) or rebuild(c, user_id, grade)


def _readiness(state):
    """Conservative *learning advice* gate, NOT a competence certification.

    We need several topics, multiple difficulties, different outcomes and
    strictly sequential evidence that improves on a running prior-rate
    baseline. Each example must already have passed the caller's review gate.
    """
    n = int(state['n'])
    topics = sum(int(v[1]) >= 3 for v in state['topic_stats'].values())
    tiers = sum(int(v[1]) >= 4 for v in state['tier_stats'].values())
    evaluated = int(state['evaluated_count'])
    model_brier = state['evaluated_model_brier'] / evaluated if evaluated else None
    baseline_brier = state['evaluated_baseline_brier'] / evaluated if evaluated else None
    reasons = []
    if n < 30: reasons.append('Cần ít nhất 30 câu trả lời đầu tiên từ câu đã duyệt.')
    if topics < 3: reasons.append('Cần dữ liệu từ ít nhất 3 chủ đề, mỗi chủ đề tối thiểu 3 câu.')
    if tiers < 2: reasons.append('Cần dữ liệu ở ít nhất 2 mức độ, mỗi mức tối thiểu 4 câu.')
    if min(int(state['right']), n-int(state['right'])) < 5:
        reasons.append('Cần quan sát cả câu đúng và sai, mỗi loại tối thiểu 5 câu.')
    if evaluated < 15:
        reasons.append('Chưa đủ câu để kiểm tra dự đoán tuần tự sau giai đoạn khởi động.')
    if (model_brier is None or baseline_brier is None
            or model_brier + .005 >= baseline_brier or model_brier >= .25):
        reasons.append('Dự đoán chưa vượt rõ ràng mô hình tham chiếu trên dữ liệu mới.')
    return not reasons, reasons, topics, tiers, model_brier, baseline_brier


def public_report(state):
    n = state['n']
    ready, reasons, topics, tiers, model_brier, baseline_brier = _readiness(state)
    return {'model': VERSION, 'trainable': True, 'examples': n,
            'correct': state['right'], 'wrong': n-state['right'],
            'distinct_topics_with_evidence': len(state['topic_stats']),
            'topics_with_3_examples': topics, 'tiers_with_4_examples': tiers,
            'evaluated_after_warmup': state['evaluated_count'],
            'prequential_brier': round(state['brier_sum'] / n, 4) if n else None,
            'held_forward_brier': round(model_brier, 4) if model_brier is not None else None,
            'reference_brier': round(baseline_brier, 4) if baseline_brier is not None else None,
            'ready_for_soft_suggestions': ready,
            'readiness_reasons': reasons,
            'population_calibrated': False,
            'note': ('So sánh dự đoán tuần tự chỉ kiểm tra khả năng dự báo nội bộ; '
                     'không chứng minh tính khách quan, độ tin cậy tâm trắc hoặc hiệu quả lộ trình. '
                     'Mô hình chưa được hiệu chuẩn trên nhóm học sinh đại diện.')}


def suggestions_for_topic(state, topic_id):
    """Expose probabilities only with both global and topic-level evidence."""
    by_tier = state['topic_tier_stats'].get(topic_id, {})
    evidence = {tier: {'correct':int(by_tier.get(tier,[0,0])[0]),
                       'answered':int(by_tier.get(tier,[0,0])[1])}
                for tier in TIERS}
    topic_samples = state['topic_stats'].get(topic_id, [0,0])[1]
    tier_diversity = sum(v['answered'] >= 2 for v in evidence.values())
    if (not public_report(state)['ready_for_soft_suggestions']
            or topic_samples < 6 or tier_diversity < 2):
        return {'predictive_ready': False, 'predicted_correct': {},
                'focus_tier': None, 'tier_evidence': evidence,
                'reason': 'Chưa đủ bằng chứng đa dạng và dự đoán được kiểm định để khuyến nghị bằng xác suất.'}
    probs = {tier: round(probability(state, topic_id, tier), 3) for tier in TIERS}
    focus = next((tier for tier in TIERS if probs[tier] < .67), 'nâng cao')
    return {'predictive_ready': True, 'predicted_correct': probs,
            'focus_tier': focus, 'tier_evidence': evidence,
            'reason': 'Gợi ý dự báo thử nghiệm, không sử dụng để quyết định đỗ/trượt hoặc mở khóa.'}


def save(c, user_id, grade, state):
    create_table(c)
    c.execute('''INSERT INTO roadmap_v2_personal_predictors
       (user_id,grade,version,state_json,trained_count,updated_at) VALUES (?,?,?,?,?,?)
       ON CONFLICT(user_id,grade) DO UPDATE SET version=excluded.version,
          state_json=excluded.state_json,trained_count=excluded.trained_count,
          updated_at=excluded.updated_at''',
       (user_id, grade, VERSION, json.dumps(state, ensure_ascii=False, separators=(',', ':')),
        state['n'], datetime.now(timezone.utc).isoformat()))

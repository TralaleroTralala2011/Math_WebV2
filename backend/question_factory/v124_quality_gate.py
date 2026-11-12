"""V124 conservative audit: never certifies mathematical method novelty automatically."""
import json, re
from collections import Counter, defaultdict
from pathlib import Path

PATTERN = re.compile(r'Trong các số nguyên từ 1 đến (\d+), có bao nhiêu số chia hết cho (\d+) nhưng không chia hết cho (\d+)\?')

def count_direct(n, a, b):
    return sum(k % a == 0 and k % b != 0 for k in range(1, n + 1))

def independent_check_delta(row):
    matches = PATTERN.findall(row['stem'])
    if row.get('family') != 'v123_delta_menh_de_tap_hop' or len(matches) != 2:
        return None
    vals = [count_direct(*map(int, item)) for item in matches]
    expected = vals[1] - vals[0]
    return str(expected) == str(row.get('numeric_result'))

def audit(candidates, questions):
    c = [json.loads(line) for line in Path(candidates).open(encoding='utf8') if line.strip()]
    q = [json.loads(line) for line in Path(questions).open(encoding='utf8') if line.strip()]
    family_counts = Counter(row['family'] for row in q)
    candidate_ids = {row['family'] for row in c}
    topic_counts = Counter(row['topic'] for row in c)
    method_clusters = defaultdict(list)
    for row in c:
        method_clusters[row['source_family']].append(row['family'])
    checked = [independent_check_delta(row) for row in q]
    verified = [x for x in checked if x is not None]
    violations = []
    if len(candidate_ids) != len(c): violations.append('duplicate_candidate_family')
    if any(n != 10 for n in family_counts.values()): violations.append('not_ten_questions_per_family')
    if set(family_counts) != candidate_ids: violations.append('candidate_question_mismatch')
    if any(row.get('published') is not False or row.get('independence_certified') is not False for row in c):
        violations.append('unreviewed_candidate_may_be_published')
    if not all(verified): violations.append('independent_oracle_disagreement')
    return {
        'release':'V124','source':'V123','candidate_records':len(c), 'question_records':len(q),
        'topics':len(topic_counts),'questions_per_candidate_valid':all(n==10 for n in family_counts.values()),
        'source_method_clusters':len(method_clusters),
        'largest_shared_core_cluster':max(map(len,method_clusters.values()),default=0),
        'independent_arithmetic_oracle_checked':len(verified),
        'independent_arithmetic_oracle_passed':sum(verified),
        'new_independent_methods_certified':0,
        'novelty_assessment':'NOT CERTIFIED: shared core method and generic operators',
        'violations':violations,
        'pass':not violations,
    }

if __name__ == '__main__':
    import sys
    print(json.dumps(audit(sys.argv[1],sys.argv[2]),ensure_ascii=False,indent=2))

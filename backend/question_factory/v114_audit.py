"""Audit V114 expansion against legacy bank; stream data, never inflate type counts.

Run in backend:
 python -m question_factory.v114_audit --out-dir ../V114_AUDIT \
     --legacy app/ai/verified_seed/verified_seed_bank.jsonl
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
from .bootstrap import CATALOG
from .engine import generate, independently_verify
from .expanded_catalog import BLUEPRINTS as V113, CONCEPT_COLLISIONS
from .v114_catalog import BLUEPRINTS as V114

# False positives should be escalated to an expert, never counted as proof.
CONCEPT_WARNINGS = {
    'linear_zero': 'linear-equation-solving',
    'symmetric_system_xy': 'vieta-and-symmetric-identities',
    'vieta_squares': 'vieta-and-symmetric-identities',
    'sqrt_domain_lower_bound': 'linear-inequality-bound',
    'trig_equation_zero_solution_count': 'trig-equation-periodic-solution-count',
    'trig_cos_one_root_count': 'trig-equation-periodic-solution-count',
    'cubic_stationary_positive': 'cubic-derivative-stationary-points',
    'cubic_local_max_value': 'cubic-derivative-stationary-points',
    'right_triangle_median': 'right-triangle-geometry',
    'three_perpendiculars_ramp': 'pythagorean-distance',
    'rectangular_prism_diagonal': 'pythagorean-distance',
    'tangent_segment_length': 'pythagorean-distance',
    'circle_chord_length': 'pythagorean-distance',
    'skew_axis_distance': 'coordinate-orthogonal-distance',
    'skew_lines_scalar_triple': 'scalar-triple-product',
    'tetrahedron_volume_determinant': 'scalar-triple-product',
    'log_change_of_base': 'logarithm-inverse',
    'distance_parallel_planes_3d': 'normal-distance',
    'closest_point_to_plane_squared': 'normal-distance',
    'parabola_horizontal_intersections': 'quadratic-discriminant-intersections',
    'triangle_inequality_integer_sides': 'integer-interval-count',
    'integer_interval_count': 'integer-interval-count',
    'parallel_plane_normal_parameter': 'vector-proportionality',
    'line_plane_perp_condition': 'vector-proportionality',
    'parallel_3d_direction_ratio': 'vector-proportionality',
    'line_plane_parallel_condition': 'vector-dot-product-zero',
    'perpendicular_3d_dot_parameter': 'vector-dot-product-zero',
}


def normalize_question(text):
    return re.sub(r'\s+', ' ', str(text).strip().casefold())


def audit(out_dir: str, legacy: str | None=None):
    out_dir=Path(out_dir);out_dir.mkdir(parents=True,exist_ok=True)
    catalog=json.loads(Path(CATALOG).read_text(encoding='utf-8'))
    assert len(catalog)==150
    by_topic=defaultdict(list);new_rows=[];forms=[]
    for version,blueprints in [('V113',V113),('V114',V114)]:
        for family,topic_id,title,method,difficulty in blueprints:
            assert any(t['id']==topic_id for t in catalog), f'unknown topic {topic_id}'
            fingerprints=[]
            for ordinal in range(10):
                seed_key=(f'{topic_id}:v113-{family}' if version=='V113'
                          else f'{topic_id}:v114-{family}')
                q=generate(family,ordinal,difficulty,seed_key=seed_key)
                valid,evidence=independently_verify(q)
                if not valid:raise RuntimeError(f'Invalid {version}/{family}/{ordinal}: {evidence}')
                fingerprints.append(q['fingerprint'])
                item={k:q[k] for k in ('family','ordinal','params','stem','answer','solution','difficulty','fingerprint')}
                item.update(topic_id=topic_id,version=version,
                    numerical_answer_verified=True,method_independence_certified=False,
                    method_review_status='pending-expert-review',verification=evidence)
                new_rows.append(item)
            if len(set(fingerprints))!=10:
                raise RuntimeError(f'{family} has duplicate stems within its 10 exercises')
            form=dict(version=version,topic_id=topic_id,family=family,name=title,method_signature=method,
                      difficulty=difficulty,worked_examples=10,
                      concept_group=CONCEPT_WARNINGS.get(family,CONCEPT_COLLISIONS.get(family,method)),
                      review_required='human/independent-method-review',method_independence_certified=False)
            forms.append(form);by_topic[topic_id].append(form)
    fingerprints=[q['fingerprint'] for q in new_rows]
    if len(set(fingerprints))!=len(fingerprints):
        counts=Counter(fingerprints)
        raise RuntimeError(f'Candidate duplicate stems: {sum(n-1 for n in counts.values() if n>1)}')
    legacy_count=legacy_matches=invalid_json=0
    if legacy is not None:
        tested=set(fingerprints)
        with Path(legacy).open(encoding='utf-8') as stream:
            for line in stream:
                try:
                    old=json.loads(line)
                    stem=old.get('question') or old.get('stem')
                    if not stem: continue
                    legacy_count+=1
                    fp=hashlib.sha256(normalize_question(stem).encode('utf-8')).hexdigest()
                    if fp in tested: legacy_matches+=1
                except json.JSONDecodeError:invalid_json+=1
    coverage=[]
    for topic in catalog:
        families=by_topic[topic['id']];count=len(families)
        coverage.append(dict(topic_id=topic['id'],grade=topic['grade'],topic=topic['name'],
              candidate_methods=count,candidate_exercises=count*10,methods_certified=0,
              methods_target=2000,methods_not_certified=2000,questions_target=20000,
              question_target_not_certified=20000,
              warning='candidate methods are not approved or certified distinct'))
    concept_counts=Counter(f['concept_group'] for f in forms)
    report=dict(version='V114',legacy_questions_inspected=legacy_count,legacy_invalid_json=invalid_json,
        new_stem_exact_collisions_with_legacy=legacy_matches,
        course_topics_in_catalog=150,topics_with_a_new_candidate= sum(x['candidate_methods']>0 for x in coverage),
        v113_blueprints=len(V113),v114_blueprints=len(V114),
        new_v114_questions=len(V114)*10,
        total_v113_v114_candidate_blueprints=len(forms),
        total_v113_v114_math_verified_candidate_questions=len(new_rows),
        distinct_candidate_stems=len(set(fingerprints)),
        coarse_method_concept_groups=len(concept_counts),
        potentially_colliding_concept_groups=sum(n>1 for n in concept_counts.values()),
        independently_certified_methods=0,expert_review_approved_methods=0,
        target_methods=300000,target_questions=3000000,
        note='ALL 165 family methods are review candidates. No global method uniqueness certification. This is NOT 100% completion.')
    (out_dir/'V114_REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (out_dir/'V114_150_TOPIC_COVERAGE.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2),encoding='utf-8')
    with (out_dir/'V114_150_TOPIC_COVERAGE.csv').open('w',encoding='utf-8-sig',newline='') as w:
        writer=csv.DictWriter(w,fieldnames=list(coverage[0]));writer.writeheader();writer.writerows(coverage)
    with (out_dir/'V114_CANDIDATE_METHODS.jsonl').open('w',encoding='utf-8') as w:
        for entry in forms:w.write(json.dumps(entry,ensure_ascii=False)+'\n')
    with (out_dir/'V114_1650_MATH_VERIFIED_PENDING_REVIEW.jsonl').open('w',encoding='utf-8') as w:
        for row in new_rows:w.write(json.dumps(row,ensure_ascii=False)+'\n')
    return report


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out-dir',default='../V114_AUDIT');parser.add_argument('--legacy',default=None)
    a=parser.parse_args();print(json.dumps(audit(a.out_dir,a.legacy),ensure_ascii=False,indent=2))

if __name__=='__main__':main()

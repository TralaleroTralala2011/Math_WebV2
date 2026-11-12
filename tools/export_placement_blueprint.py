"""Export honest per-grade placement coverage from the current database.

Example:
  cd MATH_WEB_GITHUB_READY
  python tools/export_placement_blueprint.py --out placement-audit

The JSON files are blueprints, NOT completed question papers.
They contain no learner responses, answers or account credentials.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from app.roadmap_v2_routes import coverage, DIFFICULTY


def build(grade):
    stats=coverage(grade)
    topics=[]
    for t in stats['topics']:
        missing={tier:max(0,3-t['by_difficulty'][tier]) for tier in DIFFICULTY}
        topics.append({
            'topic_id':t['id'],'title':t['title'],
            'target':{'nền tảng':3,'trung cấp':3,'nâng cao':3},
            'approved_by_tier':t['by_difficulty'],
            'missing_by_tier':missing,
            'reviewed_total':t['certified'],
            'candidate_total':t['available']-t['certified'],
            'missing_to_30_question_exam':max(0,30-t['certified']),
            'ready_for_placement':t['minimum_met'],
            'ready_for_topic_exam':t['eligible_for_30_question_exam'],
        })
    return {
        'grade':grade,'status':'coverage_blueprint_not_a_completed_exam',
        'requirements':{'tiers':list(DIFFICULTY),'min_per_tier':3,'max_per_tier':4,
                        'topic_exam_questions':30,'topic_exam_pass':25},
        'topic_count':stats['topic_count'],
        'candidate_questions':sum(t['candidate_total'] for t in topics),
        'reviewed_questions':sum(t['reviewed_total'] for t in topics),
        'topics_ready_for_placement':sum(t['ready_for_placement'] for t in topics),
        'topics_ready_for_30_question_exam':sum(t['ready_for_topic_exam'] for t in topics),
        'missing_reviewed_tier_slots':sum(sum(t['missing_by_tier'].values()) for t in topics),
        'missing_reviewed_exam_slots':sum(t['missing_to_30_question_exam'] for t in topics),
        'topics':topics,
        'warning':'Không tính câu chưa được duyệt là câu đã kiểm chứng. Dữ liệu có thể thay đổi sau khi Admin duyệt.'
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=ROOT/'placement-audit')
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    for grade in (10,11,12):
        data=build(grade)
        path=args.out/f'placement_grade_{grade}_coverage.json'
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
        print(grade,'topics',data['topic_count'],'candidates',data['candidate_questions'],
              'reviewed',data['reviewed_questions'],'missing tier slots',data['missing_reviewed_tier_slots'])


if __name__=='__main__':main()

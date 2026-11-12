#!/usr/bin/env python3
"""Conservative, explicit migration of topic aliases in V186–V190 patches.
Unmapped/unsupported items remain quarantined, never invent a new topic.
"""
import json,sys,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MAPPING={
 ('V186','conditional_without_replacement'):(11,'xac_suat_11'),
 ('V187','point_line_distance'):(10,'toa_do_phang'),
 ('V187','rectangle_area'):(10,'hinh_hoc_co_ban_10'),
 ('V188','quadratic_parameter_double_root'):(10,'phuong_trinh'),
 ('V188','log_inequality_integer_count'):(12,'bpt_logarit'),
 ('V189','independent_events_union'):(11,'xac_suat_11'),
 ('V189','vector_dot_product_3d'):(12,'toa_do_khong_gian'),
 ('V189','logarithm_product_rule'):(12,'ham_logarit'),
 ('V189','combinations_selection'):(10,'hoan_vi_chinh_hop_to_hop'),
 ('V190','quadratic_inequality_interval_length'):(10,'bat_phuong_trinh'),
 ('V190','orthogonal_projection_coefficient'):(12,'toa_do_khong_gian')
}
SOURCES={186:'V186_NEW_QUESTIONS',187:'V187_NEW_QUESTIONS',188:'V188_NEW_QUESTIONS',189:'V189_NEW_QUESTIONS',190:'V190_NEW_QUESTIONS'}
CAT=json.loads((ROOT/'backend/question_factory/catalog_150.json').read_text())
VALID={(c['grade'],c['id']) for c in CAT}
if __name__=='__main__':
 rows=[];skipped=[];stats=collections.Counter()
 for v,f in SOURCES.items():
  for line in (ROOT/'bank_updates'/f'{f}.jsonl').read_text(encoding='utf8').splitlines():
   r=json.loads(line); version=f'V{v}'; key=(version,r['family'])
   old=(r['grade'],r['topic']); target=MAPPING.get(key,old)
   if target not in VALID:
    skipped.append({'source_id':r['id'],'grade':r['grade'],'topic':r['topic'],'family':r['family'],'reason':'No safe exact mapping to one of 150 confirmed topics'})
    continue
   if target!=old:
    r['topic_original']=r['topic'];r['topic']=target[1];r['topic_mapping']='curated_explicit_V191'
   r['source_checkpoint_original']=r.get('source_checkpoint');r['source_checkpoint']='V190'
   r['source_bundle']='V191_RESCUE_'+version
   r['method_independence_certified']=False;r['production_integrated']=False
   r['validation_status']='prior_question_app_grader_rechecked_v191_pending_independent_solution_proof'
   rows.append(r);stats[version]+=1
 out=ROOT/'bank_updates/V191_RESCUED_PRIOR_IMPORT.jsonl'
 with out.open('w',encoding='utf-8') as z:
  for r in rows:z.write(json.dumps(r,ensure_ascii=False)+'\n')
 (ROOT/'bank_updates/V191_RESCUE_QUARANTINE.json').write_text(json.dumps(skipped,ensure_ascii=False,indent=2),encoding='utf8')
 sys.path.insert(0,str(ROOT/'backend'))
 from scripts.import_bank_updates import load_and_validate
 try: verified=load_and_validate(out)
 except Exception as e:
  print('RECHECK FAILED',repr(e));sys.exit(1)
 print(json.dumps({'rescued_qa_validated':len(verified),'skipped':len(skipped),'per_version':dict(stats),'unresolved':list({(x['grade'],x['topic']) for x in skipped})},ensure_ascii=False))

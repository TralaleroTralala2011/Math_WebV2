import zipfile,json,re,unicodedata,collections,pathlib,hashlib
R=pathlib.Path(__file__).resolve().parent
BASE=pathlib.Path('/mnt/data/MATH_WEB_GITHUB_READY_V130_METHOD_PROVENANCE_GATE.zip')
prefix='MATH_WEB_GITHUB_READY/'
forms=[json.loads(line) for line in (R/'V131_CANDIDATE_METHODS.jsonl').open(encoding='utf8')]
qs=[json.loads(line) for line in (R/'V131_VERIFIED_QUESTIONS.jsonl').open(encoding='utf8')]
def norm(t):return ' '.join(unicodedata.normalize('NFKC',t).casefold().split())
new={norm(q['question']) for q in qs}
old_stems=set();original_forms=[];scanned=0
with zipfile.ZipFile(BASE) as z:
 for f in ['V121_RESEARCH/V121_3000_NEW_QUESTIONS.jsonl','V123_RESEARCH/V123_10500_WORKED_QUESTIONS.jsonl']:
  for ln in z.read(prefix+f).decode('utf8').splitlines():
   row=json.loads(ln)
   for key in ('question','stem','prompt','text'):
    if isinstance(row.get(key),str):old_stems.add(norm(row[key]));break
   scanned+=1
 for f in ['V121_RESEARCH/V121_300_CANDIDATE_FORMS.jsonl','V123_RESEARCH/V123_1050_CANDIDATE_OBJECTIVES.jsonl']:
  original_forms.extend(json.loads(ln) for ln in z.read(prefix+f).decode('utf8').splitlines())
 topics={t['id']:t for t in json.loads(z.read(prefix+'learn-assets/topics.json'))}
exact_collisions=len(new&old_stems)
coverage=collections.Counter(q['topic'] for q in qs)
result={
 'version':'V131','base':'V130','requested_new_distinct_methods':1000,
 'candidate_methods_created':len(forms),'new_questions_created':len(qs),
 'new_topics_touched':len(coverage),'all_topics_catalogue':len(topics),
 'verified_answers_by_alternative_calculation':sum(q['answer']==q['independent_check'] for q in qs),
 'unique_question_texts':len(new),'historical_question_rows_scanned':scanned,
 'exact_question_stem_collisions_in_v121_and_v123':exact_collisions,
 'existing_form_records_examined':len(original_forms),
 'form_title_exact_normalization_collisions':sum(norm(f['title']) in {norm(x['title']) for x in original_forms} for f in forms),
 'candidate_topic_ids_valid':all(f['topic'] in topics for f in forms),
 'candidate_grade_matches_catalogue':all(f['grade']==topics[f['topic']]['grade'] for f in forms),
 'all_unpublished':all(not f['published'] and not q['published'] for f in forms for q in [] ) and all(not f['published'] for f in forms) and all(not q['published'] for q in qs),
 'new_methods_certified_independent':0,
 'reason_not_certified':'No full semantic method equivalence audit against historical and external problem archetypes, no expert pedagogical review.',
 'scope_limitation':'Exact-stem comparison only against V121 and V123 research corpora, not every historic question file. Existing test suite for whole backend/frontend not run.'}
assert result['candidate_topic_ids_valid'] and result['candidate_grade_matches_catalogue'] and result['all_unpublished']
(R/'V131_RESULTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(result,ensure_ascii=False,indent=2))

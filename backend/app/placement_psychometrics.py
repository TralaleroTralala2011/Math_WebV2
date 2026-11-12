"""Transparent classical-test-theory diagnostics for FIXED placement forms.

No ability estimates or validation claims without a sufficiently large,
representative sample. Descriptive statistics only; never train an LLM.
"""
import math
from collections import Counter

MIN_PILOT = 30


def variance(values):
    n=len(values)
    if n<2:return 0.0
    mean=sum(values)/n
    return sum((x-mean)**2 for x in values)/(n-1)


def correlation(xs,ys):
    if len(xs)<3 or len(xs)!=len(ys):return None
    mx=sum(xs)/len(xs);my=sum(ys)/len(ys)
    sx=sum((x-mx)**2 for x in xs);sy=sum((y-my)**2 for y in ys)
    if sx==0 or sy==0:return None
    return sum((x-mx)*(y-my) for x,y in zip(xs,ys))/math.sqrt(sx*sy)


def evaluate_fixed_paper(results,expected_ids,minimum=MIN_PILOT):
    """Results are server-graded review arrays, all from one immutable form.

    Duplicate learner attempts must be removed by the caller.
    Missing answers count as incorrect, but skipped rate is reported.
    """
    ids=list(expected_ids)
    if len(ids)!=len(set(ids)):
        raise ValueError('Duplicate question ID in fixed paper')
    matrices=[];skip_matrices=[]
    for result in results:
        review=result.get('review',[])
        lookup={q['qid']:q for q in review}
        if len(lookup)!=len(ids) or set(lookup)!=set(ids):continue
        matrices.append([int(lookup[qid]['verdict']=='correct') for qid in ids])
        skip_matrices.append([int(lookup[qid]['verdict']=='skipped') for qid in ids])
    n=len(matrices)
    if n<minimum:
        return {'pilot_status':'insufficient_sample','sample_size':n,'minimum_required':minimum,
                'reliability_estimated':False,
                'note':'Chưa đủ học sinh để ước lượng độ ổn định và độ phân biệt của đề. Không kết luận đề khách quan.'}
    k=len(ids)
    total_scores=[sum(row) for row in matrices]
    total_var=variance(total_scores)
    item_vars=[variance([row[j] for row in matrices]) for j in range(k)]
    alpha=(k/(k-1))*(1-sum(item_vars)/total_var) if k>1 and total_var>0 else None
    items=[]
    for j,qid in enumerate(ids):
        values=[row[j] for row in matrices]
        corrected=[total_scores[i]-values[i] for i in range(n)]
        difficulty=sum(values)/n
        discrimination=correlation(values,corrected)
        skip_rate=sum(row[j] for row in skip_matrices)/n
        warnings=[]
        if difficulty<0.15:warnings.append('very_difficult')
        if difficulty>0.95:warnings.append('very_easy')
        if discrimination is not None and discrimination<0:warnings.append('negative_discrimination')
        if skip_rate>0.30:warnings.append('high_skip_rate')
        items.append({'qid':qid,'p_correct':round(difficulty,3),
                      'corrected_item_total_correlation':round(discrimination,3) if discrimination is not None else None,
                      'skip_rate':round(skip_rate,3),'warnings':warnings})
    return {'pilot_status':'analysis_available_not_validated', 'sample_size':n,
            'minimum_required':minimum,'reliability_estimated':alpha is not None,
            'cronbach_alpha':round(alpha,3) if alpha is not None else None,
            'mean_score':round(sum(total_scores)/n,2), 'items':items,
            'note':'Độ tin cậy nội tại chỉ là một bằng chứng; cần thêm phân tích công bằng, nội dung, tính ổn định và thử nghiệm thực địa.'}

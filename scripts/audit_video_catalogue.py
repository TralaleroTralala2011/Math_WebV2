#!/usr/bin/env python3
"""Audit video inventory, topic coverage and cross-area duplicates. Run from project root."""
import json,re,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
topics=json.loads((root/'learn-assets/topics.json').read_text(encoding='utf-8'))
video=json.loads((root/'learn-assets/curated-videos.json').read_text(encoding='utf-8'))
errors=[];counts={'learning':0,'path':0};missing=[];ids={}
from collections import Counter
keycounts=Counter(f"{t['grade']}:{t['title'].strip().lower()}" for t in topics)
expected=set(keycounts)
duplicate_topic_titles={k:n for k,n in keycounts.items() if n>1}
if duplicate_topic_titles: errors.append(f'duplicate topic keys need unique IDs: {duplicate_topic_titles}')
for key in sorted(expected):
    record=video.get(key,{})
    for area in ('learning','path'):
        entries=record.get(area,[])
        if len(entries)!=3: missing.append({'topic':key,'area':area,'count':len(entries)})
        for item in entries:
            vid=item.get('id','')
            if not re.fullmatch(r'[A-Za-z0-9_-]{11}',vid):errors.append(f'{key}/{area}: invalid ID {vid}')
            if not item.get('title') or not item.get('channel'):errors.append(f'{key}/{area}: missing title/channel')
            if item.get('status')!='verified':errors.append(f'{key}/{area}: not verified')
            if vid in ids:errors.append(f'duplicate video ID {vid}: {ids[vid]} and {key}/{area}')
            ids[vid]=key+'/'+area
            counts[area]+=1
for key in video:
    if key not in expected:errors.append(f'unknown topic {key}')
report={'topics':len(topics),'unique_title_keys':len(expected),'duplicate_topic_titles':duplicate_topic_titles,'target':len(topics)*6,'counts':counts,'missing_slots':sum(3-m['count'] for m in missing if m['count']<3),'incomplete_sections':missing,'errors':errors,'note':'This validates metadata only; playback, pedagogy and embed permissions require manual or authorized external verification.'}
out=root/'VIDEO_CATALOGUE_AUDIT.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(f"Topics: {len(topics)} | video records: {sum(counts.values())}/{len(topics)*6} | errors: {len(errors)} | missing sections: {len(missing)}")
sys.exit(1 if errors or missing else 0)

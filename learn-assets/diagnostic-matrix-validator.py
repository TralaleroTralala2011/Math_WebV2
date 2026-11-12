import json,sys,collections
rows=json.load(open(sys.argv[1],encoding="utf-8"))
slots={("nen_tang","ly_thuyet","trac_nghiem"),("nen_tang","ly_thuyet","dung_sai"),("trung_cap","ly_thuyet","trac_nghiem"),("trung_cap","thuc_te","trac_nghiem"),("kho","ly_thuyet","dung_sai"),("kho","thuc_te","tra_loi_ngan")}
by=collections.defaultdict(list)
for r in rows:by[(r["grade"],r["topic_id"])].append(r)
errors=[]
for topic,rs in by.items():
 if len(rs)!=6 or {(r["difficulty"],r["context"],r["format"]) for r in rs}!=slots:errors.append(topic)
complete=sum(bool(r["question"].strip() and r["answer"].strip() and r["solution"].strip() and r["verified"]) for r in rows)
print(f"Topics={len(by)}, Slots={len(rows)}, Verified questions={complete}, Invalid matrices={len(errors)}")
if errors:print(errors);sys.exit(1)

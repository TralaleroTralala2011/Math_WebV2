import json
import tempfile
import unittest
from pathlib import Path
from scripts.audit_research_linkage_v137 import audit

class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.folder=self.root/'V999_RESEARCH';self.folder.mkdir()
        self.method={'method_id':'m1','topic':'t1','grade':10,'questions_expected':2,'published':False,'independence_certified':False}
        self.questions=[{'id':'q1','method_id':'m1','topic':'t1','grade':10,'question':'f(x)=x+(-3)','answer':'1','solution':'Step one','published':False},{'id':'q2','method_id':'m1','topic':'t1','grade':10,'question':'f(x)=x+(3)','answer':'2','solution':'Step two','published':False}]
    def tearDown(self):self.tmp.cleanup()
    def run_audit(self):
        (self.folder/'V999_CANDIDATE_METHODS.jsonl').write_text(json.dumps(self.method)+'\n')
        (self.folder/'V999_VERIFIED_QUESTIONS.jsonl').write_text('\n'.join(map(json.dumps,self.questions))+'\n')
        return audit(self.root)
    def test_sign_sensitive(self):self.assertFalse(self.run_audit()['issues'])
    def test_duplicate_detected(self):
        self.questions[1]['question']=self.questions[0]['question'];self.assertTrue(any('duplicate normalized' in str(x) for x in self.run_audit()['issues']))
    def test_orphan_detected(self):
        self.questions[1]['method_id']='missing';self.assertTrue(any('orphan' in str(x) for x in self.run_audit()['issues']))
    def test_topic_mismatch_detected(self):
        self.questions[1]['topic']='wrong';self.assertTrue(any('topic or grade mismatch' in str(x) for x in self.run_audit()['issues']))
    def test_unsafe_status_detected(self):
        self.questions[1]['published']=True;self.assertTrue(any('unsafe question' in str(x) for x in self.run_audit()['issues']))
    def test_missing_solution_detected(self):
        self.questions[1]['solution']='';self.assertTrue(any('missing question' in str(x) for x in self.run_audit()['issues']))
if __name__=='__main__':unittest.main()

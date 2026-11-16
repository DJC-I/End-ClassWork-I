"""Record exact website and Word sources used by the phase-three production."""
import hashlib
import json
from pathlib import Path
from xml.etree import ElementTree as ET
from docx import Document

ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/"docs/phase3"
sources=[]
paths=sorted((ROOT/"backend").glob("*.py"))+sorted((ROOT/"frontend/src").rglob("*"))
paths += [ROOT/x for x in ("frontend/package.json","frontend/package-lock.json","frontend/index.html","frontend/vite.config.ts","frontend/tsconfig.json","frontend/playwright.config.ts","README.md","PROJECT_STATUS.md","TASKS.md","docs/ORIGINAL_REQUEST.txt","docs/PHASE1_ACCEPTANCE.md","docs/PHASE2_ACCEPTANCE.md","docs/pytest-results.xml","docs/e2e-results.json","docs/restart-results.json","docs/scenario-results.json")]
for f in paths:
    if not f.is_file():continue
    content=f.read_bytes()
    sources.append({"file":f.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(content).hexdigest(),"bytes":len(content)})
phase2=json.loads((ROOT/"docs/phase2/verification.json").read_text(encoding="utf-8"))
documents=[]
for result in phase2["outputs"]:
    f=ROOT/result["file"]
    sha=hashlib.sha256(f.read_bytes()).hexdigest()
    assert sha==result["sha256"]
    d=Document(f)
    text="\n".join([p.text for p in d.paragraphs]+[" | ".join(c.text for c in row.cells) for t in d.tables for row in t.rows])
    (QA/(f.stem+"_来源全文.txt")).write_text(text,encoding="utf-8")
    documents.append({"file":result["file"],"sha256":sha,"pages_from_phase2":result["pages"],"paragraphs":len(d.paragraphs),"tables":len(d.tables),"images":len(d.inline_shapes),"text_characters":len(text)})
xml=ET.parse(ROOT/"docs/pytest-results.xml").getroot()
suites=list(xml.iter("testsuite"))
prior_pytest={k:sum(int(s.get(k,"0")) for s in suites) for k in ("tests","failures","errors","skipped")}
assert prior_pytest=={"tests":28,"failures":0,"errors":0,"skipped":0}
e2e=json.loads((ROOT/"docs/e2e-results.json").read_text(encoding="utf-8"))["stats"]
assert e2e["expected"]==4 and e2e["unexpected"]==0 and e2e["skipped"]==0
assert json.loads((ROOT/"docs/restart-results.json").read_text(encoding="utf-8"))["passed"] is True
simulation=[]
prior=json.loads((ROOT/"docs/scenario-results.json").read_text(encoding="utf-8"))
for name in ("rain","snow","normal"):
    result=json.loads((QA/f"{name}-recorded-simulation.json").read_text(encoding="utf-8"))
    simulation.append({"scenario":name,"before":result["before"],"after":result["after"],"orders":result["order_count"],"samples_each_side":result["sample_count"]})
audit={"phase":3,"documents_unchanged":True,"website_sources":sources,"documents":documents,"previous_phase_test_evidence":{"pytest":prior_pytest,"edge_expected":e2e["expected"],"edge_unexpected":e2e["unexpected"],"tests_rerun_this_phase":False},"new_actual_recorded_simulation_results":simulation,"production_database_used_for_recording":False,"recording_database":".tools/phase3/recording.db"}
(QA/"source-audit.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding="utf-8")
print("Verified",len(sources),"sources and",len(documents),"actual DOCX files; prior tests 28 + 4 confirmed")

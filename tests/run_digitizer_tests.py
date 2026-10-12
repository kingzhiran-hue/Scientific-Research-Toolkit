import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_digitizer.py')
result=unittest.TextTestRunner(verbosity=2).run(suite)
out=ROOT/'outputs/tests';out.mkdir(parents=True,exist_ok=True)
(out/'digitizer_test_summary.json').write_text(json.dumps(dict(PASS=result.wasSuccessful(),tests=result.testsRun,failures=len(result.failures),errors=len(result.errors)),indent=2),encoding='utf-8')
raise SystemExit(0 if result.wasSuccessful() else 1)

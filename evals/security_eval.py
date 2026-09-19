# Deterministic security-policy checks; no LLM required.
import sys
sys.path.insert(0,"../python-gateway")
from app.security import authenticate,authorize
from app.policy import evaluate

tests=[]
reader=authenticate("demo-reader-token")
try:
    authorize(reader,"ops_restart_service")
    tests.append(("reader_write_denied",False))
except PermissionError:
    tests.append(("reader_write_denied",True))

tests.append(("prod_approval",evaluate("ops_restart_service",{"environment":"production"}).approval_required))
tests.append(("dev_no_approval",not evaluate("ops_restart_service",{"environment":"dev"}).approval_required))
tests.append(("bad_priority_denied",not evaluate("crm_create_ticket",{"priority":"superurgent"}).allowed))

for name,ok in tests: print("PASS" if ok else "FAIL",name)
raise SystemExit(0 if all(x[1] for x in tests) else 1)

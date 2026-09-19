from app.security import authenticate,authorize
from app.policy import evaluate
def test_reader_cannot_write():
    ident=authenticate("demo-reader-token")
    try:
        authorize(ident,"crm_create_ticket")
        assert False
    except PermissionError: pass
def test_prod_restart_requires_approval():
    d=evaluate("ops_restart_service",{"environment":"production"})
    assert d.allowed and d.approval_required
def test_dev_restart_no_approval():
    d=evaluate("ops_restart_service",{"environment":"dev"})
    assert d.allowed and not d.approval_required

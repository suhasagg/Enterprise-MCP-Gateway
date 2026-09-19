from dataclasses import dataclass
from fastapi import HTTPException

@dataclass(frozen=True)
class Identity:
    subject:str
    tenant_id:str
    scopes:frozenset[str]

# Local demo only. Replace with OAuth/OIDC JWT validation in production.
TOKENS={
 "demo-reader-token":Identity("alice","acme",frozenset({"crm:read","ops:read"})),
 "demo-operator-token":Identity("bob","acme",frozenset({"crm:read","crm:write","ops:read","ops:write"})),
 "other-tenant-token":Identity("charlie","globex",frozenset({"crm:read"})),
}

def authenticate(token:str|None)->Identity:
    if not token or token not in TOKENS: raise PermissionError("invalid bearer token")
    return TOKENS[token]

TOOL_SCOPES={
 "crm_get_customer":"crm:read",
 "crm_create_ticket":"crm:write",
 "ops_get_deployment":"ops:read",
 "ops_restart_service":"ops:write",
}
def authorize(identity:Identity,tool:str):
    required=TOOL_SCOPES.get(tool)
    if required is None: raise PermissionError("tool not registered")
    if required not in identity.scopes: raise PermissionError(f"missing scope {required}")

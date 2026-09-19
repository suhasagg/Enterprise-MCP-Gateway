import json
from .database import Session
from .models import AuditEvent
async def write_audit(request_id,identity,tool,decision,args,result=""):
    async with Session() as db:
        db.add(AuditEvent(request_id=request_id,tenant_id=identity.tenant_id,
            principal=identity.subject,tool=tool,decision=decision,arguments=args,
            result_summary=str(result)[:2000]))
        await db.commit()

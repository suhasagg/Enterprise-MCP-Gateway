import asyncio,uuid,os
from mcp.server.fastmcp import FastMCP
from redis.asyncio import Redis
from prometheus_client import Counter
from .config import settings
from .database import init_db
from .security import authenticate,authorize
from .policy import evaluate
from .rate_limit import RateLimiter
from .downstream import Downstreams
from .audit import write_audit

mcp=FastMCP("enterprise-mcp-gateway",host="0.0.0.0",port=8000,stateless_http=True)
redis=Redis.from_url(settings.redis_url,decode_responses=True)
limiter=RateLimiter(redis)
downstreams=Downstreams()
CALLS=Counter("mcp_gateway_tool_calls_total","Gateway tool calls",["tool","decision"])

async def governed(tool:str,args:dict,access_token:str,approval_token:str|None=None):
    rid="req-"+uuid.uuid4().hex[:12]
    try:
        identity=authenticate(access_token)
        authorize(identity,tool)
        if not await limiter.allow(identity.tenant_id,identity.subject):
            CALLS.labels(tool,"rate_limited").inc()
            await write_audit(rid,identity,tool,"RATE_LIMITED",args)
            return {"ok":False,"error":"rate limit exceeded","request_id":rid}
        decision=evaluate(tool,args)
        if not decision.allowed:
            CALLS.labels(tool,"denied").inc()
            await write_audit(rid,identity,tool,"DENIED",args)
            return {"ok":False,"error":decision.reason,"request_id":rid}
        if decision.approval_required and approval_token != f"approve:{identity.tenant_id}:{tool}":
            CALLS.labels(tool,"approval_required").inc()
            await write_audit(rid,identity,tool,"APPROVAL_REQUIRED",args)
            return {"ok":False,"error":"human approval required","request_id":rid,
                    "approval_scope":f"{identity.tenant_id}:{tool}"}
        result=await downstreams.call(tool,args,identity.tenant_id)
        CALLS.labels(tool,"allowed").inc()
        await write_audit(rid,identity,tool,"ALLOWED",args,result)
        return {"ok":True,"request_id":rid,"result":str(result)}
    except PermissionError as e:
        # No identity may be available for invalid token; don't persist secrets.
        CALLS.labels(tool,"unauthorized").inc()
        return {"ok":False,"error":str(e),"request_id":rid}

@mcp.tool()
async def crm_get_customer(customer_id:str,access_token:str)->dict:
    """Read a customer. Requires crm:read."""
    return await governed("crm_get_customer",{"customer_id":customer_id},access_token)

@mcp.tool()
async def crm_create_ticket(customer_id:str,title:str,description:str,priority:str,
                            access_token:str)->dict:
    """Create a support ticket. Requires crm:write."""
    return await governed("crm_create_ticket",
        {"customer_id":customer_id,"title":title,"description":description,"priority":priority},
        access_token)

@mcp.tool()
async def ops_get_deployment(service:str,environment:str,access_token:str)->dict:
    """Read deployment state. Requires ops:read."""
    return await governed("ops_get_deployment",
        {"service":service,"environment":environment},access_token)

@mcp.tool()
async def ops_restart_service(service:str,environment:str,reason:str,access_token:str,
                              approval_token:str|None=None)->dict:
    """Restart a service. Production requires explicit human approval."""
    return await governed("ops_restart_service",
        {"service":service,"environment":environment,"reason":reason},
        access_token,approval_token)

if __name__=="__main__":
    asyncio.run(init_db())
    mcp.run(transport="streamable-http")

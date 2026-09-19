from agents.mcp import MCPServerStreamableHttp
from .config import settings

class Downstreams:
    def server_for(self,tool:str):
        if tool.startswith("crm_"): return settings.crm_mcp_url
        if tool.startswith("ops_"): return settings.ops_mcp_url
        raise ValueError("unknown route")

    async def call(self,tool:str,args:dict,tenant_id:str):
        # Gateway names are intentionally decoupled from backend names.
        mapping={
          "crm_get_customer":"get_customer",
          "crm_create_ticket":"create_ticket",
          "ops_get_deployment":"get_deployment",
          "ops_restart_service":"restart_service",
        }
        backend=mapping[tool]
        async with MCPServerStreamableHttp(
            name="downstream",
            params={"url":self.server_for(tool),"headers":{"X-Tenant-Id":tenant_id},"timeout":10},
            cache_tools_list=True,max_retry_attempts=2,use_structured_content=True
        ) as server:
            return await server.call_tool(backend,args)

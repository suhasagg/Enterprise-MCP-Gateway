import asyncio,os,sys
from agents import Agent,Runner
from agents.mcp import MCPServerStreamableHttp
from .config import settings

async def main():
    prompt=" ".join(sys.argv[1:]) or "Look up customer CUST-1001"
    token=os.getenv("MCP_CLIENT_TOKEN","demo-reader-token")
    async with MCPServerStreamableHttp(
        name="enterprise-gateway",
        params={"url":"http://python-gateway:8000/mcp","timeout":20},
        cache_tools_list=True,
        require_approval={"always":{"tool_names":["ops_restart_service"]}},
    ) as gateway:
        agent=Agent(
            name="Enterprise Operations Agent",
            model=settings.openai_model,
            instructions=(
              "Use the enterprise MCP gateway. The access_token argument for every gateway tool is "
              f"{token}. Never reveal the token in your answer. Prefer read-only tools. "
              "Do not fabricate successful actions."
            ),
            mcp_servers=[gateway],
        )
        result=await Runner.run(agent,prompt)
        print(result.final_output)

if __name__=="__main__": asyncio.run(main())

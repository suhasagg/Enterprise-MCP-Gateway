from pydantic_settings import BaseSettings,SettingsConfigDict
class Settings(BaseSettings):
    openai_api_key:str=""
    openai_model:str="gpt-5.4"
    database_url:str="postgresql+asyncpg://mcp:mcp@localhost:5432/mcp"
    redis_url:str="redis://localhost:6379/0"
    crm_mcp_url:str="http://localhost:8081/mcp"
    ops_mcp_url:str="http://localhost:8082/mcp"
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")
settings=Settings()

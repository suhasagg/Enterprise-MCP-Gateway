import time
from redis.asyncio import Redis
class RateLimiter:
    def __init__(self,redis:Redis,limit=60,window=60):
        self.redis,self.limit,self.window=redis,limit,window
    async def allow(self,tenant:str,principal:str)->bool:
        bucket=int(time.time()//self.window)
        key=f"rl:{tenant}:{principal}:{bucket}"
        n=await self.redis.incr(key)
        if n==1: await self.redis.expire(key,self.window+2)
        return n<=self.limit

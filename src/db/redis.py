import redis.asyncio as aioredis
from src.config import Config

token_block_list = aioredis.from_url(Config.REDIS_URL)

async def add_jti_to_blocklist(jti: str) -> None:
    await token_block_list.set(jti, "true", ex=Config.ACCESS_TOKEN_EXPIRY_MINUTE * 60)
    
async def token_in_blocklist(jti: str) -> bool:
    return (await token_block_list.get(jti)) is not None


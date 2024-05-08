from starlette.requests import Request
from app.logging import logger
from redis.asyncio import Redis

async def get_redis_client(request: Request):
    try:
        redis_client = Redis(connection_pool=request.app.state.redis_pool, decode_responses=True)
        yield redis_client
    except Exception as e:
        logger.exception({"get_redis_client()": f"Error: {e}"})
    finally:
        await redis_client.close(close_connection_pool=True)
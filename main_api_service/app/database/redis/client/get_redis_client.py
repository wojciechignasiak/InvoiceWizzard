from starlette.requests import Request
from app.logging import logger

async def get_redis_client(request: Request):
    try:
        yield request.app.state.redis_client
    except Exception as e:
        logger.exception({"get_redis_client": f"Error: {e}"})

from starlette.requests import Request
from app.logging import logger

async def get_repositories_registry(request: Request):
    try:
        yield request.app.state.repositories_registry
    except Exception as e:
        logger.exception({"get_repositories_registry": f"Error: {e}"})
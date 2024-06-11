from starlette.requests import Request
from app.logging import logger

async def get_repositories_factory(request: Request):
    try:
        yield request.app.state.repositories_factory
    except Exception as e:
        logger.exception({"get_repositories_factory": f"Error: {e}"})
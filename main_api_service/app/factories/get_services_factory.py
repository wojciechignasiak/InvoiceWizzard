from starlette.requests import Request
from app.logging import logger

async def get_services_factory(request: Request):
    try:
        yield request.app.state.services_factory
    except Exception as e:
        logger.exception({"get_services_factory": f"Error: {e}"})
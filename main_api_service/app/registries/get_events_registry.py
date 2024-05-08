from starlette.requests import Request
from app.logging import logger

async def get_events_registry(request: Request):
    try:
        yield request.app.state.events_registry
    except Exception as e:
        logger.exception({"get_events_registry": f"Error: {e}"})
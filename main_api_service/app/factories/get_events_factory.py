from starlette.requests import Request
from app.logging import logger

async def get_events_factory(request: Request):
    try:
        yield request.app.state.events_factory
    except Exception as e:
        logger.exception({"get_events_factory": f"Error: {e}"})
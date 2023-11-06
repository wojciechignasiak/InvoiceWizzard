from starlette.requests import Request

async def get_redis_client(request: Request):
    try:
        return request.app.state.redis_client
    except Exception as e:
        print({"get_redis_client": f"Error: {e}"})
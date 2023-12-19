from starlette.requests import Request

async def get_repositories_registry(request: Request):
    try:
        yield request.app.state.repositories_registry
    except Exception as e:
        print({"get_repositories_registry": f"Error: {e}"})
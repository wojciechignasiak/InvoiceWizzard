
from fastapi import FastAPI
from contextlib import asynccontextmanager
from starlette.middleware.cors import CORSMiddleware
from starlette import middleware


middleware = [
    middleware.Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods="*",
        allow_headers=["*"]
    )]



@asynccontextmanager
async def lifespan(app: FastAPI):
    ''' Run at startup
        Initialise databases clients.
    '''

    yield
    ''' Run on shutdown
        Close the connection
        Clear variables and release the resources
    '''


def create_application() -> FastAPI:
    application = FastAPI(lifespan=lifespan, openapi_url="/openapi.json", docs_url="/docs", middleware=middleware)
    return application

app = create_application()
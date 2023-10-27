import os
import asyncio
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
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

POSTGRES_USERNAME = os.environ.get("POSTGRES_USERNAME")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT")
POSTGRES_DB = os.environ.get("POSTGRES_DB")

POSTGRES_URL = f"postgresql+asyncpg://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

@asynccontextmanager
async def lifespan(app: FastAPI):
    ''' Run at startup
        Initialise databases clients.
    '''
    while True:
        try:
            print("Creating PostgreSQL engine...")
            app.state.engine: AsyncEngine = create_async_engine(
                                POSTGRES_URL,
                                echo=False,
                                future=True
                            )
            print("Testing connection to PostgreSQL...")
            async with app.state.engine.connect() as connection:
                result = await connection.execute(text("SELECT current_user;"))
                current_user = result.scalar()

            if current_user == POSTGRES_USERNAME:
                print('Connection to PostgreSQL status: Connected')
            else:
                print('Connection to PostgreSQL status: Failed. Retrying...')
                raise SQLAlchemyError
            break
        except SQLAlchemyError:
            await asyncio.sleep(3)

    yield
    ''' Run on shutdown
        Close the connection
        Clear variables and release the resources
    '''
    print("Disposing PostgreSQL engine...")
    await app.state.engine.dispose()


def create_application() -> FastAPI:
    application = FastAPI(lifespan=lifespan, openapi_url="/openapi.json", docs_url="/docs", middleware=middleware)
    return application

app = create_application()
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi import Request
from app.database.postgres.exceptions.custom_postgres_exceptions import PostgreSQLDatabaseError, PostgreSQLIntegrityError

async def get_session(request: Request) -> AsyncGenerator:
        AsyncSessionFactory: sessionmaker = sessionmaker(request.app.state.engine, class_=AsyncSession, autoflush=False, expire_on_commit=False)
        async with AsyncSessionFactory() as session:
            try:
                yield session
                await session.commit()
            except (PostgreSQLIntegrityError, PostgreSQLDatabaseError):
                await session.rollback()
            finally:
                await session.close()

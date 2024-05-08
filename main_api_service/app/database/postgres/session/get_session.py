from fastapi import Request
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, async_sessionmaker

async def get_session(request: Request):
        try:
            session = async_scoped_session(async_sessionmaker(request.app.state.engine, expire_on_commit=False, class_=AsyncSession), scopefunc=asyncio.current_task)
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
        finally:
            await session.remove()
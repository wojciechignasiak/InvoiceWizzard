from sqlalchemy.ext.asyncio import AsyncSession
from app.database.postgres.session.get_session import get_session
from fastapi import Depends


class BasePostgresRepository:
    __slots__ = 'session'
    
    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self.session: AsyncSession = session
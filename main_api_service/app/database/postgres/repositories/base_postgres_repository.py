from sqlalchemy.ext.asyncio import AsyncSession

class BasePostgresRepository:
    __slots__ = 'session'
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session
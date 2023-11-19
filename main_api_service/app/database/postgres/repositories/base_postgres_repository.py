from sqlalchemy.ext.asyncio import AsyncSession

class BasePostgresRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session
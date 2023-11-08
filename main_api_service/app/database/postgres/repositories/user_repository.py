from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from app.schema.schema import User
from app.models.user_model import NewUserTemporaryModel
from datetime import date

class UserPostgresRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    async def create_new_user(self, user: NewUserTemporaryModel):
        try:
            stmt = (insert(User).
                    values(
                        email=user.email, 
                        password=user.password, 
                        salt=user.salt, 
                        registration_date=user.registration_date,
                        last_login=date.today().isoformat()
                        ))
            result = await self.session.execute(stmt)
            print(result)
        except Exception as e:
            self.session.rollback()
            print(e)

    async def find_user_by_email(self, email: str) -> list:
        try:
            stmt = select(User).where(User.email == email)
            result = await self.session.execute(stmt)
            return result.all()
        except Exception as e:
            print(e)

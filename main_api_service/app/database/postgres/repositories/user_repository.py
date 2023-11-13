from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update
from app.schema.schema import User
from app.models.user_model import NewUserTemporaryModel, UserPersonalInformation
from datetime import datetime, date
from uuid import uuid4


class UserPostgresRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    async def create_new_user(self, user: NewUserTemporaryModel):
        try:
            stmt = (
                insert(User).
                values(
                    id=uuid4(),
                    email=user.email, 
                    password=user.password,
                    salt=user.salt, 
                    registration_date=datetime.strptime(user.registration_date, '%Y-%m-%d').date(),
                    last_login=date.today()
                    ).
                    returning(User.id)
                )
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.all()
        except Exception as e:
            await self.session.rollback()
            print(e)

    async def find_user_by_email(self, email: str) -> User:
        try:
            stmt = select(User).where(User.email == email)
            result = await self.session.scalar(stmt)
        
            return result
        except Exception as e:
            print(e)

    async def update_last_login(self, id: str) -> list|None:
        try:
            stmt = (
                update(User).
                where(User.id == id).
                values(last_login = date.today()).
                returning(User.last_login)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()

            if result:
                return result.all()
            else:
                return None

        except Exception as e:
            await self.session.rollback()
            print(e)

    async def update_personal_info(self, id: str, personal_info: UserPersonalInformation) -> list|None:
        try:
            stmt = (
                update(User).
                where(User.id == id).
                values(first_name = personal_info.first_name,
                    last_name = personal_info.last_name,
                    phone_number = personal_info.phone_number,
                    city = personal_info.city,
                    street = personal_info.street).
                    returning(User.id)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            if result:
                return result.all()
            else:
                return None
        except Exception as e:
            await self.session.rollback()
            print(e)



from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from app.schema.schema import User
from app.models.account_registration_model import AccountRegistrationTemporaryDataModel
from datetime import date

class AccountRegistrationPostgresRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    async def create(self, account: AccountRegistrationTemporaryDataModel):
        try:
            stmt = (insert(User).
                    values(
                        email=account.email, 
                        password=account.password, 
                        salt=account.salt, 
                        registration_date=account.registration_date,
                        last_login=date.today().isoformat()
                        ))
            result = await self.session.execute(stmt)
            print(result)
        except Exception as e:
            self.session.rollback()
            print(e)

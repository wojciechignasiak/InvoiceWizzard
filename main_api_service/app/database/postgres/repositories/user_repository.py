#internal modules
from main_api_service.app.database.postgres.repositories.base_postgres_repository import BasePostgresRepository
from main_api_service.app.custom_exceptions.custom_exceptions import DatabaseError
from main_api_service.app.schema.schema import User
from main_api_service.app.models.user_model import (
    CreateUserModel,
    UserPersonalInformationModel,
    ConfirmedUserEmailChangeModel, 
    ConfirmedUserPasswordChangeModel
    )

#3rd party libraries
from fastapi import status
from sqlalchemy import insert, select, update, Select

#1st party libraries
from typing import Protocol
from datetime import date
from uuid import UUID

class IUserPostgresRepository(Protocol):

    async def create_user(self, new_user: CreateUserModel) -> User:
        ...

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        ...

    async def get_user_by_email_address(self, user_email_address: str) -> User | None:
        ...

    async def update_user_last_login(self, user_id: UUID) -> None:
        ...

    async def update_user_personal_information(self, user_id: UUID, personal_information: UserPersonalInformationModel) -> None:
        ...

    async def update_user_email_address(self, new_email: ConfirmedUserEmailChangeModel) -> None:
        ...

    async def update_user_password(self, new_password: ConfirmedUserPasswordChangeModel) -> None:
        ...

async def new_user_postgres_repository(session: AsyncSession = Depends(get_session)) -> IUserPostgresRepository:
    try:
        return UserPostgresRepository(
            session
        )
    except Exception as e:
        raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred while creating user repository.",
                argument=None,
                child_error=e
            )

class UserPostgresRepository(BasePostgresRepository):

    async def create_user(self, new_user: CreateUserModel) -> User:
        try:
            stmt = (
                insert(User).
                values(
                    id=new_user.id,
                    email=new_user.email, 
                    password=new_user.password,
                    salt=new_user.salt, 
                    registration_date=new_user.registration_date,
                    last_login=new_user.last_login
                    ).
                    returning(User)
                )
            user = await self.session.scalar(stmt)
            return user
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred while creating new user in sql database.",
                argument={'new_user': new_user},
                child_error=e
            )

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        try:
            stmt: Select[tuple[User]] = select(User).where(User.id == user_id)
            user: User | None = await self.session.scalar(stmt)
            return user
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred while getting user by id: {user_id} from sql database.",
                class_and_method="UserPostgresRepository.get_user_by_id()",
                argument={'user_id': user_id},
                child_error=e
            )

    async def get_user_by_email_address(self, user_email_address: str) -> User | None:
        try:
            stmt: Select[tuple[User]] = select(User).where(User.email == user_email_address)
            user: User | None = await self.session.scalar(stmt)
            return user
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred while getting user by email address: {user_email_address} from sql database.",
                argument={'user_email_address': user_email_address},
                child_error=e
            )

    async def update_user_last_login(self, user_id: UUID) -> None:
        try:
            stmt = (
                update(User).
                where(User.id == user_id).
                values(last_login = date.today())
            )
            await self.session.execute(stmt)
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred while updating user last login by user id: {user_id} in sql database.",
                argument={'user_id': user_id},
                child_error=e
            )

    async def update_user_personal_information(self, user_id: UUID, personal_information: UserPersonalInformationModel) -> None:
        try:
            stmt = (
                update(User).
                where(User.id == user_id).
                values(
                    first_name = personal_information.first_name,
                    last_name = personal_information.last_name,
                    phone_number = personal_information.phone_number,
                    postal_code = personal_information.postal_code,
                    city = personal_information.city,
                    street = personal_information.street)
            )
            await self.session.execute(stmt)
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred while updating personal information for user with id: {user_id} in sql database.",
                argument={'user_id': user_id, 'personal_information': personal_information},
                child_error=e
            )

    async def update_user_email_address(self, new_email: ConfirmedUserEmailChangeModel) -> None:
        try:
            stmt = (
                update(User).
                where(User.id == new_email.id).
                values(email = new_email.new_email)
            )
            await self.session.execute(stmt)
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred while updating user email address for user with id: {new_email.id} in sql database.",
                argument={'new_email': new_email},
                child_error=e
            )

    async def update_user_password(self, new_password: ConfirmedUserPasswordChangeModel) -> None:
        try:
            stmt = (
                update(User).
                where(User.id == new_password.id).
                values(password = new_password.new_password, salt = new_password.salt)
            )
            await self.session.execute(stmt)
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred while updating user password for user with id: {new_password.id} in sql database.",
                argument={'new_password': 'anonymized'},
                child_error=e
            )

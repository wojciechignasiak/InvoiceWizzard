from app.database.postgres.repositories.base_postgres_repository import BasePostgresRepository
from app.custom_exceptions.custom_exceptions import DatabaseError
from sqlalchemy import insert, select, update, Select
from app.schema.schema import User
from app.models.user_model import (
    CreateUserModel,
    UserPersonalInformationModel,
    ConfirmedUserEmailChangeModel, 
    ConfirmedUserPasswordChangeModel
    )
from datetime import date
from fastapi import status

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
                class_and_method="UserPostgresRepository.create_user()",
                argument={'new_user': new_user},
                child_error=e
            )

    async def get_user_by_id(self, user_id: str) -> User | None:
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

    async def get_user_by_email_address(self, user_email_adress: str) -> User | None:
        try:
            stmt: Select[tuple[User]] = select(User).where(User.email == user_email_adress)
            user: User | None = await self.session.scalar(stmt)
            return user
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred while getting user by email address: {user_email_adress} from sql database.",
                class_and_method="UserPostgresRepository.get_user_by_email_address()",
                argument={'user_email_adress': user_email_adress},
                child_error=e
            )

    async def update_user_last_login(self, user_id: str) -> None:
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
                class_and_method="UserPostgresRepository.update_user_last_login()",
                argument={'user_id': user_id},
                child_error=e
            )

    async def update_user_personal_information(self, user_id: str, personal_information: UserPersonalInformationModel) -> None:
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
                message=f"Unexpected error occurred while updating personal informations for user with id: {user_id} in sql database.",
                class_and_method="UserPostgresRepository.update_user_personal_information()",
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
                class_and_method="UserPostgresRepository.update_user_email_address()",
                argument={'new_email': new_email},
                child_error=e
            )

    async def update_user_password(self, new_password: ConfirmedUserPasswordChangeModel) -> None:
        try:
            stmt = (
                update(User).
                where(User.id == new_password.id).
                values(password = new_password.new_password)
            )
            await self.session.execute(stmt)
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred while updating user password for user with id: {new_password.id} in sql database.",
                class_and_method="UserPostgresRepository.update_user_password()",
                argument={'anonimized': 'anonimized'},
                child_error=e
            )

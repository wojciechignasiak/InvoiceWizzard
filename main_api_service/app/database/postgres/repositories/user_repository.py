from sqlalchemy.exc import (
    IntegrityError, 
    DataError, 
    StatementError,
    DatabaseError,
    InterfaceError,
    OperationalError,
    ProgrammingError
    )
from app.database.postgres.repositories.base_postgres_repository import BasePostgresRepository
from app.database.postgres.repositories.user_repository_abc import UserPostgresRepositoryABC
from app.database.postgres.exceptions.custom_postgres_exceptions import (
    PostgreSQLDatabaseError,
    PostgreSQLIntegrityError,
    PostgreSQLNotFoundError
)
from app.logging import logger
from sqlalchemy import insert, select, update
from app.schema.schema import User
from app.models.user_model import (
    CreateUserModel,
    UserPersonalInformationModel,
    ConfirmedUserEmailChangeModel, 
    ConfirmedUserPasswordChangeModel
    )
from datetime import datetime, date
from uuid import uuid4


class UserPostgresRepository(BasePostgresRepository, UserPostgresRepositoryABC):

    async def create_user(self, new_user: CreateUserModel) -> User:
        try:
            stmt = (
                insert(User).
                values(
                    id=uuid4(),
                    email=new_user.email, 
                    password=new_user.password,
                    salt=new_user.salt, 
                    registration_date=datetime.strptime(new_user.registration_date, '%Y-%m-%d').date(),
                    last_login=date.today()
                    ).
                    returning(User)
                )
            user = await self.session.scalar(stmt)
            return user
        except IntegrityError as e:
            logger.error(f"UserPostgresRepository.create_user() Error: {e}")
            raise PostgreSQLIntegrityError("Cannot create new user in database. Integrity error occured.")
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"UserPostgresRepository.create_user() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")


    async def get_user_by_id(self, user_id: str) -> User:
        try:
            stmt = select(User).where(User.id == user_id)
            user = await self.session.scalar(stmt)
            if user == None:
                raise PostgreSQLNotFoundError("User with provided id not found in database.")
            return user
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"UserPostgresRepository.get_user_by_id() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")


    async def get_user_by_email_address(self, user_email_adress: str) -> User:
        try:
            stmt = select(User).where(User.email == user_email_adress)
            user = await self.session.scalar(stmt)
            if user == None:
                raise PostgreSQLNotFoundError("User with provided email address not found in database.")
            return user
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"UserPostgresRepository.get_user_by_email_address() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")


    async def is_email_address_arleady_taken(self, user_email_adress: str) -> bool:
        try:
            stmt = select(User).where(User.email == user_email_adress)
            user = await self.session.scalar(stmt)

            if user is not None:
                return True
            else:
                return False
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"UserPostgresRepository.is_email_address_arleady_taken() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")


    async def update_user_last_login(self, user_id: str) -> User:
        try:
            stmt = (
                update(User).
                where(User.id == user_id).
                values(last_login = date.today()).
                returning(User.id, User.last_login)
            )
            user = await self.session.scalar(stmt)

            if user == None:
                raise PostgreSQLNotFoundError("User with provided id not found in database.")
            return user
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"UserPostgresRepository.update_user_last_login() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")


    async def update_user_personal_information(self, user_id: str, personal_information: UserPersonalInformationModel) -> User:
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
                    street = personal_information.street).
                    returning(
                        User.id, 
                        User.first_name, 
                        User.last_name, 
                        User.phone_number, 
                        User.postal_code, 
                        User.city, 
                        User.street
                        )
            )
            user = await self.session.scalar(stmt)
            if user == None:
                raise PostgreSQLNotFoundError("User with provided id not found in database.")
            return user    
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"UserPostgresRepository.update_user_personal_information() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")


    async def update_user_email_address(self, new_email: ConfirmedUserEmailChangeModel) -> User:
        try:
            stmt = (
                update(User).
                where(User.id == new_email.id).
                values(email = new_email.new_email).
                returning(User)
            )
            user = await self.session.scalar(stmt)
            if user == None:
                raise PostgreSQLNotFoundError("User with provided id not found in database.")
            return user
        except IntegrityError as e:
            logger.error(f"UserPostgresRepository.update_user_email_address() Error: {e}")
            raise PostgreSQLIntegrityError("Cannot update user email address. Integrity error occured.")
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"UserPostgresRepository.update_user_email_address() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")


    async def update_user_password(self, new_password: ConfirmedUserPasswordChangeModel) -> User:
        try:
            stmt = (
                update(User).
                where(User.id == new_password.id).
                values(email = new_password.new_password).
                returning(User)
            )
            user = await self.session.scalar(stmt)
            if user == None:
                raise PostgreSQLNotFoundError("User with provided id not found in database.")
            return user
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"UserPostgresRepository.update_user_password() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")

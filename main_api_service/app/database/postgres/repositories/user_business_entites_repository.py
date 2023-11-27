from app.database.postgres.repositories.base_postgres_repository import BasePostgresRepository
from app.database.postgres.repositories.user_business_entites_repository_abc import UserBusinessEntityRepositoryABC
from app.schema.schema import UserBusinessEntity
from app.models.user_business_entity_model import CreateUserBusinessEntityModel
from app.database.postgres.exceptions.custom_postgres_exceptions import (
    PostgreSQLDatabaseError,
    PostgreSQLIntegrityError
    )
from sqlalchemy.exc import (
    IntegrityError, 
    DataError, 
    StatementError,
    DatabaseError,
    InterfaceError,
    OperationalError,
    ProgrammingError
    )
from app.logging import logger
from sqlalchemy import insert
from uuid import uuid4, UUID

class UserBusinessEntityRepository(BasePostgresRepository, UserBusinessEntityRepositoryABC):

    async def create_user_business_entity(self, user_id: str, new_business: CreateUserBusinessEntityModel) -> UserBusinessEntity:
        try:
            stmt = (
                insert(UserBusinessEntity).
                values(
                    id=uuid4(),
                    user_id=UUID(user_id),
                    company_name=new_business.company_name,
                    city=new_business.city,
                    postal_code=new_business.postal_code,
                    street=new_business.street,
                    nip=new_business.nip,
                    krs=new_business.krs
                    ).
                    returning(UserBusinessEntity)
                )
            user_business_entity = await self.session.scalar(stmt)
            return user_business_entity
        except IntegrityError as e:
            logger.error(f"UserBusinessEntityRepository.create_user_business_entity() Error: {e}")
            raise PostgreSQLIntegrityError("Cannot create new user business entity in database. Integrity error occured.")
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"UserBusinessEntityRepository.create_user_business_entity() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
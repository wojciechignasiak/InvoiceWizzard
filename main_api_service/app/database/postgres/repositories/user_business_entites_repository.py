from app.database.postgres.repositories.base_postgres_repository import BasePostgresRepository
from app.database.postgres.repositories.user_business_entites_repository_abc import UserBusinessEntityRepositoryABC
from app.schema.schema import UserBusinessEntity
from app.models.user_business_entity_model import (
    CreateUserBusinessEntityModel,
    UpdateUserBusinessEntityModel
)
from app.database.postgres.exceptions.custom_postgres_exceptions import (
    PostgreSQLDatabaseError,
    PostgreSQLIntegrityError,
    PostgreSQLNotFoundError
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
from sqlalchemy import insert, update
from uuid import uuid4, UUID

class UserBusinessEntityRepository(BasePostgresRepository, UserBusinessEntityRepositoryABC):

    async def create_user_business_entity(self, user_id: str, new_user_business_entity: CreateUserBusinessEntityModel) -> UserBusinessEntity:
        try:
            stmt = (
                insert(UserBusinessEntity).
                values(
                    id=uuid4(),
                    user_id=UUID(user_id),
                    company_name=new_user_business_entity.company_name,
                    city=new_user_business_entity.city,
                    postal_code=new_user_business_entity.postal_code,
                    street=new_user_business_entity.street,
                    nip=new_user_business_entity.nip,
                    krs=new_user_business_entity.krs
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
        
    async def update_user_business_entity(self, update_user_business_entity: UpdateUserBusinessEntityModel) -> UserBusinessEntity:
        try:
            stmt = (
                update(UserBusinessEntity).
                where(UserBusinessEntity.id == update_user_business_entity.id).
                values(
                    company_name=update_user_business_entity.company_name,
                    city=update_user_business_entity.city,
                    postal_code=update_user_business_entity.postal_code,
                    street=update_user_business_entity.street,
                    nip=update_user_business_entity.nip,
                    krs=update_user_business_entity.krs
                ).
                returning(UserBusinessEntity)
            )
            updated_user_business_entity = await self.session.scalar(stmt)
            if updated_user_business_entity == None:
                raise PostgreSQLNotFoundError("User Business Entity with provided id not found in database.")
            return updated_user_business_entity
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"UserBusinessEntityRepository.update_user_business_entity() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
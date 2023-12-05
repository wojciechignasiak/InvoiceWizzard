from app.database.postgres.repositories.base_postgres_repository import BasePostgresRepository
from app.database.postgres.repositories.external_business_entity_repository_abc import ExternalBusinessEntityPostgresRepositoryABC
from app.schema.schema import ExternalBusinessEntity
from app.models.external_business_entity_model import (
    CreateExternalBusinessEntityModel
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
from sqlalchemy import insert, update, delete, select, or_
from uuid import uuid4, UUID

class ExternalBusinessEntityPostgresRepository(BasePostgresRepository, ExternalBusinessEntityPostgresRepositoryABC):
    
    async def create_external_business_entity(self, user_id: str, new_external_business_entity: CreateExternalBusinessEntityModel) -> ExternalBusinessEntity:
        try:
            stmt = (
                insert(ExternalBusinessEntity).
                values(
                    id=uuid4(),
                    user_id=UUID(user_id),
                    company_name=new_external_business_entity.company_name,
                    city=new_external_business_entity.city,
                    postal_code=new_external_business_entity.postal_code,
                    street=new_external_business_entity.street,
                    nip=new_external_business_entity.nip,
                    krs=new_external_business_entity.krs
                    ).
                    returning(ExternalBusinessEntity)
                )
            external_business_entity = await self.session.scalar(stmt)
            return external_business_entity
        except IntegrityError as e:
            logger.error(f"ExternalBusinessEntityPostgresRepository.create_external_business_entity() Error: {e}")
            raise PostgreSQLIntegrityError("Cannot create new external business entity in database. Integrity error occured.")
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"ExternalBusinessEntityPostgresRepository.create_external_business_entity() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
        
    async def is_external_business_entity_unique(self, user_id: str, new_external_business_entity: CreateExternalBusinessEntityModel) -> bool:
        try:
            stmt = (
                select(ExternalBusinessEntity).
                where(
                        or_(
                            (ExternalBusinessEntity.user_id == user_id) & (ExternalBusinessEntity.company_name == new_external_business_entity.company_name),
                            (ExternalBusinessEntity.user_id == user_id) & (ExternalBusinessEntity.nip == new_external_business_entity.nip),
                            (ExternalBusinessEntity.user_id == user_id) & (ExternalBusinessEntity.krs == new_external_business_entity.krs)
                        )
                    )
                )
            user_business_entity = await self.session.scalar(stmt)
            if user_business_entity == None:
                return True
            else:
                return False
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"ExternalBusinessEntityPostgresRepository.is_external_business_entity_unique() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
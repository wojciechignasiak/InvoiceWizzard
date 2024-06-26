from app.database.postgres.repositories.base_postgres_repository import BasePostgresRepository
from app.database.postgres.repositories.external_business_entity_repository_abc import ExternalBusinessEntityPostgresRepositoryABC
from app.schema.schema import ExternalBusinessEntity
from app.models.external_business_entity_model import (
    CreateExternalBusinessEntityModel,
    UpdateExternalBusinessEntityModel
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
from typing import Optional

class ExternalBusinessEntityPostgresRepository(BasePostgresRepository, ExternalBusinessEntityPostgresRepositoryABC):
    
    async def create_external_business_entity(self, user_id: str, new_external_business_entity: CreateExternalBusinessEntityModel) -> ExternalBusinessEntity:
        try:
            stmt = (
                insert(ExternalBusinessEntity).
                values(
                    id=new_external_business_entity.id,
                    user_id=UUID(user_id),
                    name=new_external_business_entity.name,
                    city=new_external_business_entity.city,
                    postal_code=new_external_business_entity.postal_code,
                    street=new_external_business_entity.street,
                    nip=new_external_business_entity.nip
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
                            (ExternalBusinessEntity.user_id == user_id) & (ExternalBusinessEntity.name == new_external_business_entity.name),
                            (ExternalBusinessEntity.user_id == user_id) & (ExternalBusinessEntity.nip == new_external_business_entity.nip)
                        )
                    )
                )
            user_business_entity = await self.session.scalar(stmt)
            if user_business_entity is None:
                return True
            else:
                return False
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"ExternalBusinessEntityPostgresRepository.is_external_business_entity_unique() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
        
    async def update_external_business_entity(self, user_id: str, update_external_business_entity: UpdateExternalBusinessEntityModel) -> ExternalBusinessEntity:
        try:
            stmt = (
                update(ExternalBusinessEntity).
                where(
                    ExternalBusinessEntity.id == update_external_business_entity.id,
                    ExternalBusinessEntity.user_id == user_id
                    ).
                values(
                    name=update_external_business_entity.name,
                    city=update_external_business_entity.city,
                    postal_code=update_external_business_entity.postal_code,
                    street=update_external_business_entity.street,
                    nip=update_external_business_entity.nip
                ).
                returning(ExternalBusinessEntity)
            )
            updated_external_business_entity = await self.session.scalar(stmt)
            if updated_external_business_entity is None:
                raise PostgreSQLNotFoundError("External Business Entity with provided id not found in database.")
            return updated_external_business_entity
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"ExternalBusinessEntityPostgresRepository.update_external_business_entity() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
        
    async def is_external_business_entity_unique_beside_one_to_update(self, user_id: str, update_external_business_entity: UpdateExternalBusinessEntityModel) -> bool:
        try:
            stmt = (
                select(ExternalBusinessEntity).
                where(
                        or_(
                            (ExternalBusinessEntity.user_id == user_id) & (ExternalBusinessEntity.name == update_external_business_entity.name) & (ExternalBusinessEntity.id != update_external_business_entity.id),
                            (ExternalBusinessEntity.user_id == user_id) & (ExternalBusinessEntity.nip == update_external_business_entity.nip) & (ExternalBusinessEntity.id != update_external_business_entity.id)
                        )
                    )
                )
            external_business_entity = await self.session.scalar(stmt)
            if external_business_entity is None:
                return True
            else:
                return False
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"ExternalBusinessEntityPostgresRepository.is_external_business_entity_unique_beside_one_to_update() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
        
    async def get_external_business_entity(self, user_id: str, external_business_entity_id: str) -> ExternalBusinessEntity:
        try:
            stmt = (
                select(ExternalBusinessEntity).
                where(
                    ExternalBusinessEntity.id == external_business_entity_id,
                    ExternalBusinessEntity.user_id == user_id
                )
            )
            external_business_entity = await self.session.scalar(stmt)
            if external_business_entity is None:
                raise PostgreSQLNotFoundError("External Business Entity with provided id not found in database.")
            return external_business_entity
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"ExternalBusinessEntityPostgresRepository.get_external_business_entity() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
        
    async def get_all_external_business_entities(self, 
                                                user_id: str, 
                                                page: int = 1, 
                                                items_per_page: int = 10,
                                                name: Optional[str] = None,
                                                city: Optional[str] = None,
                                                postal_code: Optional[str] = None,
                                                street: Optional[str] = None,
                                                nip: Optional[str] = None) -> list:
        try:
            stmt = select(ExternalBusinessEntity).where((ExternalBusinessEntity.user_id == user_id))
                    
            if name:
                stmt = stmt.where(ExternalBusinessEntity.name.ilike(f"%{name}%") )

            if city:
                stmt = stmt.where(ExternalBusinessEntity.city.ilike(f"%{city}%"))

            if postal_code:
                stmt = stmt.where(ExternalBusinessEntity.postal_code.ilike(f"%{postal_code}%"))

            if street:
                stmt = stmt.where(ExternalBusinessEntity.street.ilike(f"%{street}%"))

            if nip:
                stmt = stmt.where(ExternalBusinessEntity.nip.ilike(f"%{nip}%"))

            stmt = stmt.limit(items_per_page).offset((page - 1) * items_per_page)
            
            external_business_entities = await self.session.scalars(stmt)
            external_business_entities_list: list = external_business_entities.all()
            if not external_business_entities_list:
                raise PostgreSQLNotFoundError("No External Business Entities found in database.")
            return external_business_entities_list
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"ExternalBusinessEntityPostgresRepository.get_all_external_business_entities() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
    
    async def remove_external_business_entity(self, user_id: str, external_business_entity_id: str) -> bool:
        try:
            stmt = (
                delete(ExternalBusinessEntity).
                where(
                    ExternalBusinessEntity.id == external_business_entity_id,
                    ExternalBusinessEntity.user_id == user_id)
            )
            deleted_external_business_entity = await self.session.execute(stmt)
            rows_after_delete = deleted_external_business_entity.rowcount

            if rows_after_delete == 1:
                return True
            else:
                return False
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"ExternalBusinessEntityPostgresRepository.remove_external_business_entity() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
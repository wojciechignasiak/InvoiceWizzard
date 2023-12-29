from app.database.postgres.repositories.base_postgres_repository import BasePostgresRepository
from app.database.postgres.repositories.user_business_entity_repository_abc import UserBusinessEntityPostgresRepositoryABC
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
from sqlalchemy import insert, update, delete, select, or_
from uuid import uuid4, UUID
from typing import Optional

class UserBusinessEntityPostgresRepository(BasePostgresRepository, UserBusinessEntityPostgresRepositoryABC):

    async def create_user_business_entity(self, user_id: str, new_user_business_entity: CreateUserBusinessEntityModel) -> UserBusinessEntity:
        try:
            stmt = (
                insert(UserBusinessEntity).
                values(
                    id=new_user_business_entity.id,
                    user_id=UUID(user_id),
                    company_name=new_user_business_entity.company_name,
                    city=new_user_business_entity.city,
                    postal_code=new_user_business_entity.postal_code,
                    street=new_user_business_entity.street,
                    nip=new_user_business_entity.nip
                    ).
                    returning(UserBusinessEntity)
                )
            user_business_entity = await self.session.scalar(stmt)
            return user_business_entity
        except IntegrityError as e:
            logger.error(f"UserBusinessEntityPostgresRepository.create_user_business_entity() Error: {e}")
            raise PostgreSQLIntegrityError("Cannot create new user business entity in database. Integrity error occured.")
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"UserBusinessEntityPostgresRepository.create_user_business_entity() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
    
    async def is_user_business_entity_unique(self, user_id: str, new_user_business_entity: CreateUserBusinessEntityModel) -> bool:
        try:
            stmt = (
                select(UserBusinessEntity).
                where(
                        or_(
                            (UserBusinessEntity.user_id == user_id) & (UserBusinessEntity.company_name == new_user_business_entity.company_name),
                            (UserBusinessEntity.user_id == user_id) & (UserBusinessEntity.nip == new_user_business_entity.nip)
                        )
                    )
                )
            user_business_entity = await self.session.scalar(stmt)
            if user_business_entity == None:
                return True
            else:
                return False
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"UserBusinessEntityPostgresRepository.is_user_business_entity_unique() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
        
    async def update_user_business_entity(self, user_id: str, update_user_business_entity: UpdateUserBusinessEntityModel) -> UserBusinessEntity:
        try:
            stmt = (
                update(UserBusinessEntity).
                where(
                    UserBusinessEntity.id == update_user_business_entity.id,
                    UserBusinessEntity.user_id == user_id
                    ).
                values(
                    company_name=update_user_business_entity.company_name,
                    city=update_user_business_entity.city,
                    postal_code=update_user_business_entity.postal_code,
                    street=update_user_business_entity.street,
                    nip=update_user_business_entity.nip
                ).
                returning(UserBusinessEntity)
            )
            updated_user_business_entity = await self.session.scalar(stmt)
            if updated_user_business_entity == None:
                raise PostgreSQLNotFoundError("User Business Entity with provided id not found in database.")
            return updated_user_business_entity
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"UserBusinessEntityPostgresRepository.update_user_business_entity() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
    
    async def is_user_business_entity_unique_beside_one_to_update(self, user_id: str, update_user_business_entity: UpdateUserBusinessEntityModel) -> bool:
        try:
            stmt = (
                select(UserBusinessEntity).
                where(
                        or_(
                            (UserBusinessEntity.user_id == user_id) & (UserBusinessEntity.company_name == update_user_business_entity.company_name) & (UserBusinessEntity.id != update_user_business_entity.id),
                            (UserBusinessEntity.user_id == user_id) & (UserBusinessEntity.nip == update_user_business_entity.nip) & (UserBusinessEntity.id != update_user_business_entity.id)
                        )
                    )
                )
            user_business_entity = await self.session.scalar(stmt)
            if user_business_entity == None:
                return True
            else:
                return False
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"UserBusinessEntityPostgresRepository.is_user_business_entity_unique_beside_one_to_update() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
        
    async def remove_user_business_entity(self, user_id: str, user_business_entity_id: str) -> bool:
        try:
            stmt = (
                delete(UserBusinessEntity).
                where(
                    UserBusinessEntity.id == user_business_entity_id,
                    UserBusinessEntity.user_id == user_id)
            )
            deleted_user_business_entity = await self.session.execute(stmt)
            rows_after_delete = deleted_user_business_entity.rowcount

            if rows_after_delete == 1:
                return True
            else:
                return False
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"UserBusinessEntityPostgresRepository.remove_user_business_entity() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
        
    async def get_user_business_entity(self, user_id: str, user_business_entity_id: str) -> UserBusinessEntity:
        try:
            stmt = (
                select(UserBusinessEntity).
                where(
                    UserBusinessEntity.id == user_business_entity_id,
                    UserBusinessEntity.user_id == user_id
                )
            )
            user_business_entity = await self.session.scalar(stmt)
            if user_business_entity == None:
                raise PostgreSQLNotFoundError("User Business Entity with provided id not found in database.")
            return user_business_entity
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"UserBusinessEntityPostgresRepository.get_user_business_entity() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
        
    async def get_all_user_business_entities(self, 
                                            user_id: str,
                                            page: int = 1, 
                                            items_per_page: int = 10,
                                            company_name: Optional[str] = None,
                                            city: Optional[str] = None,
                                            postal_code: Optional[str] = None,
                                            street: Optional[str] = None,
                                            nip: Optional[str] = None) -> list:
        try:
            stmt = (
                select(UserBusinessEntity).
                where(
                    (UserBusinessEntity.user_id == user_id) &
                    (UserBusinessEntity.company_name.ilike(f"%{company_name}%") if company_name else True) &
                    (UserBusinessEntity.city.ilike(f"%{city}%") if city else True) &
                    (UserBusinessEntity.postal_code.ilike(f"%{postal_code}%") if postal_code else True) &
                    (UserBusinessEntity.street.ilike(f"%{street}%") if street else True) &
                    (UserBusinessEntity.nip.ilike(f"%{nip}%") if nip else True)
                ).
                limit(items_per_page).
                offset((page - 1) * items_per_page)
            )
            user_business_entities = await self.session.scalars(stmt)
            if not user_business_entities:
                raise PostgreSQLNotFoundError("No User Business Entities found in database.")
            return user_business_entities
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"UserBusinessEntityPostgresRepository.get_all_user_business_entities() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
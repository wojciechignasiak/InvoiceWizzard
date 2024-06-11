from app.services.user_service_abc import UserServiceABC
from fastapi import Depends
from app.factories.get_repositories_factory import get_repositories_factory
from app.factories.repositories_factory_abc import RepositoriesFactoryABC
from app.factories.get_events_factory import get_events_factory
from app.factories.events_factory_abc import EventsFactoryABC
from app.models.user_model import (
    UserModel,
    CreateUserModel,
    RegisterUserModel
)
from app.schema.schema import User
from app.database.postgres.repositories.user_repository_abc import UserPostgresRepositoryABC
from app.database.redis.repositories.user_repository_abc import UserRedisRepositoryABC
from app.database.postgres.exceptions.custom_postgres_exceptions import (
    PostgreSQLDatabaseError, 
    PostgreSQLIntegrityError, 
    PostgreSQLNotFoundError
    )
from app.database.redis.exceptions.custom_redis_exceptions import (
    RedisSetError, 
    RedisDatabaseError, 
    RedisNotFoundError, 
    RedisJWTNotFoundError
    )
from app.kafka.exceptions.custom_kafka_exceptions import KafkaBaseError
from app.kafka.events.user_events_abc import UserEventsABC
from fastapi import HTTPException, status
from uuid import uuid4

class UserService(UserServiceABC):

    def __init__(
            self, 
            repositories_factory: RepositoriesFactoryABC = Depends(get_repositories_factory),
            events_factory: EventsFactoryABC = Depends(get_events_factory)
            ) -> None:
        self.repositories_factory: RepositoriesFactoryABC = repositories_factory
        self.events_factory: EventsFactoryABC = events_factory

    async def get_current_user(self, user_id: str) -> UserModel:
        try:
            user_postgres_repository: UserPostgresRepositoryABC = await self.repositories_factory.return_user_postgres_repository()
            user: User = await user_postgres_repository.get_user_by_id(user_id)
            user_model: UserModel = UserModel.user_schema_to_model(user)
            return user_model
        except PostgreSQLDatabaseError as e:
            raise e
        
    async def confirm_account(self, key_id: str) -> None:
        try:
            user_postgres_repository: UserPostgresRepositoryABC = await self.repositories_factory.return_user_postgres_repository()
            user_redis_repository: UserRedisRepositoryABC = await self.repositories_factory.return_user_redis_repository()
            user_events: UserEventsABC = await self.events_factory.return_user_events()

            user_to_confirm_data: bytes = await user_redis_repository.search_user_by_id(key_id=key_id)
            
            new_user: CreateUserModel = CreateUserModel.model_validate_json(json_data=user_to_confirm_data)
            
            created_user: User = await user_postgres_repository.create_user(new_user=new_user)

            await user_redis_repository.delete_user_by_id(key_id=key_id)
            
            await user_events.account_confirmed_event(email_address=created_user.email)

        except (PostgreSQLIntegrityError, RedisNotFoundError, RedisDatabaseError, PostgreSQLDatabaseError, KafkaBaseError) as e:
            raise e
        
    async def register_account(self, new_user: RegisterUserModel, personal_salt: str, hashed_password: str):
        try:
            user_postgres_repository: UserPostgresRepositoryABC = await self.repositories_factory.return_user_postgres_repository()
            user_redis_repository: UserRedisRepositoryABC = await self.repositories_factory.return_user_redis_repository()
            user_events: UserEventsABC = await self.events_factory.return_user_events()
            
            is_email_address_arleady_taken: bool = await user_postgres_repository.is_email_address_arleady_taken(
                            user_email_adress=new_user.email
                            )
            
            if is_email_address_arleady_taken == True:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account with this email adress already exists.")

            new_user_to_redis = CreateUserModel(
                email=new_user.email, 
                password=hashed_password,
                salt=personal_salt
                )
            
            is_user_arleady_registered: bool = await user_redis_repository.is_user_arleady_registered(
                email_address=new_user.email
            )

            if is_user_arleady_registered == True:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email address already registered.")
            
            key_id: str = str(uuid4())

            await user_redis_repository.create_user(
                key_id=key_id,
                new_user=new_user_to_redis
                )
            
            await user_events.account_registered_event(
                id=key_id,
                email_address=new_user.email
            )
        except Exception as e:
            pass

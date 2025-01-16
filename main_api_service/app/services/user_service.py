#internal modules
from app.database.postgres.repositories.user_repository_interface import IUserPostgresRepository
from app.database.postgres.repositories.user_repository import UserPostgresRepository
from app.database.redis.repositories.user_repository_interface import IUserRedisRepository
from app.database.redis.repositories.user_repository import UserRedisRepository
from app.kafka.events.user_events_interface import IUserEvents
from app.kafka.events.user_events import UserEvents
from app.models.user_model import User, UserModel
from app.custom_exceptions.custom_exceptions import DataNotFoundError, ServiceError, DatabaseError
#3rd party libraries
from fastapi import Depends, status

class UserService:
    def __init__(
            self, 
            user_postgres_repository: IUserPostgresRepository = Depends(UserPostgresRepository),
            user_redis_repository: IUserRedisRepository = Depends(UserRedisRepository),
            user_events: IUserEvents = Depends(UserEvents)
            ):
        self._user_postgres_repository: IUserPostgresRepository = user_postgres_repository
        self._user_redis_repository: IUserRedisRepository = user_redis_repository
        self._user_events: IUserEvents = user_events

    async def get_user_by_id(self, user_id: str) -> UserModel:
        try:
            user: User = await self._user_postgres_repository.get_user_by_id(user_id)
            if not user:
                raise DataNotFoundError(status_code=status.HTTP_404_NOT_FOUND, message="User not found.")
            user_model: UserModel = await self._convert_user_schema_to_user_model(user)
            return user_model
        except DataNotFoundError as e:
            raise DataNotFoundError(
                status_code=e.args[0],
                message=e.message,
                class_and_method="UserService.get_user_by_id()",
                argument={'user_id': user_id},
                child_error=e
            )
        except (ServiceError, DatabaseError) as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                class_and_method="UserService.get_user_by_id()",
                argument={'user_id': user_id},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in UserService while getting user by id from database.",
                class_and_method="UserService.get_user_by_id()",
                argument={'user_id': user_id},
                child_error=e,
            )

    @staticmethod
    async def _convert_user_schema_to_user_model(user: User) -> UserModel:
        try:
            return UserModel(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone_number=user.phone_number,
            city=user.city,
            postal_code=user.postal_code,
            street=user.street,
            registration_date=user.registration_date,
            last_login=user.last_login,
            email_notification=user.email_notification,
            push_notification=user.push_notification
        )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in UserService while converting user schema to user model.",
                class_and_method="UserService._convert_user_schema_to_user_model()",
                argument={'user': user},
                child_error=e,
            )

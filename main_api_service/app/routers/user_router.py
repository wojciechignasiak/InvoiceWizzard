from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from redis.asyncio import Redis
from app.registries.get_repositories_registry import get_repositories_registry
from app.registries.repositories_registry_abc import RepositoriesRegistryABC
from app.database.redis.client.get_redis_client import get_redis_client
from app.types.postgres_repository_abstract_types import (
    UserPostgresRepositoryABC
)
from app.types.redis_repository_abstract_types import (
    UserRedisRepositoryABC
)
from app.types.kafka_event_abstract_types import (
    UserEventsABC
)
from app.database.redis.exceptions.custom_redis_exceptions import (
    RedisSetError, 
    RedisDatabaseError, 
    RedisNotFoundError, 
    RedisJWTNotFoundError
    )
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.postgres.session.get_session import get_session
from app.database.postgres.exceptions.custom_postgres_exceptions import (
    PostgreSQLDatabaseError, 
    PostgreSQLIntegrityError, 
    PostgreSQLNotFoundError
    )
from app.schema.schema import User
from app.registries.get_events_registry import get_events_registry
from app.registries.events_registry_abc import EventsRegistryABC
from app.kafka.exceptions.custom_kafka_exceptions import KafkaBaseError
from app.models.jwt_model import (
    JWTDataModel, 
    JWTPayloadModel
)
from app.models.authentication_model import LogInModel
from app.models.user_model import (
    UserModel,
    RegisterUserModel, 
    CreateUserModel, 
    UserPersonalInformationModel, 
    UpdateUserEmailModel, 
    ConfirmedUserEmailChangeModel, 
    ConfirmedUserPasswordChangeModel, 
    UpdateUserPasswordModel, 
    ResetUserPasswordModel
    )
from app.auth.auth_tools import AuthTools
from app.auth.auth_tools_abc import AuthToolsABC
from aiokafka import AIOKafkaProducer
from app.kafka.clients.get_kafka_producer_client import get_kafka_producer_client
from uuid import uuid4
import datetime


from app.services.auth_service import IAuthService, AuthService
from app.services.user_service import IUserService, UserService
from app.services.register_account_service import IRegisterAccountService, RegisterAccountService
from app.services.login_service import LoginService, ILoginService
from app.services.logout_service import ILogoutService, LogoutService
from app.custom_exceptions.custom_exceptions import CustomException
from fastapi.security import HTTPAuthorizationCredentials

router = APIRouter()
http_bearer = HTTPBearer()

@router.get("/user-module/get-current-user/", response_model=UserModel)
async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    auth_service: IAuthService = Depends(AuthService),
    user_service: IUserService = Depends(UserService)
    ):
    try:
        jwt_payload: JWTPayloadModel = await auth_service.get_jwt(token)
        user_model: UserModel = await user_service.get_user_by_id(user_id=jwt_payload.id)
        return JSONResponse(status_code=status.HTTP_200_OK, content=user_model.model_dump())
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.post("/user-module/register-account/")
async def register_account(
    new_user: RegisterUserModel,
    register_account_service: IRegisterAccountService = Depends(RegisterAccountService)
    ):
    try:
        await register_account_service.register_user(new_user)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Account registered. Now confirm your email address."})
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.patch("/user-module/confirm-account/")
async def confirm_account(
    key_id: str,
    user_service: IUserService = Depends(UserService)
    ):
    try:
        await user_service.confirm_user_account(key_id)
        return JSONResponse(content={"detail": "Account confirmed."})
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.post("/user-module/login/")
async def login(
    login: LogInModel,
    login_service: ILoginService = Depends(LoginService)
    ):
    try:
        jwt_token: str = await login_service.login(login)
        return JSONResponse(content={"message": f"{jwt_token}"})
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.delete("/user-module/logout/")
async def logout(
    token = Depends(http_bearer),
    logout_service: ILogoutService = Depends(LogoutService),
    
    ):
    try:
        await logout_service.logout(token)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Logout successfull."})
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

    
@router.delete("/user-module/log-out-from-all-devices/")
async def log_out_from_all_devices(
    token = Depends(http_bearer),
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client)
    ):

    try:
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        
        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        await user_redis_repository.delete_all_jwt_tokens_of_user(
            user_id=jwt_payload.id,
        )

        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "User logged out from all devices."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except (Exception, RedisDatabaseError, RedisSetError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.patch("/user-module/update-personal-information/")
async def update_personal_information(
    user_personal_info: UserPersonalInformationModel,
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    token = Depends(http_bearer), 
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session)):

    try:
        user_postgres_repository: UserPostgresRepositoryABC = await repositories_registry.return_user_postgres_repository(postgres_session)
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        
        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        await user_postgres_repository.update_user_personal_information(
            user_id=jwt_payload.id, 
            personal_information=user_personal_info
            )

        return JSONResponse(content={"message": "Personal information has been updated."})
    
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, RedisDatabaseError, PostgreSQLDatabaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.put("/user-module/change-email-address/")
async def change_email_address(
    new_email: UpdateUserEmailModel,
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    events_registry: EventsRegistryABC = Depends(get_events_registry),
    token = Depends(http_bearer), 
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    kafka_producer_client: AIOKafkaProducer = Depends(get_kafka_producer_client)
    ):

    try:
        user_postgres_repository: UserPostgresRepositoryABC = await repositories_registry.return_user_postgres_repository(postgres_session)
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        user_events: UserEventsABC = await events_registry.return_user_events(kafka_producer_client)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        user: User = await user_postgres_repository.get_user_by_id(
            user_id=jwt_payload.id
            )

        is_email_address_arleady_taken: bool = await user_postgres_repository.is_email_address_arleady_taken(
            user_email_adress=new_email.new_email
            )

        if is_email_address_arleady_taken == True:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email address arleady in use.")
        
        new_email_data: ConfirmedUserEmailChangeModel = ConfirmedUserEmailChangeModel(
            id=jwt_payload.id, 
            new_email=new_email.new_email
            )
        
        key_id = str(uuid4())
        await user_redis_repository.save_new_email(
            key_id=key_id,
            new_email=new_email_data)
        
        await user_events.change_email_event(
            id=key_id,
            email_address=user.email
        )

        return JSONResponse(content={"message": "New email has been saved. Email message with confirmation link has been send to old email address."})
    
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except RedisSetError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, RedisDatabaseError, PostgreSQLDatabaseError, KafkaBaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.patch("/user-module/confirm-email-address-change/")
async def confirm_email_address_change(
    id: str,
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    events_registry: EventsRegistryABC = Depends(get_events_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    kafka_producer_client: AIOKafkaProducer = Depends(get_kafka_producer_client)
    ):

    try:
        user_postgres_repository: UserPostgresRepositoryABC = await repositories_registry.return_user_postgres_repository(postgres_session)
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        user_events: UserEventsABC = await events_registry.return_user_events(kafka_producer_client)

        new_email_data: bytes = await user_redis_repository.retrieve_new_email(
            key_id=id
            )

        new_email_data: ConfirmedUserEmailChangeModel = ConfirmedUserEmailChangeModel.model_validate_json(new_email_data)

        is_email_address_arleady_taken: bool = await user_postgres_repository.is_email_address_arleady_taken(
            user_email_adress=new_email_data.new_email
            )
        
        if is_email_address_arleady_taken == True:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email address arleady in use.")
        
        user: User = await user_postgres_repository.update_user_email_address(
            new_email=new_email_data
            )
        
        await user_redis_repository.delete_all_jwt_tokens_of_user(
            user_id=str(user.id)
        )

        await user_redis_repository.delete_new_email(
            key_id=id
        )
        
        await user_events.email_changed_event(
            email_address=user.email
        )
        
        return JSONResponse(content={"message": "New email has been set. You have been logged off from all devices."})
    
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except PostgreSQLIntegrityError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except (RedisNotFoundError, PostgreSQLNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, KafkaBaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/user-module/change-password/")
async def change_password(
    new_password: UpdateUserPasswordModel,
    token = Depends(http_bearer),
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    events_registry: EventsRegistryABC = Depends(get_events_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    auth_tools: AuthToolsABC = Depends(AuthTools),
    kafka_producer_client: AIOKafkaProducer = Depends(get_kafka_producer_client)
    ):

    try:
        user_postgres_repository: UserPostgresRepositoryABC = await repositories_registry.return_user_postgres_repository(postgres_session)
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        user_events: UserEventsABC = await events_registry.return_user_events(kafka_producer_client)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        user: User = await user_postgres_repository.get_user_by_id(
            user_id=jwt_payload.id
            )

        password_match: bool = await auth_tools.verify_password(
            salt=user.salt, 
            password=new_password.current_password,
            hash=user.password
            )

        if password_match == False:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong current password.")

        
        hashed_new_password: str = await auth_tools.hash_password(
            salt=user.salt, 
            password=new_password.new_password
            )

        new_password_data: ConfirmedUserPasswordChangeModel = ConfirmedUserPasswordChangeModel(
            id=str(user.id), 
            new_password=hashed_new_password
            )
        
        key_id = str(uuid4())

        await user_redis_repository.save_new_password(
            key_id=key_id,
            new_password=new_password_data
            )

        await user_events.change_password_event(
            id=key_id,
            email_address=user.email
            )
            
        return JSONResponse(content={"message": "New password has been saved. Email message with confirmation link has been send to email address."})
    
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, RedisSetError, KafkaBaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/user-module/reset-password/")
async def reset_password(
    reset_password: ResetUserPasswordModel,
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    auth_tools: AuthToolsABC = Depends(AuthTools),
    events_registry: EventsRegistryABC = Depends(get_events_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    kafka_producer_client: AIOKafkaProducer = Depends(get_kafka_producer_client)
    ):
    try:
        user_postgres_repository: UserPostgresRepositoryABC = await repositories_registry.return_user_postgres_repository(postgres_session)
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        user_events: UserEventsABC = await events_registry.return_user_events(kafka_producer_client)
        
        user: User = await user_postgres_repository.get_user_by_email_address(
            user_email_adress=reset_password.email
            )

        hashed_new_password = await auth_tools.hash_password(
            salt=user.salt, 
            password=reset_password.new_password)

        new_password_data = ConfirmedUserPasswordChangeModel(
            id=str(user.id), 
            new_password=hashed_new_password
            )
        
        key_id = str(uuid4())
        await user_redis_repository.save_new_password(
            key_id=key_id,
            new_password=new_password_data)

        await user_events.reset_password_event(
            id=key_id,
            email_address=user.email
        )
        
        return JSONResponse(content={"message": "If provided email address is correct you will get email message with url to confirm your new password."})
    
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except (PostgreSQLNotFoundError, RedisNotFoundError) as e:
        return JSONResponse(content={"message": "If provided email address is correct you will get email message with url to confirm your new password."})
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, RedisSetError, KafkaBaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.patch("/user-module/confirm-password-change/")
async def confirm_password_change(
    id: str,
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    events_registry: EventsRegistryABC = Depends(get_events_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    kafka_producer_client: AIOKafkaProducer = Depends(get_kafka_producer_client)
    ):
    try:
        user_postgres_repository: UserPostgresRepositoryABC = await repositories_registry.return_user_postgres_repository(postgres_session)
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        user_events: UserEventsABC = await events_registry.return_user_events(kafka_producer_client)

        new_password_data: bytes = await user_redis_repository.retrieve_new_password(
            key_id=id
            )

        new_password_data: ConfirmedUserPasswordChangeModel = ConfirmedUserPasswordChangeModel.model_validate_json(new_password_data)
        
        user: User = await user_postgres_repository.update_user_password(
            new_password=new_password_data
            )

        await user_redis_repository.delete_all_jwt_tokens_of_user(
            user_id=str(user.id)
        )

        await user_redis_repository.delete_new_password(
            key_id=id
        )

        await user_events.password_changed_event(
            email_address=user.email
        )

        return JSONResponse(content={"message": "New password has been set. You have been logged out from all devices."})
    
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except (RedisNotFoundError, PostgreSQLNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, RedisDatabaseError, PostgreSQLDatabaseError, KafkaBaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
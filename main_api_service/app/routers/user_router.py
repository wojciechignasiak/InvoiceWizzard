from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
import redis
from app.registries.get_repositories_registry import get_repositories_registry
from app.registries.repositories_registry import RepositoriesRegistry
from app.database.redis.client.get_redis_client import get_redis_client
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
from app.kafka.events.user_events import UserEvents
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
from app.utils.user_utils import UserUtils
from aiokafka import AIOKafkaProducer
from app.kafka.clients.get_kafka_producer_client import get_kafka_producer_client
from datetime import date
from uuid import uuid4
import datetime


router = APIRouter()
http_bearer = HTTPBearer()

@router.get("/user-module/get-current-user/", response_model=UserModel)
async def get_current_user(
    repositories_registry: RepositoriesRegistry = Depends(get_repositories_registry),
    token = Depends(http_bearer), 
    redis_client: redis.Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):

    try:
        user_postgres_repository = await repositories_registry.return_user_postgres_repository(postgres_session)
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        user: User = await user_postgres_repository.get_user_by_id(
            user_id=jwt_payload.id
            )

        user_model: UserModel = UserModel.user_schema_to_model(user) 

        return JSONResponse(status_code=status.HTTP_200_OK, content=user_model.model_dump())
    
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, RedisDatabaseError, PostgreSQLDatabaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/user-module/register-account/")
async def register_account(
    new_user: RegisterUserModel,
    background_tasks: BackgroundTasks,
    repositories_registry: RepositoriesRegistry = Depends(get_repositories_registry),
    redis_client: redis.Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    kafka_producer_client: AIOKafkaProducer = Depends(get_kafka_producer_client),
    ):

    try:
        user_postgres_repository = await repositories_registry.return_user_postgres_repository(postgres_session)
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)
        event_producer: UserEvents = UserEvents(kafka_producer_client)
        user_utils: UserUtils = UserUtils()
        
        is_email_address_arleady_taken: bool = await user_postgres_repository.is_email_address_arleady_taken(
            user_email_adress=new_user.email
            )

        if is_email_address_arleady_taken == True:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account with this email adress already exists.")
        
        personal_salt: str = await user_utils.salt_generator()

        hashed_password: str = await user_utils.hash_password(
            salt=personal_salt, 
            password=new_user.password
            )
        
        new_user_to_redis = CreateUserModel(
            email=new_user.email, 
            password=hashed_password,
            salt=personal_salt,
            registration_date=date.today().isoformat()
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
        
        background_tasks.add_task(
            event_producer.account_registered_event,
            id=key_id,
            email_address=new_user.email
        )
        
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"detail": "Account has been registered. Now confirm your email address."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except (Exception, PostgreSQLDatabaseError, RedisSetError, RedisDatabaseError, KafkaBaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    

@router.patch("/user-module/confirm-account/")
async def confirm_account(
    id: str,
    background_tasks: BackgroundTasks,
    repositories_registry: RepositoriesRegistry = Depends(get_repositories_registry),
    redis_client: redis.Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    kafka_producer_client: AIOKafkaProducer = Depends(get_kafka_producer_client)
    ):

    try:
        user_postgres_repository = await repositories_registry.return_user_postgres_repository(postgres_session)
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)
        event_producer: UserEvents = UserEvents(kafka_producer_client)

        user_to_confirm_data: bytes = await user_redis_repository.search_user_by_id(
            key_id=id
            )
        
        user_to_confirm_data = CreateUserModel.model_validate_json(user_to_confirm_data)
        
        created_user: User = await user_postgres_repository.create_user(
            new_user=user_to_confirm_data
            )

        background_tasks.add_task(
            user_redis_repository.delete_user_by_id,
            key_id=id
        )
        
        background_tasks.add_task(
            event_producer.account_confirmed_event,
            email_address=created_user.email
            )
        
        return JSONResponse(content={"detail": "Account has been confirmed. Now you can log in."})
    
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except PostgreSQLIntegrityError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except RedisNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, RedisDatabaseError, PostgreSQLDatabaseError, KafkaBaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/user-module/log-in/")
async def log_in(
    log_in: LogInModel,
    background_tasks: BackgroundTasks,
    repositories_registry: RepositoriesRegistry = Depends(get_repositories_registry),
    redis_client: redis.Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session)
    ):

    try:
        user_postgres_repository = await repositories_registry.return_user_postgres_repository(postgres_session)
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)
        user_utils = UserUtils()

        user: User = await user_postgres_repository.get_user_by_email_address(
            user_email_adress=log_in.email
        )

        verify_password: bool = await user_utils.verify_password(
            salt=user.salt, 
            password=log_in.password, 
            hash=user.password
            )

        if verify_password == False:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong email adress or password.")
        
        if log_in.remember_me == True:
            jwt_expiration_time: datetime = datetime.datetime.utcnow() + datetime.timedelta(hours=24*14)
        else:
            jwt_expiration_time: datetime = datetime.datetime.utcnow() + datetime.timedelta(hours=12)

        jwt_payload: JWTPayloadModel = JWTPayloadModel(
            id=str(user.id), 
            email=user.email, 
            exp=jwt_expiration_time
            )

        jwt_data: JWTDataModel = JWTDataModel(
            secret=user.salt, 
            payload=jwt_payload
            )

        jwt_token: str = await user_utils.jwt_encoder(
            jwt_data=jwt_data
            )
        
        await user_redis_repository.save_jwt(
            jwt_token=jwt_token, 
            jwt_payload=jwt_payload
        )

        background_tasks.add_task(
            user_postgres_repository.update_user_last_login,
            user_id=jwt_payload.id
        )

        return JSONResponse(content={"jwt_token": f"{jwt_token}"})

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong email adress or password.")
    except (Exception, RedisDatabaseError, PostgreSQLDatabaseError, RedisSetError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@router.patch("/user-module/update-personal-information/")
async def update_personal_information(
    user_personal_info: UserPersonalInformationModel,
    repositories_registry: RepositoriesRegistry = Depends(get_repositories_registry),
    token = Depends(http_bearer), 
    redis_client: redis.Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session)):

    try:
        user_postgres_repository = await repositories_registry.return_user_postgres_repository(postgres_session)
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)
        
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
    background_tasks: BackgroundTasks,
    repositories_registry: RepositoriesRegistry = Depends(get_repositories_registry),
    token = Depends(http_bearer), 
    redis_client: redis.Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    kafka_producer_client: AIOKafkaProducer = Depends(get_kafka_producer_client)
    ):

    try:
        user_postgres_repository = await repositories_registry.return_user_postgres_repository(postgres_session)
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)
        event_producer: UserEvents = UserEvents(kafka_producer_client)

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
        
        background_tasks.add_task(
            event_producer.change_email_event,
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
    background_tasks: BackgroundTasks,
    repositories_registry: RepositoriesRegistry = Depends(get_repositories_registry),
    redis_client: redis.Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    kafka_producer_client: AIOKafkaProducer = Depends(get_kafka_producer_client)
    ):

    try:
        user_postgres_repository = await repositories_registry.return_user_postgres_repository(postgres_session)
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)
        event_producer: UserEvents = UserEvents(kafka_producer_client)

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
        
        background_tasks.add_task(
            user_redis_repository.delete_all_jwt_tokens_of_user,
            user_id=str(user.id)
        )
        
        background_tasks.add_task(
            user_redis_repository.delete_new_email,
            key_id=id
        )
        background_tasks.add_task(
            event_producer.email_changed_event,
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
    background_tasks: BackgroundTasks,
    token = Depends(http_bearer),
    repositories_registry: RepositoriesRegistry = Depends(get_repositories_registry),
    redis_client: redis.Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    user_utils: UserUtils = Depends(UserUtils),
    kafka_producer_client: AIOKafkaProducer = Depends(get_kafka_producer_client)
    ):

    try:
        user_postgres_repository = await repositories_registry.return_user_postgres_repository(postgres_session)
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)
        event_producer: UserEvents = UserEvents(kafka_producer_client)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        user: User = await user_postgres_repository.get_user_by_id(
            user_id=jwt_payload.id
            )

        password_match: bool = await user_utils.verify_password(
            salt=user.salt, 
            password=new_password.current_password,
            hash=user.password
            )

        if password_match == False:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong current password.")

        
        hashed_new_password: str = await user_utils.hash_password(
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

        background_tasks.add_task(
            event_producer.change_password_event,
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
    background_tasks: BackgroundTasks,
    repositories_registry: RepositoriesRegistry = Depends(get_repositories_registry),
    redis_client: redis.Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    kafka_producer_client: AIOKafkaProducer = Depends(get_kafka_producer_client)
    ):
    try:
        user_postgres_repository = await repositories_registry.return_user_postgres_repository(postgres_session)
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)
        user_utils: UserUtils = UserUtils()
        event_producer: UserEvents = UserEvents(kafka_producer_client)
        
        user: User = await user_postgres_repository.get_user_by_email_address(
            user_email_adress=reset_password.email
            )

        hashed_new_password = await user_utils.hash_password(
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

        background_tasks.add_task(
            event_producer.reset_password_event,
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
    background_tasks: BackgroundTasks,
    repositories_registry: RepositoriesRegistry = Depends(get_repositories_registry),
    redis_client: redis.Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    kafka_producer_client: AIOKafkaProducer = Depends(get_kafka_producer_client)
    ):
    try:
        user_postgres_repository = await repositories_registry.return_user_postgres_repository(postgres_session)
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)
        event_producer: UserEvents = UserEvents(kafka_producer_client)

        new_password_data: bytes = await user_redis_repository.retrieve_new_password(
            key_id=id
            )

        new_password_data: ConfirmedUserPasswordChangeModel = ConfirmedUserPasswordChangeModel.model_validate_json(new_password_data)
        
        user: User = await user_postgres_repository.update_user_password(
            new_password=new_password_data
            )

        background_tasks.add_task(
            user_redis_repository.delete_all_jwt_tokens_of_user,
            user_id=str(user.id)
        )
        
        background_tasks.add_task(
            user_redis_repository.delete_new_password,
            key_id=id
        )

        background_tasks.add_task(
            event_producer.password_changed_event,
            email_address=user.email
        )

        return JSONResponse(content={"message": "New password has been set. You have been logged out from all devices."})
    
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except (RedisNotFoundError, PostgreSQLNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, RedisDatabaseError, PostgreSQLDatabaseError, KafkaBaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
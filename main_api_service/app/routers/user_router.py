from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from app.database.redis.client.get_redis_client import get_redis_client
from app.database.redis.repositories.user_repository import UserRedisRepository
from app.kafka.producer.kafka_producer import KafkaProducer
from app.utils.user_utils import UserUtils
from app.models.user_model import RegisterUserModel, CreateUserModel, UserPersonalInformationModel, UpdateUserEmailModel, ConfirmedUserEmailChangeModel, ConfirmedUserPasswordChangeModel
from app.database.postgres.exceptions.custom_postgres_exceptions import PostgreSQLDatabaseError, PostgreSQLIntegrityError, PostgreSQLNotFoundError
from app.database.redis.exceptions.custom_redis_exceptions import RedisSetError, RedisDatabaseError, RedisNotFoundError
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.postgres.session.get_session import get_session
from app.database.postgres.repositories.user_repository import UserPostgresRepository
from datetime import date
from app.models.kafka_topics_enum import KafkaTopicsEnum
from app.schema.schema import User
from app.models.jwt_model import JWTDataModel, JWTPayloadModel
from fastapi.security import HTTPBearer
import datetime
from uuid import uuid4
import redis
import re

router = APIRouter()
http_bearer = HTTPBearer()

@router.post("/user-module/register-account/")
async def register_account(new_user: RegisterUserModel, 
                        redis_client: redis.Redis = Depends(get_redis_client),
                        postgres_session: AsyncSession = Depends(get_session)):
    try:
        user_redis_repository = UserRedisRepository(redis_client)
        user_postgres_repository = UserPostgresRepository(postgres_session)
        user_utils = UserUtils()
        kafka_producer = KafkaProducer()

        if new_user.email != new_user.repeated_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provided email adresses don't match.")
        if new_user.password != new_user.repeated_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provided passwords don't match.")
        if len(new_user.password) < 8:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provided password is too short.")
        if not re.search(r'\d', new_user.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password needs to contatain at least 1 digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_user.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password needs to contatain at least 1 special character.")
        
        is_email_address_arleady_taken: bool = await user_postgres_repository.is_email_addres_arleady_taken(
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
        
        await kafka_producer.produce_event(
            topic=KafkaTopicsEnum.account_registered.value,
            message={"id": key_id, "email": new_user.email}
            )
        
        return JSONResponse(content={"detail": "Account has been registered. Now confirm your email address."})
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except (Exception, PostgreSQLDatabaseError, RedisSetError, RedisDatabaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    

@router.patch("/user-module/confirm-account/")
async def confirm_account(id: str, 
                        redis_client: redis.Redis = Depends(get_redis_client),
                        postgres_session: AsyncSession = Depends(get_session)):
    try:
        user_postgres_repository = UserPostgresRepository(postgres_session)
        user_redis_repository = UserRedisRepository(redis_client)
        kafka_producer = KafkaProducer()

        user_to_confirm_data: bytes = await user_redis_repository.search_user_by_id(
            id=id
            )
        
        user_to_confirm_data = CreateUserModel.model_validate_json(user_to_confirm_data)
        
        created_user: User = await user_postgres_repository.create_user(
            new_user=user_to_confirm_data
            )

        await user_redis_repository.delete_user_by_id(
            id=id
            )
        
        await kafka_producer.produce_event(
            topic=KafkaTopicsEnum.account_confirmed.value, 
            message={"email": created_user.email}
            )
        
        return JSONResponse(content={"detail": "Account has been confirmed. Now you can log in."})
    
    except RedisNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There is no such account to confirm.")
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except (Exception, PostgreSQLIntegrityError, PostgreSQLDatabaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)


@router.get("/user-module/log-in/")
async def log_in(email: str, password: str, remember_me: bool, 
                        redis_client: redis.Redis = Depends(get_redis_client),
                        postgres_session: AsyncSession = Depends(get_session)):
    try:
        user_postgres_repository = UserPostgresRepository(postgres_session)
        user_redis_repository = UserRedisRepository(redis_client)
        user_utils = UserUtils()

        user: User = await user_postgres_repository.get_user_by_email_address(
            user_email_adress=email
        )

        verify_password: bool = await user_utils.verify_password(
            salt=user.salt, 
            password=password, 
            hash=user.password
            )

        if verify_password == False:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong email adress or password.")
        
        if remember_me == True:
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

        return JSONResponse(content={"jwt_token": f"{jwt_token}"})

    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong email adress or password.")
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except (Exception, RedisDatabaseError, RedisSetError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    

@router.patch("/user-module/update-personal-info/")
async def update_personal_info(user_personal_info: UserPersonalInformationModel,
                        token = Depends(http_bearer), 
                        redis_client: redis.Redis = Depends(get_redis_client),
                        postgres_session: AsyncSession = Depends(get_session)):
    try:
        user_postgres_repository = UserPostgresRepository(postgres_session)
        user_redis_repository = UserRedisRepository(redis_client)
        
        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        await user_postgres_repository.update_user_personal_information(
            user_id=jwt_payload.id, 
            personal_information=user_personal_info
            )

        return JSONResponse(content={"message": "Personal information has been updated."})
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e)
    except RedisNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access or JWT token expired.")
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except (Exception, RedisDatabaseError, PostgreSQLDatabaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    
@router.patch("/user-module/change-email/")
async def change_email(new_email: UpdateUserEmailModel,
                        token = Depends(http_bearer), 
                        redis_client: redis.Redis = Depends(get_redis_client),
                        postgres_session: AsyncSession = Depends(get_session)):
    try:
        user_redis_repository = UserRedisRepository(redis_client)
        user_postgres_repository = UserPostgresRepository(postgres_session)
        kafka_producer = KafkaProducer()

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        user: User = await user_postgres_repository.get_user_by_id(
            user_id=jwt_payload.id
            )

        if new_email.current_email != user.email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provided email adress don't match with current email.")
        if new_email.new_email != new_email.new_repeated_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provided email adresses don't match.")

        is_email_address_arleady_taken: bool = await user_postgres_repository.is_email_addres_arleady_taken(
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
        
        await kafka_producer.produce_event(KafkaTopicsEnum.change_email.value, {"id": id,"email": jwt_payload.email})

        return JSONResponse(content={"message": "New email has been saved. Email message with confirmation link has been send to old email address."})
    except RedisSetError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    except RedisNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access or JWT token expired.")
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except (Exception, RedisDatabaseError, PostgreSQLDatabaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    
@router.patch("/user-module/confirm-email-change/")
async def confirm_email_change(id: str,
                        redis_client: redis.Redis = Depends(get_redis_client),
                        postgres_session: AsyncSession = Depends(get_session)):
    try:
        user_postgres_repository = UserPostgresRepository(postgres_session)
        user_redis_repository = UserRedisRepository(redis_client)
        kafka_producer = KafkaProducer()

        new_email_data: bytes = await user_redis_repository.retrieve_new_email(
            key_id=id
            )

        new_email_data: ConfirmedUserEmailChangeModel = ConfirmedUserEmailChangeModel.model_validate_json(new_email_data)

        is_email_address_arleady_taken: bool = await user_postgres_repository.is_email_addres_arleady_taken(
            user_email_adress=new_email_data.new_email
            )
        
        if is_email_address_arleady_taken == True:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email address arleady in use.")
        
        user: User = await user_postgres_repository.update_user_email_address(
            new_email=new_email_data
            )

        await user_redis_repository.delete_all_jwt_tokens_of_user(
            user_id=user.id
            )
        
        await user_redis_repository.delete_new_email(
            key_id=id
            )

        await kafka_producer.produce_event(KafkaTopicsEnum.email_changed.value, {"id": user.id,"email": user.email})

        return JSONResponse(content={"message": "New email has been set. You have been logged off from all devices."})
    except (RedisNotFoundError, PostgreSQLNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)

@router.patch("/user-module/change-password/")
async def change_password(new_password: UpdateUserPassword,
                        token = Depends(http_bearer), 
                        redis_client: redis.Redis = Depends(get_redis_client),
                        postgres_session: AsyncSession = Depends(get_session)):
    try:
        user_redis_repository = UserRedisRepository(redis_client)
        
        jwt_payload = await user_redis_repository.retrieve_jwt(token.credentials)
        
        if jwt_payload == None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access")
        
        jwt_payload = JWTPayloadModel.model_validate_json(jwt_payload)

        user_postgres_repository = UserPostgresRepository(postgres_session)

        user: User = await user_postgres_repository.get_user_by_id(jwt_payload.id)

        user_utils = UserUtils()

        password_match = await user_utils.verify_password(user.salt, new_password.current_password, user.password)

        if password_match == False:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong current password.")
        if new_password.new_password != new_password.new_repeated_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provided new passwords don't match")
        if len(new_password.new_password) < 8:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provided new password is too short")
        if not re.search(r'\d', new_password.new_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password needs to contatain at least 1 digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password.new_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password needs to contatain at least 1 special character")
        
        hashed_new_password = await user_utils.hash_password(user.salt, new_password.new_password)

        new_password_data = ConfirmUserPasswordChange(id=jwt_payload.id, new_password=hashed_new_password)

        id = await user_redis_repository.save_new_password(new_password_data)

        if id == None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error occured durning saving new password to database.")
        
        kafka_producer = KafkaProducer()
        await kafka_producer.produce_event(KafkaTopicsEnum.change_password.value, {"id": id, "email": jwt_payload.email})

        return JSONResponse(content={"message": "New password has been saved. Email message with confirmation link has been send to email address."})

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    
@router.patch("/user-module/confirm-password-change/")
async def confirm_password_change(id: str,
                        redis_client: redis.Redis = Depends(get_redis_client),
                        postgres_session: AsyncSession = Depends(get_session)):
    try:
        user_redis_repository = UserRedisRepository(redis_client)

        new_password_data = await user_redis_repository.retrieve_new_password(id)

        if new_password_data == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found new password to confirm with provided id.")

        new_password_data = ConfirmUserPasswordChange.model_validate_json(new_password_data)
        
        user_postgres_repository = UserPostgresRepository(postgres_session)
        
        updated_user_id: list = await user_postgres_repository.update_password(new_password_data)

        if not updated_user_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error occured durning updating password in database.")
        
        user: User = await user_postgres_repository.get_user_by_id(str(updated_user_id[0][0])) 

        await user_redis_repository.delete_all_jwt_of_user(str(updated_user_id[0][0]))
        await user_redis_repository.delete_new_password(id)

        kafka_producer = KafkaProducer()
        await kafka_producer.produce_event(KafkaTopicsEnum.password_changed.value, {"id": str(updated_user_id[0][0]),"email": user.email})

        return JSONResponse(content={"message": "New password has been set. You have been logged off from all devices."})

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    

@router.patch("/user-module/reset-password/")
async def reset_password(reset_password: ResetPasswordModel,
                        redis_client: redis.Redis = Depends(get_redis_client),
                        postgres_session: AsyncSession = Depends(get_session)):
    try:
        user_redis_repository = UserRedisRepository(redis_client)
        user_postgres_repository = UserPostgresRepository(postgres_session)



        user_utils = UserUtils()

        if reset_password.new_password != reset_password.new_repeated_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provided passwords don't match")
        if len(reset_password.new_password) < 8:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provided password is too short")
        if not re.search(r'\d', reset_password.new_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password needs to contatain at least 1 digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', reset_password.new_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password needs to contatain at least 1 special character")
        
        user: User = await user_postgres_repository.find_user_by_email(reset_password.email)

        if not user:
            return JSONResponse(content={"message": "If provided email address is correct you will get email message with url to confirm your new password."})
        

        hashed_new_password = await user_utils.hash_password(user.salt, reset_password.new_password)

        new_password_data = ConfirmUserPasswordChange(id=user.id, new_password=hashed_new_password)

        id = await user_redis_repository.save_reset_password(new_password_data)

        if id == None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error occured durning saving new password to database.")
        
        kafka_producer = KafkaProducer()
        await kafka_producer.produce_event(KafkaTopicsEnum.reset_password.value, {"id": id,"email": user.email})

        return JSONResponse(content={"message": "If provided email address is correct you will get email message with url to confirm your new password."})

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    
@router.patch("/user-module/confirm-password-reset/")
async def confirm_password_reset(id: str,
                        redis_client: redis.Redis = Depends(get_redis_client),
                        postgres_session: AsyncSession = Depends(get_session)):
    try:
        user_redis_repository = UserRedisRepository(redis_client)

        new_password_data = await user_redis_repository.retrieve_reset_password(id)

        if new_password_data == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found reset password to confirm with provided id.")

        new_password_data = ConfirmUserPasswordChange.model_validate_json(new_password_data)
        
        user_postgres_repository = UserPostgresRepository(postgres_session)
        
        updated_user_id: list = await user_postgres_repository.update_password(new_password_data)

        if not updated_user_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error occured durning updating password in database.")
        
        user: User = await user_postgres_repository.get_user_by_id(str(updated_user_id[0][0])) 

        await user_redis_repository.delete_all_jwt_of_user(str(updated_user_id[0][0]))
        await user_redis_repository.delete_new_password(id)

        kafka_producer = KafkaProducer()
        await kafka_producer.produce_event(KafkaTopicsEnum.password_reseted.value, {"id": str(updated_user_id[0][0]),"email": user.email})

        return JSONResponse(content={"message": "New password has been set. You have been logged off from all devices."})

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
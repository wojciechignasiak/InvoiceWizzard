from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from app.database.redis.client.get_redis_client import get_redis_client
from app.database.redis.repositories.user_repository import UserRedisRepository
from app.kafka.producer.kafka_producer import KafkaProducer
from app.utils.user_utils import UserUtils
from app.models.user_model import RegisterUserModel, NewUserTemporaryModel, UserPersonalInformation, UpdateUserEmail, UpdateUserPassword
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.postgres.session.get_session import get_session
from app.database.postgres.repositories.user_repository import UserPostgresRepository
from datetime import date
from app.models.kafka_topics_enum import KafkaTopicsEnum
from app.schema.schema import User
from app.models.jwt_model import JWTDataModel, JWTPayloadModel
from fastapi.security import HTTPBearer
import datetime
import redis
import re

router = APIRouter()
http_bearer = HTTPBearer()

@router.post("/user-module/register-account/")
async def register_account(new_user: RegisterUserModel, 
                        redis_client: redis.Redis = Depends(get_redis_client),
                        postgres_session: AsyncSession = Depends(get_session)):
    try:
        if new_user.email != new_user.repeated_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provided email adresses don't match")
        if new_user.password != new_user.repeated_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provided passwords don't match")
        if len(new_user.password) < 8:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provided password is too short")
        if not re.search(r'\d', new_user.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password needs to contatain at least 1 digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_user.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password needs to contatain at least 1 special character")
        
        user_postgres_repository = UserPostgresRepository(postgres_session)

        user_list: list = await user_postgres_repository.find_user_by_email(new_user.email)

        if user_list:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account with this email adress already exists")
        
        user_utils = UserUtils()

        salt = await user_utils.salt_generator()
        hashed_password = await user_utils.hash_password(salt,new_user.password)
        
        new_user_to_redis = NewUserTemporaryModel(email=new_user.email, 
                                                    password=hashed_password,
                                                    salt=salt,
                                                    registration_date=date.today().isoformat())
        
        user_redis_repository = UserRedisRepository(redis_client)
        
        is_user_arleady_registered: bytes = await user_redis_repository.search_user_by_id_or_email(value=new_user.email, search_by_email=True)

        if is_user_arleady_registered:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account with this email address already registered")
        
        redis_key_id = await user_redis_repository.create_user(new_user_to_redis)
        
        if redis_key_id:

            kafka_producer = KafkaProducer()

            await kafka_producer.produce_event(
                topic=KafkaTopicsEnum.account_registered.value,
                message={"id": redis_key_id, "email": new_user.email}
            )
            return JSONResponse(content={"detail": "Account has been registered. Now confirm your email address."})
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    

@router.patch("/user-module/confirm-account/")
async def confirm_account(id: str, 
                        redis_client: redis.Redis = Depends(get_redis_client),
                        postgres_session: AsyncSession = Depends(get_session)):
    try:
        user_redis_repository = UserRedisRepository(redis_client)

        temporary_user_data = await user_redis_repository.search_user_by_id_or_email(id)

        if not temporary_user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There is no such account to confirm.")
        
        temporary_user_data = NewUserTemporaryModel.model_validate_json(temporary_user_data)

        user_postgres_repository = UserPostgresRepository(postgres_session)
        
        result: list = await user_postgres_repository.create_new_user(temporary_user_data)

        if not result:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error occured durning saving account to database")
        
        await user_redis_repository.delete_user_by_id(id)
        
        kafka_producer = KafkaProducer()
        await kafka_producer.produce_event(
            topic=KafkaTopicsEnum.account_confirmed.value, 
            message={"email": temporary_user_data.email})
        
        return JSONResponse(content={"detail": "Account has been confirmed. Now you can log in."})

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    
@router.get("/user-module/log-in/")
async def log_in(email: str, password: str, remember_me: bool, 
                        redis_client: redis.Redis = Depends(get_redis_client),
                        postgres_session: AsyncSession = Depends(get_session)):
    try:
        user_postgres_repository = UserPostgresRepository(postgres_session)

        user: User = await user_postgres_repository.find_user_by_email(email)
        if not user:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Wrong email adress or password.")
        
        user_utils = UserUtils()
        verify_password: bool = await user_utils.verify_password(user.salt, password, user.password)

        if verify_password == False:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Wrong email adress or password.")
        
        if remember_me == True:
            jwt_expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=24*14)
        else:
            jwt_expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=12)

        jwt_payload = JWTPayloadModel(id=str(user.id), email=user.email, exp=jwt_expiration_time)

        jwt_data = JWTDataModel(secret=user.salt, payload=jwt_payload)

        jwt_token = await user_utils.jwt_encoder(jwt_data)

        user_redis_repository = UserRedisRepository(redis_client)

        result = await user_redis_repository.save_jwt(jwt_token, jwt_payload)

        if result == False:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error occured durning saving JWT token to database")
        
        return JSONResponse(content={"jwt_token": f"{jwt_token}"})

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    

@router.patch("/user-module/update-personal-info/")
async def update_personal_info(user_personal_info: UserPersonalInformation,
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

        result = await user_postgres_repository.update_personal_info(jwt_payload.id, user_personal_info)

        if result == None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error occured durning updating personal information.")

        return JSONResponse(content={"message": "Personal information has been updated."})

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    
@router.patch("/user-module/change-email/")
async def change_email(new_email: UpdateUserEmail,
                        token = Depends(http_bearer), 
                        redis_client: redis.Redis = Depends(get_redis_client),
                        postgres_session: AsyncSession = Depends(get_session)):
    try:
        
        user_redis_repository = UserRedisRepository(redis_client)
        
        jwt_payload = await user_redis_repository.retrieve_jwt(token.credentials)
        
        if jwt_payload == None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access")
        
        jwt_payload = JWTPayloadModel.model_validate_json(jwt_payload)

        if new_email.current_email != jwt_payload.email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provided email adress don't match with current email.")
        if new_email.new_email != new_email.new_repeated_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provided email adresses don't match.")

        user_postgres_repository = UserPostgresRepository(postgres_session)

        result = user_postgres_repository.find_user_by_email(new_email.new_email)
        if result:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email address arleady in use.")
        
        id = await user_redis_repository.save_new_email(jwt_payload.id, new_email.new_email)

        if id == None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error occured durning saving new email to database.")
        
        kafka_producer = KafkaProducer()
        await kafka_producer.produce_event(KafkaTopicsEnum.change_email.value, {"id": id,"email": jwt_payload.email})

        return JSONResponse(content={"message": "New email has been saved. Email message with confirmation link has been send to old email address."})

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
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
        id = await user_redis_repository.save_new_password(jwt_payload.id, hashed_new_password)

        if id == None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error occured durning saving new password to database.")
        
        kafka_producer = KafkaProducer()
        await kafka_producer.produce_event(KafkaTopicsEnum.change_password.value, {"id": id, "email": jwt_payload.email})

        return JSONResponse(content={"message": "New password has been saved. Email message with confirmation link has been send to email address."})

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
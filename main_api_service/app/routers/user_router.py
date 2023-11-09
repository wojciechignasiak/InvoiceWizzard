from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from app.database.redis.client.get_redis_client import get_redis_client
from app.database.redis.repositories.user_repository import UserRedisRepository
from app.kafka.producer.kafka_producer import KafkaProducer
from app.utils.user_utils import UserUtils
from app.models.user_model import RegisterUserModel, NewUserTemporaryModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.postgres.session.get_session import get_session
from app.database.postgres.repositories.user_repository import UserPostgresRepository
from datetime import date
from app.models.kafka_topics_enum import KafkaTopicsEnum
import redis
import re

router = APIRouter()

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
    

@router.post("/user-module/confirm-account/")
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
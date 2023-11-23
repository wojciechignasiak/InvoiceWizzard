import pytest
from app.database.redis.repositories.user_repository import UserRedisRepository
from app.database.redis.exceptions.custom_redis_exceptions import (
    RedisDatabaseError,
    RedisNotFoundError,
    RedisSetError,
    RedisJWTNotFoundError
)
from app.models.jwt_model import JWTPayloadModel
from redis.exceptions import (
    RedisError, 
    ConnectionError, 
    TimeoutError, 
    ResponseError
)
from app.models.user_model import (
    CreateUserModel, 
    ConfirmedUserEmailChangeModel, 
    ConfirmedUserPasswordChangeModel
    )
from uuid import uuid4
from datetime import date, datetime

@pytest.mark.asyncio
async def test_create_user_success(mock_redis_client):
    mock_id = uuid4()

    user_to_be_created = CreateUserModel(
        email="email@example.com",
        password="passw0rd!",
        salt="123456789podwajkdjadsakdjkanw",
        registration_date=date.today().isoformat()
    )

    mock_redis_client.setex.return_value = True
    
    user_redis_repository = UserRedisRepository(mock_redis_client)
    is_created = await user_redis_repository.create_user(str(mock_id), user_to_be_created)
    
    assert isinstance(is_created, bool)

@pytest.mark.asyncio
async def test_create_user_redis_set_error(mock_redis_client):
    mock_id = uuid4()

    user_to_be_created = CreateUserModel(
        email="email@example.com",
        password="passw0rd!",
        salt="123456789podwajkdjadsakdjkanw",
        registration_date=date.today().isoformat()
    )

    mock_redis_client.setex.return_value = False
    
    user_redis_repository = UserRedisRepository(mock_redis_client)
    with pytest.raises(RedisSetError):
        await user_redis_repository.create_user(str(mock_id), user_to_be_created)

@pytest.mark.asyncio
async def test_create_user_redis_error(mock_redis_client):
    mock_id = uuid4()

    user_to_be_created = CreateUserModel(
        email="email@example.com",
        password="passw0rd!",
        salt="123456789podwajkdjadsakdjkanw",
        registration_date=date.today().isoformat()
    )

    mock_redis_client.setex.side_effect = RedisError("Redis error")
    
    user_redis_repository = UserRedisRepository(mock_redis_client)

    with pytest.raises(RedisDatabaseError):
        await user_redis_repository.create_user(str(mock_id), user_to_be_created)



@pytest.mark.asyncio
async def test_search_user_by_id_success(mock_redis_client):
    mock_id = uuid4()

    mock_redis_client.get.return_value = bytes("Test", "utf-8")
    mock_redis_client.keys.return_value = ["key"]
    
    user_redis_repository = UserRedisRepository(mock_redis_client)
    bytes_result = await user_redis_repository.search_user_by_id(str(mock_id))
    
    assert isinstance(bytes_result, bytes)

@pytest.mark.asyncio
async def test_search_user_by_id_not_found(mock_redis_client):
    mock_id = uuid4()
    mock_redis_client.keys.return_value = []
    
    user_redis_repository = UserRedisRepository(mock_redis_client)
    
    with pytest.raises(RedisNotFoundError):
        await user_redis_repository.search_user_by_id(str(mock_id))

@pytest.mark.asyncio
async def test_search_user_by_id_redis_error(mock_redis_client):
    mock_id = uuid4()
    mock_redis_client.keys.side_effect = RedisError("Redis error")
    
    user_redis_repository = UserRedisRepository(mock_redis_client)
    
    with pytest.raises(RedisDatabaseError):
        await user_redis_repository.search_user_by_id(str(mock_id))



@pytest.mark.asyncio
async def test_is_user_arleady_registered_success(mock_redis_client):
    mock_email = "email@example.com"
    mock_redis_client.keys.return_value = ["key"]
    
    user_redis_repository = UserRedisRepository(mock_redis_client)
    is_user_registered = await user_redis_repository.is_user_arleady_registered(mock_email)
    
    assert isinstance(is_user_registered, bool)
    assert is_user_registered == True

@pytest.mark.asyncio
async def test_is_user_arleady_registered_redis_error(mock_redis_client):
    mock_email = "email@example.com"
    mock_redis_client.keys.side_effect = RedisError("Redis error")
    
    user_redis_repository = UserRedisRepository(mock_redis_client)
    
    with pytest.raises(RedisDatabaseError):
        await user_redis_repository.is_user_arleady_registered(mock_email)



@pytest.mark.asyncio
async def test_delete_user_by_id_success(mock_redis_client):
    mock_id = uuid4()
    mock_redis_client.keys.return_value = ["key"]
    
    user_redis_repository = UserRedisRepository(mock_redis_client)
    is_user_deleted = await user_redis_repository.delete_user_by_id(str(mock_id))
    
    assert isinstance(is_user_deleted, bool)
    assert is_user_deleted == True

@pytest.mark.asyncio
async def test_delete_user_by_id_redis_error(mock_redis_client):
    mock_id = uuid4()
    mock_redis_client.keys.side_effect = RedisError("Redis error")
    
    user_redis_repository = UserRedisRepository(mock_redis_client)

    with pytest.raises(RedisDatabaseError):
        await user_redis_repository.delete_user_by_id(str(mock_id))



@pytest.mark.asyncio
async def test_save_jwt_success(mock_redis_client):
    mock_jwt_token = "1234567890"
    mock_jwt_payload = JWTPayloadModel(
        id="1",
        email="email@example.com",
        exp=datetime.utcnow()
    )
    mock_redis_client.setex.return_value = True
    
    user_redis_repository = UserRedisRepository(mock_redis_client)
    is_jwt_saved = await user_redis_repository.save_jwt(mock_jwt_token, mock_jwt_payload)
    
    assert isinstance(is_jwt_saved, bool)
    assert is_jwt_saved == True

@pytest.mark.asyncio
async def test_save_jwt_redis_set_error(mock_redis_client):
    mock_jwt_token = "1234567890"
    mock_jwt_payload = JWTPayloadModel(
        id="1",
        email="email@example.com",
        exp=datetime.utcnow()
    )
    mock_redis_client.setex.return_value = False
    
    user_redis_repository = UserRedisRepository(mock_redis_client)

    with pytest.raises(RedisSetError):
        await user_redis_repository.save_jwt(mock_jwt_token, mock_jwt_payload)

@pytest.mark.asyncio
async def test_save_jwt_redis_error(mock_redis_client):
    mock_jwt_token = "1234567890"
    mock_jwt_payload = JWTPayloadModel(
        id="1",
        email="email@example.com",
        exp=datetime.utcnow()
    )
    mock_redis_client.setex.side_effect = RedisError("Redis error")
    
    user_redis_repository = UserRedisRepository(mock_redis_client)

    with pytest.raises(RedisDatabaseError):
        await user_redis_repository.save_jwt(mock_jwt_token, mock_jwt_payload)



@pytest.mark.asyncio
async def test_retrieve_jwt_success(mock_redis_client):
    mock_jwt_token = "1234567890"
    mock_redis_client.get.return_value = bytes("Test", "utf-8")
    mock_redis_client.keys.return_value = ["key"]
    
    user_redis_repository = UserRedisRepository(mock_redis_client)
    jwt = await user_redis_repository.retrieve_jwt(mock_jwt_token)
    
    assert isinstance(jwt, bytes)

@pytest.mark.asyncio
async def test_retrieve_jwt_redis_jwt_not_found_error(mock_redis_client):
    mock_jwt_token = "1234567890"
    
    mock_redis_client.keys.return_value = []
    
    user_redis_repository = UserRedisRepository(mock_redis_client)
    
    with pytest.raises(RedisJWTNotFoundError):
        await user_redis_repository.retrieve_jwt(mock_jwt_token)

@pytest.mark.asyncio
async def test_retrieve_jwt_redis_error(mock_redis_client):
    mock_jwt_token = "1234567890"
    
    mock_redis_client.keys.side_effect = RedisError("Redis error")
    
    user_redis_repository = UserRedisRepository(mock_redis_client)
    
    with pytest.raises(RedisDatabaseError):
        await user_redis_repository.retrieve_jwt(mock_jwt_token)



@pytest.mark.asyncio
async def test_save_new_email_success(mock_redis_client):
    mock_id = uuid4()
    mock_new_email = ConfirmedUserEmailChangeModel(
        id="123",
        new_email="email@example.com"
    )
    mock_redis_client.setex.return_value = True
    
    user_redis_repository = UserRedisRepository(mock_redis_client)
    is_new_email_saved = await user_redis_repository.save_new_email(str(mock_id), mock_new_email)
    
    assert isinstance(is_new_email_saved, bool)
    assert is_new_email_saved == True

@pytest.mark.asyncio
async def test_save_new_email_redis_set_error(mock_redis_client):
    mock_id = uuid4()
    mock_new_email = ConfirmedUserEmailChangeModel(
        id="123",
        new_email="email@example.com"
    )
    mock_redis_client.setex.return_value = False
    
    user_redis_repository = UserRedisRepository(mock_redis_client)
    with pytest.raises(RedisSetError):
        await user_redis_repository.save_new_email(str(mock_id), mock_new_email)

@pytest.mark.asyncio
async def test_save_new_email_redis_database_error(mock_redis_client):
    mock_id = uuid4()
    mock_new_email = ConfirmedUserEmailChangeModel(
        id="123",
        new_email="email@example.com"
    )
    mock_redis_client.setex.side_effect = RedisError("Redis error")
    
    user_redis_repository = UserRedisRepository(mock_redis_client)
    with pytest.raises(RedisDatabaseError):
        await user_redis_repository.save_new_email(str(mock_id), mock_new_email)



@pytest.mark.asyncio
async def test_retrieve_new_email_success(mock_redis_client):
    mock_id = uuid4()
    mock_redis_client.get.return_value = bytes("Test", "utf-8")
    
    user_redis_repository = UserRedisRepository(mock_redis_client)
    new_email = await user_redis_repository.retrieve_new_email(str(mock_id))
    
    assert isinstance(new_email, bytes)

@pytest.mark.asyncio
async def test_retrieve_new_email_redis_not_found_error(mock_redis_client):
    mock_id = uuid4()
    mock_redis_client.get.return_value = None
    
    user_redis_repository = UserRedisRepository(mock_redis_client)
    
    with pytest.raises(RedisNotFoundError):
        await user_redis_repository.retrieve_new_email(str(mock_id))

@pytest.mark.asyncio
async def test_retrieve_new_email_redis_database_error(mock_redis_client):
    mock_id = uuid4()
    mock_redis_client.get.side_effect = RedisError("Redis error")
    
    user_redis_repository = UserRedisRepository(mock_redis_client)
    
    with pytest.raises(RedisDatabaseError):
        await user_redis_repository.retrieve_new_email(str(mock_id))



@pytest.mark.asyncio
async def test_save_new_password_success(mock_redis_client):
    mock_id = uuid4()
    mock_new_password = ConfirmedUserPasswordChangeModel(
        id="123",
        new_password="password123"
    )
    mock_redis_client.setex.return_value = True
    
    user_redis_repository = UserRedisRepository(mock_redis_client)
    is_new_password_saved = await user_redis_repository.save_new_password(str(mock_id), mock_new_password)
    
    assert isinstance(is_new_password_saved, bool)
    assert is_new_password_saved == True

@pytest.mark.asyncio
async def test_save_new_password_redis_set_error(mock_redis_client):
    mock_id = uuid4()
    mock_new_password = ConfirmedUserPasswordChangeModel(
        id="123",
        new_password="password123"
    )
    mock_redis_client.setex.return_value = False
    
    user_redis_repository = UserRedisRepository(mock_redis_client)
    with pytest.raises(RedisSetError):
        await user_redis_repository.save_new_password(str(mock_id), mock_new_password)

@pytest.mark.asyncio
async def test_save_new_password_redis_database_error(mock_redis_client):
    mock_id = uuid4()
    mock_new_password = ConfirmedUserPasswordChangeModel(
        id="123",
        new_password="password123"
    )
    mock_redis_client.setex.side_effect = RedisError("Redis error")
    
    user_redis_repository = UserRedisRepository(mock_redis_client)
    with pytest.raises(RedisDatabaseError):
        await user_redis_repository.save_new_password(str(mock_id), mock_new_password)



@pytest.mark.asyncio
async def test_retrieve_new_password_success(mock_redis_client):
    mock_id = uuid4()
    mock_redis_client.get.return_value = bytes("Test", "utf-8")
    
    user_redis_repository = UserRedisRepository(mock_redis_client)
    new_password = await user_redis_repository.retrieve_new_password(str(mock_id))
    
    assert isinstance(new_password, bytes)

@pytest.mark.asyncio
async def test_retrieve_new_password_redis_not_found_error(mock_redis_client):
    mock_id = uuid4()
    mock_redis_client.get.return_value = None
    
    user_redis_repository = UserRedisRepository(mock_redis_client)
    
    with pytest.raises(RedisNotFoundError):
        await user_redis_repository.retrieve_new_password(str(mock_id))

@pytest.mark.asyncio
async def test_retrieve_new_password_redis_database_error(mock_redis_client):
    mock_id = uuid4()
    mock_redis_client.get.side_effect = RedisError("Redis error")
    
    user_redis_repository = UserRedisRepository(mock_redis_client)
    
    with pytest.raises(RedisDatabaseError):
        await user_redis_repository.retrieve_new_password(str(mock_id))
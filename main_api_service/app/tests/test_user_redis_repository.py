import pytest
from app.database.redis.repositories.user_repository import UserRedisRepository
from app.database.redis.exceptions.custom_redis_exceptions import (
    RedisDatabaseError,
    RedisNotFoundError,
    RedisSetError,
    RedisJWTNotFoundError
)
from redis.exceptions import (
    RedisError
)
from uuid import uuid4

# UserRedisRepository.create_user()

@pytest.mark.asyncio
async def test_create_user_success(
    mock_redis_client,
    mock_create_user_model_object):
    user_redis_repository = UserRedisRepository(mock_redis_client)
    mock_redis_client.set.return_value = True
    is_created = await user_redis_repository.create_user(str(uuid4()), mock_create_user_model_object)
    assert isinstance(is_created, bool)

@pytest.mark.asyncio
async def test_create_user_redis_set_error(
    mock_redis_client,
    mock_create_user_model_object):

    user_redis_repository = UserRedisRepository(mock_redis_client)
    mock_redis_client.set.return_value = False
    
    with pytest.raises(RedisSetError):
        await user_redis_repository.create_user(str(uuid4()), mock_create_user_model_object)

@pytest.mark.asyncio
async def test_create_user_redis_error(
    mock_redis_client,
    mock_create_user_model_object):

    user_redis_repository = UserRedisRepository(mock_redis_client)
    mock_redis_client.set.side_effect = RedisError("Redis error")

    with pytest.raises(RedisDatabaseError):
        await user_redis_repository.create_user(str(uuid4()), mock_create_user_model_object)

# UserRedisRepository.search_user_by_id()

@pytest.mark.asyncio
async def test_search_user_by_id_success(
    mock_redis_client,
    mock_create_user_model_object):

    mock_id = uuid4()
    user_redis_repository = UserRedisRepository(mock_redis_client)
    mock_redis_client.get.return_value = bytes(mock_create_user_model_object.model_dump_json(), "utf-8")
    mock_redis_client.keys.return_value = ["key"]
    bytes_result = await user_redis_repository.search_user_by_id(str(mock_id))
    
    assert isinstance(bytes_result, bytes)

@pytest.mark.asyncio
async def test_search_user_by_id_not_found(mock_redis_client):
    
    user_redis_repository = UserRedisRepository(mock_redis_client)
    mock_redis_client.keys.return_value = []
    
    with pytest.raises(RedisNotFoundError):
        await user_redis_repository.search_user_by_id(str(uuid4()))

@pytest.mark.asyncio
async def test_search_user_by_id_redis_error(mock_redis_client):
    
    user_redis_repository = UserRedisRepository(mock_redis_client)
    mock_redis_client.keys.side_effect = RedisError("Redis error")
    
    with pytest.raises(RedisDatabaseError):
        await user_redis_repository.search_user_by_id(str(uuid4()))

# UserRedisRepository.is_user_arleady_registered()

@pytest.mark.asyncio
async def test_is_user_arleady_registered_success(mock_redis_client):

    user_redis_repository = UserRedisRepository(mock_redis_client)
    mock_redis_client.keys.return_value = ["key"]
    is_user_registered = await user_redis_repository.is_user_arleady_registered("email@example.com")
    
    assert isinstance(is_user_registered, bool)
    assert is_user_registered == True

@pytest.mark.asyncio
async def test_is_user_arleady_registered_redis_error(mock_redis_client):

    user_redis_repository = UserRedisRepository(mock_redis_client)
    mock_redis_client.keys.side_effect = RedisError("Redis error")
    
    with pytest.raises(RedisDatabaseError):
        await user_redis_repository.is_user_arleady_registered("email@example.com")

# UserRedisRepository.delete_user_by_id()

@pytest.mark.asyncio
async def test_delete_user_by_id_success(mock_redis_client):

    user_redis_repository = UserRedisRepository(mock_redis_client)
    mock_redis_client.keys.return_value = ["key"]
    is_user_deleted = await user_redis_repository.delete_user_by_id(str(uuid4()))
    
    assert isinstance(is_user_deleted, bool)
    assert is_user_deleted == True

@pytest.mark.asyncio
async def test_delete_user_by_id_redis_error(mock_redis_client):

    user_redis_repository = UserRedisRepository(mock_redis_client)
    mock_redis_client.keys.side_effect = RedisError("Redis error")

    with pytest.raises(RedisDatabaseError):
        await user_redis_repository.delete_user_by_id(str(uuid4()))

# UserRedisRepository.save_jwt()

@pytest.mark.asyncio
async def test_save_jwt_success(
    mock_redis_client,
    mock_jwt_payload_model_object,
    mock_jwt_token):

    user_redis_repository = UserRedisRepository(mock_redis_client)
    mock_redis_client.set.return_value = True
    is_jwt_saved = await user_redis_repository.save_jwt(mock_jwt_token, mock_jwt_payload_model_object)
    
    assert isinstance(is_jwt_saved, bool)
    assert is_jwt_saved == True

@pytest.mark.asyncio
async def test_save_jwt_redis_set_error(
    mock_redis_client,
    mock_jwt_payload_model_object,
    mock_jwt_token):

    user_redis_repository = UserRedisRepository(mock_redis_client)
    mock_redis_client.set.return_value = False
    
    with pytest.raises(RedisSetError):
        await user_redis_repository.save_jwt(mock_jwt_token, mock_jwt_payload_model_object)

@pytest.mark.asyncio
async def test_save_jwt_redis_error(
    mock_redis_client,
    mock_jwt_payload_model_object,
    mock_jwt_token):


    user_redis_repository = UserRedisRepository(mock_redis_client)
    mock_redis_client.set.side_effect = RedisError("Redis error")
    
    with pytest.raises(RedisDatabaseError):
        await user_redis_repository.save_jwt(mock_jwt_token, mock_jwt_payload_model_object)

# UserRedisRepository.retrieve_jwt()

@pytest.mark.asyncio
async def test_retrieve_jwt_success(
    mock_redis_client,
    mock_jwt_payload_model_object,
    mock_jwt_token):

    user_redis_repository = UserRedisRepository(mock_redis_client)
    mock_redis_client.get.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_redis_client.keys.return_value = [mock_jwt_token]
    jwt = await user_redis_repository.retrieve_jwt(mock_jwt_token)
    
    assert isinstance(jwt, bytes)

@pytest.mark.asyncio
async def test_retrieve_jwt_redis_jwt_not_found_error(
    mock_redis_client,
    mock_jwt_token):

    user_redis_repository = UserRedisRepository(mock_redis_client)
    mock_redis_client.keys.return_value = []

    with pytest.raises(RedisJWTNotFoundError):
        await user_redis_repository.retrieve_jwt(mock_jwt_token)

@pytest.mark.asyncio
async def test_retrieve_jwt_redis_error(
    mock_redis_client,
    mock_jwt_token):

    user_redis_repository = UserRedisRepository(mock_redis_client)
    mock_redis_client.keys.side_effect = RedisError("Redis error")
    
    with pytest.raises(RedisDatabaseError):
        await user_redis_repository.retrieve_jwt(mock_jwt_token)

# UserRedisRepository.save_new_email()

@pytest.mark.asyncio
async def test_save_new_email_success(
    mock_redis_client,
    mock_confirmed_user_email_change_model_object):

    user_redis_repository = UserRedisRepository(mock_redis_client)
    mock_redis_client.set.return_value = True
    is_new_email_saved = await user_redis_repository.save_new_email(str(uuid4()), mock_confirmed_user_email_change_model_object)
    
    assert isinstance(is_new_email_saved, bool)
    assert is_new_email_saved == True

@pytest.mark.asyncio
async def test_save_new_email_redis_set_error(
    mock_redis_client,
    mock_confirmed_user_email_change_model_object):

    user_redis_repository = UserRedisRepository(mock_redis_client)
    mock_redis_client.set.return_value = False
    
    with pytest.raises(RedisSetError):
        await user_redis_repository.save_new_email(str(uuid4()), mock_confirmed_user_email_change_model_object)

@pytest.mark.asyncio
async def test_save_new_email_redis_database_error(
    mock_redis_client,
    mock_confirmed_user_email_change_model_object):

    user_redis_repository = UserRedisRepository(mock_redis_client)
    mock_redis_client.set.side_effect = RedisError("Redis error")
    
    with pytest.raises(RedisDatabaseError):
        await user_redis_repository.save_new_email(str(uuid4()), mock_confirmed_user_email_change_model_object)

# UserRedisRepository.retrieve_new_email()

@pytest.mark.asyncio
async def test_retrieve_new_email_success(
    mock_redis_client,
    mock_confirmed_user_email_change_model_object):

    user_redis_repository = UserRedisRepository(mock_redis_client)
    mock_redis_client.get.return_value = bytes(mock_confirmed_user_email_change_model_object.model_dump_json(), "utf-8")
    new_email = await user_redis_repository.retrieve_new_email(str(uuid4()))
    
    assert isinstance(new_email, bytes)

@pytest.mark.asyncio
async def test_retrieve_new_email_redis_not_found_error(mock_redis_client):

    user_redis_repository = UserRedisRepository(mock_redis_client)
    mock_redis_client.get.return_value = None
    
    with pytest.raises(RedisNotFoundError):
        await user_redis_repository.retrieve_new_email(str(uuid4()))

@pytest.mark.asyncio
async def test_retrieve_new_email_redis_database_error(mock_redis_client):

    user_redis_repository = UserRedisRepository(mock_redis_client)
    mock_redis_client.get.side_effect = RedisError("Redis error")
    
    with pytest.raises(RedisDatabaseError):
        await user_redis_repository.retrieve_new_email(str(uuid4()))

# UserRedisRepository.save_new_password()

@pytest.mark.asyncio
async def test_save_new_password_success(
    mock_redis_client,
    mock_confirmed_user_password_change_model_object):

    user_redis_repository = UserRedisRepository(mock_redis_client)
    mock_redis_client.set.return_value = True
    is_new_password_saved = await user_redis_repository.save_new_password(str(uuid4()), mock_confirmed_user_password_change_model_object)
    
    assert isinstance(is_new_password_saved, bool)
    assert is_new_password_saved == True

@pytest.mark.asyncio
async def test_save_new_password_redis_set_error(
    mock_redis_client,
    mock_confirmed_user_password_change_model_object):

    user_redis_repository = UserRedisRepository(mock_redis_client)
    mock_redis_client.set.return_value = False
    
    with pytest.raises(RedisSetError):
        await user_redis_repository.save_new_password(str(uuid4()), mock_confirmed_user_password_change_model_object)

@pytest.mark.asyncio
async def test_save_new_password_redis_database_error(
    mock_redis_client,
    mock_confirmed_user_password_change_model_object):

    user_redis_repository = UserRedisRepository(mock_redis_client)
    mock_redis_client.set.side_effect = RedisError("Redis error")
    
    with pytest.raises(RedisDatabaseError):
        await user_redis_repository.save_new_password(str(uuid4()), mock_confirmed_user_password_change_model_object)

# UserRedisRepository.retrieve_new_password()

@pytest.mark.asyncio
async def test_retrieve_new_password_success(
    mock_redis_client,
    mock_confirmed_user_password_change_model_object):

    user_redis_repository = UserRedisRepository(mock_redis_client)
    mock_redis_client.get.return_value = bytes(mock_confirmed_user_password_change_model_object.model_dump_json(), "utf-8")
    new_password = await user_redis_repository.retrieve_new_password(str(uuid4()))
    
    assert isinstance(new_password, bytes)

@pytest.mark.asyncio
async def test_retrieve_new_password_redis_not_found_error(mock_redis_client):

    user_redis_repository = UserRedisRepository(mock_redis_client)
    mock_redis_client.get.return_value = None
    
    with pytest.raises(RedisNotFoundError):
        await user_redis_repository.retrieve_new_password(str(uuid4()))

@pytest.mark.asyncio
async def test_retrieve_new_password_redis_database_error(mock_redis_client):

    user_redis_repository = UserRedisRepository(mock_redis_client)
    mock_redis_client.get.side_effect = RedisError("Redis error")
    
    with pytest.raises(RedisDatabaseError):
        await user_redis_repository.retrieve_new_password(str(uuid4()))
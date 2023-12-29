import pytest

from app.database.redis.exceptions.custom_redis_exceptions import (
    RedisDatabaseError,
    RedisNotFoundError,
    RedisSetError,
)
from redis.exceptions import (
    RedisError
)
from app.database.redis.repositories.external_business_entity_repository import ExternalBusinessEntityRedisRepository

# ExternalBusinessEntityRedisRepository.initialize_external_business_entity_removal()

@pytest.mark.asyncio
async def test_initialize_external_business_entity_removal_success(
    mock_redis_client,
    mock_external_business_entity_model_object):

    external_business_entity_redis_repository = ExternalBusinessEntityRedisRepository(mock_redis_client)
    mock_redis_client.set.return_value = True
    is_created = await external_business_entity_redis_repository.initialize_external_business_entity_removal(
        'some_unique_id',
        mock_external_business_entity_model_object.id
    )
    
    assert isinstance(is_created, bool)
    assert is_created == True

@pytest.mark.asyncio
async def test_initialize_external_business_entity_removal_error(
    mock_redis_client,
    mock_external_business_entity_model_object):

    external_business_entity_redis_repository = ExternalBusinessEntityRedisRepository(mock_redis_client)
    mock_redis_client.set.return_value = False
    
    with pytest.raises(RedisSetError):
        await external_business_entity_redis_repository.initialize_external_business_entity_removal(
        'some_unique_id',
        mock_external_business_entity_model_object.id
    )

@pytest.mark.asyncio
async def test_initialize_external_business_entity_removal_database_error(
    mock_redis_client,
    mock_external_business_entity_model_object):

    external_business_entity_redis_repository = ExternalBusinessEntityRedisRepository(mock_redis_client)
    mock_redis_client.set.side_effect = RedisError()
    
    with pytest.raises(RedisDatabaseError):
        await external_business_entity_redis_repository.initialize_external_business_entity_removal(
        'some_unique_id',
        mock_external_business_entity_model_object.id
    )

# ExternalBusinessEntityRedisRepository.retrieve_external_business_entity_removal()

@pytest.mark.asyncio
async def test_retrieve_external_business_entity_removal_success(
    mock_redis_client):

    external_business_entity_redis_repository = ExternalBusinessEntityRedisRepository(mock_redis_client)
    mock_redis_client.get.return_value = bytes("some_entity_id", "utf-8")
    result = await external_business_entity_redis_repository.retrieve_external_business_entity_removal(
        'some_unique_id'
    )
    
    assert isinstance(result, bytes)

@pytest.mark.asyncio
async def test_retrieve_external_business_entity_removal_not_found_error(
    mock_redis_client):

    external_business_entity_redis_repository = ExternalBusinessEntityRedisRepository(mock_redis_client)
    mock_redis_client.get.return_value = None
    
    with pytest.raises(RedisNotFoundError):
        await external_business_entity_redis_repository.retrieve_external_business_entity_removal(
        'some_unique_id'
    )
        
@pytest.mark.asyncio
async def test_retrieve_external_business_entity_removal_database_error(
    mock_redis_client):

    external_business_entity_redis_repository = ExternalBusinessEntityRedisRepository(mock_redis_client)
    mock_redis_client.get.side_effect = RedisError()
    
    with pytest.raises(RedisDatabaseError):
        await external_business_entity_redis_repository.retrieve_external_business_entity_removal(
        'some_unique_id'
    )
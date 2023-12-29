import pytest

from app.database.redis.exceptions.custom_redis_exceptions import (
    RedisDatabaseError,
    RedisNotFoundError,
    RedisSetError,
)
from redis.exceptions import (
    RedisError
)
from app.database.redis.repositories.invoice_repository import InvoiceRedisRepository


@pytest.mark.asyncio
async def test_initialize_user_business_entity_removal_success(
    mock_redis_client,
    mock_invoice_model_object):

    invoice_redis_repository = InvoiceRedisRepository(mock_redis_client)
    mock_redis_client.set.return_value = True
    is_created = await invoice_redis_repository.initialize_invoice_removal(
        'some_unique_id',
        mock_invoice_model_object.id
    )
    
    assert isinstance(is_created, bool)
    assert is_created == True

@pytest.mark.asyncio
async def test_initialize_user_business_entity_removal_error(
    mock_redis_client,
    mock_invoice_model_object):

    invoice_redis_repository = InvoiceRedisRepository(mock_redis_client)
    mock_redis_client.set.return_value = False
    
    with pytest.raises(RedisSetError):
        await invoice_redis_repository.initialize_invoice_removal(
        'some_unique_id',
        mock_invoice_model_object.id
    )

@pytest.mark.asyncio
async def test_initialize_invoice_removal_database_error(
    mock_redis_client,
    mock_invoice_model_object):

    invoice_redis_repository = InvoiceRedisRepository(mock_redis_client)
    mock_redis_client.set.side_effect = RedisError()
    
    with pytest.raises(RedisDatabaseError):
        await invoice_redis_repository.initialize_invoice_removal(
        'some_unique_id',
        mock_invoice_model_object.id
    )


@pytest.mark.asyncio
async def test_retrieve_invoice_removal_success(
    mock_redis_client):

    invoice_redis_repository = InvoiceRedisRepository(mock_redis_client)
    mock_redis_client.get.return_value = bytes("some_invoice_id", "utf-8")
    result = await invoice_redis_repository.retrieve_invoice_removal(
        'some_unique_id'
    )
    
    assert isinstance(result, bytes)

@pytest.mark.asyncio
async def test_retrieve_invoice_removal_not_found_error(
    mock_redis_client):

    invoice_redis_repository = InvoiceRedisRepository(mock_redis_client)
    mock_redis_client.get.return_value = None
    
    with pytest.raises(RedisNotFoundError):
        await invoice_redis_repository.retrieve_invoice_removal(
        'some_unique_id'
    )
        
@pytest.mark.asyncio
async def test_retrieve_invoice_removal_database_error(
    mock_redis_client):

    invoice_redis_repository = InvoiceRedisRepository(mock_redis_client)
    mock_redis_client.get.side_effect = RedisError()
    
    with pytest.raises(RedisDatabaseError):
        await invoice_redis_repository.retrieve_invoice_removal(
        'some_unique_id'
    )
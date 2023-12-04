import pytest
from app.schema.schema import UserBusinessEntity
from app.database.postgres.exceptions.custom_postgres_exceptions import (
    PostgreSQLDatabaseError,
    PostgreSQLIntegrityError,
    PostgreSQLNotFoundError
    )
from sqlalchemy.exc import (
    IntegrityError, 
    DatabaseError
    )
from app.database.postgres.repositories.user_business_entity_repository import UserBusinessEntityPostgresRepository

# UserBusinessEntityPostgresRepository.create_user_business_entity()

@pytest.mark.asyncio
async def test_create_user_business_entity_success(
    mock_postgres_async_session, 
    mock_user_business_entity_schema_object,
    mock_jwt_payload_model_object,
    mock_create_user_business_entity_model_object):

    user_business_entity_postgres_repository = UserBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = mock_user_business_entity_schema_object
    user_business_entity = await user_business_entity_postgres_repository.create_user_business_entity(
        mock_jwt_payload_model_object.id,
        mock_create_user_business_entity_model_object
        )
    
    assert isinstance(user_business_entity, UserBusinessEntity)

@pytest.mark.asyncio
async def test_create_user_business_entity_integrity_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_create_user_business_entity_model_object):

    user_business_entity_postgres_repository = UserBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = IntegrityError('Integrity error', {}, None)
    
    with pytest.raises(PostgreSQLIntegrityError):
        await user_business_entity_postgres_repository.create_user_business_entity(
            mock_jwt_payload_model_object.id,
            mock_create_user_business_entity_model_object)
        
@pytest.mark.asyncio
async def test_create_user_business_entity_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_create_user_business_entity_model_object):

    user_business_entity_postgres_repository = UserBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)
    
    with pytest.raises(PostgreSQLDatabaseError):
        await user_business_entity_postgres_repository.create_user_business_entity(
            mock_jwt_payload_model_object.id,
            mock_create_user_business_entity_model_object)

# UserBusinessEntityPostgresRepository.is_user_business_entity_unique()

@pytest.mark.asyncio
async def test_is_user_business_entity_unique_success(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_create_user_business_entity_model_object
):
    user_business_entity_postgres_repository = UserBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = None

    is_unique = await user_business_entity_postgres_repository.is_user_business_entity_unique(
        mock_jwt_payload_model_object.id,
        mock_create_user_business_entity_model_object
        )
    
    assert isinstance(is_unique, bool)
    assert is_unique == True

@pytest.mark.asyncio
async def test_is_user_business_entity_unique_not_unique_error(
    mock_postgres_async_session, 
    mock_user_business_entity_schema_object,
    mock_jwt_payload_model_object,
    mock_create_user_business_entity_model_object
):
    user_business_entity_postgres_repository = UserBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = mock_user_business_entity_schema_object

    is_unique = await user_business_entity_postgres_repository.is_user_business_entity_unique(
        mock_jwt_payload_model_object.id,
        mock_create_user_business_entity_model_object
        )
    
    assert isinstance(is_unique, bool)
    assert is_unique == False

@pytest.mark.asyncio
async def test_is_user_business_entity_unique_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_create_user_business_entity_model_object
):
    user_business_entity_postgres_repository = UserBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)
    
    with pytest.raises(PostgreSQLDatabaseError):
        await user_business_entity_postgres_repository.is_user_business_entity_unique(
        mock_jwt_payload_model_object.id,
        mock_create_user_business_entity_model_object
        )

# UserBusinessEntityPostgresRepository.update_user_business_entity()

@pytest.mark.asyncio
async def test_update_user_business_entity_success(
    mock_postgres_async_session, 
    mock_user_business_entity_schema_object,
    mock_jwt_payload_model_object,
    mock_update_user_business_entity_model_object):

    user_business_entity_postgres_repository = UserBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = mock_user_business_entity_schema_object
    user_business_entity = await user_business_entity_postgres_repository.update_user_business_entity(
        mock_jwt_payload_model_object.id,
        mock_update_user_business_entity_model_object
        )
    
    assert isinstance(user_business_entity, UserBusinessEntity)

@pytest.mark.asyncio
async def test_update_user_business_entity_not_found_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_update_user_business_entity_model_object):

    user_business_entity_postgres_repository = UserBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = None
    
    with pytest.raises(PostgreSQLNotFoundError):
        await user_business_entity_postgres_repository.update_user_business_entity(
            mock_jwt_payload_model_object.id,
            mock_update_user_business_entity_model_object)
        
@pytest.mark.asyncio
async def test_update_user_business_entity_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_update_user_business_entity_model_object):

    user_business_entity_postgres_repository = UserBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)
    
    with pytest.raises(PostgreSQLDatabaseError):
        await user_business_entity_postgres_repository.update_user_business_entity(
            mock_jwt_payload_model_object.id,
            mock_update_user_business_entity_model_object)
        
# UserBusinessEntityPostgresRepository.is_user_business_entity_unique_beside_one_to_update()

@pytest.mark.asyncio
async def test_is_user_business_entity_unique_beside_one_to_update_success(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_update_user_business_entity_model_object
):
    user_business_entity_postgres_repository = UserBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = None

    is_unique = await user_business_entity_postgres_repository.is_user_business_entity_unique_beside_one_to_update(
        mock_jwt_payload_model_object.id,
        mock_update_user_business_entity_model_object
        )
    
    assert isinstance(is_unique, bool)
    assert is_unique == True

@pytest.mark.asyncio
async def test_is_user_business_entity_unique_beside_one_to_update_not_unique_error(
    mock_postgres_async_session, 
    mock_user_business_entity_schema_object,
    mock_jwt_payload_model_object,
    mock_update_user_business_entity_model_object
):
    user_business_entity_postgres_repository = UserBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = mock_user_business_entity_schema_object

    is_unique = await user_business_entity_postgres_repository.is_user_business_entity_unique_beside_one_to_update(
        mock_jwt_payload_model_object.id,
        mock_update_user_business_entity_model_object
        )
    
    assert isinstance(is_unique, bool)
    assert is_unique == False

@pytest.mark.asyncio
async def test_is_user_business_entity_unique_beside_one_to_update_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_update_user_business_entity_model_object
):
    user_business_entity_postgres_repository = UserBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)
    
    with pytest.raises(PostgreSQLDatabaseError):
        await user_business_entity_postgres_repository.is_user_business_entity_unique_beside_one_to_update(
        mock_jwt_payload_model_object.id,
        mock_update_user_business_entity_model_object
        )

# UserBusinessEntityPostgresRepository.remove_user_business_entity()

@pytest.mark.asyncio
async def test_remove_user_business_entity_success(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_user_business_entity_model_object):

    user_business_entity_postgres_repository = UserBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.execute.return_value.rowcount = 1
    result = await user_business_entity_postgres_repository.remove_user_business_entity(
        mock_jwt_payload_model_object.id,
        mock_user_business_entity_model_object.id
        )
    
    assert isinstance(result, bool)
    assert result == True

@pytest.mark.asyncio
async def test_remove_user_business_entity_not_deleted(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_user_business_entity_model_object):

    user_business_entity_postgres_repository = UserBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.execute.return_value.rowcount = 0
    result = await user_business_entity_postgres_repository.remove_user_business_entity(
        mock_jwt_payload_model_object.id,
        mock_user_business_entity_model_object.id
        )
    
    assert isinstance(result, bool)
    assert result == False

@pytest.mark.asyncio
async def test_remove_user_business_entity_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_user_business_entity_model_object):

    user_business_entity_postgres_repository = UserBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.execute.side_effect = DatabaseError('Database error', {}, None)
    
    with pytest.raises(PostgreSQLDatabaseError):
        await user_business_entity_postgres_repository.remove_user_business_entity(
        mock_jwt_payload_model_object.id,
        mock_user_business_entity_model_object.id
        )

# UserBusinessEntityPostgresRepository.get_user_business_entity()

@pytest.mark.asyncio
async def test_get_user_business_entity_success(
    mock_postgres_async_session, 
    mock_user_business_entity_schema_object,
    mock_jwt_payload_model_object,
    mock_user_business_entity_model_object):

    user_business_entity_postgres_repository = UserBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = mock_user_business_entity_schema_object
    user_business_entity = await user_business_entity_postgres_repository.get_user_business_entity(
        mock_jwt_payload_model_object.id,
        mock_user_business_entity_model_object.id
        )
    
    assert isinstance(user_business_entity, UserBusinessEntity)

@pytest.mark.asyncio
async def test_get_user_business_entity_not_found_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_user_business_entity_model_object):

    user_business_entity_postgres_repository = UserBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = None
    
    with pytest.raises(PostgreSQLNotFoundError):
        await user_business_entity_postgres_repository.get_user_business_entity(
        mock_jwt_payload_model_object.id,
        mock_user_business_entity_model_object.id
        )

@pytest.mark.asyncio
async def test_get_user_business_entity_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_user_business_entity_model_object):

    user_business_entity_postgres_repository = UserBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)
    
    with pytest.raises(PostgreSQLDatabaseError):
        await user_business_entity_postgres_repository.get_user_business_entity(
        mock_jwt_payload_model_object.id,
        mock_user_business_entity_model_object.id
        )

# UserBusinessEntityPostgresRepository.get_all_user_business_entities()

@pytest.mark.asyncio
async def test_get_all_user_business_entities_success(
    mock_postgres_async_session, 
    mock_user_business_entity_schema_object,
    mock_jwt_payload_model_object):

    user_business_entity_postgres_repository = UserBusinessEntityPostgresRepository(mock_postgres_async_session)
    
    mock_postgres_async_session.scalars.return_value = [
        mock_user_business_entity_schema_object,
        mock_user_business_entity_schema_object,
    ]

    user_business_entities = await user_business_entity_postgres_repository.get_all_user_business_entities(
        mock_jwt_payload_model_object.id
        )
    
    assert isinstance(user_business_entities, list)

@pytest.mark.asyncio
async def test_get_all_user_business_entities_not_found_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object):

    user_business_entity_postgres_repository = UserBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalars.return_value = []
    
    with pytest.raises(PostgreSQLNotFoundError):
        await user_business_entity_postgres_repository.get_all_user_business_entities(
        mock_jwt_payload_model_object.id
        )

@pytest.mark.asyncio
async def test_get_all_user_business_entities_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object):

    user_business_entity_postgres_repository = UserBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalars.side_effect = DatabaseError('Database error', {}, None)
    
    with pytest.raises(PostgreSQLDatabaseError):
        await user_business_entity_postgres_repository.get_all_user_business_entities(
        mock_jwt_payload_model_object.id
        )
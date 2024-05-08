import pytest
from unittest.mock import Mock
from app.schema.schema import ExternalBusinessEntity
from app.database.postgres.exceptions.custom_postgres_exceptions import (
    PostgreSQLDatabaseError,
    PostgreSQLIntegrityError,
    PostgreSQLNotFoundError
    )
from sqlalchemy.exc import (
    IntegrityError, 
    DatabaseError
    )
from app.database.postgres.repositories.external_business_entity_repository import ExternalBusinessEntityPostgresRepository

# ExternalBusinessEntityPostgresRepository.create_external_business_entity()

@pytest.mark.asyncio
async def test_create_external_business_entity_success(
    mock_postgres_async_session, 
    mock_external_business_entity_schema_object,
    mock_jwt_payload_model_object,
    mock_create_external_business_entity_model_object):

    external_business_entity_postgres_repository = ExternalBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = mock_external_business_entity_schema_object
    external_business_entity = await external_business_entity_postgres_repository.create_external_business_entity(
        mock_jwt_payload_model_object.id,
        mock_create_external_business_entity_model_object
        )
    
    assert isinstance(external_business_entity, ExternalBusinessEntity)

@pytest.mark.asyncio
async def test_create_external_business_entity_integrity_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_create_external_business_entity_model_object):

    external_business_entity_postgres_repository = ExternalBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = IntegrityError('Integrity error', {}, None)
    
    with pytest.raises(PostgreSQLIntegrityError):
        await external_business_entity_postgres_repository.create_external_business_entity(
            mock_jwt_payload_model_object.id,
            mock_create_external_business_entity_model_object)
        
@pytest.mark.asyncio
async def test_create_external_business_entity_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_create_external_business_entity_model_object):

    external_business_entity_postgres_repository = ExternalBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)
    
    with pytest.raises(PostgreSQLDatabaseError):
        await external_business_entity_postgres_repository.create_external_business_entity(
            mock_jwt_payload_model_object.id,
            mock_create_external_business_entity_model_object)

# ExternalBusinessEntityPostgresRepository.is_external_business_entity_unique()

@pytest.mark.asyncio
async def test_is_external_business_entity_unique_success(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_create_external_business_entity_model_object
):
    external_business_entity_postgres_repository = ExternalBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = None

    is_unique = await external_business_entity_postgres_repository.is_external_business_entity_unique(
        mock_jwt_payload_model_object.id,
        mock_create_external_business_entity_model_object
        )
    
    assert isinstance(is_unique, bool)
    assert is_unique == True

@pytest.mark.asyncio
async def test_is_external_business_entity_unique_not_unique_error(
    mock_postgres_async_session, 
    mock_external_business_entity_schema_object,
    mock_jwt_payload_model_object,
    mock_create_external_business_entity_model_object
):
    external_business_entity_postgres_repository = ExternalBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = mock_external_business_entity_schema_object

    is_unique = await external_business_entity_postgres_repository.is_external_business_entity_unique(
        mock_jwt_payload_model_object.id,
        mock_create_external_business_entity_model_object
        )
    
    assert isinstance(is_unique, bool)
    assert is_unique == False

@pytest.mark.asyncio
async def test_is_external_business_entity_unique_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_create_external_business_entity_model_object
):
    external_business_entity_postgres_repository = ExternalBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)
    
    with pytest.raises(PostgreSQLDatabaseError):
        await external_business_entity_postgres_repository.is_external_business_entity_unique(
        mock_jwt_payload_model_object.id,
        mock_create_external_business_entity_model_object
        )

# ExternalBusinessEntityPostgresRepository.update_external_business_entity()

@pytest.mark.asyncio
async def test_update_external_business_entity_success(
    mock_postgres_async_session, 
    mock_external_business_entity_schema_object,
    mock_jwt_payload_model_object,
    mock_update_external_business_entity_model_object):

    external_business_entity_postgres_repository = ExternalBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = mock_external_business_entity_schema_object
    external_business_entity = await external_business_entity_postgres_repository.update_external_business_entity(
        mock_jwt_payload_model_object.id,
        mock_update_external_business_entity_model_object
        )
    
    assert isinstance(external_business_entity, ExternalBusinessEntity)

@pytest.mark.asyncio
async def test_update_external_business_entity_not_found_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_update_external_business_entity_model_object):

    external_business_entity_postgres_repository = ExternalBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = None
    
    with pytest.raises(PostgreSQLNotFoundError):
        await external_business_entity_postgres_repository.update_external_business_entity(
            mock_jwt_payload_model_object.id,
            mock_update_external_business_entity_model_object)
        
@pytest.mark.asyncio
async def test_update_external_business_entity_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_update_external_business_entity_model_object):

    external_business_entity_postgres_repository = ExternalBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)
    
    with pytest.raises(PostgreSQLDatabaseError):
        await external_business_entity_postgres_repository.update_external_business_entity(
            mock_jwt_payload_model_object.id,
            mock_update_external_business_entity_model_object)
        
# ExternalBusinessEntityPostgresRepository.is_external_business_entity_unique_beside_one_to_update()

@pytest.mark.asyncio
async def test_is_external_business_entity_unique_beside_one_to_update_success(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_update_external_business_entity_model_object
):
    external_business_entity_postgres_repository = ExternalBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = None

    is_unique = await external_business_entity_postgres_repository.is_external_business_entity_unique_beside_one_to_update(
        mock_jwt_payload_model_object.id,
        mock_update_external_business_entity_model_object
        )
    
    assert isinstance(is_unique, bool)
    assert is_unique == True

@pytest.mark.asyncio
async def test_is_external_business_entity_unique_beside_one_to_update_not_unique_error(
    mock_postgres_async_session, 
    mock_external_business_entity_schema_object,
    mock_jwt_payload_model_object,
    mock_update_external_business_entity_model_object
):
    external_business_entity_postgres_repository = ExternalBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = mock_external_business_entity_schema_object

    is_unique = await external_business_entity_postgres_repository.is_external_business_entity_unique_beside_one_to_update(
        mock_jwt_payload_model_object.id,
        mock_update_external_business_entity_model_object
        )
    
    assert isinstance(is_unique, bool)
    assert is_unique == False

@pytest.mark.asyncio
async def test_is_external_business_entity_unique_beside_one_to_update_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_update_external_business_entity_model_object
):
    external_business_entity_postgres_repository = ExternalBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)
    
    with pytest.raises(PostgreSQLDatabaseError):
        await external_business_entity_postgres_repository.is_external_business_entity_unique_beside_one_to_update(
        mock_jwt_payload_model_object.id,
        mock_update_external_business_entity_model_object
        )

# ExternalBusinessEntityPostgresRepository.remove_external_business_entity()

@pytest.mark.asyncio
async def test_remove_external_business_entity_success(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_external_business_entity_model_object):

    external_business_entity_postgres_repository = ExternalBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.execute.return_value.rowcount = 1
    result = await external_business_entity_postgres_repository.remove_external_business_entity(
        mock_jwt_payload_model_object.id,
        mock_external_business_entity_model_object.id
        )
    
    assert isinstance(result, bool)
    assert result == True

@pytest.mark.asyncio
async def test_remove_external_business_entity_not_deleted(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_external_business_entity_model_object):

    external_business_entity_postgres_repository = ExternalBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.execute.return_value.rowcount = 0
    result = await external_business_entity_postgres_repository.remove_external_business_entity(
        mock_jwt_payload_model_object.id,
        mock_external_business_entity_model_object.id
        )
    
    assert isinstance(result, bool)
    assert result == False

@pytest.mark.asyncio
async def test_remove_external_business_entity_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_external_business_entity_model_object):

    external_business_entity_postgres_repository = ExternalBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.execute.side_effect = DatabaseError('Database error', {}, None)
    
    with pytest.raises(PostgreSQLDatabaseError):
        await external_business_entity_postgres_repository.remove_external_business_entity(
        mock_jwt_payload_model_object.id,
        mock_external_business_entity_model_object.id
        )

# ExternalBusinessEntityPostgresRepository.get_external_business_entity()

@pytest.mark.asyncio
async def test_get_external_business_entity_success(
    mock_postgres_async_session, 
    mock_external_business_entity_schema_object,
    mock_jwt_payload_model_object,
    mock_external_business_entity_model_object):

    external_business_entity_postgres_repository = ExternalBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = mock_external_business_entity_schema_object
    external_business_entity = await external_business_entity_postgres_repository.get_external_business_entity(
        mock_jwt_payload_model_object.id,
        mock_external_business_entity_model_object.id
        )
    
    assert isinstance(external_business_entity, ExternalBusinessEntity)

@pytest.mark.asyncio
async def test_get_external_business_entity_not_found_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_external_business_entity_model_object):

    external_business_entity_postgres_repository = ExternalBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = None
    
    with pytest.raises(PostgreSQLNotFoundError):
        await external_business_entity_postgres_repository.get_external_business_entity(
        mock_jwt_payload_model_object.id,
        mock_external_business_entity_model_object.id
        )

@pytest.mark.asyncio
async def test_get_external_business_entity_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_external_business_entity_model_object):

    external_business_entity_postgres_repository = ExternalBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)
    
    with pytest.raises(PostgreSQLDatabaseError):
        await external_business_entity_postgres_repository.get_external_business_entity(
        mock_jwt_payload_model_object.id,
        mock_external_business_entity_model_object.id
        )

# ExternalBusinessEntityPostgresRepository.get_all_external_business_entities()

@pytest.mark.asyncio
async def test_get_all_external_business_entities_success(
    mock_postgres_async_session, 
    mock_external_business_entity_schema_object,
    mock_jwt_payload_model_object):

    external_business_entity_postgres_repository = ExternalBusinessEntityPostgresRepository(mock_postgres_async_session)
    scalar_result = Mock()
    scalar_result.all.return_value = [
        mock_external_business_entity_schema_object,
        mock_external_business_entity_schema_object,
    ]
    mock_postgres_async_session.scalars.return_value = scalar_result

    external_business_entities = await external_business_entity_postgres_repository.get_all_external_business_entities(
        mock_jwt_payload_model_object.id
        )
    
    assert isinstance(external_business_entities, list)

@pytest.mark.asyncio
async def test_get_all_external_business_entities_not_found_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object):

    external_business_entity_postgres_repository = ExternalBusinessEntityPostgresRepository(mock_postgres_async_session)

    scalar_result = Mock()
    scalar_result.all.return_value = []
    mock_postgres_async_session.scalars.return_value = scalar_result
    
    with pytest.raises(PostgreSQLNotFoundError):
        await external_business_entity_postgres_repository.get_all_external_business_entities(
        mock_jwt_payload_model_object.id
        )

@pytest.mark.asyncio
async def test_get_all_external_business_entities_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object):

    external_business_entity_postgres_repository = ExternalBusinessEntityPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalars.side_effect = DatabaseError('Database error', {}, None)
    
    with pytest.raises(PostgreSQLDatabaseError):
        await external_business_entity_postgres_repository.get_all_external_business_entities(
        mock_jwt_payload_model_object.id
        )
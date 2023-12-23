import pytest
from app.schema.schema import InvoiceItem
from app.database.postgres.exceptions.custom_postgres_exceptions import (
    PostgreSQLDatabaseError,
    PostgreSQLIntegrityError,
    PostgreSQLNotFoundError
    )
from sqlalchemy.exc import (
    IntegrityError, 
    DatabaseError
    )
from sqlalchemy import ScalarResult
from app.database.postgres.repositories.invoice_item_repository import InvoiceItemPostgresRepository

@pytest.mark.asyncio
async def test_create_invoice_item_success(
    mock_postgres_async_session, 
    mock_invoice_item_schema_object,
    mock_jwt_payload_model_object,
    mock_create_invoice_item_model_object,
    mock_invoice_model_object):

    invoice_item_postgres_repository = InvoiceItemPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = mock_invoice_item_schema_object
    invoice_item = await invoice_item_postgres_repository.create_invoice_item(
        mock_jwt_payload_model_object.id,
        mock_invoice_model_object.id,
        mock_create_invoice_item_model_object
        )
    
    assert isinstance(invoice_item, InvoiceItem)

@pytest.mark.asyncio
async def test_create_invoice_item_integrity_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_create_invoice_item_model_object,
    mock_invoice_model_object):

    invoice_item_postgres_repository = InvoiceItemPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = IntegrityError('Integrity error', {}, None)
    
    with pytest.raises(PostgreSQLIntegrityError):
        await invoice_item_postgres_repository.create_invoice_item(
        mock_jwt_payload_model_object.id,
        mock_invoice_model_object.id,
        mock_create_invoice_item_model_object
        )

@pytest.mark.asyncio
async def test_create_invoice_item_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_create_invoice_item_model_object,
    mock_invoice_model_object):

    invoice_item_postgres_repository = InvoiceItemPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)
    
    with pytest.raises(PostgreSQLDatabaseError):
        await invoice_item_postgres_repository.create_invoice_item(
        mock_jwt_payload_model_object.id,
        mock_invoice_model_object.id,
        mock_create_invoice_item_model_object
        )

@pytest.mark.asyncio
async def test_get_invoice_item_success(
    mock_postgres_async_session, 
    mock_invoice_item_schema_object,
    mock_jwt_payload_model_object,
    mock_invoice_item_model_object):

    invoice_item_postgres_repository = InvoiceItemPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = mock_invoice_item_schema_object
    invoice_item = await invoice_item_postgres_repository.get_invoice_item(
        mock_jwt_payload_model_object.id,
        mock_invoice_item_model_object.id
    )
    
    assert isinstance(invoice_item, InvoiceItem)

@pytest.mark.asyncio
async def test_get_invoice_item_not_found_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_invoice_item_model_object):

    invoice_item_postgres_repository = InvoiceItemPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = None
    
    with pytest.raises(PostgreSQLNotFoundError):
        await invoice_item_postgres_repository.get_invoice_item(
        mock_jwt_payload_model_object.id,
        mock_invoice_item_model_object.id
    )

@pytest.mark.asyncio
async def test_get_invoice_item_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_invoice_item_model_object):

    invoice_item_postgres_repository = InvoiceItemPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)
    
    with pytest.raises(PostgreSQLDatabaseError):
        await invoice_item_postgres_repository.get_invoice_item(
        mock_jwt_payload_model_object.id,
        mock_invoice_item_model_object.id
    )
        
@pytest.mark.asyncio
async def test_get_invoice_item_by_invoice_id_success(
    mock_postgres_async_session, 
    mock_invoice_item_schema_object,
    mock_jwt_payload_model_object,
    mock_invoice_model_object):

    invoice_item_postgres_repository = InvoiceItemPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalars.return_value = [mock_invoice_item_schema_object]
    invoice_item = await invoice_item_postgres_repository.get_invoice_items_by_invoice_id(
        mock_jwt_payload_model_object.id,
        mock_invoice_model_object.id,
        False
    )
    assert isinstance(invoice_item, list)

@pytest.mark.asyncio
async def test_get_invoice_item_by_invoice_id_not_found_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_invoice_model_object):

    invoice_item_postgres_repository = InvoiceItemPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalars.return_value = []

    with pytest.raises(PostgreSQLNotFoundError):
        await invoice_item_postgres_repository.get_invoice_items_by_invoice_id(
            mock_jwt_payload_model_object.id,
            mock_invoice_model_object.id,
            False
        )
    
@pytest.mark.asyncio
async def test_get_invoice_item_by_invoice_id_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_invoice_model_object):

    invoice_item_postgres_repository = InvoiceItemPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalars.side_effect = DatabaseError('Database error', {}, None)

    with pytest.raises(PostgreSQLDatabaseError):
        await invoice_item_postgres_repository.get_invoice_items_by_invoice_id(
            mock_jwt_payload_model_object.id,
            mock_invoice_model_object.id,
            False
        )

@pytest.mark.asyncio
async def test_update_invoice_item_success(
    mock_postgres_async_session, 
    mock_invoice_item_schema_object,
    mock_jwt_payload_model_object,
    mock_update_invoice_item_model_object):

    invoice_item_postgres_repository = InvoiceItemPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = mock_invoice_item_schema_object
    await invoice_item_postgres_repository.update_invoice_item(
        mock_jwt_payload_model_object.id,
        mock_update_invoice_item_model_object
    )

@pytest.mark.asyncio
async def test_update_invoice_item_not_found_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_update_invoice_item_model_object):

    invoice_item_postgres_repository = InvoiceItemPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = None

    with pytest.raises(PostgreSQLNotFoundError):
        await invoice_item_postgres_repository.update_invoice_item(
            mock_jwt_payload_model_object.id,
            mock_update_invoice_item_model_object
        )

@pytest.mark.asyncio
async def test_update_invoice_item_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_update_invoice_item_model_object):

    invoice_item_postgres_repository = InvoiceItemPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)

    with pytest.raises(PostgreSQLDatabaseError):
        await invoice_item_postgres_repository.update_invoice_item(
            mock_jwt_payload_model_object.id,
            mock_update_invoice_item_model_object
        )

@pytest.mark.asyncio
async def test_update_invoice_item_in_trash_status_success(
    mock_postgres_async_session, 
    mock_invoice_item_schema_object,
    mock_jwt_payload_model_object,
    mock_invoice_item_model_object):

    invoice_item_postgres_repository = InvoiceItemPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = mock_invoice_item_schema_object
    await invoice_item_postgres_repository.update_invoice_item_in_trash_status(
        mock_jwt_payload_model_object.id,
        mock_invoice_item_model_object.id,
        True
    )

@pytest.mark.asyncio
async def test_update_invoice_item_in_trash_status_not_found_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_invoice_item_model_object):

    invoice_item_postgres_repository = InvoiceItemPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = None

    with pytest.raises(PostgreSQLNotFoundError):
        await invoice_item_postgres_repository.update_invoice_item_in_trash_status(
            mock_jwt_payload_model_object.id,
            mock_invoice_item_model_object.id,
            True
        )

@pytest.mark.asyncio
async def test_update_invoice_item_in_trash_status_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_invoice_item_model_object):

    invoice_item_postgres_repository = InvoiceItemPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)

    with pytest.raises(PostgreSQLDatabaseError):
        await invoice_item_postgres_repository.update_invoice_item_in_trash_status(
            mock_jwt_payload_model_object.id,
            mock_invoice_item_model_object.id,
            True
        )

@pytest.mark.asyncio
async def test_update_all_invoice_items_in_trash_status_by_invoice_id_success(
    mock_postgres_async_session, 
    mock_invoice_item_schema_object,
    mock_jwt_payload_model_object,
    mock_invoice_model_object):

    invoice_item_postgres_repository = InvoiceItemPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.execute.return_value = mock_invoice_item_schema_object
    await invoice_item_postgres_repository.update_all_invoice_items_in_trash_status_by_invoice_id(
        mock_jwt_payload_model_object.id,
        mock_invoice_model_object.id,
        True
    )


@pytest.mark.asyncio
async def test_update_all_invoice_items_in_trash_status_by_invoice_id_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_invoice_model_object):

    invoice_item_postgres_repository = InvoiceItemPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.execute.side_effect = DatabaseError('Database error', {}, None)

    with pytest.raises(PostgreSQLDatabaseError):
        await invoice_item_postgres_repository.update_all_invoice_items_in_trash_status_by_invoice_id(
            mock_jwt_payload_model_object.id,
            mock_invoice_model_object.id,
            True
        )


@pytest.mark.asyncio
async def test_remove_invoice_item_success(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_invoice_item_model_object):

    invoice_item_postgres_repository = InvoiceItemPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.execute.return_value.rowcount = 1
    await invoice_item_postgres_repository.remove_invoice_item(
        mock_jwt_payload_model_object.id,
        mock_invoice_item_model_object.id
    )


@pytest.mark.asyncio
async def test_remove_invoice_item_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_invoice_item_model_object):

    invoice_item_postgres_repository = InvoiceItemPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.execute.side_effect = DatabaseError('Database error', {}, None)

    with pytest.raises(PostgreSQLDatabaseError):
        await invoice_item_postgres_repository.remove_invoice_item(
            mock_jwt_payload_model_object.id,
            mock_invoice_item_model_object.id
        )
import pytest
from app.schema.schema import Invoice
from app.database.postgres.exceptions.custom_postgres_exceptions import (
    PostgreSQLDatabaseError,
    PostgreSQLIntegrityError,
    PostgreSQLNotFoundError
    )
from sqlalchemy.exc import (
    IntegrityError, 
    DatabaseError
    )
from app.database.postgres.repositories.invoice_repository import InvoicePostgresRepository

@pytest.mark.asyncio
async def test_create_invoice_success(
    mock_postgres_async_session, 
    mock_invoice_schema_object,
    mock_jwt_payload_model_object,
    mock_create_invoice_model_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = mock_invoice_schema_object
    invoice = await invoice_postgres_repository.create_invoice(
        mock_jwt_payload_model_object.id,
        mock_create_invoice_model_object
        )
    
    assert isinstance(invoice, Invoice)

@pytest.mark.asyncio
async def test_create_invoice_integrity_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_create_invoice_model_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = IntegrityError('Integrity error', {}, None)
    
    with pytest.raises(PostgreSQLIntegrityError):
        await invoice_postgres_repository.create_invoice(
        mock_jwt_payload_model_object.id,
        mock_create_invoice_model_object
        )

@pytest.mark.asyncio
async def test_create_invoice_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_create_invoice_model_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)
    
    with pytest.raises(PostgreSQLDatabaseError):
        await invoice_postgres_repository.create_invoice(
        mock_jwt_payload_model_object.id,
        mock_create_invoice_model_object
        )

@pytest.mark.asyncio
async def test_get_invoice_success(
    mock_postgres_async_session, 
    mock_invoice_schema_object,
    mock_jwt_payload_model_object,
    mock_invoice_model_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = mock_invoice_schema_object
    invoice = await invoice_postgres_repository.get_invoice(
        mock_jwt_payload_model_object.id,
        mock_invoice_model_object.id
        )
    
    assert isinstance(invoice, Invoice)

@pytest.mark.asyncio
async def test_get_invoice_not_found_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_invoice_model_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = None
    
    with pytest.raises(PostgreSQLNotFoundError):
        await invoice_postgres_repository.get_invoice(
        mock_jwt_payload_model_object.id,
        mock_invoice_model_object.id
        )

@pytest.mark.asyncio
async def test_get_invoice_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_invoice_model_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)
    
    with pytest.raises(PostgreSQLDatabaseError):
        await invoice_postgres_repository.get_invoice(
        mock_jwt_payload_model_object.id,
        mock_invoice_model_object.id
        )

@pytest.mark.asyncio
async def test_get_all_invoices_success(
    mock_postgres_async_session, 
    mock_invoice_schema_object,
    mock_jwt_payload_model_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalars.return_value = [mock_invoice_schema_object]
    invoice_list = await invoice_postgres_repository.get_all_invoices(
        mock_jwt_payload_model_object.id,
    )
    
    assert isinstance(invoice_list, list)

@pytest.mark.asyncio
async def test_get_all_invoices_not_found_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)

    mock_postgres_async_session.scalars.return_value = []

    with pytest.raises(PostgreSQLNotFoundError):
        await invoice_postgres_repository.get_all_invoices(
        mock_jwt_payload_model_object.id,
    )
        
@pytest.mark.asyncio
async def test_get_all_invoices_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)

    mock_postgres_async_session.scalars.side_effect = DatabaseError('Database error', {}, None)

    with pytest.raises(PostgreSQLDatabaseError):
        await invoice_postgres_repository.get_all_invoices(
        mock_jwt_payload_model_object.id
    )
        
@pytest.mark.asyncio
async def test_update_invoice_success(
    mock_postgres_async_session, 
    mock_invoice_schema_object,
    mock_jwt_payload_model_object,
    mock_update_invoice_model_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = mock_invoice_schema_object
    await invoice_postgres_repository.update_invoice(
        mock_jwt_payload_model_object.id,
        mock_update_invoice_model_object
        )
    
@pytest.mark.asyncio
async def test_update_invoice_not_found_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_update_invoice_model_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = None
    
    with pytest.raises(PostgreSQLNotFoundError):
        await invoice_postgres_repository.update_invoice(
        mock_jwt_payload_model_object.id,
        mock_update_invoice_model_object
        )

@pytest.mark.asyncio
async def test_update_invoice_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_update_invoice_model_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)
    
    with pytest.raises(PostgreSQLDatabaseError):
        await invoice_postgres_repository.update_invoice(
        mock_jwt_payload_model_object.id,
        mock_update_invoice_model_object
        )


@pytest.mark.asyncio
async def test_update_invoice_in_trash_status_success(
    mock_postgres_async_session, 
    mock_invoice_schema_object,
    mock_jwt_payload_model_object,
    mock_invoice_model_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = mock_invoice_schema_object
    await invoice_postgres_repository.update_invoice_in_trash_status(
        mock_jwt_payload_model_object.id,
        mock_invoice_model_object.id,
        in_trash=True
        )

    
@pytest.mark.asyncio
async def test_update_invoice_in_trash_status_not_found_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_invoice_model_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = None
    
    with pytest.raises(PostgreSQLNotFoundError):
        await invoice_postgres_repository.update_invoice_in_trash_status(
        mock_jwt_payload_model_object.id,
        mock_invoice_model_object.id,
        in_trash=True
        )

@pytest.mark.asyncio
async def test_update_invoice_in_trash_status_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_invoice_model_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)
    
    with pytest.raises(PostgreSQLDatabaseError):
        await invoice_postgres_repository.update_invoice_in_trash_status(
        mock_jwt_payload_model_object.id,
        mock_invoice_model_object.id,
        in_trash=True
        )

@pytest.mark.asyncio
async def test_remove_invoice_success(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_create_invoice_model_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.execute.return_value.rowcount = 1
    result = await invoice_postgres_repository.remove_invoice(
        mock_jwt_payload_model_object.id,
        mock_create_invoice_model_object.id
    )
    
    assert isinstance(result, bool)
    assert result == True

@pytest.mark.asyncio
async def test_remove_invoice_not_found_result(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_create_invoice_model_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.execute.return_value.rowcount = 0
    result = await invoice_postgres_repository.remove_invoice(
        mock_jwt_payload_model_object.id,
        mock_create_invoice_model_object.id
    )
    
    assert isinstance(result, bool)
    assert result == False

@pytest.mark.asyncio
async def test_remove_invoice_database_error_result(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_create_invoice_model_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.execute.side_effect = DatabaseError('Database error', {}, None)

    with pytest.raises(PostgreSQLDatabaseError):
        await invoice_postgres_repository.remove_invoice(
            mock_jwt_payload_model_object.id,
            mock_create_invoice_model_object.id
        )

@pytest.mark.asyncio
async def test_is_invoice_unique_success(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_create_invoice_model_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = None
    result = await invoice_postgres_repository.is_invoice_unique(
        mock_jwt_payload_model_object.id,
        mock_create_invoice_model_object
    )
    
    assert isinstance(result, bool)
    assert result == True

@pytest.mark.asyncio
async def test_is_invoice_unique_not_unique_result(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_create_invoice_model_object,
    mock_invoice_schema_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = mock_invoice_schema_object
    result = await invoice_postgres_repository.is_invoice_unique(
        mock_jwt_payload_model_object.id,
        mock_create_invoice_model_object
    )
    
    assert isinstance(result, bool)
    assert result == False

@pytest.mark.asyncio
async def test_is_invoice_unique_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_create_invoice_model_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)
    
    with pytest.raises(PostgreSQLDatabaseError):
        await invoice_postgres_repository.is_invoice_unique(
            mock_jwt_payload_model_object.id,
            mock_create_invoice_model_object
        )

@pytest.mark.asyncio
async def test_is_invoice_unique_beside_one_to_update_success(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_update_invoice_model_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = None
    result = await invoice_postgres_repository.is_invoice_unique_beside_one_to_update(
        mock_jwt_payload_model_object.id,
        mock_update_invoice_model_object
    )
    
    assert isinstance(result, bool)
    assert result == True

@pytest.mark.asyncio
async def test_is_invoice_unique_beside_one_to_update_not_unique_result(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_update_invoice_model_object,
    mock_invoice_schema_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = mock_invoice_schema_object
    result = await invoice_postgres_repository.is_invoice_unique_beside_one_to_update(
        mock_jwt_payload_model_object.id,
        mock_update_invoice_model_object
    )
    
    assert isinstance(result, bool)
    assert result == False

@pytest.mark.asyncio
async def test_is_invoice_unique_beside_one_to_update_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_update_invoice_model_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)
    
    with pytest.raises(PostgreSQLDatabaseError):
        await invoice_postgres_repository.is_invoice_unique_beside_one_to_update(
            mock_jwt_payload_model_object.id,
            mock_update_invoice_model_object
        )

@pytest.mark.asyncio
async def test_update_invoice_file_success(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_invoice_schema_object,
    mock_invoice_model_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = mock_invoice_schema_object
    await invoice_postgres_repository.update_invoice_file(
        mock_jwt_payload_model_object.id,
        mock_invoice_model_object.id,
        mock_invoice_model_object.invoice_pdf
    )

@pytest.mark.asyncio
async def test_update_invoice_file_not_found_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_invoice_model_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = None

    with pytest.raises(PostgreSQLNotFoundError):
        await invoice_postgres_repository.update_invoice_file(
            mock_jwt_payload_model_object.id,
            mock_invoice_model_object.id,
            mock_invoice_model_object.invoice_pdf
        )

@pytest.mark.asyncio
async def test_update_invoice_file_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_invoice_model_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)

    with pytest.raises(PostgreSQLDatabaseError):
        await invoice_postgres_repository.update_invoice_file(
            mock_jwt_payload_model_object.id,
            mock_invoice_model_object.id,
            mock_invoice_model_object.invoice_pdf
        )


@pytest.mark.asyncio
async def test_remove_invoice_file_success(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_invoice_schema_object,
    mock_invoice_model_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = mock_invoice_schema_object
    await invoice_postgres_repository.remove_invoice_file(
        mock_jwt_payload_model_object.id,
        mock_invoice_model_object.id
    )

@pytest.mark.asyncio
async def test_remove_invoice_file_not_found_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_invoice_model_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = None

    with pytest.raises(PostgreSQLNotFoundError):
        await invoice_postgres_repository.remove_invoice_file(
            mock_jwt_payload_model_object.id,
            mock_invoice_model_object.id
        )

@pytest.mark.asyncio
async def test_remove_invoice_file_database_error(
    mock_postgres_async_session, 
    mock_jwt_payload_model_object,
    mock_invoice_model_object):

    invoice_postgres_repository = InvoicePostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)

    with pytest.raises(PostgreSQLDatabaseError):
        await invoice_postgres_repository.remove_invoice_file(
            mock_jwt_payload_model_object.id,
            mock_invoice_model_object.id
        )
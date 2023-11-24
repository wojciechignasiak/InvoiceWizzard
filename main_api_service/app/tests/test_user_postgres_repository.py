import pytest
from sqlalchemy.exc import (
    IntegrityError, 
    DatabaseError
    )
from app.database.postgres.exceptions.custom_postgres_exceptions import (
    PostgreSQLDatabaseError,
    PostgreSQLIntegrityError,
    PostgreSQLNotFoundError
)
from app.database.postgres.repositories.user_repository import UserPostgresRepository
from app.schema.schema import User

# UserPostgresRepository.create_user()

@pytest.mark.asyncio
async def test_create_user_success(
    mock_postgres_async_session, 
    mock_user_schema_object, 
    mock_create_user_model_object):

    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = mock_user_schema_object
    user = await user_postgres_repository.create_user(mock_create_user_model_object)
    
    assert isinstance(user, User)

@pytest.mark.asyncio
async def test_create_user_integrity_error(
    mock_postgres_async_session,
    mock_create_user_model_object):

    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = IntegrityError('Integrity error', {}, None)
    
    with pytest.raises(PostgreSQLIntegrityError):
        await user_postgres_repository.create_user(mock_create_user_model_object)

@pytest.mark.asyncio
async def test_create_user_database_error(
    mock_postgres_async_session,
    mock_create_user_model_object):

    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)
    
    with pytest.raises(PostgreSQLDatabaseError):
        await user_postgres_repository.create_user(mock_create_user_model_object)

# UserPostgresRepository.get_user_by_id()

@pytest.mark.asyncio
async def test_get_user_by_id_success(
    mock_postgres_async_session,
    mock_user_schema_object):
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = mock_user_schema_object
    user = await user_postgres_repository.get_user_by_id(str(mock_user_schema_object.id))
    
    assert isinstance(user, User)

@pytest.mark.asyncio
async def test_get_user_by_id_not_found(
    mock_postgres_async_session,
    mock_user_schema_object):

    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = None

    with pytest.raises(PostgreSQLNotFoundError):
        await user_postgres_repository.get_user_by_id(str(mock_user_schema_object.id))

@pytest.mark.asyncio
async def test_get_user_by_id_database_error(
    mock_postgres_async_session,
    mock_user_schema_object):

    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)

    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)

    with pytest.raises(PostgreSQLDatabaseError):
        await user_postgres_repository.get_user_by_id(str(mock_user_schema_object.id))

# UserPostgresRepository.get_user_by_email()

@pytest.mark.asyncio
async def test_get_user_by_email_address_success(
    mock_postgres_async_session, 
    mock_user_schema_object):

    mock_postgres_async_session.scalar.return_value = mock_user_schema_object
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    user = await user_postgres_repository.get_user_by_email_address(mock_user_schema_object.email)
    
    assert isinstance(user, User)

@pytest.mark.asyncio
async def test_get_user_by_email_address_not_found(mock_postgres_async_session):
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)

    mock_postgres_async_session.scalar.return_value = None

    with pytest.raises(PostgreSQLNotFoundError):
        await user_postgres_repository.get_user_by_email_address("email@example.com")

@pytest.mark.asyncio
async def test_get_user_by_email_address_database_error(mock_postgres_async_session):

    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)

    with pytest.raises(PostgreSQLDatabaseError):
        await user_postgres_repository.get_user_by_email_address("email@example.com")

# UserPostgresRepository.is_email_address_arleady_taken()

@pytest.mark.asyncio
async def test_is_email_addres_arleady_taken_success(mock_postgres_async_session):

    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = None
    is_email_in_use = await user_postgres_repository.is_email_addres_arleady_taken("email@example.com")
    
    assert isinstance(is_email_in_use, bool)
    assert is_email_in_use == False

@pytest.mark.asyncio
async def test_get_user_by_email_address_database_error(mock_postgres_async_session):

    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)

    with pytest.raises(PostgreSQLDatabaseError):
        await user_postgres_repository.is_email_addres_arleady_taken("email@example.com")

# UserPostgresRepository.update_user_last_login()

@pytest.mark.asyncio
async def test_update_user_last_login_success(
    mock_postgres_async_session, 
    mock_user_schema_object):
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = mock_user_schema_object
    user = await user_postgres_repository.update_user_last_login(str(mock_user_schema_object.id))
    
    assert isinstance(user, User)

@pytest.mark.asyncio
async def test_update_user_last_login_not_found(
    mock_postgres_async_session,
    mock_user_schema_object):

    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = None

    with pytest.raises(PostgreSQLNotFoundError):
        await user_postgres_repository.update_user_last_login(str(mock_user_schema_object.id))

@pytest.mark.asyncio
async def test_update_user_last_login_database_error(
    mock_postgres_async_session,
    mock_user_schema_object):

    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)

    with pytest.raises(PostgreSQLDatabaseError):
        await user_postgres_repository.update_user_last_login(str(mock_user_schema_object.id))

# UserPostgresRepository.update_user_personal_information()

@pytest.mark.asyncio
async def test_update_user_personal_information_success(
    mock_postgres_async_session,
    mock_user_schema_object,
    mock_user_personal_information_model_object):
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = mock_user_schema_object
    user = await user_postgres_repository.update_user_personal_information(
        str(mock_user_schema_object.id), 
        mock_user_personal_information_model_object)
    
    assert isinstance(user, User)

@pytest.mark.asyncio
async def test_update_user_personal_information_not_found(
    mock_postgres_async_session,
    mock_user_schema_object,
    mock_user_personal_information_model_object):
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = None

    with pytest.raises(PostgreSQLNotFoundError):
        await user_postgres_repository.update_user_personal_information(
            str(mock_user_schema_object.id),
            mock_user_personal_information_model_object)
    
@pytest.mark.asyncio
async def test_update_user_personal_information_database_error(
    mock_postgres_async_session,
    mock_user_schema_object,
    mock_user_personal_information_model_object):
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)

    with pytest.raises(PostgreSQLDatabaseError):
        await user_postgres_repository.update_user_personal_information(
            str(mock_user_schema_object.id), 
            mock_user_personal_information_model_object)

# UserPostgresRepository.update_user_email_address()

@pytest.mark.asyncio
async def test_update_user_email_address_success(
    mock_postgres_async_session,
    mock_user_schema_object,
    mock_confirmed_user_email_change_model_object):
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = mock_user_schema_object
    user = await user_postgres_repository.update_user_email_address(mock_confirmed_user_email_change_model_object)
    
    assert isinstance(user, User)

@pytest.mark.asyncio
async def test_update_user_email_address_not_found(
    mock_postgres_async_session,
    mock_confirmed_user_email_change_model_object):
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = None

    with pytest.raises(PostgreSQLNotFoundError):
        await user_postgres_repository.update_user_email_address(mock_confirmed_user_email_change_model_object)

@pytest.mark.asyncio
async def test_update_user_email_address_integrity_error(
    mock_postgres_async_session,
    mock_confirmed_user_email_change_model_object):
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)

    with pytest.raises(PostgreSQLDatabaseError):
        await user_postgres_repository.update_user_email_address(mock_confirmed_user_email_change_model_object)

@pytest.mark.asyncio
async def test_update_user_email_address_database_error(
    mock_postgres_async_session,
    mock_confirmed_user_email_change_model_object):
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)

    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)

    with pytest.raises(PostgreSQLDatabaseError):
        await user_postgres_repository.update_user_email_address(mock_confirmed_user_email_change_model_object)

# UserPostgresRepository.update_user_password()

@pytest.mark.asyncio
async def test_update_update_user_password_success(
    mock_postgres_async_session,
    mock_user_schema_object,
    mock_confirmed_user_password_change_model_object):
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = mock_user_schema_object
    user = await user_postgres_repository.update_user_password(mock_confirmed_user_password_change_model_object)
    
    assert isinstance(user, User)

@pytest.mark.asyncio
async def test_update_update_user_password_not_found(
    mock_postgres_async_session,
    mock_confirmed_user_password_change_model_object):
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.return_value = None
    
    with pytest.raises(PostgreSQLNotFoundError):
        await user_postgres_repository.update_user_password(mock_confirmed_user_password_change_model_object)

@pytest.mark.asyncio
async def test_update_update_user_password_database_error(
    mock_postgres_async_session,
    mock_confirmed_user_password_change_model_object):
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)

    with pytest.raises(PostgreSQLDatabaseError):
        await user_postgres_repository.update_user_password(mock_confirmed_user_password_change_model_object)
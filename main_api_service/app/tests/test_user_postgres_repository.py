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
from app.models.user_model import (
    CreateUserModel,
    UserPersonalInformationModel,
    ConfirmedUserEmailChangeModel,
    ConfirmedUserPasswordChangeModel
)
from datetime import datetime, date
from uuid import uuid4

@pytest.mark.asyncio
async def test_create_user_success(mock_postgres_async_session):
    user_to_be_created = CreateUserModel(
        email="email@example.com",
        password="passw0rd!",
        salt="123456789podwajkdjadsakdjkanw",
        registration_date=date.today().isoformat()
    )

    user_object = User(
        id=uuid4(),
        email=user_to_be_created.email, 
        password=user_to_be_created.password,
        salt=user_to_be_created.salt, 
        registration_date=datetime.strptime(user_to_be_created.registration_date, '%Y-%m-%d').date(),
        last_login=date.today()
    )
    mock_postgres_async_session.scalar.return_value = user_object
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    user = await user_postgres_repository.create_user(user_to_be_created)
    
    assert isinstance(user, User)
    assert user.email == user_to_be_created.email
    assert user.password == user_to_be_created.password
    assert user.salt == user_to_be_created.salt

@pytest.mark.asyncio
async def test_create_user_integrity_error(mock_postgres_async_session):
    user_to_be_created = CreateUserModel(
        email="email@example.com",
        password="passw0rd!",
        salt="123456789podwajkdjadsakdjkanw",
        registration_date=date.today().isoformat()
    )

    mock_postgres_async_session.scalar.side_effect = IntegrityError('Integrity error', {}, None)
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)

    with pytest.raises(PostgreSQLIntegrityError):
        await user_postgres_repository.create_user(user_to_be_created)

@pytest.mark.asyncio
async def test_create_user_database_error(mock_postgres_async_session):
    user_to_be_created = CreateUserModel(
        email="email@example.com",
        password="passw0rd!",
        salt="123456789podwajkdjadsakdjkanw",
        registration_date=date.today().isoformat()
    )

    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)

    with pytest.raises(PostgreSQLDatabaseError):
        await user_postgres_repository.create_user(user_to_be_created)



@pytest.mark.asyncio
async def test_get_user_by_id_success(mock_postgres_async_session):
    mock_uuid4 = uuid4()
    user_object = User(
        id=mock_uuid4,
        email="email@example.com", 
        password="passw0rd!",
        salt="123456789podwajkdjadsakdjkanw", 
        registration_date=datetime.strptime(str(date.today()), '%Y-%m-%d').date(),
        last_login=date.today()
    )
    mock_postgres_async_session.scalar.return_value = user_object
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    user = await user_postgres_repository.get_user_by_id(str(mock_uuid4))
    
    assert isinstance(user, User)
    assert user_object.id == mock_uuid4

@pytest.mark.asyncio
async def test_get_user_by_id_not_found(mock_postgres_async_session):
    mock_uuid4 = uuid4()

    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)

    mock_postgres_async_session.scalar.return_value = None

    with pytest.raises(PostgreSQLNotFoundError):
        await user_postgres_repository.get_user_by_id(str(mock_uuid4))

@pytest.mark.asyncio
async def test_get_user_by_id_database_error(mock_postgres_async_session):
    mock_uuid4 = uuid4()

    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)

    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)

    with pytest.raises(PostgreSQLDatabaseError):
        await user_postgres_repository.get_user_by_id(str(mock_uuid4))



@pytest.mark.asyncio
async def test_get_user_by_email_address_success(mock_postgres_async_session):
    mock_uuid4 = uuid4()
    user_object = User(
        id=mock_uuid4,
        email="email@example.com", 
        password="passw0rd!",
        salt="123456789podwajkdjadsakdjkanw", 
        registration_date=datetime.strptime(str(date.today()), '%Y-%m-%d').date(),
        last_login=date.today()
    )
    mock_postgres_async_session.scalar.return_value = user_object
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    user = await user_postgres_repository.get_user_by_email_address(user_object.email)
    
    assert isinstance(user, User)
    assert user_object.id == mock_uuid4
    assert user_object.email == user_object.email

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



@pytest.mark.asyncio
async def test_is_email_addres_arleady_taken_success(mock_postgres_async_session):
    mock_postgres_async_session.scalar.return_value = None
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    is_email_in_use = await user_postgres_repository.is_email_addres_arleady_taken("email@example.com")
    
    assert isinstance(is_email_in_use, bool)
    assert is_email_in_use == False

@pytest.mark.asyncio
async def test_get_user_by_email_address_database_error(mock_postgres_async_session):
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)

    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)

    with pytest.raises(PostgreSQLDatabaseError):
        await user_postgres_repository.is_email_addres_arleady_taken("email@example.com")



@pytest.mark.asyncio
async def test_update_user_last_login_success(mock_postgres_async_session):
    mock_uuid4 = uuid4()
    user_object = User(
        id=mock_uuid4,
        email="email@example.com", 
        password="passw0rd!",
        salt="123456789podwajkdjadsakdjkanw", 
        registration_date=datetime.strptime(str(date.today()), '%Y-%m-%d').date(),
        last_login=date.today()
    )
    
    mock_postgres_async_session.scalar.return_value = user_object
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    user = await user_postgres_repository.update_user_last_login(str(mock_uuid4))
    
    assert isinstance(user, User)

@pytest.mark.asyncio
async def test_update_user_last_login_not_found(mock_postgres_async_session):
    mock_uuid4 = uuid4()
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)

    mock_postgres_async_session.scalar.return_value = None

    with pytest.raises(PostgreSQLNotFoundError):
        await user_postgres_repository.update_user_last_login(str(mock_uuid4))

@pytest.mark.asyncio
async def test_update_user_last_login_database_error(mock_postgres_async_session):
    mock_uuid4 = uuid4()
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)

    with pytest.raises(PostgreSQLDatabaseError):
        await user_postgres_repository.update_user_last_login(str(mock_uuid4))



@pytest.mark.asyncio
async def test_update_user_personal_information_success(mock_postgres_async_session):
    mock_uuid4 = uuid4()
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    personal_info = UserPersonalInformationModel(
        first_name="John",
        last_name="Smith",
        phone_number="123456789",
        city="Warsaw",
        postal_code="00-000",
        street="ul. Nowa 1/2"
    )

    user_object = User(
        id=mock_uuid4,
        email="email@example.com", 
        password="passw0rd!",
        first_name=personal_info.first_name,
        last_name=personal_info.last_name,
        phone_number=personal_info.phone_number,
        city=personal_info.city,
        postal_code=personal_info.postal_code,
        street=personal_info.street,
        salt="123456789podwajkdjadsakdjkanw", 
        registration_date=datetime.strptime(str(date.today()), '%Y-%m-%d').date(),
        last_login=date.today()
    )

    mock_postgres_async_session.scalar.return_value = user_object

    user = await user_postgres_repository.update_user_personal_information(str(mock_uuid4), personal_info)
    
    assert isinstance(user, User)

@pytest.mark.asyncio
async def test_update_user_personal_information_not_found(mock_postgres_async_session):
    mock_uuid4 = uuid4()
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    personal_info = UserPersonalInformationModel(
        first_name="John",
        last_name="Smith",
        phone_number="123456789",
        city="Warsaw",
        postal_code="00-000",
        street="ul. Nowa 1/2"
    )

    mock_postgres_async_session.scalar.return_value = None

    with pytest.raises(PostgreSQLNotFoundError):
        await user_postgres_repository.update_user_personal_information(str(mock_uuid4), personal_info)
    
@pytest.mark.asyncio
async def test_update_user_personal_information_database_error(mock_postgres_async_session):
    mock_uuid4 = uuid4()
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    personal_info = UserPersonalInformationModel(
        first_name="John",
        last_name="Smith",
        phone_number="123456789",
        city="Warsaw",
        postal_code="00-000",
        street="ul. Nowa 1/2"
    )

    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)

    with pytest.raises(PostgreSQLDatabaseError):
        await user_postgres_repository.update_user_personal_information(str(mock_uuid4), personal_info)



@pytest.mark.asyncio
async def test_update_user_email_address_success(mock_postgres_async_session):
    mock_uuid4 = uuid4()
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    new_email = ConfirmedUserEmailChangeModel(
        id=str(mock_uuid4),
        new_email="email1@example.com"
    )

    user_object = User(
        id=mock_uuid4,
        email="email1@example.com", 
        password="passw0rd!",
        salt="123456789podwajkdjadsakdjkanw", 
        registration_date=datetime.strptime(str(date.today()), '%Y-%m-%d').date(),
        last_login=date.today()
    )

    mock_postgres_async_session.scalar.return_value = user_object

    user = await user_postgres_repository.update_user_email_address(new_email)
    
    assert isinstance(user, User)

@pytest.mark.asyncio
async def test_update_user_email_address_not_found(mock_postgres_async_session):
    mock_uuid4 = uuid4()
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    new_email = ConfirmedUserEmailChangeModel(
        id=str(mock_uuid4),
        new_email="email1@example.com"
    )

    mock_postgres_async_session.scalar.return_value = None

    with pytest.raises(PostgreSQLNotFoundError):
        await user_postgres_repository.update_user_email_address(new_email)

@pytest.mark.asyncio
async def test_update_user_email_address_integrity_error(mock_postgres_async_session):
    mock_uuid4 = uuid4()
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    new_email = ConfirmedUserEmailChangeModel(
        id=str(mock_uuid4),
        new_email="email1@example.com"
    )

    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)

    with pytest.raises(PostgreSQLDatabaseError):
        await user_postgres_repository.update_user_email_address(new_email)

@pytest.mark.asyncio
async def test_update_user_email_address_database_error(mock_postgres_async_session):
    mock_uuid4 = uuid4()
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    new_email = ConfirmedUserEmailChangeModel(
        id=str(mock_uuid4),
        new_email="email1@example.com"
    )

    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)

    with pytest.raises(PostgreSQLDatabaseError):
        await user_postgres_repository.update_user_email_address(new_email)



@pytest.mark.asyncio
async def test_update_update_user_password_success(mock_postgres_async_session):
    mock_uuid4 = uuid4()
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    new_password = ConfirmedUserPasswordChangeModel(
        id=str(mock_uuid4),
        new_password="passw0rd!1"
    )

    user_object = User(
        id=mock_uuid4,
        email="email1@example.com", 
        password="passw0rd!1",
        salt="123456789podwajkdjadsakdjkanw"
    )

    mock_postgres_async_session.scalar.return_value = user_object

    user = await user_postgres_repository.update_user_password(new_password)
    
    assert isinstance(user, User)

@pytest.mark.asyncio
async def test_update_update_user_password_not_found(mock_postgres_async_session):
    mock_uuid4 = uuid4()
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    new_password = ConfirmedUserPasswordChangeModel(
        id=str(mock_uuid4),
        new_password="passw0rd!1"
    )

    mock_postgres_async_session.scalar.return_value = None
    
    with pytest.raises(PostgreSQLNotFoundError):
        await user_postgres_repository.update_user_password(new_password)

@pytest.mark.asyncio
async def test_update_update_user_password_database_error(mock_postgres_async_session):
    mock_uuid4 = uuid4()
    
    user_postgres_repository = UserPostgresRepository(mock_postgres_async_session)
    new_password = ConfirmedUserPasswordChangeModel(
        id=str(mock_uuid4),
        new_password="passw0rd!1"
    )

    mock_postgres_async_session.scalar.side_effect = DatabaseError('Database error', {}, None)

    with pytest.raises(PostgreSQLDatabaseError):
        await user_postgres_repository.update_user_password(new_password)
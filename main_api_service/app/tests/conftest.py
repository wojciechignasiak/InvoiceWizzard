import pytest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis
from app.schema.schema import User
from app.models.user_model import CreateUserModel, UserPersonalInformationModel, ConfirmedUserEmailChangeModel, ConfirmedUserPasswordChangeModel
from app.models.jwt_model import JWTPayloadModel
from uuid import UUID
from datetime import datetime, date

@pytest.fixture
def mock_postgres_async_session():
    yield AsyncMock(spec=AsyncSession)

@pytest.fixture
def mock_redis_client():
    yield AsyncMock(spec=Redis)

@pytest.fixture
def mock_user_schema_object():
    user_schema_object = User(
        id=UUID("7024353b-aa89-4097-8925-f2855519c0ae"),
        email="email@example.com", 
        password="passw0rd!",
        first_name="John",
        last_name="Smith",
        phone_number="123007456",
        city="Warsaw",
        postal_code="00-000",
        street="ul. Nowa 3/4",
        salt="123456789podwajkdjadsakdjkanw", 
        registration_date=datetime.strptime(str(date.today()), '%Y-%m-%d').date(),
        last_login=date.today(),
        email_notification=True,
        push_notification=True
    )

    return user_schema_object

@pytest.fixture
def mock_create_user_model_object():
    create_user_model_object = CreateUserModel(
        email="email@example.com",
        password="passw0rd!",
        salt="123456789podwajkdjadsakdjkanw",
        registration_date=datetime.strptime(str(date.today()), '%Y-%m-%d').strftime('%Y-%m-%d')
    )

    return create_user_model_object

@pytest.fixture
def mock_user_personal_information_model_object():
    user_personal_information_model_object = UserPersonalInformationModel(
        first_name="John",
        last_name="Smith",
        phone_number="123007456",
        city="Warsaw",
        postal_code="00-000",
        street="ul. Nowa 3/4",
    )

    return user_personal_information_model_object

@pytest.fixture
def mock_confirmed_user_email_change_model_object():
    confirmed_user_email_change_model_object = ConfirmedUserEmailChangeModel(
        id="7024353b-aa89-4097-8925-f2855519c0ae",
        new_email="email1@example.com"
    )

    return confirmed_user_email_change_model_object

@pytest.fixture
def mock_confirmed_user_password_change_model_object():
    confirmed_user_password_change_model_object = ConfirmedUserPasswordChangeModel(
        id="7024353b-aa89-4097-8925-f2855519c0ae",
        new_password="passw0rd!1"
    )

    return confirmed_user_password_change_model_object

@pytest.fixture
def mock_jwt_payload_model_object():
    jwt_payload_model_object = JWTPayloadModel(
        id="1",
        email="email@example.com",
        exp=datetime.utcnow()
    )

    return jwt_payload_model_object
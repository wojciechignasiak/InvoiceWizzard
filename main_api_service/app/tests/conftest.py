import pytest
from unittest.mock import AsyncMock, Mock
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis
from aiokafka import AIOKafkaProducer
from app.schema.schema import User, UserBusinessEntity
from app.models.user_model import (
    CreateUserModel, 
    UserPersonalInformationModel, 
    ConfirmedUserEmailChangeModel, 
    ConfirmedUserPasswordChangeModel, 
    RegisterUserModel,
    UpdateUserEmailModel,
    UpdateUserPasswordModel,
    ResetUserPasswordModel
)
from app.models.jwt_model import JWTPayloadModel
from app.models.user_business_entity_model import (
    CreateUserBusinessEntityModel, 
    UserBusinessEntityModel, 
    UpdateUserBusinessEntityModel
)
from uuid import UUID
from datetime import datetime, date
from app.database.redis.repositories.user_repository import UserRedisRepository
from app.database.redis.repositories.user_business_entity_repository import UserBusinessEntityRedisRepository
from app.database.postgres.repositories.user_repository import UserPostgresRepository
from app.database.postgres.repositories.user_business_entity_repository import UserBusinessEntityPostgresRepository
from app.database.repositories_registry import RepositoriesRegistry


@pytest.fixture
def mock_postgres_async_session():
    yield AsyncMock(spec=AsyncSession)

@pytest.fixture
def mock_redis_client():
    yield AsyncMock(spec=Redis)

@pytest.fixture
def mock_kafka_producer_client():
    yield AsyncMock(spec=AIOKafkaProducer)

#MOCKED SCHEMA

@pytest.fixture
def mock_user_schema_object():
    user_schema_object = User(
        id=UUID("7024353b-aa89-4097-8925-f2855519c0ae"),
        email="email@example.com", 
        password="$argon2id$v=19$m=65536,t=3,p=4$S/JebuHd4wVIFeVEEBFgxg$0LSXgrPERjr4y/9rhVuwMAT0EoiUUNNAZ3zkcaXfWAk",
        first_name="John",
        last_name="Smith",
        phone_number="123007456",
        city="Warsaw",
        postal_code="00-000",
        street="ul. Nowa 3/4",
        salt="/fBgLFRPzmpEUnYArkRQhQ==",
        registration_date=datetime.strptime(str(date.today()), '%Y-%m-%d').date(),
        last_login=date.today(),
        email_notification=True,
        push_notification=True
    )

    return user_schema_object

@pytest.fixture
def mock_user_business_entity_schema_object():
    user_business_entity_schema_object = UserBusinessEntity(
        id=UUID("c487e563-a0e5-4bf7-ba20-d747db6da205"),
        user_id=UUID("7024353b-aa89-4097-8925-f2855519c0ae"),
        company_name="Company Name",
        city="Warsaw",
        postal_code="00-000",
        street="ul. Nowa 3/4",
        nip="8386732400",
        krs="0123624482"
    )
    
    return user_business_entity_schema_object

@pytest.fixture
def mock_jwt_token():
    jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjcwMjQzNTNiLWFhODktNDA5Ny04OTI1LWYyODU1NTE5YzBhZSIsImVtYWlsIjoiZW1haWxAZXhhbXBsZS5jb20iLCJleHAiOjE1MTYyMzkwMjJ9.bpoXUQdibTb0nltDSQF7ujjSHv-v0nb7qdvhnkXdv4c"

    return jwt_token

#MOCKED REPOSITORIES

@pytest.fixture
def mock_user_redis_repository_object():
    user_redis_repository_mock_object = Mock(spec=UserRedisRepository)

    return user_redis_repository_mock_object

@pytest.fixture
def mock_user_postgres_repository_object():
    user_postgres_repository_mock_object = Mock(spec=UserPostgresRepository)

    return user_postgres_repository_mock_object

@pytest.fixture
def mock_user_business_entity_postgres_repository_object():
    user_business_entity_repository_postgres_mock_object = Mock(spec=UserBusinessEntityPostgresRepository)

    return user_business_entity_repository_postgres_mock_object

@pytest.fixture
def mock_user_business_entity_redis_repository_object():
    user_business_entity_repository_redis_mock_object = Mock(spec=UserBusinessEntityRedisRepository)

    return user_business_entity_repository_redis_mock_object

@pytest.fixture
def mock_registry_repository_object():
    repositories_registry_mock_object = Mock(spec=RepositoriesRegistry)

    return repositories_registry_mock_object

#MOCKED MODELS

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
        id="7024353b-aa89-4097-8925-f2855519c0ae",
        email="email@example.com",
        exp=datetime.utcnow()
    )

    return jwt_payload_model_object

@pytest.fixture
def mock_register_user_model_object():
    register_user_model_mock_object = RegisterUserModel(
        email="email@example.com",
        repeated_email="email@example.com",
        password="passw0rd!",
        repeated_password="passw0rd!"
    )

    return register_user_model_mock_object

@pytest.fixture
def mock_update_user_email_model_object():
    update_user_email_model_mock_object = UpdateUserEmailModel(
        current_email="email@example.com",
        new_email="email1@example.com",
        new_repeated_email="email1@example.com"
    )

    return update_user_email_model_mock_object

@pytest.fixture
def mock_update_user_password_model_object():
    update_user_password_model_mock_object = UpdateUserPasswordModel(
        current_password="passw0rd!",
        new_password="passw0rd!1",
        new_repeated_password="passw0rd!1"
    )

    return update_user_password_model_mock_object

@pytest.fixture
def mock_reset_user_password_model_object():
    reset_user_password_model_mock_object = ResetUserPasswordModel(
        email="email@example.com",
        new_password="passw0rd!1",
        new_repeated_password="passw0rd!1"
    )

    return reset_user_password_model_mock_object

@pytest.fixture
def mock_create_user_business_entity_model_object():
    create_user_business_entity_model_object = CreateUserBusinessEntityModel(
        company_name = "Warsaw",
        city = "Warsaw",
        postal_code = "00-000",
        street = "ul. Nowa 3/4",
        nip = "8386732400",
        krs = "0123624482"
    )

    return create_user_business_entity_model_object

@pytest.fixture
def mock_update_user_business_entity_model_object():
    update_user_business_entity_model_object = UpdateUserBusinessEntityModel(
        id="c487e563-a0e5-4bf7-ba20-d747db6da205",
        company_name = "Warsaw",
        city = "Warsaw",
        postal_code = "00-000",
        street = "ul. Nowa 3/4",
        nip = "8386732400",
        krs = "0123624482"
    )
    
    return update_user_business_entity_model_object

@pytest.fixture
def mock_user_business_entity_model_object():
    user_business_entity_model_object = UserBusinessEntityModel(
        id="c487e563-a0e5-4bf7-ba20-d747db6da205",
        company_name = "Warsaw",
        city = "Warsaw",
        postal_code = "00-000",
        street = "ul. Nowa 3/4",
        nip = "8386732400",
        krs = "0123624482"
    )

    return user_business_entity_model_object
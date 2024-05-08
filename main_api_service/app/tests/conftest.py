import pytest
import pytest_asyncio
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from aiokafka import AIOKafkaProducer
from app.schema.schema import User, UserBusinessEntity, ExternalBusinessEntity, InvoiceItem, Invoice
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
from app.models.external_business_entity_model import (
    CreateExternalBusinessEntityModel,
    UpdateExternalBusinessEntityModel,
    ExternalBusinessEntityModel
)
from app.models.authentication_model import LogInModel
from app.models.invoice_model import (
    CreateInvoiceModel,
    InvoiceModel,
    UpdateInvoiceModel
)
from app.models.invoice_item_model import (
    InvoiceItemModel,
    CreateInvoiceItemModel,
    UpdateInvoiceItemModel
)
from uuid import UUID
from pathlib import Path
from datetime import datetime, date
from app.database.redis.repositories.user_repository import UserRedisRepository
from app.database.redis.repositories.user_business_entity_repository import UserBusinessEntityRedisRepository
from app.database.redis.repositories.external_business_entity_repository import ExternalBusinessEntityRedisRepository
from app.database.postgres.repositories.user_repository import UserPostgresRepository
from app.database.postgres.repositories.user_business_entity_repository import UserBusinessEntityPostgresRepository
from app.database.postgres.repositories.external_business_entity_repository import ExternalBusinessEntityPostgresRepository
from app.database.postgres.repositories.invoice_repository import InvoicePostgresRepository
from app.database.redis.repositories.invoice_repository import InvoiceRedisRepository
from app.database.postgres.repositories.invoice_item_repository import InvoiceItemPostgresRepository
from app.files.files_repository import FilesRepository
from app.registries.repositories_registry import RepositoriesRegistry
from app.registries.events_registry import EventsRegistry


@pytest_asyncio.fixture
async def mock_postgres_async_session():
    yield AsyncMock(spec=AsyncSession)

@pytest_asyncio.fixture
async def mock_redis_client():
    return AsyncMock()

@pytest_asyncio.fixture
async def mock_kafka_producer_client():
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
        nip="8386732400"
    )
    
    return user_business_entity_schema_object

@pytest.fixture
def mock_external_business_entity_schema_object():
    external_business_entity_schema_object = ExternalBusinessEntity(
        id=UUID("c487e563-a0e5-4bf7-ba20-d747db6da205"),
        user_id=UUID("7024353b-aa89-4097-8925-f2855519c0ae"),
        name="Name",
        city="Warsaw",
        postal_code="00-000",
        street="ul. Nowa 3/4",
        nip="8386732400"
    )
    
    return external_business_entity_schema_object

@pytest.fixture
def mock_invoice_schema_object():
    invoice_schema_object = Invoice(
        id=UUID("378cd98c-d144-49bd-8e4f-07613ccd3701"),
        user_id=UUID("7024353b-aa89-4097-8925-f2855519c0ae"),
        user_business_entity_id=UUID("c487e563-a0e5-4bf7-ba20-d747db6da205"),
        external_business_entity_id=UUID("c487e563-a0e5-4bf7-ba20-d747db6da205"),
        invoice_pdf="/invoice.pdf",
        invoice_number="12/2023",
        issue_date="2023-12-05",
        sale_date="2023-12-05",
        notes="My Invoice notes",
        payment_method="Card",
        payment_deadline="2023-12-05",
        added_date="2023-12-05",
        is_settled=True,
        is_issued=True,
        in_trash=False
    )
    return invoice_schema_object

@pytest.fixture
def mock_invoice_item_schema_object():
    invoice_item_schema_object = InvoiceItem(
        id=UUID("10852ddf-c3f0-4bb4-8cf3-b2ba5566a28b"),
        user_id=UUID("7024353b-aa89-4097-8925-f2855519c0ae"),
        invoice_id=UUID("378cd98c-d144-49bd-8e4f-07613ccd3701"),
        item_description="This is item description",
        number_of_items=2,
        net_value=8.0,
        gross_value=10.0,
        in_trash=False
    )
    return invoice_item_schema_object


@pytest.fixture
def mock_jwt_token():
    jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjcwMjQzNTNiLWFhODktNDA5Ny04OTI1LWYyODU1NTE5YzBhZSIsImVtYWlsIjoiZW1haWxAZXhhbXBsZS5jb20iLCJleHAiOjE1MTYyMzkwMjJ9.bpoXUQdibTb0nltDSQF7ujjSHv-v0nb7qdvhnkXdv4c"

    return jwt_token

#MOCKED REPOSITORIES

@pytest.fixture
def mock_user_redis_repository_object():
    user_redis_repository_mock_object = AsyncMock(spec=UserRedisRepository)

    return user_redis_repository_mock_object

@pytest.fixture
def mock_user_postgres_repository_object():
    user_postgres_repository_mock_object = AsyncMock(spec=UserPostgresRepository)

    return user_postgres_repository_mock_object

@pytest.fixture
def mock_user_business_entity_postgres_repository_object():
    user_business_entity_repository_postgres_mock_object = AsyncMock(spec=UserBusinessEntityPostgresRepository)

    return user_business_entity_repository_postgres_mock_object

@pytest.fixture
def mock_user_business_entity_redis_repository_object():
    user_business_entity_repository_redis_mock_object = AsyncMock(spec=UserBusinessEntityRedisRepository)

    return user_business_entity_repository_redis_mock_object

@pytest.fixture
def mock_external_business_entity_postgres_repository_object():
    external_business_entity_repository_postgres_mock_object = AsyncMock(spec=ExternalBusinessEntityPostgresRepository)

    return external_business_entity_repository_postgres_mock_object

@pytest.fixture
def mock_external_business_entity_redis_repository_object():
    external_business_entity_repository_redis_mock_object = AsyncMock(spec=ExternalBusinessEntityRedisRepository)

    return external_business_entity_repository_redis_mock_object

@pytest.fixture
def mock_invoice_postgres_repository_object():
    invoice_repository_postgres_mock_object = AsyncMock(spec=InvoicePostgresRepository)

    return invoice_repository_postgres_mock_object

@pytest.fixture
def mock_invoice_redis_repository_object():
    invoice_repository_redis_mock_object = AsyncMock(spec=InvoiceRedisRepository)

    return invoice_repository_redis_mock_object

@pytest.fixture
def mock_invoice_item_postgres_repository_object():
    invoice_item_repository_postgres_mock_object = AsyncMock(spec=InvoiceItemPostgresRepository)

    return invoice_item_repository_postgres_mock_object

@pytest.fixture
def mock_files_repository_object():
    files_repository_mock_object = AsyncMock(spec=FilesRepository)
    return files_repository_mock_object
#MOCKED REGISTRIES

@pytest.fixture
def mock_registry_repository_object():
    repositories_registry_mock_object = AsyncMock(spec=RepositoriesRegistry)

    return repositories_registry_mock_object

@pytest.fixture
def mock_registry_events_object():
    events_registry_mock_object = AsyncMock(spec=EventsRegistry)

    return events_registry_mock_object

#MOCKED MODELS

@pytest.fixture
def mock_create_user_model_object():
    create_user_model_object = CreateUserModel(
        email="email@example.com",
        password="passw0rd!",
        salt="123456789podwajkdjadsakdjkanw"
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
        company_name = "Company Name",
        city = "Warsaw",
        postal_code = "00-000",
        street = "ul. Nowa 3/4",
        nip = "8386732400"
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
        nip = "8386732400"
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
        nip = "8386732400"
    )

    return user_business_entity_model_object

@pytest.fixture
def mock_log_in_model_object():
    log_in_model_object = LogInModel(
        email="email@example.com",
        password="passw0rd!",
        remember_me=True
    )

    return log_in_model_object

@pytest.fixture
def mock_create_external_business_entity_model_object():
    create_external_business_entity_model_object = CreateExternalBusinessEntityModel(
        name = "Name/Company Name",
        city = "Warsaw",
        postal_code = "00-000",
        street = "ul. Nowa 3/4",
        nip = "8386732400"
    )

    return create_external_business_entity_model_object

@pytest.fixture
def mock_update_external_business_entity_model_object():
    update_external_business_entity_model_object = UpdateExternalBusinessEntityModel(
        id="c487e563-a0e5-4bf7-ba20-d747db6da205",
        name = "Name/Company Name",
        city = "Warsaw",
        postal_code = "00-000",
        street = "ul. Nowa 3/4",
        nip = "8386732400"
    )
    
    return update_external_business_entity_model_object

@pytest.fixture
def mock_external_business_entity_model_object():
    external_business_entity_model_object = ExternalBusinessEntityModel(
        id="c487e563-a0e5-4bf7-ba20-d747db6da205",
        name = "Name/Company Name",
        city = "Warsaw",
        postal_code = "00-000",
        street = "ul. Nowa 3/4",
        nip = "8386732400"
    )

    return external_business_entity_model_object

@pytest.fixture
def mock_create_invoice_model_object():
    create_invoice_model_object = CreateInvoiceModel(
        user_business_entity_id="c487e563-a0e5-4bf7-ba20-d747db6da205",
        external_business_entity_id="c487e563-a0e5-4bf7-ba20-d747db6da205",
        invoice_number="12/2023",
        issue_date="2023-12-05",
        sale_date="2023-12-05",
        payment_method="Card",
        payment_deadline="2023-12-05",
        notes="My Invoice notes",
        is_settled=False,
        is_issued=True
    )

    return create_invoice_model_object

@pytest.fixture
def mock_invoice_model_object():
    invoice_model_object = InvoiceModel(
        id="15b8d02b-1f21-4bd3-83c9-a1ebb105aba3",
        user_business_entity_id="c487e563-a0e5-4bf7-ba20-d747db6da205",
        external_business_entity_id="c487e563-a0e5-4bf7-ba20-d747db6da205",
        invoice_number="12/2023",
        issue_date="2023-12-05",
        added_date="2023-12-05",
        sale_date="2023-12-05",
        payment_method="Card",
        payment_deadline="2023-12-05",
        notes="My Invoice notes",
        is_settled=False,
        is_issued=True,
        in_trash=False
    )

    return invoice_model_object

@pytest.fixture
def mock_update_invoice_model_object():
    update_invoice_model_object = UpdateInvoiceModel(
        id="15b8d02b-1f21-4bd3-83c9-a1ebb105aba3",
        user_business_entity_id="c487e563-a0e5-4bf7-ba20-d747db6da205",
        external_business_entity_id="c487e563-a0e5-4bf7-ba20-d747db6da205",
        invoice_number="12/2023",
        issue_date="2023-12-05",
        sale_date="2023-12-05",
        payment_method="Card",
        payment_deadline="2023-12-05",
        notes="My Invoice notes",
        is_settled=False,
        is_issued=True
    )

    return update_invoice_model_object

@pytest.fixture
def mock_create_invoice_item_model_object():
    create_invoice_item_model_object = CreateInvoiceItemModel(
        item_description="My product/service name",
        number_of_items=1,
        net_value=8.00,
        gross_value=10.00
    )

    return create_invoice_item_model_object

@pytest.fixture
def mock_invoice_item_model_object():
    invoice_item_model_object = InvoiceItemModel(
        id="378cd98c-d144-49bd-8e4f-07613ccd3701",
        invoice_id="15b8d02b-1f21-4bd3-83c9-a1ebb105aba3",
        item_description="My product/service name",
        number_of_items=1,
        net_value=8.00,
        gross_value=10.00,
        in_trash=False
    )

    return invoice_item_model_object

@pytest.fixture
def mock_update_invoice_item_model_object():
    update_invoice_item_model_object = UpdateInvoiceItemModel(
        id="378cd98c-d144-49bd-8e4f-07613ccd3701",
        invoice_id="15b8d02b-1f21-4bd3-83c9-a1ebb105aba3",
        item_description="My product/service name",
        number_of_items=1,
        net_value=8.00,
        gross_value=10.00,
        in_trash=False
    )

    return update_invoice_item_model_object

@pytest.fixture
def mock_path_file_object():
    path_file_object = AsyncMock(spec=Path)

    return path_file_object
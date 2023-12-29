import pytest
from app.main import app
from app.database.postgres.session.get_session import get_session
from app.database.redis.client.get_redis_client import get_redis_client
from app.registries.get_repositories_registry import get_repositories_registry
from app.registries.get_events_registry import get_events_registry
from app.kafka.clients.get_kafka_producer_client import get_kafka_producer_client
from fastapi.testclient import TestClient
from app.database.redis.exceptions.custom_redis_exceptions import (
    RedisSetError, 
    RedisDatabaseError, 
    RedisNotFoundError, 
    RedisJWTNotFoundError
    )
from app.database.postgres.exceptions.custom_postgres_exceptions import (
    PostgreSQLDatabaseError, 
    PostgreSQLNotFoundError,
    PostgreSQLIntegrityError
    )
import json

client = TestClient(app)

# invoice_router.create_invoice()

@pytest.mark.asyncio
async def test_create_invoice_success(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_create_invoice_model_object,
    mock_create_invoice_item_model_object,
    mock_invoice_schema_object,
    mock_invoice_item_schema_object,
    mock_invoice_postgres_repository_object,
    mock_invoice_item_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    
    mock_invoice_postgres_repository_object.create_invoice.return_value = mock_invoice_schema_object
    mock_invoice_item_postgres_repository_object.create_invoice_item.return_value = mock_invoice_item_schema_object

    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    data = {
        "new_invoice": json.loads(mock_create_invoice_model_object.model_dump_json()),
        "invoice_items":[json.loads(mock_create_invoice_item_model_object.model_dump_json())]
    }
    

    response = client.post(
        "/invoice-module/create-invoice/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=data)
    
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_create_invoice_postgres_integrity_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_create_invoice_model_object,
    mock_create_invoice_item_model_object,
    mock_invoice_item_schema_object,
    mock_invoice_postgres_repository_object,
    mock_invoice_item_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    
    mock_invoice_postgres_repository_object.create_invoice.side_effect = PostgreSQLIntegrityError()
    mock_invoice_item_postgres_repository_object.create_invoice_item.return_value = mock_invoice_item_schema_object

    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    data = {
        "new_invoice": json.loads(mock_create_invoice_model_object.model_dump_json()),
        "invoice_items":[json.loads(mock_create_invoice_item_model_object.model_dump_json())]
    }
    

    response = client.post(
        "/invoice-module/create-invoice/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=data)
    
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_create_invoice_not_authenticated_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_create_invoice_model_object,
    mock_create_invoice_item_model_object,
    mock_invoice_schema_object,
    mock_invoice_item_schema_object,
    mock_invoice_postgres_repository_object,
    mock_invoice_item_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisJWTNotFoundError()
    
    mock_invoice_postgres_repository_object.create_invoice.return_value = mock_invoice_schema_object
    mock_invoice_item_postgres_repository_object.create_invoice_item.return_value = mock_invoice_item_schema_object

    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    data = {
        "new_invoice": json.loads(mock_create_invoice_model_object.model_dump_json()),
        "invoice_items":[json.loads(mock_create_invoice_item_model_object.model_dump_json())]
    }
    

    response = client.post(
        "/invoice-module/create-invoice/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=data)
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_create_invoice_redis_database_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_create_invoice_model_object,
    mock_create_invoice_item_model_object,
    mock_invoice_schema_object,
    mock_invoice_item_schema_object,
    mock_invoice_postgres_repository_object,
    mock_invoice_item_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisDatabaseError()
    
    mock_invoice_postgres_repository_object.create_invoice.return_value = mock_invoice_schema_object
    mock_invoice_item_postgres_repository_object.create_invoice_item.return_value = mock_invoice_item_schema_object

    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    data = {
        "new_invoice": json.loads(mock_create_invoice_model_object.model_dump_json()),
        "invoice_items":[json.loads(mock_create_invoice_item_model_object.model_dump_json())]
    }
    

    response = client.post(
        "/invoice-module/create-invoice/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=data)
    
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_create_invoice_postgres_database_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_create_invoice_model_object,
    mock_create_invoice_item_model_object,
    mock_invoice_item_schema_object,
    mock_invoice_postgres_repository_object,
    mock_invoice_item_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    
    mock_invoice_postgres_repository_object.create_invoice.side_effect = PostgreSQLDatabaseError()
    mock_invoice_item_postgres_repository_object.create_invoice_item.return_value = mock_invoice_item_schema_object

    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    data = {
        "new_invoice": json.loads(mock_create_invoice_model_object.model_dump_json()),
        "invoice_items":[json.loads(mock_create_invoice_item_model_object.model_dump_json())]
    }
    

    response = client.post(
        "/invoice-module/create-invoice/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=data)
    
    assert response.status_code == 500

# invoice_router.get_invoice()

@pytest.mark.asyncio
async def test_get_invoice_success(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_schema_object,
    mock_invoice_item_schema_object,
    mock_user_business_entity_schema_object,
    mock_external_business_entity_schema_object,
    mock_invoice_postgres_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_user_business_entity_postgres_repository_object,
    mock_external_business_entity_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    
    mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object
    mock_invoice_item_postgres_repository_object.get_invoice_items_by_invoice_id.return_value = [mock_invoice_item_schema_object]
    mock_user_business_entity_postgres_repository_object.get_user_business_entity.return_value = mock_user_business_entity_schema_object
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object

    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_user_business_entity_postgres_repository.return_value = mock_user_business_entity_postgres_repository_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object


    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    response = client.get(
        "/invoice-module/get-invoice/?invoice_id=cc50870e-c58d-4f1d-bb45-d258ed621426",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_invoice_not_authenticated_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_schema_object,
    mock_invoice_item_schema_object,
    mock_user_business_entity_schema_object,
    mock_external_business_entity_schema_object,
    mock_invoice_postgres_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_user_business_entity_postgres_repository_object,
    mock_external_business_entity_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisJWTNotFoundError()
    
    mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object
    mock_invoice_item_postgres_repository_object.get_invoice_items_by_invoice_id.return_value = [mock_invoice_item_schema_object]
    mock_user_business_entity_postgres_repository_object.get_user_business_entity.return_value = mock_user_business_entity_schema_object
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object

    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_user_business_entity_postgres_repository.return_value = mock_user_business_entity_postgres_repository_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object


    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    response = client.get(
        "/invoice-module/get-invoice/?invoice_id=cc50870e-c58d-4f1d-bb45-d258ed621426",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_invoice_not_authenticated_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_schema_object,
    mock_invoice_item_schema_object,
    mock_user_business_entity_schema_object,
    mock_external_business_entity_schema_object,
    mock_invoice_postgres_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_user_business_entity_postgres_repository_object,
    mock_external_business_entity_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisDatabaseError()
    
    mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object
    mock_invoice_item_postgres_repository_object.get_invoice_items_by_invoice_id.return_value = [mock_invoice_item_schema_object]
    mock_user_business_entity_postgres_repository_object.get_user_business_entity.return_value = mock_user_business_entity_schema_object
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object

    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_user_business_entity_postgres_repository.return_value = mock_user_business_entity_postgres_repository_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object


    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    response = client.get(
        "/invoice-module/get-invoice/?invoice_id=cc50870e-c58d-4f1d-bb45-d258ed621426",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 500


@pytest.mark.asyncio
async def test_get_invoice_postges_not_found_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_item_schema_object,
    mock_user_business_entity_schema_object,
    mock_external_business_entity_schema_object,
    mock_invoice_postgres_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_user_business_entity_postgres_repository_object,
    mock_external_business_entity_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    
    mock_invoice_postgres_repository_object.get_invoice.side_effect = PostgreSQLNotFoundError()
    mock_invoice_item_postgres_repository_object.get_invoice_items_by_invoice_id.return_value = [mock_invoice_item_schema_object]
    mock_user_business_entity_postgres_repository_object.get_user_business_entity.return_value = mock_user_business_entity_schema_object
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object

    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_user_business_entity_postgres_repository.return_value = mock_user_business_entity_postgres_repository_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object


    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    response = client.get(
        "/invoice-module/get-invoice/?invoice_id=cc50870e-c58d-4f1d-bb45-d258ed621426",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_invoice_postges_database_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_item_schema_object,
    mock_user_business_entity_schema_object,
    mock_external_business_entity_schema_object,
    mock_invoice_postgres_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_user_business_entity_postgres_repository_object,
    mock_external_business_entity_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    
    mock_invoice_postgres_repository_object.get_invoice.side_effect = PostgreSQLDatabaseError()
    mock_invoice_item_postgres_repository_object.get_invoice_items_by_invoice_id.return_value = [mock_invoice_item_schema_object]
    mock_user_business_entity_postgres_repository_object.get_user_business_entity.return_value = mock_user_business_entity_schema_object
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object

    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_user_business_entity_postgres_repository.return_value = mock_user_business_entity_postgres_repository_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object


    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    response = client.get(
        "/invoice-module/get-invoice/?invoice_id=cc50870e-c58d-4f1d-bb45-d258ed621426",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 500


# invoice_router.get_all_invoices()

@pytest.mark.asyncio
async def test_get_all_invoices_success(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_schema_object,
    mock_invoice_item_schema_object,
    mock_user_business_entity_schema_object,
    mock_external_business_entity_schema_object,
    mock_invoice_postgres_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_user_business_entity_postgres_repository_object,
    mock_external_business_entity_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    
    mock_invoice_postgres_repository_object.get_all_invoices.return_value = [mock_invoice_schema_object]
    mock_invoice_item_postgres_repository_object.get_invoice_items_by_invoice_id.return_value = [mock_invoice_item_schema_object]
    mock_user_business_entity_postgres_repository_object.get_user_business_entity.return_value = mock_user_business_entity_schema_object
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object

    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_user_business_entity_postgres_repository.return_value = mock_user_business_entity_postgres_repository_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object


    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    response = client.get(
        "/invoice-module/get-all-invoices/?page=1&items_per_page=50",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_all_invoices_not_authenticated_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_schema_object,
    mock_invoice_item_schema_object,
    mock_user_business_entity_schema_object,
    mock_external_business_entity_schema_object,
    mock_invoice_postgres_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_user_business_entity_postgres_repository_object,
    mock_external_business_entity_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisJWTNotFoundError()
    
    mock_invoice_postgres_repository_object.get_all_invoices.return_value = [mock_invoice_schema_object]
    mock_invoice_item_postgres_repository_object.get_invoice_items_by_invoice_id.return_value = [mock_invoice_item_schema_object]
    mock_user_business_entity_postgres_repository_object.get_user_business_entity.return_value = mock_user_business_entity_schema_object
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object

    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_user_business_entity_postgres_repository.return_value = mock_user_business_entity_postgres_repository_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object


    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    response = client.get(
        "/invoice-module/get-all-invoices/?page=1&items_per_page=50",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_all_invoices_redis_database_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_schema_object,
    mock_invoice_item_schema_object,
    mock_user_business_entity_schema_object,
    mock_external_business_entity_schema_object,
    mock_invoice_postgres_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_user_business_entity_postgres_repository_object,
    mock_external_business_entity_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisDatabaseError()
    
    mock_invoice_postgres_repository_object.get_all_invoices.return_value = [mock_invoice_schema_object]
    mock_invoice_item_postgres_repository_object.get_invoice_items_by_invoice_id.return_value = [mock_invoice_item_schema_object]
    mock_user_business_entity_postgres_repository_object.get_user_business_entity.return_value = mock_user_business_entity_schema_object
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object

    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_user_business_entity_postgres_repository.return_value = mock_user_business_entity_postgres_repository_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object


    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    response = client.get(
        "/invoice-module/get-all-invoices/?page=1&items_per_page=50",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 500


@pytest.mark.asyncio
async def test_get_all_invoices_postgres_database_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_item_schema_object,
    mock_user_business_entity_schema_object,
    mock_external_business_entity_schema_object,
    mock_invoice_postgres_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_user_business_entity_postgres_repository_object,
    mock_external_business_entity_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    
    mock_invoice_postgres_repository_object.get_all_invoices.side_effect = PostgreSQLDatabaseError()
    mock_invoice_item_postgres_repository_object.get_invoice_items_by_invoice_id.return_value = [mock_invoice_item_schema_object]
    mock_user_business_entity_postgres_repository_object.get_user_business_entity.return_value = mock_user_business_entity_schema_object
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object

    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_user_business_entity_postgres_repository.return_value = mock_user_business_entity_postgres_repository_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object


    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    response = client.get(
        "/invoice-module/get-all-invoices/?page=1&items_per_page=50",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 500


@pytest.mark.asyncio
async def test_get_all_invoices_not_found_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_item_schema_object,
    mock_user_business_entity_schema_object,
    mock_external_business_entity_schema_object,
    mock_invoice_postgres_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_user_business_entity_postgres_repository_object,
    mock_external_business_entity_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    
    mock_invoice_postgres_repository_object.get_all_invoices.side_effect = PostgreSQLNotFoundError()
    mock_invoice_item_postgres_repository_object.get_invoice_items_by_invoice_id.return_value = [mock_invoice_item_schema_object]
    mock_user_business_entity_postgres_repository_object.get_user_business_entity.return_value = mock_user_business_entity_schema_object
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object

    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_user_business_entity_postgres_repository.return_value = mock_user_business_entity_postgres_repository_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object


    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    response = client.get(
        "/invoice-module/get-all-invoices/?page=1&items_per_page=50",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 404


# invoice_router.update_invoice()

@pytest.mark.asyncio
async def test_update_invoice_success(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_update_invoice_model_object,
    mock_invoice_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    
    mock_invoice_postgres_repository_object.is_invoice_unique_beside_one_to_update.return_value = True

    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object


    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    data = json.loads(mock_update_invoice_model_object.model_dump_json())

    response = client.patch(
        "/invoice-module/update-invoice/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=data)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_invoice_not_authenticated_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_update_invoice_model_object,
    mock_invoice_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisJWTNotFoundError()
    
    mock_invoice_postgres_repository_object.is_invoice_unique_beside_one_to_update.return_value = True

    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object


    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    data = json.loads(mock_update_invoice_model_object.model_dump_json())

    response = client.patch(
        "/invoice-module/update-invoice/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=data)

    assert response.status_code == 401

@pytest.mark.asyncio
async def test_update_invoice_not_unique_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_update_invoice_model_object,
    mock_invoice_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    
    mock_invoice_postgres_repository_object.is_invoice_unique_beside_one_to_update.return_value = False

    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object


    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    data = json.loads(mock_update_invoice_model_object.model_dump_json())

    response = client.patch(
        "/invoice-module/update-invoice/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=data)

    assert response.status_code == 409

@pytest.mark.asyncio
async def test_update_invoice_redis_database_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_update_invoice_model_object,
    mock_invoice_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisDatabaseError()
    
    mock_invoice_postgres_repository_object.is_invoice_unique_beside_one_to_update.return_value = False

    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object


    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    data = json.loads(mock_update_invoice_model_object.model_dump_json())

    response = client.patch(
        "/invoice-module/update-invoice/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=data)

    assert response.status_code == 500

@pytest.mark.asyncio
async def test_update_invoice_postgres_database_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_update_invoice_model_object,
    mock_invoice_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    
    mock_invoice_postgres_repository_object.is_invoice_unique_beside_one_to_update.side_effect = PostgreSQLDatabaseError()

    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object


    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    data = json.loads(mock_update_invoice_model_object.model_dump_json())

    response = client.patch(
        "/invoice-module/update-invoice/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=data)

    assert response.status_code == 500


# invoice_router.update_invoice_in_trash_status()

@pytest.mark.asyncio
async def test_update_invoice_in_trash_status_success(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_invoice_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    
    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object


    response = client.patch(
        "/invoice-module/update-invoice-in-trash-status/?invoice_id=123&in_trash=true",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_update_invoice_in_trash_status_not_found_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_invoice_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    
    mock_invoice_postgres_repository_object.update_invoice_in_trash_status.side_effect = PostgreSQLNotFoundError()

    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object


    response = client.patch(
        "/invoice-module/update-invoice-in-trash-status/?invoice_id=123&in_trash=true",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_invoice_in_trash_status_unauthorized_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_invoice_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisJWTNotFoundError()
    
    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object


    response = client.patch(
        "/invoice-module/update-invoice-in-trash-status/?invoice_id=123&in_trash=true",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 401

@pytest.mark.asyncio
async def test_update_invoice_in_trash_status_postgres_database_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_invoice_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    
    mock_invoice_postgres_repository_object.update_invoice_in_trash_status.side_effect = PostgreSQLDatabaseError()

    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object


    response = client.patch(
        "/invoice-module/update-invoice-in-trash-status/?invoice_id=123&in_trash=true",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 500

@pytest.mark.asyncio
async def test_update_invoice_in_trash_status_redis_database_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_invoice_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisDatabaseError()
    
    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object


    response = client.patch(
        "/invoice-module/update-invoice-in-trash-status/?invoice_id=123&in_trash=true",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 500


# invoice_router.initialize_invoice_removal()

@pytest.mark.asyncio
async def test_initialize_invoice_removal_success(
    mock_registry_repository_object,
    mock_registry_events_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_kafka_producer_client,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_redis_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_invoice_postgres_repository_object,
    mock_user_business_entity_postgres_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_invoice_schema_object,
    mock_user_business_entity_schema_object,
    mock_external_business_entity_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    
    mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object
    mock_user_business_entity_postgres_repository_object.get_user_business_entity.return_value = mock_user_business_entity_schema_object
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object

    mock_registry_repository_object.return_invoice_redis_repository.return_value = mock_invoice_redis_repository_object
    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_user_business_entity_postgres_repository.return_value = mock_user_business_entity_postgres_repository_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    app.dependency_overrides[get_events_registry] = lambda:mock_registry_events_object
    app.dependency_overrides[get_kafka_producer_client] = lambda:mock_kafka_producer_client


    response = client.put(
        "/invoice-module/initialize-invoice-removal/?invoice_id=123",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_initialize_invoice_removal_unauthorized_error(
    mock_registry_repository_object,
    mock_registry_events_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_kafka_producer_client,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_redis_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_invoice_postgres_repository_object,
    mock_user_business_entity_postgres_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_invoice_schema_object,
    mock_user_business_entity_schema_object,
    mock_external_business_entity_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisJWTNotFoundError()
    
    mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object
    mock_user_business_entity_postgres_repository_object.get_user_business_entity.return_value = mock_user_business_entity_schema_object
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object

    mock_registry_repository_object.return_invoice_redis_repository.return_value = mock_invoice_redis_repository_object
    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_user_business_entity_postgres_repository.return_value = mock_user_business_entity_postgres_repository_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    app.dependency_overrides[get_events_registry] = lambda:mock_registry_events_object
    app.dependency_overrides[get_kafka_producer_client] = lambda:mock_kafka_producer_client


    response = client.put(
        "/invoice-module/initialize-invoice-removal/?invoice_id=123",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 401

@pytest.mark.asyncio
async def test_initialize_invoice_removal_not_found_error(
    mock_registry_repository_object,
    mock_registry_events_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_kafka_producer_client,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_redis_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_invoice_postgres_repository_object,
    mock_user_business_entity_postgres_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_business_entity_schema_object,
    mock_external_business_entity_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    
    mock_invoice_postgres_repository_object.get_invoice.side_effect = PostgreSQLNotFoundError()
    mock_user_business_entity_postgres_repository_object.get_user_business_entity.return_value = mock_user_business_entity_schema_object
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object

    mock_registry_repository_object.return_invoice_redis_repository.return_value = mock_invoice_redis_repository_object
    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_user_business_entity_postgres_repository.return_value = mock_user_business_entity_postgres_repository_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    app.dependency_overrides[get_events_registry] = lambda:mock_registry_events_object
    app.dependency_overrides[get_kafka_producer_client] = lambda:mock_kafka_producer_client


    response = client.put(
        "/invoice-module/initialize-invoice-removal/?invoice_id=123",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 404

@pytest.mark.asyncio
async def test_initialize_invoice_removal_redis_set_error(
    mock_registry_repository_object,
    mock_registry_events_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_kafka_producer_client,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_redis_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_invoice_postgres_repository_object,
    mock_user_business_entity_postgres_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_invoice_schema_object,
    mock_user_business_entity_schema_object,
    mock_external_business_entity_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    
    mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object
    mock_user_business_entity_postgres_repository_object.get_user_business_entity.return_value = mock_user_business_entity_schema_object
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object
    mock_invoice_redis_repository_object.initialize_invoice_removal.side_effect = RedisSetError()

    mock_registry_repository_object.return_invoice_redis_repository.return_value = mock_invoice_redis_repository_object
    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_user_business_entity_postgres_repository.return_value = mock_user_business_entity_postgres_repository_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    app.dependency_overrides[get_events_registry] = lambda:mock_registry_events_object
    app.dependency_overrides[get_kafka_producer_client] = lambda:mock_kafka_producer_client


    response = client.put(
        "/invoice-module/initialize-invoice-removal/?invoice_id=123",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 500

@pytest.mark.asyncio
async def test_initialize_invoice_removal_postgres_database_error(
    mock_registry_repository_object,
    mock_registry_events_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_kafka_producer_client,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_redis_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_invoice_postgres_repository_object,
    mock_user_business_entity_postgres_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_business_entity_schema_object,
    mock_external_business_entity_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    
    mock_invoice_postgres_repository_object.get_invoice.side_effect = PostgreSQLDatabaseError()
    mock_user_business_entity_postgres_repository_object.get_user_business_entity.return_value = mock_user_business_entity_schema_object
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object

    mock_registry_repository_object.return_invoice_redis_repository.return_value = mock_invoice_redis_repository_object
    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_user_business_entity_postgres_repository.return_value = mock_user_business_entity_postgres_repository_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    app.dependency_overrides[get_events_registry] = lambda:mock_registry_events_object
    app.dependency_overrides[get_kafka_producer_client] = lambda:mock_kafka_producer_client


    response = client.put(
        "/invoice-module/initialize-invoice-removal/?invoice_id=123",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 500


@pytest.mark.asyncio
async def test_initialize_invoice_removal_redis_database_error(
    mock_registry_repository_object,
    mock_registry_events_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_kafka_producer_client,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_redis_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_invoice_postgres_repository_object,
    mock_user_business_entity_postgres_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_invoice_schema_object,
    mock_user_business_entity_schema_object,
    mock_external_business_entity_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisDatabaseError()
    
    mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object
    mock_user_business_entity_postgres_repository_object.get_user_business_entity.return_value = mock_user_business_entity_schema_object
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object

    mock_registry_repository_object.return_invoice_redis_repository.return_value = mock_invoice_redis_repository_object
    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_user_business_entity_postgres_repository.return_value = mock_user_business_entity_postgres_repository_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    app.dependency_overrides[get_events_registry] = lambda:mock_registry_events_object
    app.dependency_overrides[get_kafka_producer_client] = lambda:mock_kafka_producer_client


    response = client.put(
        "/invoice-module/initialize-invoice-removal/?invoice_id=123",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 500


# invoice_router.confirm_invoice_removal()

@pytest.mark.asyncio
async def test_confirm_invoice_removal_success(
    mock_registry_repository_object,
    mock_registry_events_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_kafka_producer_client,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_redis_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_invoice_postgres_repository_object,
    mock_user_business_entity_postgres_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_invoice_schema_object,
    mock_user_business_entity_schema_object,
    mock_external_business_entity_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    
    mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object
    retrieve_result = json.dumps({"id":"some_random_key"})
    mock_invoice_redis_repository_object.retrieve_invoice_removal.return_value = bytes(retrieve_result, "utf-8")
    mock_user_business_entity_postgres_repository_object.get_user_business_entity.return_value = mock_user_business_entity_schema_object
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object

    mock_registry_repository_object.return_invoice_redis_repository.return_value = mock_invoice_redis_repository_object
    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_user_business_entity_postgres_repository.return_value = mock_user_business_entity_postgres_repository_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    app.dependency_overrides[get_events_registry] = lambda:mock_registry_events_object
    app.dependency_overrides[get_kafka_producer_client] = lambda:mock_kafka_producer_client


    response = client.delete(
        "/invoice-module/confirm-invoice-removal/?key_id=123",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    print(response.json())
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_confirm_invoice_removal_unauthorized_error(
    mock_registry_repository_object,
    mock_registry_events_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_kafka_producer_client,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_redis_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_invoice_postgres_repository_object,
    mock_user_business_entity_postgres_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_invoice_schema_object,
    mock_user_business_entity_schema_object,
    mock_external_business_entity_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisJWTNotFoundError()
    
    mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object
    retrieve_result = json.dumps({"id":"some_random_key"})
    mock_invoice_redis_repository_object.retrieve_invoice_removal.return_value = bytes(retrieve_result, "utf-8")
    mock_user_business_entity_postgres_repository_object.get_user_business_entity.return_value = mock_user_business_entity_schema_object
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object

    mock_registry_repository_object.return_invoice_redis_repository.return_value = mock_invoice_redis_repository_object
    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_user_business_entity_postgres_repository.return_value = mock_user_business_entity_postgres_repository_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    app.dependency_overrides[get_events_registry] = lambda:mock_registry_events_object
    app.dependency_overrides[get_kafka_producer_client] = lambda:mock_kafka_producer_client


    response = client.delete(
        "/invoice-module/confirm-invoice-removal/?key_id=123",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_confirm_invoice_removal_postgres_not_found_error(
    mock_registry_repository_object,
    mock_registry_events_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_kafka_producer_client,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_redis_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_invoice_postgres_repository_object,
    mock_user_business_entity_postgres_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_invoice_schema_object,
    mock_external_business_entity_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    
    mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object
    retrieve_result = json.dumps({"id":"some_random_key"})
    mock_invoice_redis_repository_object.retrieve_invoice_removal.return_value = bytes(retrieve_result, "utf-8")
    mock_user_business_entity_postgres_repository_object.get_user_business_entity.side_effect = PostgreSQLNotFoundError()
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object

    mock_registry_repository_object.return_invoice_redis_repository.return_value = mock_invoice_redis_repository_object
    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_user_business_entity_postgres_repository.return_value = mock_user_business_entity_postgres_repository_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    app.dependency_overrides[get_events_registry] = lambda:mock_registry_events_object
    app.dependency_overrides[get_kafka_producer_client] = lambda:mock_kafka_producer_client


    response = client.delete(
        "/invoice-module/confirm-invoice-removal/?key_id=123",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_confirm_invoice_removal_redis_not_found_error(
    mock_registry_repository_object,
    mock_registry_events_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_kafka_producer_client,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_redis_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_invoice_postgres_repository_object,
    mock_user_business_entity_postgres_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_invoice_schema_object,
    mock_user_business_entity_schema_object,
    mock_external_business_entity_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    
    mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object
    mock_invoice_redis_repository_object.retrieve_invoice_removal.side_effect = RedisNotFoundError()
    mock_user_business_entity_postgres_repository_object.get_user_business_entity.return_value = mock_user_business_entity_schema_object
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object

    mock_registry_repository_object.return_invoice_redis_repository.return_value = mock_invoice_redis_repository_object
    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_user_business_entity_postgres_repository.return_value = mock_user_business_entity_postgres_repository_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    app.dependency_overrides[get_events_registry] = lambda:mock_registry_events_object
    app.dependency_overrides[get_kafka_producer_client] = lambda:mock_kafka_producer_client


    response = client.delete(
        "/invoice-module/confirm-invoice-removal/?key_id=123",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_confirm_invoice_removal_postgres_database_error(
    mock_registry_repository_object,
    mock_registry_events_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_kafka_producer_client,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_redis_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_invoice_postgres_repository_object,
    mock_user_business_entity_postgres_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_invoice_schema_object,
    mock_external_business_entity_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    
    mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object
    retrieve_result = json.dumps({"id":"some_random_key"})
    mock_invoice_redis_repository_object.retrieve_invoice_removal.return_value = bytes(retrieve_result, "utf-8")
    mock_user_business_entity_postgres_repository_object.get_user_business_entity.side_effect = PostgreSQLDatabaseError()
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object

    mock_registry_repository_object.return_invoice_redis_repository.return_value = mock_invoice_redis_repository_object
    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_user_business_entity_postgres_repository.return_value = mock_user_business_entity_postgres_repository_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    app.dependency_overrides[get_events_registry] = lambda:mock_registry_events_object
    app.dependency_overrides[get_kafka_producer_client] = lambda:mock_kafka_producer_client


    response = client.delete(
        "/invoice-module/confirm-invoice-removal/?key_id=123",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 500


@pytest.mark.asyncio
async def test_confirm_invoice_removal_redis_database_error(
    mock_registry_repository_object,
    mock_registry_events_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_kafka_producer_client,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_redis_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_invoice_postgres_repository_object,
    mock_user_business_entity_postgres_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_invoice_schema_object,
    mock_user_business_entity_schema_object,
    mock_external_business_entity_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    
    mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object
    mock_invoice_redis_repository_object.retrieve_invoice_removal.side_effect = RedisDatabaseError()
    mock_user_business_entity_postgres_repository_object.get_user_business_entity.return_value = mock_user_business_entity_schema_object
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object

    mock_registry_repository_object.return_invoice_redis_repository.return_value = mock_invoice_redis_repository_object
    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_user_business_entity_postgres_repository.return_value = mock_user_business_entity_postgres_repository_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    app.dependency_overrides[get_events_registry] = lambda:mock_registry_events_object
    app.dependency_overrides[get_kafka_producer_client] = lambda:mock_kafka_producer_client


    response = client.delete(
        "/invoice-module/confirm-invoice-removal/?key_id=123",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 500


# invoice_router.add_file_to_invoice()

@pytest.mark.asyncio
async def test_add_file_to_invoice_success(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_postgres_repository_object,
    mock_invoice_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_invoice_schema_object.invoice_pdf = None

    mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object
    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    file_content = b"example file content"
    file = {"invoice_file": ("example_file.pdf", file_content)}
    
    response = client.post(
        "/invoice-module/add-file-to-invoice/?invoice_id={invoice_id}",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        files=file)
    
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_add_file_to_invoice_file_arleady_exists_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_postgres_repository_object,
    mock_invoice_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")

    mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object
    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    file_content = b"example file content"
    file = {"invoice_file": ("example_file.pdf", file_content)}
    
    response = client.post(
        "/invoice-module/add-file-to-invoice/?invoice_id={invoice_id}",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        files=file)
    
    assert response.status_code == 409

@pytest.mark.asyncio
async def test_add_file_to_invoice_unsupported_media_type_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_postgres_repository_object,
    mock_invoice_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_invoice_schema_object.invoice_pdf = None

    mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object
    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    file_content = b"example file content"
    file = {"invoice_file": ("example_file.txt", file_content)}
    
    response = client.post(
        "/invoice-module/add-file-to-invoice/?invoice_id={invoice_id}",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        files=file)
    
    assert response.status_code == 415

@pytest.mark.asyncio
async def test_add_file_to_invoice_unauthorized_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_postgres_repository_object,
    mock_invoice_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisJWTNotFoundError()
    mock_invoice_schema_object.invoice_pdf = None

    mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object
    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    file_content = b"example file content"
    file = {"invoice_file": ("example_file.txt", file_content)}
    
    response = client.post(
        "/invoice-module/add-file-to-invoice/?invoice_id={invoice_id}",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        files=file)
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_add_file_to_invoice_postgres_not_found_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_postgres_repository_object,
    mock_invoice_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_invoice_schema_object.invoice_pdf = None

    mock_invoice_postgres_repository_object.get_invoice.side_effect = PostgreSQLNotFoundError()
    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    file_content = b"example file content"
    file = {"invoice_file": ("example_file.txt", file_content)}
    
    response = client.post(
        "/invoice-module/add-file-to-invoice/?invoice_id={invoice_id}",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        files=file)
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_add_file_to_invoice_postgres_database_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_postgres_repository_object,
    mock_invoice_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_invoice_schema_object.invoice_pdf = None

    mock_invoice_postgres_repository_object.get_invoice.side_effect = PostgreSQLDatabaseError()
    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    file_content = b"example file content"
    file = {"invoice_file": ("example_file.txt", file_content)}
    
    response = client.post(
        "/invoice-module/add-file-to-invoice/?invoice_id={invoice_id}",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        files=file)
    
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_add_file_to_invoice_redis_database_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_postgres_repository_object,
    mock_invoice_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisDatabaseError()
    mock_invoice_schema_object.invoice_pdf = None

    mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object
    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    file_content = b"example file content"
    file = {"invoice_file": ("example_file.txt", file_content)}
    
    response = client.post(
        "/invoice-module/add-file-to-invoice/?invoice_id={invoice_id}",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        files=file)
    
    assert response.status_code == 500

# invoice_router.delete_invoice_pdf()

@pytest.mark.asyncio
async def test_delete_invoice_pdf_success(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_postgres_repository_object,
    mock_invoice_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")

    mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object
    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    
    response = client.delete(
        "/invoice-module/delete-invoice-pdf/?invoice_id={invoice_id}",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_delete_invoice_pdf_no_file_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_postgres_repository_object,
    mock_invoice_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_invoice_schema_object.invoice_pdf = None
    mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object
    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    
    response = client.delete(
        "/invoice-module/delete-invoice-pdf/?invoice_id={invoice_id}",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_invoice_pdf_unauthorized_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_postgres_repository_object,
    mock_invoice_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisJWTNotFoundError()

    mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object
    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    
    response = client.delete(
        "/invoice-module/delete-invoice-pdf/?invoice_id={invoice_id}",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_delete_invoice_pdf_redis_database_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_postgres_repository_object,
    mock_invoice_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisDatabaseError()

    mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object
    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    
    response = client.delete(
        "/invoice-module/delete-invoice-pdf/?invoice_id={invoice_id}",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_delete_invoice_pdf_postgres_database_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_postgres_repository_object,
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")

    mock_invoice_postgres_repository_object.get_invoice.side_effect = PostgreSQLDatabaseError()
    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    
    response = client.delete(
        "/invoice-module/delete-invoice-pdf/?invoice_id={invoice_id}",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 500

# invoice_router.download_invoice_pdf()

# @pytest.mark.asyncio
# async def test_download_invoice_pdf_success(
#     mock_registry_repository_object,
#     mock_redis_client,
#     mock_postgres_async_session,
#     mock_jwt_payload_model_object,
#     mock_jwt_token,
#     mock_user_redis_repository_object,
#     mock_invoice_postgres_repository_object,
#     mock_files_repository_object,
#     mock_invoice_schema_object,
#     mock_path_file_object
#     ):

#     mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
#     mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object
#     file_content = b"example file content"
#     mock_path_file_object.is_file.return_value = True
#     mock_path_file_object.name.return_value = "invoice.pdf"
#     mock_path_file_object.read_bytes.return_value = file_content
#     mock_files_repository_object.get_invoice_pdf_file.return_value = mock_path_file_object

#     mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
#     mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
#     mock_registry_repository_object.return_files_repository.return_value = mock_files_repository_object

#     app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
#     app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
#     app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    
#     response = client.get(
#         "/invoice-module/download-invoice-pdf/?invoice_id=12345",
#         headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
#     assert response.status_code == 200


@pytest.mark.asyncio
async def test_download_invoice_pdf_unauthorized_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_postgres_repository_object,
    mock_files_repository_object,
    mock_invoice_schema_object,
    mock_path_file_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisJWTNotFoundError()
    mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object
    
    mock_path_file_object.is_file.return_value = True
    mock_path_file_object.name.return_value = "invoice.pdf"
    mock_files_repository_object.get_invoice_pdf_file.return_value = mock_path_file_object

    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_files_repository.return_value = mock_files_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    
    response = client.get(
        "/invoice-module/download-invoice-pdf/?invoice_id={invoice_id}",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_download_invoice_pdf_redis_database_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_postgres_repository_object,
    mock_files_repository_object,
    mock_invoice_schema_object,
    mock_path_file_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisDatabaseError()
    mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object

    mock_path_file_object.is_file.return_value = True
    mock_path_file_object.name.return_value = "invoice.pdf"
    mock_files_repository_object.get_invoice_pdf_file.return_value = mock_path_file_object

    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_files_repository.return_value = mock_files_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    
    response = client.get(
        "/invoice-module/download-invoice-pdf/?invoice_id={invoice_id}",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_download_invoice_pdf_postgres_database_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_postgres_repository_object,
    mock_files_repository_object,
    mock_path_file_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_invoice_postgres_repository_object.get_invoice.side_effect = PostgreSQLDatabaseError()

    mock_path_file_object.is_file.return_value = True
    mock_path_file_object.name.return_value = "invoice.pdf"
    mock_files_repository_object.get_invoice_pdf_file.return_value = mock_path_file_object

    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_files_repository.return_value = mock_files_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    
    response = client.get(
        "/invoice-module/download-invoice-pdf/?invoice_id={invoice_id}",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_download_invoice_pdf_postgres_not_found_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_postgres_repository_object,
    mock_files_repository_object,
    mock_path_file_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_invoice_postgres_repository_object.get_invoice.side_effect = PostgreSQLNotFoundError()

    mock_path_file_object.is_file.return_value = True
    mock_path_file_object.name.return_value = "invoice.pdf"
    mock_files_repository_object.get_invoice_pdf_file.return_value = mock_path_file_object

    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_files_repository.return_value = mock_files_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    
    response = client.get(
        "/invoice-module/download-invoice-pdf/?invoice_id={invoice_id}",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 404

# invoice_router.generate_invoice_pdf()

# @pytest.mark.asyncio
# async def test_generate_invoice_pdf_success(
#     mock_registry_repository_object,
#     mock_redis_client,
#     mock_postgres_async_session,
#     mock_jwt_payload_model_object,
#     mock_jwt_token,
#     mock_user_redis_repository_object,
#     mock_invoice_postgres_repository_object,
#     mock_external_business_entity_postgres_repository_object,
#     mock_user_business_entity_postgres_repository_object,
#     mock_invoice_item_postgres_repository_object,
#     mock_files_repository_object,
#     mock_invoice_schema_object,
#     mock_invoice_item_schema_object,
#     mock_external_business_entity_schema_object,
#     mock_user_business_entity_schema_object
#     ):

#     mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
#     mock_invoice_schema_object.invoice_pdf = None
#     mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object
#     mock_invoice_item_postgres_repository_object.get_invoice_items_by_invoice_id.return_value = [mock_invoice_item_schema_object]
#     mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object
#     mock_user_business_entity_postgres_repository_object.get_user_business_entity.return_value = mock_user_business_entity_schema_object


#     mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
#     mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
#     mock_registry_repository_object.return_files_repository.return_value = mock_files_repository_object
#     mock_registry_repository_object.return_invoice_item_postgres_repository = mock_invoice_item_postgres_repository_object
#     mock_registry_repository_object.return_external_business_entity_postgres_repository = mock_external_business_entity_postgres_repository_object
#     mock_registry_repository_object.return_user_business_entity_postgres_repository = mock_user_business_entity_postgres_repository_object

#     app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
#     app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
#     app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    
#     response = client.post(
#         "/invoice-module/generate-invoice-pdf/?invoice_id={invoice_id}",
#         headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
#     print(response.json())
#     assert response.status_code == 200

@pytest.mark.asyncio
async def test_generate_invoice_pdf_unauthorized_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_postgres_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_business_entity_postgres_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_files_repository_object,
    mock_invoice_schema_object,
    mock_invoice_item_schema_object,
    mock_external_business_entity_schema_object,
    mock_user_business_entity_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisJWTNotFoundError()
    mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object
    mock_invoice_item_postgres_repository_object.get_invoice_items_by_invoice_id.return_value = [mock_invoice_item_schema_object]
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object
    mock_user_business_entity_postgres_repository_object.get_user_business_entity.return_value = mock_user_business_entity_schema_object


    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_files_repository.return_value = mock_files_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_business_entity_postgres_repository = mock_user_business_entity_postgres_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    
    response = client.post(
        "/invoice-module/generate-invoice-pdf/?invoice_id={invoice_id}",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_generate_invoice_pdf_redis_database_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_postgres_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_business_entity_postgres_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_files_repository_object,
    mock_invoice_schema_object,
    mock_invoice_item_schema_object,
    mock_external_business_entity_schema_object,
    mock_user_business_entity_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisDatabaseError()
    mock_invoice_schema_object.invoice_pdf = None
    mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object
    mock_invoice_item_postgres_repository_object.get_invoice_items_by_invoice_id.return_value = [mock_invoice_item_schema_object]
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object
    mock_user_business_entity_postgres_repository_object.get_user_business_entity.return_value = mock_user_business_entity_schema_object


    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_files_repository.return_value = mock_files_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_business_entity_postgres_repository = mock_user_business_entity_postgres_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    
    response = client.post(
        "/invoice-module/generate-invoice-pdf/?invoice_id={invoice_id}",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_generate_invoice_pdf_postgres_not_found_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_postgres_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_business_entity_postgres_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_files_repository_object,
    mock_invoice_schema_object,
    mock_invoice_item_schema_object,
    mock_external_business_entity_schema_object,
    mock_user_business_entity_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_invoice_schema_object.invoice_pdf = None
    mock_invoice_postgres_repository_object.get_invoice.side_effect = PostgreSQLNotFoundError()
    mock_invoice_item_postgres_repository_object.get_invoice_items_by_invoice_id.return_value = [mock_invoice_item_schema_object]
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object
    mock_user_business_entity_postgres_repository_object.get_user_business_entity.return_value = mock_user_business_entity_schema_object


    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_files_repository.return_value = mock_files_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_business_entity_postgres_repository = mock_user_business_entity_postgres_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    
    response = client.post(
        "/invoice-module/generate-invoice-pdf/?invoice_id={invoice_id}",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 404

@pytest.mark.asyncio
async def test_generate_invoice_pdf_postgres_database_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_postgres_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_business_entity_postgres_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_files_repository_object,
    mock_invoice_schema_object,
    mock_invoice_item_schema_object,
    mock_external_business_entity_schema_object,
    mock_user_business_entity_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_invoice_schema_object.invoice_pdf = None
    mock_invoice_postgres_repository_object.get_invoice.side_effect = PostgreSQLDatabaseError()
    mock_invoice_item_postgres_repository_object.get_invoice_items_by_invoice_id.return_value = [mock_invoice_item_schema_object]
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object
    mock_user_business_entity_postgres_repository_object.get_user_business_entity.return_value = mock_user_business_entity_schema_object


    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_files_repository.return_value = mock_files_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_business_entity_postgres_repository = mock_user_business_entity_postgres_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    
    response = client.post(
        "/invoice-module/generate-invoice-pdf/?invoice_id={invoice_id}",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 500

@pytest.mark.asyncio
async def test_generate_invoice_pdf_arleady_have_file_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_postgres_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_business_entity_postgres_repository_object,
    mock_invoice_item_postgres_repository_object,
    mock_files_repository_object,
    mock_invoice_schema_object,
    mock_invoice_item_schema_object,
    mock_external_business_entity_schema_object,
    mock_user_business_entity_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_invoice_postgres_repository_object.get_invoice.return_value = mock_invoice_schema_object
    mock_invoice_item_postgres_repository_object.get_invoice_items_by_invoice_id.return_value = [mock_invoice_item_schema_object]
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object
    mock_user_business_entity_postgres_repository_object.get_user_business_entity.return_value = mock_user_business_entity_schema_object


    mock_registry_repository_object.return_invoice_postgres_repository.return_value = mock_invoice_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object
    mock_registry_repository_object.return_files_repository.return_value = mock_files_repository_object
    mock_registry_repository_object.return_invoice_item_postgres_repository = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_business_entity_postgres_repository = mock_user_business_entity_postgres_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    
    response = client.post(
        "/invoice-module/generate-invoice-pdf/?invoice_id={invoice_id}",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 409
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

# invoice_router.create_invoice_item()

@pytest.mark.asyncio
async def test_create_invoice_item_success(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_create_invoice_item_model_object,
    mock_invoice_item_schema_object,
    mock_invoice_item_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_invoice_item_postgres_repository_object.create_invoice_item.return_value = mock_invoice_item_schema_object

    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    data = json.loads(mock_create_invoice_item_model_object.model_dump_json())
    

    response = client.post(
        "/invoice-item-module/create-invoice-item/?invoice_id=12345",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=data)
    
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_create_invoice_item_unauthorized_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_create_invoice_item_model_object,
    mock_invoice_item_schema_object,
    mock_invoice_item_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisJWTNotFoundError()
    mock_invoice_item_postgres_repository_object.create_invoice_item.return_value = mock_invoice_item_schema_object

    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    data = json.loads(mock_create_invoice_item_model_object.model_dump_json())
    

    response = client.post(
        "/invoice-item-module/create-invoice-item/?invoice_id=12345",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=data)
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_create_invoice_item_postgres_integrity_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_create_invoice_item_model_object,
    mock_invoice_item_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_invoice_item_postgres_repository_object.create_invoice_item.side_effect = PostgreSQLIntegrityError()

    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    data = json.loads(mock_create_invoice_item_model_object.model_dump_json())
    

    response = client.post(
        "/invoice-item-module/create-invoice-item/?invoice_id=12345",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=data)
    
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_create_invoice_item_postgres_database_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_create_invoice_item_model_object,
    mock_invoice_item_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_invoice_item_postgres_repository_object.create_invoice_item.side_effect = PostgreSQLDatabaseError()

    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    data = json.loads(mock_create_invoice_item_model_object.model_dump_json())
    

    response = client.post(
        "/invoice-item-module/create-invoice-item/?invoice_id=12345",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=data)
    
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_create_invoice_item_redis_database_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_create_invoice_item_model_object,
    mock_invoice_item_schema_object,
    mock_invoice_item_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisDatabaseError()
    mock_invoice_item_postgres_repository_object.create_invoice_item.return_value = mock_invoice_item_schema_object

    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    data = json.loads(mock_create_invoice_item_model_object.model_dump_json())
    

    response = client.post(
        "/invoice-item-module/create-invoice-item/?invoice_id=12345",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=data)
    
    assert response.status_code == 500


# invoice_router.update_invoice_item()

@pytest.mark.asyncio
async def test_update_invoice_item_success(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_update_invoice_item_model_object,
    mock_invoice_item_schema_object,
    mock_invoice_item_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_invoice_item_postgres_repository_object.update_invoice_item.return_value = mock_invoice_item_schema_object

    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    data = json.loads(mock_update_invoice_item_model_object.model_dump_json())
    

    response = client.patch(
        "/invoice-item-module/update-invoice-item/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=data)
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_invoice_item_unauthorized_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_update_invoice_item_model_object,
    mock_invoice_item_schema_object,
    mock_invoice_item_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisJWTNotFoundError()
    mock_invoice_item_postgres_repository_object.update_invoice_item.return_value = mock_invoice_item_schema_object

    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    data = json.loads(mock_update_invoice_item_model_object.model_dump_json())
    

    response = client.patch(
        "/invoice-item-module/update-invoice-item/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=data)
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_update_invoice_item_postgres_not_found_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_update_invoice_item_model_object,
    mock_invoice_item_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_invoice_item_postgres_repository_object.update_invoice_item.side_effect = PostgreSQLNotFoundError()

    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    data = json.loads(mock_update_invoice_item_model_object.model_dump_json())
    

    response = client.patch(
        "/invoice-item-module/update-invoice-item/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=data)
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_invoice_item_postgres_database_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_update_invoice_item_model_object,
    mock_invoice_item_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_invoice_item_postgres_repository_object.update_invoice_item.side_effect = PostgreSQLDatabaseError()

    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    data = json.loads(mock_update_invoice_item_model_object.model_dump_json())
    

    response = client.patch(
        "/invoice-item-module/update-invoice-item/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=data)
    
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_update_invoice_item_redis_database_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_update_invoice_item_model_object,
    mock_invoice_item_schema_object,
    mock_invoice_item_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisDatabaseError()
    mock_invoice_item_postgres_repository_object.update_invoice_item.return_value = mock_invoice_item_schema_object

    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    data = json.loads(mock_update_invoice_item_model_object.model_dump_json())
    

    response = client.patch(
        "/invoice-item-module/update-invoice-item/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=data)
    
    assert response.status_code == 500


# invoice_router.update_invoice_item_in_trash_status()

@pytest.mark.asyncio
async def test_update_invoice_item_in_trash_status_success(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")

    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.patch(
        "/invoice-module/update-invoice-item-in-trash-status/?invoice_item_id=1234&in_trash=true",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_update_invoice_item_in_trash_status_unauthorized_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token,
    mock_user_redis_repository_object,
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisJWTNotFoundError()

    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.patch(
        "/invoice-module/update-invoice-item-in-trash-status/?invoice_item_id=1234&in_trash=true",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_update_invoice_item_in_trash_status_postgres_not_found_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_item_postgres_repository_object,
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")

    mock_invoice_item_postgres_repository_object.update_invoice_item_in_trash_status.side_effect = PostgreSQLNotFoundError()

    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.patch(
        "/invoice-module/update-invoice-item-in-trash-status/?invoice_item_id=1234&in_trash=true",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_invoice_item_in_trash_status_postgres_database_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_item_postgres_repository_object,
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")

    mock_invoice_item_postgres_repository_object.update_invoice_item_in_trash_status.side_effect = PostgreSQLDatabaseError()

    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.patch(
        "/invoice-module/update-invoice-item-in-trash-status/?invoice_item_id=1234&in_trash=true",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_update_invoice_item_in_trash_status_redis_database_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token,
    mock_user_redis_repository_object,
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisDatabaseError()

    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.patch(
        "/invoice-module/update-invoice-item-in-trash-status/?invoice_item_id=1234&in_trash=true",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 500


# invoice_router.get_invoice_items_by_invoice_id()

@pytest.mark.asyncio
async def test_get_invoice_items_by_invoice_id_success(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_item_schema_object,
    mock_invoice_item_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_invoice_item_postgres_repository_object.get_invoice_items_by_invoice_id.return_value = [mock_invoice_item_schema_object]

    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.get(
        "/invoice-item-module/get-invoice-items-by-invoice-id/?invoice_id=12345&in_trash=true",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_invoice_items_by_invoice_id_unauthorized_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_item_schema_object,
    mock_invoice_item_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisJWTNotFoundError()
    mock_invoice_item_postgres_repository_object.get_invoice_items_by_invoice_id.return_value = [mock_invoice_item_schema_object]

    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.get(
        "/invoice-item-module/get-invoice-items-by-invoice-id/?invoice_id=12345&in_trash=true",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_invoice_items_by_invoice_id_postgres_not_found_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_item_schema_object,
    mock_invoice_item_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_invoice_item_postgres_repository_object.get_invoice_items_by_invoice_id.return_value = []

    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.get(
        "/invoice-item-module/get-invoice-items-by-invoice-id/?invoice_id=12345&in_trash=true",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_invoice_items_by_invoice_id_postgres_database_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_item_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_invoice_item_postgres_repository_object.get_invoice_items_by_invoice_id.side_effect = PostgreSQLDatabaseError()

    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.get(
        "/invoice-item-module/get-invoice-items-by-invoice-id/?invoice_id=12345&in_trash=true",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_get_invoice_items_by_invoice_id_redis_database_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_item_schema_object,
    mock_invoice_item_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisDatabaseError()
    mock_invoice_item_postgres_repository_object.get_invoice_items_by_invoice_id.return_value = [mock_invoice_item_schema_object]

    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.get(
        "/invoice-item-module/get-invoice-items-by-invoice-id/?invoice_id=12345&in_trash=true",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 500


# invoice_router.delete_invoice_item()

@pytest.mark.asyncio
async def test_delete_invoice_item_success(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_item_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_invoice_item_postgres_repository_object.remove_invoice_item.return_value = None

    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.delete(
        "/invoice-item-module/delete-invoice-item/?invoice_item_id=12345",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_delete_invoice_item_postgres_not_found_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_item_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_invoice_item_postgres_repository_object.remove_invoice_item.side_effect = PostgreSQLNotFoundError()

    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.delete(
        "/invoice-item-module/delete-invoice-item/?invoice_item_id=12345",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_invoice_item_unauthorized_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_item_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisJWTNotFoundError()
    mock_invoice_item_postgres_repository_object.remove_invoice_item.return_value = None

    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.delete(
        "/invoice-item-module/delete-invoice-item/?invoice_item_id=12345",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_delete_invoice_item_postgres_not_found_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_item_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_invoice_item_postgres_repository_object.remove_invoice_item.side_effect = PostgreSQLDatabaseError()

    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.delete(
        "/invoice-item-module/delete-invoice-item/?invoice_item_id=12345",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_delete_invoice_item_redis_database_error(
    mock_registry_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token,
    mock_user_redis_repository_object,
    mock_invoice_item_postgres_repository_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisDatabaseError()
    mock_invoice_item_postgres_repository_object.remove_invoice_item.return_value = None

    mock_registry_repository_object.return_invoice_item_postgres_repository.return_value = mock_invoice_item_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.delete(
        "/invoice-item-module/delete-invoice-item/?invoice_item_id=12345",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 500
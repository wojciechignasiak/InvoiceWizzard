import pytest
from app.main import app
from app.database.postgres.session.get_session import get_session
from app.database.redis.client.get_redis_client import get_redis_client
from app.registries.get_repositories_registry import get_repositories_registry
from fastapi.testclient import TestClient
from app.database.redis.exceptions.custom_redis_exceptions import (
    RedisDatabaseError, 
    RedisJWTNotFoundError
    )
from app.database.postgres.exceptions.custom_postgres_exceptions import (
    PostgreSQLDatabaseError, 
    PostgreSQLNotFoundError
    )

client = TestClient(app)

#external_business_entity_router.create_external_business_entity()

@pytest.mark.asyncio
async def test_create_external_business_entity_success(
    mock_registry_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_external_business_entity_schema_object,
    mock_create_external_business_entity_model_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_external_business_entity_postgres_repository_object.create_external_business_entity.return_value = mock_external_business_entity_schema_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_create_external_business_entity_model_object.model_dump()
    response = client.post(
        "/external-business-entity-module/create-external-business-entity/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == str(mock_external_business_entity_schema_object.id)
    assert data["company_name"] == mock_external_business_entity_schema_object.company_name
    assert data["city"] == mock_external_business_entity_schema_object.city
    assert data["postal_code"] == mock_external_business_entity_schema_object.postal_code
    assert data["street"] == mock_external_business_entity_schema_object.street
    assert data["nip"] == mock_external_business_entity_schema_object.nip

@pytest.mark.asyncio
async def test_create_external_business_entity_not_unique_error(
    mock_registry_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_external_business_entity_schema_object,
    mock_create_external_business_entity_model_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_external_business_entity_postgres_repository_object.create_external_business_entity.return_value = mock_external_business_entity_schema_object
    mock_external_business_entity_postgres_repository_object.is_external_business_entity_unique.return_value = False
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_create_external_business_entity_model_object.model_dump()
    response = client.post(
        "/external-business-entity-module/create-external-business-entity/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    
    assert response.status_code == 409
    

@pytest.mark.asyncio
async def test_create_external_business_entity_unauthorized_error(
    mock_registry_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_external_business_entity_schema_object,
    mock_create_external_business_entity_model_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisJWTNotFoundError()
    mock_external_business_entity_postgres_repository_object.create_external_business_entity.return_value = mock_external_business_entity_schema_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_create_external_business_entity_model_object.model_dump()
    response = client.post(
        "/external-business-entity-module/create-external-business-entity/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_create_external_business_entity_redis_database_error(
    mock_registry_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_external_business_entity_schema_object,
    mock_create_external_business_entity_model_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisDatabaseError()
    mock_external_business_entity_postgres_repository_object.create_external_business_entity.return_value = mock_external_business_entity_schema_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_create_external_business_entity_model_object.model_dump()
    response = client.post(
        "/external-business-entity-module/create-external-business-entity/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_create_external_business_entity_postgres_database_error(
    mock_registry_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_create_external_business_entity_model_object,
    mock_jwt_payload_model_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_external_business_entity_postgres_repository_object.create_external_business_entity.side_effect = PostgreSQLDatabaseError()
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_create_external_business_entity_model_object.model_dump()
    response = client.post(
        "/external-business-entity-module/create-external-business-entity/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    
    assert response.status_code == 500

#external_business_entity_router.get_external_business_entity()

@pytest.mark.asyncio
async def test_get_external_business_entity_success(
    mock_registry_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_external_business_entity_schema_object,
    mock_jwt_token,
    mock_external_business_entity_model_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.get(
        f"/external-business-entity-module/get-external-business-entity/?external_business_entity_id={str(mock_external_business_entity_model_object.id)}",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(mock_external_business_entity_schema_object.id)
    assert data["company_name"] == mock_external_business_entity_schema_object.company_name
    assert data["city"] == mock_external_business_entity_schema_object.city
    assert data["postal_code"] == mock_external_business_entity_schema_object.postal_code
    assert data["street"] == mock_external_business_entity_schema_object.street
    assert data["nip"] == mock_external_business_entity_schema_object.nip

@pytest.mark.asyncio
async def test_get_external_business_entity_unauthorized_error(
    mock_registry_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_external_business_entity_schema_object,
    mock_jwt_token,
    mock_external_business_entity_model_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisJWTNotFoundError()
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.get(
        f"/external-business-entity-module/get-external-business-entity/?external_business_entity_id={str(mock_external_business_entity_model_object.id)}",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_external_business_entity_redis_database_error(
    mock_registry_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_external_business_entity_schema_object,
    mock_jwt_token,
    mock_external_business_entity_model_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisDatabaseError()
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.return_value = mock_external_business_entity_schema_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.get(
        f"/external-business-entity-module/get-external-business-entity/?external_business_entity_id={str(mock_external_business_entity_model_object.id)}",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 500

@pytest.mark.asyncio
async def test_get_external_business_entity_not_found_error(
    mock_registry_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_external_business_entity_model_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.side_effect = PostgreSQLNotFoundError()
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.get(
        f"/external-business-entity-module/get-external-business-entity/?external_business_entity_id={str(mock_external_business_entity_model_object.id)}",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_external_business_entity_postgres_database_error(
    mock_registry_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_external_business_entity_model_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_external_business_entity_postgres_repository_object.get_external_business_entity.side_effect = PostgreSQLDatabaseError()
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.get(
        f"/external-business-entity-module/get-external-business-entity/?external_business_entity_id={str(mock_external_business_entity_model_object.id)}",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 500

#external_business_entity_router.get_all_external_business_entities()

@pytest.mark.asyncio
async def test_get_all_external_business_entities_success(
    mock_registry_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_external_business_entity_schema_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_external_business_entity_postgres_repository_object.get_all_external_business_entities.return_value = [mock_external_business_entity_schema_object, mock_external_business_entity_schema_object]
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.get(
        f"/external-business-entity-module/get-all-external-business-entities/?page=1&items_per_page=1",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_all_external_business_entities_unauthorized_error(
    mock_registry_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_external_business_entity_schema_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisJWTNotFoundError()
    mock_external_business_entity_postgres_repository_object.get_all_external_business_entities.return_value = [mock_external_business_entity_schema_object, mock_external_business_entity_schema_object]
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.get(
        f"/external-business-entity-module/get-all-external-business-entities/?page=1&items_per_page=1",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_all_external_business_entities_redis_databse_error(
    mock_registry_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_external_business_entity_schema_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisDatabaseError()
    mock_external_business_entity_postgres_repository_object.get_all_external_business_entities.return_value = [mock_external_business_entity_schema_object, mock_external_business_entity_schema_object]
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.get(
        f"/external-business-entity-module/get-all-external-business-entities/?page=1&items_per_page=1",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_get_all_external_business_not_found_error(
    mock_registry_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_external_business_entity_postgres_repository_object.get_all_external_business_entities.side_effect = PostgreSQLNotFoundError()
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.get(
        f"/external-business-entity-module/get-all-external-business-entities/?page=1&items_per_page=1",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_all_external_business_postgres_database_error(
    mock_registry_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_external_business_entity_postgres_repository_object.get_all_external_business_entities.side_effect = PostgreSQLDatabaseError()
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.get(
        f"/external-business-entity-module/get-all-external-business-entities/?page=1&items_per_page=1",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 500

#external_business_entity_router.update_external_business_entity()

@pytest.mark.asyncio
async def test_update_external_business_entities_success(
    mock_registry_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_external_business_entity_schema_object,
    mock_update_external_business_entity_model_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_external_business_entity_postgres_repository_object.update_external_business_entity.return_value = mock_external_business_entity_schema_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_update_external_business_entity_model_object.model_dump()
    response = client.patch(
        f"/external-business-entity-module/update-external-business-entity/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_update_external_business_entities_not_unique_error(
    mock_registry_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_external_business_entity_schema_object,
    mock_update_external_business_entity_model_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_external_business_entity_postgres_repository_object.update_external_business_entity.return_value = mock_external_business_entity_schema_object
    mock_external_business_entity_postgres_repository_object.is_external_business_entity_unique_beside_one_to_update.return_value = False
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_update_external_business_entity_model_object.model_dump()
    response = client.patch(
        f"/external-business-entity-module/update-external-business-entity/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    
    assert response.status_code == 409

@pytest.mark.asyncio
async def test_update_external_business_entities_unauthorized_error(
    mock_registry_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_external_business_entity_schema_object,
    mock_update_external_business_entity_model_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisJWTNotFoundError()
    mock_external_business_entity_postgres_repository_object.update_external_business_entity.return_value = mock_external_business_entity_schema_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_update_external_business_entity_model_object.model_dump()
    response = client.patch(
        f"/external-business-entity-module/update-external-business-entity/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_update_external_business_entities_redis_database_error(
    mock_registry_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_external_business_entity_schema_object,
    mock_update_external_business_entity_model_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisDatabaseError()
    mock_external_business_entity_postgres_repository_object.update_external_business_entity.return_value = mock_external_business_entity_schema_object
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_update_external_business_entity_model_object.model_dump()
    response = client.patch(
        f"/external-business-entity-module/update-external-business-entity/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_update_external_business_entities_not_found_error(
    mock_registry_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_update_external_business_entity_model_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_external_business_entity_postgres_repository_object.update_external_business_entity.side_effect = PostgreSQLNotFoundError()
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_update_external_business_entity_model_object.model_dump()
    response = client.patch(
        f"/external-business-entity-module/update-external-business-entity/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_external_business_entities_postgres_database_error(
    mock_registry_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_update_external_business_entity_model_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_external_business_entity_postgres_repository_object.update_external_business_entity.side_effect = PostgreSQLDatabaseError()
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_update_external_business_entity_model_object.model_dump()
    response = client.patch(
        f"/external-business-entity-module/update-external-business-entity/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    
    assert response.status_code == 500

#external_business_entity_router.remove_external_business_entity()

@pytest.mark.asyncio
async def test_remove_external_business_entity_success(
    mock_registry_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_external_business_entity_postgres_repository_object.remove_external_business_entity.return_value = True
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    response = client.delete(
        f"/external-business-entity-module/remove-external-business-entity/?external_business_entity_id=some_random_key",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_remove_external_business_entity_unauthorized_error(
    mock_registry_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisJWTNotFoundError()
    mock_external_business_entity_postgres_repository_object.remove_external_business_entity.return_value = True
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    response = client.delete(
        f"/external-business-entity-module/remove-external-business-entity/?external_business_entity_id=some_random_key",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 401

@pytest.mark.asyncio
async def test_remove_external_business_entity_postgres_database_error(
    mock_registry_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_external_business_entity_postgres_repository_object.remove_external_business_entity.return_value = True
    mock_registry_repository_object.return_external_business_entity_postgres_repository.side_effect = PostgreSQLDatabaseError()
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    response = client.delete(
        f"/external-business-entity-module/remove-external-business-entity/?external_business_entity_id=some_random_key",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 500

@pytest.mark.asyncio
async def test_remove_external_business_entity_entity_not_deleted_error(
    mock_registry_repository_object,
    mock_external_business_entity_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_external_business_entity_postgres_repository_object.remove_external_business_entity.return_value = False
    mock_registry_repository_object.return_external_business_entity_postgres_repository.return_value = mock_external_business_entity_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object

    response = client.delete(
        f"/external-business-entity-module/remove-external-business-entity/?external_business_entity_id=some_random_key",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 500
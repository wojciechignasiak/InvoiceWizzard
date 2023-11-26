import pytest
from app.main import app
from app.database.postgres.session.get_session import get_session
from app.database.redis.client.get_redis_client import get_redis_client
from app.database.get_repositories_registry import get_repositories_registry
from app.kafka.producer.get_kafka_producer_client import get_kafka_producer_client
from fastapi.testclient import TestClient
from app.database.redis.exceptions.custom_redis_exceptions import (
    RedisSetError, 
    RedisDatabaseError, 
    RedisNotFoundError, 
    RedisJWTNotFoundError
    )
from app.database.postgres.exceptions.custom_postgres_exceptions import (
    PostgreSQLDatabaseError, 
    PostgreSQLIntegrityError, 
    PostgreSQLNotFoundError
    )

client = TestClient(app)

# user_router.get_current_user()

@pytest.mark.asyncio
async def test_get_current_user_success(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_user_schema_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_user_postgres_repository_object.get_user_by_id.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.get(
        "/user-module/get-current-user/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(mock_user_schema_object.id)
    assert data["email"] == mock_user_schema_object.email
    assert data["first_name"] == mock_user_schema_object.first_name
    assert data["last_name"] == mock_user_schema_object.last_name
    assert data["phone_number"] == mock_user_schema_object.phone_number
    assert data["city"] == mock_user_schema_object.city
    assert data["postal_code"] == mock_user_schema_object.postal_code
    assert data["street"] == mock_user_schema_object.street
    assert data["registration_date"] == str(mock_user_schema_object.registration_date)
    assert data["last_login"] == str(mock_user_schema_object.last_login)
    assert data["email_notification"] == mock_user_schema_object.email_notification
    assert data["push_notification"] == mock_user_schema_object.push_notification

@pytest.mark.asyncio
async def test_get_current_user_unauthorized_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_user_schema_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisJWTNotFoundError()
    mock_user_postgres_repository_object.get_user_by_id.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.get(
        "/user-module/get-current-user/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_current_user_not_found_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_user_postgres_repository_object.get_user_by_id.side_effect = PostgreSQLNotFoundError()
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.get(
        "/user-module/get-current-user/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 404
    
@pytest.mark.asyncio
async def test_get_current_user_redis_database_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_user_schema_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisDatabaseError()
    mock_user_postgres_repository_object.get_user_by_id.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.get(
        "/user-module/get-current-user/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 500

@pytest.mark.asyncio
async def test_get_current_user_not_found_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_user_postgres_repository_object.get_user_by_id.side_effect = PostgreSQLDatabaseError()
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    response = client.get(
        "/user-module/get-current-user/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"})

    assert response.status_code == 500

# user_router.register_account()

@pytest.mark.asyncio
async def test_register_account_success(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_register_user_model_object,
    mock_kafka_producer_client
    ):

    mock_user_redis_repository_object.is_user_arleady_registered.return_value = False
    mock_user_redis_repository_object.create_user.return_value = True
    mock_user_postgres_repository_object.is_email_address_arleady_taken.return_value = False
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    app.dependency_overrides[get_kafka_producer_client] = lambda:mock_kafka_producer_client
    
    headers = {"Content-Type": "application/json"}
    json = mock_register_user_model_object.model_dump()
    response = client.post(
        "/user-module/register-account/", 
        headers=headers,
        json=json)
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_register_account_password_or_email_format_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_register_user_model_object,
    mock_kafka_producer_client
    ):

    mock_user_redis_repository_object.is_user_arleady_registered.return_value = False
    mock_user_redis_repository_object.create_user.return_value = True
    mock_user_postgres_repository_object.is_email_address_arleady_taken.return_value = False
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    app.dependency_overrides[get_kafka_producer_client] = lambda:mock_kafka_producer_client
    
    mock_register_user_model_object.password = "password"
    headers = {"Content-Type": "application/json"}
    json = mock_register_user_model_object.model_dump()
    response = client.post(
        "/user-module/register-account/", 
        headers=headers,
        json=json)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_register_account_email_arleady_taken_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_register_user_model_object,
    mock_kafka_producer_client
    ):

    mock_user_redis_repository_object.is_user_arleady_registered.return_value = False
    mock_user_redis_repository_object.create_user.return_value = True
    mock_user_postgres_repository_object.is_email_address_arleady_taken.return_value = True
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    app.dependency_overrides[get_kafka_producer_client] = lambda:mock_kafka_producer_client
    
    headers = {"Content-Type": "application/json"}
    json = mock_register_user_model_object.model_dump()
    response = client.post(
        "/user-module/register-account/", 
        headers=headers,
        json=json)
    assert response.status_code == 409

@pytest.mark.asyncio
async def test_register_account_email_arleady_registered_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_register_user_model_object,
    mock_kafka_producer_client
    ):

    mock_user_redis_repository_object.is_user_arleady_registered.return_value = True
    mock_user_redis_repository_object.create_user.return_value = True
    mock_user_postgres_repository_object.is_email_address_arleady_taken.return_value = False
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    app.dependency_overrides[get_kafka_producer_client] = lambda:mock_kafka_producer_client
    
    headers = {"Content-Type": "application/json"}
    json = mock_register_user_model_object.model_dump()
    response = client.post(
        "/user-module/register-account/", 
        headers=headers,
        json=json)
    assert response.status_code == 409

@pytest.mark.asyncio
async def test_register_account_create_user_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_register_user_model_object,
    mock_kafka_producer_client
    ):

    mock_user_redis_repository_object.is_user_arleady_registered.return_value = False
    mock_user_redis_repository_object.create_user.side_effect = RedisSetError()
    mock_user_postgres_repository_object.is_email_address_arleady_taken.return_value = False
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    app.dependency_overrides[get_kafka_producer_client] = lambda:mock_kafka_producer_client
    
    headers = {"Content-Type": "application/json"}
    json = mock_register_user_model_object.model_dump()
    response = client.post(
        "/user-module/register-account/", 
        headers=headers,
        json=json)
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_register_account_redis_database_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_register_user_model_object,
    mock_kafka_producer_client
    ):

    mock_user_redis_repository_object.is_user_arleady_registered.return_value = False
    mock_user_redis_repository_object.create_user.side_effect = RedisDatabaseError()
    mock_user_postgres_repository_object.is_email_address_arleady_taken.return_value = False
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    app.dependency_overrides[get_kafka_producer_client] = lambda:mock_kafka_producer_client
    
    headers = {"Content-Type": "application/json"}
    json = mock_register_user_model_object.model_dump()
    response = client.post(
        "/user-module/register-account/", 
        headers=headers,
        json=json)
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_register_account_postgres_database_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_register_user_model_object,
    mock_kafka_producer_client
    ):

    mock_user_redis_repository_object.is_user_arleady_registered.return_value = False
    mock_user_redis_repository_object.create_user.return_value = True
    mock_user_postgres_repository_object.is_email_address_arleady_taken.side_effect = PostgreSQLDatabaseError()
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    app.dependency_overrides[get_kafka_producer_client] = lambda:mock_kafka_producer_client
    
    headers = {"Content-Type": "application/json"}
    json = mock_register_user_model_object.model_dump()
    response = client.post(
        "/user-module/register-account/", 
        headers=headers,
        json=json)
    assert response.status_code == 500

# user_router.confirm_account()

@pytest.mark.asyncio
async def test_confirm_account_success(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_kafka_producer_client,
    mock_create_user_model_object,
    mock_user_schema_object
    ):

    mock_user_redis_repository_object.search_user_by_id.return_value = bytes(mock_create_user_model_object.model_dump_json(), "utf-8")
    mock_user_redis_repository_object.delete_user_by_id.return_value = True
    mock_user_postgres_repository_object.create_user.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    app.dependency_overrides[get_kafka_producer_client] = lambda:mock_kafka_producer_client
    
    headers = {"Content-Type": "application/json"}
    response = client.patch(
        f"/user-module/confirm-account/?id={str(mock_user_schema_object.id)}", 
        headers=headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_confirm_account_user_not_found_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_kafka_producer_client,
    mock_user_schema_object
    ):

    mock_user_redis_repository_object.search_user_by_id.side_effect = RedisNotFoundError()
    mock_user_redis_repository_object.delete_user_by_id.return_value = True
    mock_user_postgres_repository_object.create_user.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    app.dependency_overrides[get_kafka_producer_client] = lambda:mock_kafka_producer_client
    
    headers = {"Content-Type": "application/json"}
    response = client.patch(
        f"/user-module/confirm-account/?id={str(mock_user_schema_object.id)}", 
        headers=headers)
    
    print(response.json())
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_confirm_account_postgres_integrity_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_kafka_producer_client,
    mock_create_user_model_object,
    mock_user_schema_object
    ):

    mock_user_redis_repository_object.search_user_by_id.return_value = bytes(mock_create_user_model_object.model_dump_json(), "utf-8")
    mock_user_redis_repository_object.delete_user_by_id.return_value = True
    mock_user_postgres_repository_object.create_user.side_effect = PostgreSQLIntegrityError()
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    app.dependency_overrides[get_kafka_producer_client] = lambda:mock_kafka_producer_client
    
    headers = {"Content-Type": "application/json"}
    response = client.patch(
        f"/user-module/confirm-account/?id={str(mock_user_schema_object.id)}", 
        headers=headers)
    assert response.status_code == 409

@pytest.mark.asyncio
async def test_confirm_account_postgres_database_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_kafka_producer_client,
    mock_create_user_model_object,
    mock_user_schema_object
    ):

    mock_user_redis_repository_object.search_user_by_id.return_value = bytes(mock_create_user_model_object.model_dump_json(), "utf-8")
    mock_user_redis_repository_object.delete_user_by_id.return_value = True
    mock_user_postgres_repository_object.create_user.side_effect = PostgreSQLDatabaseError()
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    app.dependency_overrides[get_kafka_producer_client] = lambda:mock_kafka_producer_client
    
    headers = {"Content-Type": "application/json"}
    response = client.patch(
        f"/user-module/confirm-account/?id={str(mock_user_schema_object.id)}", 
        headers=headers)
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_confirm_account_redis_database_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_kafka_producer_client,
    mock_user_schema_object
    ):

    mock_user_redis_repository_object.search_user_by_id.side_effect = RedisDatabaseError()
    mock_user_redis_repository_object.delete_user_by_id.return_value = True
    mock_user_postgres_repository_object.create_user.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    app.dependency_overrides[get_kafka_producer_client] = lambda:mock_kafka_producer_client
    
    headers = {"Content-Type": "application/json"}
    response = client.patch(
        f"/user-module/confirm-account/?id={str(mock_user_schema_object.id)}", 
        headers=headers)
    assert response.status_code == 500

# user_router.log_in()

@pytest.mark.asyncio
async def test_log_in_success(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_user_schema_object,
    mock_create_user_model_object
    ):

    mock_user_redis_repository_object.save_jwt.return_value = True
    mock_user_postgres_repository_object.get_user_by_email_address.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    headers = {"Content-Type": "application/json"}
    response = client.get(
        f"/user-module/log-in/?email={mock_create_user_model_object.email}&password={mock_create_user_model_object.password}&remember_me={True}",
        headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["jwt_token"]

@pytest.mark.asyncio
async def test_log_in_user_not_found_by_email_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_create_user_model_object
    ):

    mock_user_redis_repository_object.save_jwt.return_value = True
    mock_user_postgres_repository_object.get_user_by_email_address.side_effect = PostgreSQLNotFoundError()
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    headers = {"Content-Type": "application/json"}
    response = client.get(
        f"/user-module/log-in/?email={mock_create_user_model_object.email}&password={mock_create_user_model_object.password}&remember_me={True}",
        headers=headers)
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_log_in_jwt_not_saved_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_user_schema_object,
    mock_create_user_model_object
    ):

    mock_user_redis_repository_object.save_jwt.side_effect = RedisSetError()
    mock_user_postgres_repository_object.get_user_by_email_address.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    headers = {"Content-Type": "application/json"}
    response = client.get(
        f"/user-module/log-in/?email={mock_create_user_model_object.email}&password={mock_create_user_model_object.password}&remember_me={True}",
        headers=headers)
    
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_log_in_postgres_database_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_create_user_model_object
    ):

    mock_user_redis_repository_object.save_jwt.return_value = True
    mock_user_postgres_repository_object.get_user_by_email_address.side_effect = PostgreSQLDatabaseError()
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    headers = {"Content-Type": "application/json"}
    response = client.get(
        f"/user-module/log-in/?email={mock_create_user_model_object.email}&password={mock_create_user_model_object.password}&remember_me={True}",
        headers=headers)
    
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_log_in_redis_database_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_user_schema_object,
    mock_create_user_model_object
    ):

    mock_user_redis_repository_object.save_jwt.side_effect = RedisDatabaseError()
    mock_user_postgres_repository_object.get_user_by_email_address.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    headers = {"Content-Type": "application/json"}
    response = client.get(
        f"/user-module/log-in/?email={mock_create_user_model_object.email}&password={mock_create_user_model_object.password}&remember_me={True}",
        headers=headers)
    
    assert response.status_code == 500

# user_router.update_personal_information()

@pytest.mark.asyncio
async def test_update_personal_information_success(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_user_schema_object,
    mock_jwt_payload_model_object,
    mock_user_personal_information_model_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_user_postgres_repository_object.update_user_personal_information.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_user_personal_information_model_object.model_dump()
    response = client.patch(
        "/user-module/update-personal-information/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_update_personal_information_unauthorized_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_user_schema_object,
    mock_user_personal_information_model_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisJWTNotFoundError()
    mock_user_postgres_repository_object.update_user_personal_information.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_user_personal_information_model_object.model_dump()
    response = client.patch(
        "/user-module/update-personal-information/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_update_personal_information_user_not_found_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_user_personal_information_model_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_user_postgres_repository_object.update_user_personal_information.side_effect = PostgreSQLNotFoundError()
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_user_personal_information_model_object.model_dump()
    response = client.patch(
        "/user-module/update-personal-information/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_personal_information_redis_database_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_user_schema_object,
    mock_user_personal_information_model_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisDatabaseError()
    mock_user_postgres_repository_object.update_user_personal_information.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_user_personal_information_model_object.model_dump()
    response = client.patch(
        "/user-module/update-personal-information/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_update_personal_information_postgres_database_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_user_personal_information_model_object,
    mock_jwt_token
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_user_postgres_repository_object.update_user_personal_information.side_effect = PostgreSQLDatabaseError()
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_user_personal_information_model_object.model_dump()
    response = client.patch(
        "/user-module/update-personal-information/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    
    assert response.status_code == 500

# user_router.change_email_address()

@pytest.mark.asyncio
async def test_change_email_address_success(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_user_schema_object,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_update_user_email_model_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_user_redis_repository_object.save_new_email.return_value = True
    mock_user_postgres_repository_object.get_user_by_id.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_update_user_email_model_object.model_dump()
    response = client.put(
        "/user-module/change-email-address/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_change_email_address_unauthorized_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_user_schema_object,
    mock_jwt_token,
    mock_update_user_email_model_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisJWTNotFoundError()
    mock_user_redis_repository_object.save_new_email.return_value = True
    mock_user_postgres_repository_object.get_user_by_id.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_update_user_email_model_object.model_dump()
    response = client.put(
        "/user-module/change-email-address/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_change_email_address_new_email_not_saved_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_user_schema_object,
    mock_jwt_token,
    mock_update_user_email_model_object,
    mock_jwt_payload_model_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_user_redis_repository_object.save_new_email.side_effect = RedisSetError()
    mock_user_postgres_repository_object.get_user_by_id.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_update_user_email_model_object.model_dump()
    response = client.put(
        "/user-module/change-email-address/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_change_email_address_user_not_found_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_update_user_email_model_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_user_redis_repository_object.save_new_email.return_value = True
    mock_user_postgres_repository_object.get_user_by_id.side_effect = PostgreSQLNotFoundError()
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_update_user_email_model_object.model_dump()
    response = client.put(
        "/user-module/change-email-address/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_change_email_address_postgres_database_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_update_user_email_model_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_user_redis_repository_object.save_new_email.return_value = True
    mock_user_postgres_repository_object.get_user_by_id.side_effect = PostgreSQLDatabaseError()
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_update_user_email_model_object.model_dump()
    response = client.put(
        "/user-module/change-email-address/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    print(response.content)
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_change_email_address_redis_database_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_update_user_email_model_object,
    mock_user_schema_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_user_redis_repository_object.save_new_email.side_effect = RedisDatabaseError()
    mock_user_postgres_repository_object.get_user_by_id.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_update_user_email_model_object.model_dump()
    response = client.put(
        "/user-module/change-email-address/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    print(response.content)
    assert response.status_code == 500

# user_router.confirm_email_address_change()

@pytest.mark.asyncio
async def test_confirm_email_address_change_success(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_user_schema_object,
    mock_confirmed_user_email_change_model_object
    ):

    mock_user_redis_repository_object.retrieve_new_email.return_value = bytes(mock_confirmed_user_email_change_model_object.model_dump_json(), "utf-8")
    mock_user_postgres_repository_object.is_email_address_arleady_taken.return_value = False
    mock_user_postgres_repository_object.update_user_email_address.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    redis_key_id = "some-redis-key-id"
    response = client.patch(f"/user-module/confirm-email-address-change/?id={redis_key_id}")
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_confirm_email_address_change_email_not_found_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_user_schema_object
    ):

    mock_user_redis_repository_object.retrieve_new_email.side_effect = RedisNotFoundError()
    mock_user_postgres_repository_object.is_email_address_arleady_taken.return_value = False
    mock_user_postgres_repository_object.update_user_email_address.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    redis_key_id = "some-redis-key-id"
    response = client.patch(f"/user-module/confirm-email-address-change/?id={redis_key_id}")
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_confirm_email_address_change_email_arleady_in_use_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_user_schema_object,
    mock_confirmed_user_email_change_model_object
    ):

    mock_user_redis_repository_object.retrieve_new_email.return_value = bytes(mock_confirmed_user_email_change_model_object.model_dump_json(), "utf-8")
    mock_user_postgres_repository_object.is_email_address_arleady_taken.side_effect = PostgreSQLIntegrityError()
    mock_user_postgres_repository_object.update_user_email_address.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    redis_key_id = "some-redis-key-id"
    response = client.patch(f"/user-module/confirm-email-address-change/?id={redis_key_id}")
    
    assert response.status_code == 409

@pytest.mark.asyncio
async def test_confirm_email_address_change_user_not_found_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_confirmed_user_email_change_model_object
    ):

    mock_user_redis_repository_object.retrieve_new_email.return_value = bytes(mock_confirmed_user_email_change_model_object.model_dump_json(), "utf-8")
    mock_user_postgres_repository_object.is_email_address_arleady_taken.return_value = False
    mock_user_postgres_repository_object.update_user_email_address.side_effect = PostgreSQLNotFoundError()
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    redis_key_id = "some-redis-key-id"
    response = client.patch(f"/user-module/confirm-email-address-change/?id={redis_key_id}")
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_confirm_email_address_change_redis_database_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_user_schema_object
    ):

    mock_user_redis_repository_object.retrieve_new_email.side_effect = RedisDatabaseError()
    mock_user_postgres_repository_object.is_email_address_arleady_taken.return_value = False
    mock_user_postgres_repository_object.update_user_email_address.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    redis_key_id = "some-redis-key-id"
    response = client.patch(f"/user-module/confirm-email-address-change/?id={redis_key_id}")
    
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_confirm_email_address_change_postgres_database_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_confirmed_user_email_change_model_object
    ):

    mock_user_redis_repository_object.retrieve_new_email.return_value = bytes(mock_confirmed_user_email_change_model_object.model_dump_json(), "utf-8")
    mock_user_postgres_repository_object.is_email_address_arleady_taken.return_value = False
    mock_user_postgres_repository_object.update_user_email_address.side_effect = PostgreSQLDatabaseError()
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    redis_key_id = "some-redis-key-id"
    response = client.patch(f"/user-module/confirm-email-address-change/?id={redis_key_id}")
    
    assert response.status_code == 500

# user_router.change_password()

@pytest.mark.asyncio
async def test_change_password_success(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_user_schema_object,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_update_user_password_model_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_user_redis_repository_object.save_new_password.return_value = True
    mock_user_postgres_repository_object.get_user_by_id.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_update_user_password_model_object.model_dump()
    response = client.put(
        "/user-module/change-password/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_change_password_password_format_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_user_schema_object,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_update_user_password_model_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_user_redis_repository_object.save_new_password.return_value = True
    mock_user_postgres_repository_object.get_user_by_id.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    mock_update_user_password_model_object.new_password = "password"
    json = mock_update_user_password_model_object.model_dump()
    response = client.put(
        "/user-module/change-password/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_change_password_unauthorized_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_user_schema_object,
    mock_jwt_token,
    mock_update_user_password_model_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.side_effect = RedisJWTNotFoundError()
    mock_user_redis_repository_object.save_new_password.return_value = True
    mock_user_postgres_repository_object.get_user_by_id.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_update_user_password_model_object.model_dump()
    response = client.put(
        "/user-module/change-password/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_change_password_save_new_password_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_user_schema_object,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_update_user_password_model_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_user_redis_repository_object.save_new_password.side_effect = RedisSetError()
    mock_user_postgres_repository_object.get_user_by_id.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_update_user_password_model_object.model_dump()
    response = client.put(
        "/user-module/change-password/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_change_password_user_not_found_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_update_user_password_model_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_user_redis_repository_object.save_new_password.return_value = True
    mock_user_postgres_repository_object.get_user_by_id.side_effect = PostgreSQLNotFoundError()
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_update_user_password_model_object.model_dump()
    response = client.put(
        "/user-module/change-password/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_change_password_redis_database_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_user_schema_object,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_update_user_password_model_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_user_redis_repository_object.save_new_password.side_effect = RedisDatabaseError()
    mock_user_postgres_repository_object.get_user_by_id.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_update_user_password_model_object.model_dump()
    response = client.put(
        "/user-module/change-password/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_change_password_user_postgres_database_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_jwt_payload_model_object,
    mock_jwt_token,
    mock_update_user_password_model_object
    ):

    mock_user_redis_repository_object.retrieve_jwt.return_value = bytes(mock_jwt_payload_model_object.model_dump_json(), "utf-8")
    mock_user_redis_repository_object.save_new_password.return_value = True
    mock_user_postgres_repository_object.get_user_by_id.side_effect = PostgreSQLDatabaseError()
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_update_user_password_model_object.model_dump()
    response = client.put(
        "/user-module/change-password/",
        headers={"Authorization": f"Bearer {str(mock_jwt_token)}"},
        json=json)
    
    assert response.status_code == 500

# user_router.confirm_password_change()

@pytest.mark.asyncio
async def test_confirm_password_change_success(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_user_schema_object,
    mock_confirmed_user_password_change_model_object
    ):

    mock_user_redis_repository_object.retrieve_new_password.return_value = bytes(mock_confirmed_user_password_change_model_object.model_dump_json(), "utf-8")
    mock_user_postgres_repository_object.update_user_password.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    redis_key_id = "some-redis-key-id"
    response = client.patch(f"/user-module/confirm-password-change/?id={redis_key_id}")
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_confirm_password_change_new_password_not_found_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_user_schema_object
    ):

    mock_user_redis_repository_object.retrieve_new_password.side_effect = RedisNotFoundError()
    mock_user_postgres_repository_object.update_user_password.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    redis_key_id = "some-redis-key-id"
    response = client.patch(f"/user-module/confirm-password-change/?id={redis_key_id}")
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_confirm_password_change_user_not_found_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_confirmed_user_password_change_model_object
    ):

    mock_user_redis_repository_object.retrieve_new_password.return_value = bytes(mock_confirmed_user_password_change_model_object.model_dump_json(), "utf-8")
    mock_user_postgres_repository_object.update_user_password.side_effect = PostgreSQLNotFoundError()
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    redis_key_id = "some-redis-key-id"
    response = client.patch(f"/user-module/confirm-password-change/?id={redis_key_id}")
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_confirm_password_change_redis_database_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_user_schema_object
    ):

    mock_user_redis_repository_object.retrieve_new_password.side_effect = RedisDatabaseError()
    mock_user_postgres_repository_object.update_user_password.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    redis_key_id = "some-redis-key-id"
    response = client.patch(f"/user-module/confirm-password-change/?id={redis_key_id}")
    
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_confirm_password_change_postgres_database_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_confirmed_user_password_change_model_object
    ):

    mock_user_redis_repository_object.retrieve_new_password.return_value = bytes(mock_confirmed_user_password_change_model_object.model_dump_json(), "utf-8")
    mock_user_postgres_repository_object.update_user_password.side_effect = PostgreSQLDatabaseError()
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    redis_key_id = "some-redis-key-id"
    response = client.patch(f"/user-module/confirm-password-change/?id={redis_key_id}")
    
    assert response.status_code == 500

# user_router.reset_password()

@pytest.mark.asyncio
async def test_reset_password_success(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_user_schema_object,
    mock_reset_user_password_model_object
    ):

    mock_user_redis_repository_object.save_new_password.return_value = True
    mock_user_postgres_repository_object.get_user_by_email_address.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_reset_user_password_model_object.model_dump()
    response = client.put(
        "/user-module/reset-password/",
        json=json)

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_reset_password_bad_password_format(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_user_schema_object,
    mock_reset_user_password_model_object
    ):

    mock_user_redis_repository_object.save_new_password.return_value = True
    mock_user_postgres_repository_object.get_user_by_email_address.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    mock_reset_user_password_model_object.new_password = "password"
    json = mock_reset_user_password_model_object.model_dump()
    response = client.put(
        "/user-module/reset-password/",
        json=json)

    assert response.status_code == 400

@pytest.mark.asyncio
async def test_reset_password_save_new_password_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_user_schema_object,
    mock_reset_user_password_model_object
    ):

    mock_user_redis_repository_object.save_new_password.side_effect = RedisSetError()
    mock_user_postgres_repository_object.get_user_by_email_address.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_reset_user_password_model_object.model_dump()
    response = client.put(
        "/user-module/reset-password/",
        json=json)
    
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_reset_password_user_not_found_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_reset_user_password_model_object
    ):

    mock_user_redis_repository_object.save_new_password.return_value = True
    mock_user_postgres_repository_object.get_user_by_email_address.side_effect = PostgreSQLNotFoundError()
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_reset_user_password_model_object.model_dump()
    response = client.put(
        "/user-module/reset-password/",
        json=json)
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_reset_password_redis_database_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_user_schema_object,
    mock_reset_user_password_model_object
    ):

    mock_user_redis_repository_object.save_new_password.side_effect = RedisDatabaseError()
    mock_user_postgres_repository_object.get_user_by_email_address.return_value = mock_user_schema_object
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_reset_user_password_model_object.model_dump()
    response = client.put(
        "/user-module/reset-password/",
        json=json)
    
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_reset_password_user_postgres_database_error(
    mock_registry_repository_object,
    mock_user_postgres_repository_object,
    mock_user_redis_repository_object,
    mock_redis_client,
    mock_postgres_async_session,
    mock_reset_user_password_model_object
    ):

    mock_user_redis_repository_object.save_new_password.return_value = True
    mock_user_postgres_repository_object.get_user_by_email_address.side_effect = PostgreSQLDatabaseError()
    mock_registry_repository_object.return_user_postgres_repository.return_value = mock_user_postgres_repository_object
    mock_registry_repository_object.return_user_redis_repository.return_value = mock_user_redis_repository_object

    app.dependency_overrides[get_session] = lambda:mock_postgres_async_session
    app.dependency_overrides[get_redis_client] = lambda:mock_redis_client
    app.dependency_overrides[get_repositories_registry] = lambda:mock_registry_repository_object
    
    json = mock_reset_user_password_model_object.model_dump()
    response = client.put(
        "/user-module/reset-password/",
        json=json)
    
    assert response.status_code == 500
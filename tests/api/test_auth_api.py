"""API tests for authentication endpoints."""


def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@test.com",
            "username": "newuser",
            "full_name": "New User",
            "password": "password123",
            "role": "agent",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@test.com"
    assert data["username"] == "newuser"
    assert data["role"] == "agent"
    assert "id" in data


def test_register_duplicate_email(client, test_user):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "agent@test.com",
            "username": "differentuser",
            "full_name": "Another User",
            "password": "password123",
        },
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_register_duplicate_username(client, test_user):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "different@test.com",
            "username": "testagent",
            "full_name": "Another User",
            "password": "password123",
        },
    )
    assert response.status_code == 400
    assert "already taken" in response.json()["detail"]


def test_login_success(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testagent", "password": "testpass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testagent", "password": "wrongpass"},
    )
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "noone", "password": "pass"},
    )
    assert response.status_code == 401


def test_refresh_token(client, test_user):
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "testagent", "password": "testpass123"},
    )
    refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_refresh_token_invalid(client):
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid-token"},
    )
    assert response.status_code == 401

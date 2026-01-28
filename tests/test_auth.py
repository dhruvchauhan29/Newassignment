"""Test authentication endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    """Test user registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    """Test user login."""
    # Register user first
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
        },
    )

    # Login
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient):
    """Test get current user."""
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
        },
    )

    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword123",
        },
    )
    token = login_response.json()["access_token"]

    # Get current user
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"

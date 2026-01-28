"""Test project endpoints."""
import pytest
from httpx import AsyncClient


async def get_auth_token(client: AsyncClient) -> str:
    """Helper to get authentication token."""
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
    return login_response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_project(client: AsyncClient):
    """Test project creation."""
    token = await get_auth_token(client)

    response = await client.post(
        "/api/v1/projects/",
        json={
            "name": "Test Project",
            "description": "A test project",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_projects(client: AsyncClient):
    """Test listing projects."""
    token = await get_auth_token(client)

    # Create a project
    await client.post(
        "/api/v1/projects/",
        json={"name": "Test Project"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # List projects
    response = await client.get(
        "/api/v1/projects/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Project"


@pytest.mark.asyncio
async def test_get_project(client: AsyncClient):
    """Test getting a specific project."""
    token = await get_auth_token(client)

    # Create a project
    create_response = await client.post(
        "/api/v1/projects/",
        json={"name": "Test Project"},
        headers={"Authorization": f"Bearer {token}"},
    )
    project_id = create_response.json()["id"]

    # Get project
    response = await client.get(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == "Test Project"


@pytest.mark.asyncio
async def test_update_project(client: AsyncClient):
    """Test updating a project."""
    token = await get_auth_token(client)

    # Create a project
    create_response = await client.post(
        "/api/v1/projects/",
        json={"name": "Test Project"},
        headers={"Authorization": f"Bearer {token}"},
    )
    project_id = create_response.json()["id"]

    # Update project
    response = await client.put(
        f"/api/v1/projects/{project_id}",
        json={"name": "Updated Project"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Project"


@pytest.mark.asyncio
async def test_delete_project(client: AsyncClient):
    """Test deleting a project."""
    token = await get_auth_token(client)

    # Create a project
    create_response = await client.post(
        "/api/v1/projects/",
        json={"name": "Test Project"},
        headers={"Authorization": f"Bearer {token}"},
    )
    project_id = create_response.json()["id"]

    # Delete project
    response = await client.delete(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204

    # Verify deletion
    get_response = await client.get(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_response.status_code == 404

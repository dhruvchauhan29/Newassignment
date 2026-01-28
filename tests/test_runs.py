"""Test run endpoints."""
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


async def create_project(client: AsyncClient, token: str) -> int:
    """Helper to create a project."""
    response = await client.post(
        "/api/v1/projects/",
        json={"name": "Test Project"},
        headers={"Authorization": f"Bearer {token}"},
    )
    return response.json()["id"]


@pytest.mark.asyncio
async def test_create_run(client: AsyncClient):
    """Test run creation."""
    token = await get_auth_token(client)
    project_id = await create_project(client, token)

    response = await client.post(
        "/api/v1/runs/",
        json={
            "project_id": project_id,
            "product_idea": "A revolutionary AI-powered task management app",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["product_idea"] == "A revolutionary AI-powered task management app"
    assert data["status"] == "pending"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_run(client: AsyncClient):
    """Test getting a specific run."""
    token = await get_auth_token(client)
    project_id = await create_project(client, token)

    # Create a run
    create_response = await client.post(
        "/api/v1/runs/",
        json={
            "project_id": project_id,
            "product_idea": "A revolutionary AI-powered task management app",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    run_id = create_response.json()["id"]

    # Get run
    response = await client.get(
        f"/api/v1/runs/{run_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == run_id


@pytest.mark.asyncio
async def test_list_project_runs(client: AsyncClient):
    """Test listing runs for a project."""
    token = await get_auth_token(client)
    project_id = await create_project(client, token)

    # Create a run
    await client.post(
        "/api/v1/runs/",
        json={
            "project_id": project_id,
            "product_idea": "A revolutionary AI-powered task management app",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    # List runs
    response = await client.get(
        f"/api/v1/runs/project/{project_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

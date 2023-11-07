import pytest
from fastapi import BackgroundTasks
from httpx import AsyncClient


async def register_user(async_client: AsyncClient, email: str, password: str):
    return await async_client.post(
        "/register", json={"email": email, "password": password}
    )


@pytest.mark.anyio
async def test_register_user(async_client: AsyncClient):
    response = await register_user(async_client, "test@example", "test")
    assert response.status_code == 201
    assert "User created" in response.json().get("detail")


@pytest.mark.anyio
async def test_register_user_already_exists(
    async_client: AsyncClient, confirmed_user: dict
):
    response = await register_user(
        async_client, confirmed_user["email"], confirmed_user["password"]
    )
    assert response.status_code == 400
    assert (
        f"User with email {confirmed_user['email']} already exists"
        in response.json().get("detail")
    )


@pytest.mark.anyio
async def test_confirm_user(async_client: AsyncClient, mocker):
    spy = mocker.spy(BackgroundTasks, "add_task")
    await register_user(async_client, "test@example.com", "test")
    confirmation_url = str(spy.call_args[1].get("confirmation_url"))
    response = await async_client.get(confirmation_url)
    assert response.status_code == 200
    assert "User confirmed" in response.json().get("detail")


@pytest.mark.anyio
async def test_confirm_user_invalid_token(async_client: AsyncClient):
    response = await async_client.get("/confirm/invalid")
    assert response.status_code == 401
    assert "Invalid token" in response.json().get("detail")


@pytest.mark.anyio
async def test_confirm_user_expired_token(async_client: AsyncClient, mocker):
    mocker.patch(
        "socialmedia.security.confirmation_token_expire_minutes", return_value=-1
    )
    spy = mocker.spy(BackgroundTasks, "add_task")
    await register_user(async_client, "test@example.com", "test")
    confirmation_url = str(spy.call_args[1].get("confirmation_url"))
    response = await async_client.get(confirmation_url)
    assert response.status_code == 401
    assert "Token has been expired" in response.json().get("detail")


@pytest.mark.anyio
async def test_login_user_not_exist(async_client: AsyncClient):
    response = await async_client.post(
        "/token", json={"email": "test@example", "password": "test"}
    )
    assert response.status_code == 401
    assert "detail" in response.json()
    assert "Invalid email or password" in response.json().get("detail")


@pytest.mark.anyio
async def test_login_user_not_confirmed(
    async_client: AsyncClient, registered_user: dict
):
    response = await async_client.post("/token", json=registered_user)
    assert response.status_code == 401
    assert "detail" in response.json()
    assert "Please confirm your email" in response.json().get("detail")


@pytest.mark.anyio
async def test_login_user(async_client: AsyncClient, confirmed_user: dict):
    response = await async_client.post(
        "/token",
        json={
            "email": confirmed_user["email"],
            "password": confirmed_user["password"],
        },
    )
    assert response.status_code == 201
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert "bearer" in response.json().get("token_type")

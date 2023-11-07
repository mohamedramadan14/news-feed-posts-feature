"""
Fixtures for testing with pytest is way to share data between multiple tests.
"""

import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, Request, Response

# from socialmedia.routers.post import comments_table , post_table

os.environ["ENV_STATE"] = "test"

from socialmedia.database import database, user_table  # noqa: E402
from socialmedia.main import app  # noqa: E402


@pytest.fixture(
    scope="session"
)  # scope=session : means it runs once for an entire test session
def anyio_backend():
    return "asyncio"  # when we use any async function in tests env we need an async backend like platform to runs functions(async) on it


# 1- create testClient to interact with instead of starting fastAPI app : this is like mocked env of fastAPI for testing


@pytest.fixture()
def client() -> Generator:
    yield TestClient(
        app
    )  # we yield instead of return to make it async and to do work before it or after it if we want


# 2- clear db tables before each test


@pytest.fixture(
    autouse=True
)  # autouse : to make it run on starting of running of every test
async def db() -> AsyncGenerator:
    await database.connect()
    yield
    await database.disconnect()


# 3- create async client to make test runs in an async manner
@pytest.fixture()
async def async_client(
    client,
) -> AsyncGenerator:  # client here is name of fixture this a shape of dependency injection
    async with AsyncClient(app=app, base_url=client.base_url) as ac:
        yield ac


@pytest.fixture()
async def registered_user(async_client: AsyncClient) -> dict:
    user_details = {"email": "test@example.com", "password": "test"}
    await async_client.post("/register", json=user_details)
    query = user_table.select().where(user_table.c.email == user_details["email"])
    user = await database.fetch_one(query)
    user_details["id"] = user.id
    return user_details


@pytest.fixture()
async def confirmed_user(registered_user: dict) -> dict:
    query = (
        user_table.update()
        .where(user_table.c.email == registered_user["email"])
        .values(is_confirmed=True)
    )
    await database.execute(query)

    # registered_user["is_confirmed"] = True
    return registered_user


@pytest.fixture()
async def logged_in_token(async_client: AsyncClient, confirmed_user: dict) -> str:
    response = await async_client.post(
        "/token",
        json=confirmed_user,
    )
    return response.json().get("access_token")


@pytest.fixture(autouse=True)
def mock_httpx_client(mocker):
    mocked_client = mocker.patch("socialmedia.tasks.httpx.AsyncClient")
    mocked_async_client = Mock()
    response = Response(status_code=200, content="", request=Request("POST", "//"))
    mocked_async_client.post = AsyncMock(return_value=response)
    mocked_client.return_value.__aenter__.return_value = mocked_async_client
    return mocked_async_client
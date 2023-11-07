import pytest
from httpx import AsyncClient

from socialmedia import security


async def create_post(
    body: str, async_client: AsyncClient, confirmed_user: dict, logged_in_token: str
) -> dict:
    response = await async_client.post(
        "/post",
        json={"body": body, "user_id": confirmed_user["id"], "image_url": None},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    return response.json()


async def create_comment(
    body: str,
    post_id: int,
    async_client: AsyncClient,
    confirmed_user: dict,
    logged_in_token: str,
) -> dict:
    response = await async_client.post(
        "/comment",
        json={"body": body, "post_id": post_id, "user_id": confirmed_user["id"]},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    return response.json()


@pytest.fixture()
async def created_comment(
    async_client: AsyncClient,
    created_post: dict,
    registered_user: dict,
    logged_in_token: str,
):
    return await create_comment(
        "Test Comment",
        created_post["id"],
        async_client,
        registered_user,
        logged_in_token,
    )


@pytest.fixture()
async def created_post(
    async_client: AsyncClient, registered_user: dict, logged_in_token: str
):
    return await create_post(
        "My first post", async_client, registered_user, logged_in_token
    )


@pytest.mark.anyio
async def test_create_post(
    async_client: AsyncClient, confirmed_user: dict, logged_in_token: str
):
    body = "Test Post /post endpoint"
    response = await async_client.post(
        "/post",
        json={"body": body, "user_id": confirmed_user["id"], "image_url": None},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    assert response.status_code == 201
    assert {"id": 1, "body": body}.items() <= response.json().items()


# mocker : allows us to modify functionality of a function in our code
@pytest.mark.anyio
async def test_create_post_expired_token(
    async_client: AsyncClient, confirmed_user: dict, mocker
):
    mocker.patch("socialmedia.security.access_token_expire_minutes", return_value=-1)
    token = security.create_access_token(confirmed_user["email"])
    response = await async_client.post(
        "/post",
        json={"body": "Test Post /post endpoint", "user_id": confirmed_user["id"]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401
    assert "Token has been expired" in response.json().get("detail")


@pytest.mark.anyio
async def test_create_post_no_body(async_client: AsyncClient, logged_in_token: str):
    response = await async_client.post(
        "/post", json={}, headers={"Authorization": f"Bearer {logged_in_token}"}
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_like_post(
    async_client: AsyncClient, created_post: dict, logged_in_token: str
):
    response = await async_client.post(
        "/like",
        json={"post_id": created_post["id"]},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    assert response.status_code == 201
    assert {"post_id": created_post["id"]}.items() <= response.json().items()


@pytest.mark.anyio
async def test_get_all_posts(async_client: AsyncClient, created_post: dict):
    response = await async_client.get("/post")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert created_post.items() <= response.json()[0].items()


@pytest.mark.anyio
@pytest.mark.parametrize("sorting , expected_order", [("new", [2, 1]), ("old", [1, 2])])
async def test_get_all_posts_sorting(
    async_client: AsyncClient,
    registered_user: dict,
    logged_in_token: str,
    sorting: str,
    expected_order: list[int],
):
    await create_post(
        "Post 1", async_client, registered_user, logged_in_token=logged_in_token
    )
    await create_post(
        "Post 2", async_client, registered_user, logged_in_token=logged_in_token
    )
    response = await async_client.get("/post", params={"sorting": sorting})
    data = response.json()

    post_ids = [post["id"] for post in data]
    assert response.status_code == 200
    assert post_ids == expected_order


@pytest.mark.anyio
async def test_get_all_posts_sort_likes(
    async_client: AsyncClient,
    registered_user: dict,
    logged_in_token: str,
):
    await create_post(
        "Post 1", async_client, registered_user, logged_in_token=logged_in_token
    )
    await create_post(
        "Post 2", async_client, registered_user, logged_in_token=logged_in_token
    )
    await like_post(1, async_client, logged_in_token)
    response = await async_client.get("/post", params={"sorting": "most_liked"})
    data = response.json()
    expected_order = [1, 2]
    post_ids = [post["id"] for post in data]
    assert response.status_code == 200
    assert post_ids == expected_order


@pytest.mark.anyio
async def test_get_all_posts_wrong_sorting(async_client: AsyncClient):
    response = await async_client.get("/post", params={"sorting": "wrong"})
    assert response.status_code == 422


@pytest.mark.anyio
async def test_create_comment(
    async_client: AsyncClient,
    created_post: dict,
    confirmed_user: dict,
    logged_in_token: str,
):
    body = "Test Comment /comment endpoint"
    response = await async_client.post(
        "/comment",
        json={
            "body": body,
            "post_id": created_post["id"],
            "user_id": confirmed_user["id"],
        },
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    assert response.status_code == 201
    assert {
        "id": 1,
        "body": body,
        "post_id": created_post["id"],
    }.items() <= response.json().items()


@pytest.mark.anyio
async def test_get_all_comments_on_post(
    async_client: AsyncClient, created_comment: dict, created_post: dict
):
    response = await async_client.get(f"/post/{created_post['id']}/comments")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json() == [created_comment]


@pytest.mark.anyio
async def test_get_comments_on_post_no_comments(
    async_client: AsyncClient, created_post: dict
):
    response = await async_client.get(f"/post/{created_post['id']}/comments")
    assert response.status_code == 200
    assert len(response.json()) == 0
    assert response.json() == []


@pytest.mark.anyio
async def test_get_comments_on_post_no_post_id(async_client: AsyncClient):
    response = await async_client.get("/post/{dad}/comments")
    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_post_with_comments(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get(f"/post/{created_post['id']}")
    assert response.status_code == 200
    assert response.json() == {
        "post": {**created_post, "likes": 0},
        "comments": [created_comment],
    }


@pytest.mark.anyio
async def test_get_post_with_comments_no_post(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get("/post/999999999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Post not found"}


async def like_post(
    post_id: int, async_client: AsyncClient, logged_in_token: str
) -> dict:
    response = await async_client.post(
        "/like",
        json={"post_id": post_id},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    return response.json()

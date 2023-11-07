import pytest
from fastapi import HTTPException
from jose import jwt

from socialmedia import security


def test_access_token_expire_minutes():
    assert security.access_token_expire_minutes() == 30


def test_confirmation_token_expire_minutes():
    assert security.confirmation_token_expire_minutes() == 1440


def test_create_access_token():
    token = security.create_access_token("test")
    assert token
    assert {"sub": "test", "type": "access"}.items() <= jwt.decode(
        token, key=security.SECRET_KEY, algorithms=[security.ALGORITHM]
    ).items()


def test_create_confirmation_token():
    token = security.create_confirmation_token("test")
    assert token
    assert {"sub": "test", "type": "confirmation"}.items() <= jwt.decode(
        token, key=security.SECRET_KEY, algorithms=[security.ALGORITHM]
    ).items()


def test_get_subject_for_token_type_valid_confirmation():
    email = "test@example.com"
    token = security.create_confirmation_token(email)
    assert email == security.get_subject_for_token_type(token, "confirmation")


def test_get_subject_for_token_type_valid_access():
    email = "test@example.com"
    token = security.create_access_token(email)
    assert email == security.get_subject_for_token_type(token, "access")


def test_get_subject_for_token_type_expired(mocker):
    mocker.patch("socialmedia.security.access_token_expire_minutes", return_value=-1)
    email = "test@example.com"
    token = security.create_access_token(email)
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "access")
        exc_info.value.status_code == 401
        exc_info.value.detail == "Token has been expired"


def test_get_subject_for_invalid_token():
    token = "invalid token"
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "access")
        exc_info.value.status_code == 401
        exc_info.value.detail == "Invalid token"


def test_get_subject_for_token_sub_field_missing():
    email = "test@example.com"
    token = security.create_access_token(email)
    payload = jwt.decode(
        token, key=security.SECRET_KEY, algorithms=[security.ALGORITHM]
    )
    del payload["sub"]
    token = jwt.encode(payload, key=security.SECRET_KEY, algorithm=security.ALGORITHM)

    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "access")
        exc_info.value.status_code == 401
        exc_info.value.detail == "Token is missing 'sub' field"


def test_get_subject_for_token_type_wrong_type():
    email = "test@example.com"
    token = security.create_access_token(email)
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "confirmation")
        exc_info.value.status_code == 401
        exc_info.value.detail == "Token has incorrect type , expected : 'access'"


@pytest.mark.anyio
async def test_password_hashes():
    password = "test"
    hashed_password = security.get_password_hash(password)
    assert security.verify_password(password, hashed_password)


@pytest.mark.anyio
async def test_get_user(registered_user: dict):
    user = await security.get_user(registered_user["email"])
    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_get_user_not_found():
    user = await security.get_user("koko@example")
    assert user is None


@pytest.mark.anyio
async def test_authenticate_user(confirmed_user: dict):
    user = await security.authenticate_user(
        confirmed_user["email"], confirmed_user["password"]
    )
    assert user.email == confirmed_user["email"]


@pytest.mark.anyio
async def test_authenticate_user_not_exist():
    with pytest.raises(security.HTTPException):
        await security.authenticate_user("koko@example", "test")


@pytest.mark.anyio
async def test_authenticate_user_wrong_password(registered_user: dict):
    with pytest.raises(security.HTTPException):
        await security.authenticate_user(
            registered_user["email"], registered_user["password"] + "wrong"
        )


@pytest.mark.anyio
async def test_get_current_user_(registered_user: dict):
    token = security.create_access_token(registered_user["email"])
    user = await security.get_current_user(token)
    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_get_current_user_not_exist():
    token = security.create_access_token("koko@example")
    with pytest.raises(HTTPException):
        await security.get_current_user(token)


@pytest.mark.anyio
async def test_get_current_user_invalid_token():
    token = "invalid_token"
    with pytest.raises(HTTPException):
        await security.get_current_user(token)


@pytest.mark.anyio
async def test_get_current_user_expired_token(registered_user: dict, mocker):
    mocker.patch("socialmedia.security.access_token_expire_minutes", return_value=-1)
    token = security.create_access_token(registered_user["email"])
    with pytest.raises(HTTPException):
        await security.get_current_user(token)


@pytest.mark.anyio
async def test_get_current_user_wrong_type_token(registered_user: dict):
    token = security.create_confirmation_token(registered_user["email"])
    with pytest.raises(HTTPException):
        await security.get_current_user(token)

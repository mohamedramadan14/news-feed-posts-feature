import logging
from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from socialmedia.database import database, user_table

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"])


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token"
)  # populate docs and grab token from response


def access_token_expire_minutes() -> int:
    return 30


def confirmation_token_expire_minutes() -> int:
    return 1440


def create_access_token(email: str):
    logger.debug("Creating access token", extra={"email": email})
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=access_token_expire_minutes()
    )
    jwt_data = {
        "sub": email,
        "exp": expire,
        "type": "access",
    }
    token = jwt.encode(jwt_data, key=SECRET_KEY, algorithm=ALGORITHM)
    return token


def create_confirmation_token(email: str):
    logger.debug("Creating access token", extra={"email": email})
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=confirmation_token_expire_minutes()
    )
    jwt_data = {
        "sub": email,
        "exp": expire,
        "type": "confirmation",
    }
    token = jwt.encode(jwt_data, key=SECRET_KEY, algorithm=ALGORITHM)
    return token


def get_subject_for_token_type(
    token: str, type: Literal["access", "confirmation"]
) -> str:
    logger.debug("Getting subject for token type" + type)

    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])

    except ExpiredSignatureError as e:
        raise create_credentials_exception("Token has been expired") from e

    except JWTError as e:
        raise create_credentials_exception("Invalid token") from e

    email: str = payload.get("sub")
    if email is None:
        raise create_credentials_exception("Token is missing 'sub' field")

    token_type = payload.get("type")
    if token_type != type or token_type is None:
        raise create_credentials_exception(
            f"Token has incorrect type , expected : '{token_type}'"
        )

    return email


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_user(email: str):
    logger.debug("Fetching user from the database", extra={"email": email})
    query = user_table.select().where(user_table.c.email == email)
    logger.debug(query)
    result = await database.fetch_one(query)
    if result:
        return result
    return None


"""
steps for hashing password:
1- define algorithm for hashing
2- hash password
3- verify password matches the hashed password
"""


def create_credentials_exception(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def authenticate_user(email: str, password: str):
    logger.debug("Authenticating user", extra={"email": email})
    user = await get_user(email)
    if not user:
        raise create_credentials_exception("Invalid email or password")
    if not verify_password(password, user.password):
        raise create_credentials_exception("Invalid email or password")

    if not user.is_confirmed:
        raise create_credentials_exception("Please confirm your email")
    return user


# Dependency Injection : here we are using get_current_user function and inject token automatically using oauth2_scheme function
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    email = get_subject_for_token_type(token, "access")
    user = await get_user(email)
    if user is None:
        raise create_credentials_exception("Could not find user with given token")
    return user

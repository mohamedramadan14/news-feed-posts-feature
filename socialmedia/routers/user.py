import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status

from socialmedia import tasks
from socialmedia.database import database, user_table
from socialmedia.models.user import UserIn
from socialmedia.security import (
    authenticate_user,
    create_access_token,
    create_confirmation_token,
    get_password_hash,
    get_subject_for_token_type,
    get_user,
)

logger = logging.getLogger(__name__)

router = APIRouter()

'''
Usually BackgroundTasks used in input / output bound Jobs which jobs that are slow
but not good for now for running a machine learning model use task worker ex: arq , salari so you've separate python process usually in separate python server 
'''

@router.post("/register", status_code=201)
async def register(user: UserIn, background_tasks: BackgroundTasks, request: Request):
    existed_user = await get_user(email=user.email)
    if existed_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email {user.email} already exists",
        )
    # This is very Bad Practices Password should be hashed
    hashed_password = get_password_hash(user.password)
    query = user_table.insert().values(email=user.email, password=hashed_password)

    logger.debug(query)

    await database.execute(query)
    background_tasks.add_task(
        tasks.send_registration_email,
        user.email,
        confirmation_url=request.url_for(
            "confirm_email",
            token=create_confirmation_token(user.email),
        ),
    )
    return {"detail": "User created. Please confirm your email"}


@router.post("/token", status_code=201)
async def login(user: UserIn):
    user = await authenticate_user(user.email, user.password)
    access_token = create_access_token(user.email)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirm/{token}")
async def confirm_email(token: str):
    email = get_subject_for_token_type(token, "confirmation")
    user = await get_user(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    query = (
        user_table.update().where(user_table.c.email == email).values(is_confirmed=True)
    )
    logger.debug(query)
    await database.execute(query)
    return {"detail": "User confirmed"}

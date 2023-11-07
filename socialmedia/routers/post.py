import logging
from enum import Enum
from typing import Annotated

import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException

from socialmedia.database import comment_table, database, like_table, post_table
from socialmedia.models.post import (
    Comment,
    CommentIn,
    PostLike,
    PostLikeIn,
    UserPost,
    UserPostIn,
    UserPostsWithLikes,
    UserPostWithComments,
)
from socialmedia.models.user import User
from socialmedia.security import get_current_user

router = APIRouter()

logger = logging.getLogger(__name__)


select_post_likes = (
    sqlalchemy.select(post_table, sqlalchemy.func.count(like_table.c.id).label("likes"))
    .select_from(post_table.outerjoin(like_table))
    .group_by(post_table.c.id)
)


@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(
    post: UserPostIn, current_user: Annotated[User, Depends(get_current_user)]
):
    logger.info("Creating Post")

    data = {**post.model_dump(), "user_id": current_user.id}
    query = post_table.insert().values(data)

    logger.debug(query)

    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


class PostSorting(str, Enum):
    new = "new"
    old = "old"
    most_liked = "most_liked"


@router.get("/post", response_model=list[UserPostsWithLikes], status_code=200)
async def get_posts(
    sorting: PostSorting = PostSorting.new,
):  # sorting will reach to here as query parameter ex : api/post?sorting=most_liked
    logger.info("Getting All Posts")

    # TODO : using match sorting: case PostSorting.new ..etc
    if sorting == PostSorting.new:
        query = select_post_likes.order_by(post_table.c.id.desc())
    elif sorting == PostSorting.old:
        query = select_post_likes.order_by(post_table.c.id.asc())
    elif sorting == PostSorting.most_liked:
        query = select_post_likes.order_by(sqlalchemy.desc("likes"))

    logger.debug(query)
    return await database.fetch_all(query)


async def find_post(post_id: int):
    logger.info(f"Finding post with id: {post_id}")

    query = post_table.select().where(post_table.c.id == post_id)

    logger.debug(query)
    return await database.fetch_one(query)


@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(
    comment: CommentIn, current_user: Annotated[User, Depends(get_current_user)]
):
    logger.info(f"Creating comment for post with id: {comment.post_id}")

    post = await find_post(comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = {**comment.model_dump(), "user_id": current_user.id}
    query = comment_table.insert().values(data)
    last_record_id = await database.execute(query)
    logger.debug(query)
    return {**data, "id": last_record_id}


@router.get("/post/{post_id}/comments", response_model=list[Comment], status_code=200)
async def get_comments_on_post(post_id: int):
    logger.info(f"Getting comments for post with id: {post_id}")
    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    query = comment_table.select().where(comment_table.c.post_id == post_id)
    logger.debug(query)
    return await database.fetch_all(query)


@router.get("/post/{post_id}", response_model=UserPostWithComments, status_code=200)
async def get_post_with_comments(post_id: int):
    logger.info(f"Getting post with id: {post_id}")

    query = select_post_likes.where(post_table.c.id == post_id)

    logger.debug(query)

    post = await database.fetch_one(query)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return {"post": post, "comments": await get_comments_on_post(post_id)}


@router.post("/like", response_model=PostLike, status_code=201)
async def like_post(
    like: PostLikeIn, current_user: Annotated[User, Depends(get_current_user)]
):
    logger.info(f"Creating like for post with id: {like.post_id}")

    post = await find_post(like.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = {**like.model_dump(), "user_id": current_user.id}
    query = like_table.insert().values(data)

    logger.debug(query)

    last_record_id = await database.execute(query)

    return {**data, "id": last_record_id}

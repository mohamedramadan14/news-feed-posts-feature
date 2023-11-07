from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserPostIn(BaseModel):
    body: str


class UserPost(UserPostIn):
    model_config = ConfigDict(from_attributes=True, extra="allow")
    id: int
    user_id: int
    image_url: Optional[str] = None


class CommentIn(BaseModel):
    body: str
    post_id: int


class Comment(CommentIn):
    model_config = ConfigDict(from_attributes=True, extra="allow")
    id: int
    user_id: int


class PostLikeIn(BaseModel):
    post_id: int


class PostLike(PostLikeIn):
    model_config = ConfigDict(from_attributes=True, extra="allow")
    id: int
    user_id: int


"""
This is the response when getting post with comments
{
  "post": {
    "id": 1,
    "body": "My first post"
    },
  "comments": [
    {
      "id": 1,
      "body": "This is my first comment",
      "post_id": 1
    }
  ]
  }
}
"""


class UserPostsWithLikes(UserPost):
    model_config = ConfigDict(from_attributes=True, extra="allow")
    likes: int


class UserPostWithComments(BaseModel):
    post: UserPostsWithLikes
    comments: list[Comment]

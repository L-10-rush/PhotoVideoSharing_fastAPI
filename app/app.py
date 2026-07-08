from fastapi import FastAPI, HTTPException, Depends, Form, UploadFile, File
from app.schemas import PostCreate, PostResponse
from app.db import Post, User, create_async_engine, get_async_session, create_db_and_tables


from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager # contextlib built in the python 
from datetime import datetime
from sqlalchemy import select

from app.images import imagekit
# from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions

import uuid
import os

from app.users import auth_backend, current_active_user, fastapi_users

from app.schemas import UserCreate, UserRead, UserUpdate

from sqlalchemy.orm import selectinload 

@asynccontextmanager
async def lifespan(app:FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(fastapi_users.get_auth_router(auth_backend), prefix='/auth/jwt', tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix='/auth', tags=['auth'])
app.include_router(fastapi_users.get_reset_password_router(), prefix='/auth', tags=['auth'])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix='/auth', tags=['auth'])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix='/users', tags=['Users'])


# fast API is async as default 
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(""),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session) # this is dependence injection 
):

    try:
        file_bytes = await file.read()
        upload_result = imagekit.files.upload(
            file=file_bytes,
            file_name=file.filename,
            use_unique_file_name=True,
            tags=["backend-uplaod"]
        )
        
        post = Post(
            user_id = user.id,
            caption=caption,
            url= upload_result.url,
            file_type="video" if file.content_type.startswith("video/") else "image",
            file_name=upload_result.name
        )
        session.add(post)
        await session.commit()
        await session.refresh(post)
        
        return post

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        await file.close()

@app.get("/feed")
async def get_feed(
    session: AsyncSession=Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    result = await session.execute(
        select(Post)
        .options(selectinload(Post.user))
        .order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]
    posts_data = []

    for post in posts:
        if post.user is None:
            continue
        posts_data.append(
            {
                "id": str(post.id),
                "user_id":str(post.user_id),
                "caption": post.caption,
                "url": post.url,
                "file_type":post.file_type,
                "file_name":post.file_name,
                "created_at":post.created_at.isoformat(),
                "is_owner":post.user_id == user.id,
                "email":post.user.email
            }
        )
    
    return {"posts": posts_data}


@app.delete("/posts/{post_id}")
async def delete_post(post_id: str, session: AsyncSession = Depends(get_async_session), user: User = Depends(current_active_user)):
    try:
        post_uuid = uuid.UUID(post_id)

        result = await session.execute(select(Post).where(Post.id == post_uuid) )
        post = result.scalars().first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if post.user_id != user.id:
            raise HTTPException(status_code=403, detail="U dont have permission to delete this post")
        
        await session.delete(post)
        await session.commit()
        return {"success": True, "message": "Post deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#this is the endpoint 
# @app.get("/hello-world") #this is the decorator
# def hello_world():
#     return {"message":"Hello World"} #json ->Javascript Object Notation
# text_posts = {
#     1: {"title": "New Post", "content": "cool test post"},
#     2: {"title": "Hello World", "content": "This is my first real post!"},
#     3: {"title": "Python Tips", "content": "Remember to use list comprehensions for cleaner code."},
#     4: {"title": "Weather Update", "content": "It's sunny today with a chance of rain."},
#     5: {"title": "Book Review", "content": "Just finished reading 'Atomic Habits' - highly recommend!"},
#     6: {"title": "Coding Challenge", "content": "Try to solve the FizzBuzz problem in one line."},
#     7: {"title": "Weekend Plans", "content": "Going hiking with friends, can't wait!"},
#     8: {"title": "New Recipe", "content": "Tried making homemade pasta – it was delicious!"},
#     9: {"title": "Tech News", "content": "New AI model released that can generate music."},
#     10: {"title": "Motivation", "content": "Keep pushing forward, every step counts."}
# }
# @app.get("/posts") #path parameter
# def get_all_post(limit: int = None):
#     if limit:
#         return list(text_posts.values())[:limit]
#     return text_posts

# @app.get("/posts/{id}") #query parameter
# def get_post(id: int) -> PostResponse:
#     if id not in text_posts:
#         raise HTTPException(status_code=404, detail="Post not found") # raise the http exception 
#     return text_posts.get(id)

# @app.post("/posts") #request body in this if we have to send file we will use schemas
# def create_post( post: PostCreate) -> PostResponse: 
#     new_post =  {"title":post.title, "content": post.content}
#     text_posts[max(text_posts.keys()) + 1] = new_post
#     return new_post
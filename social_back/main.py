from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from passlib.context import CryptContext
from typing import List
import sqlite3

app = FastAPI()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "your_secret_key" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

conn = sqlite3.connect("social_media.db")
cursor = conn.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        hashed_password TEXT
    )
    """
)
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT,
        username TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
)
conn.commit()
conn.close()


def get_current_user(token: str = Depends(oauth2_scheme)):
    return token


class User(BaseModel):
    username: str


class Post(BaseModel):
    text: str


class UserInDB(User):
    hashed_password: str


# Create User
@app.post("/users/", response_model=User)
async def create_user(user: User):
    conn = sqlite3.connect("social_media.db")
    cursor = conn.cursor()
    hashed_password = "hashed_password"  # Use a proper password hashing library
    cursor.execute("INSERT INTO users (username, hashed_password) VALUES (?, ?)", (user.username, hashed_password))
    conn.commit()
    conn.close()
    return user


# User Login
@app.post("/login/")
async def login(username: str, password: str):
    # 
    return {"message": "Logged in successfully"}


# Create Post
@app.post("/posts/", response_model=Post)
async def create_post(post: Post, current_user: str = Depends(get_current_user)):
    conn = sqlite3.connect("social_media.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO posts (text, username) VALUES (?, ?)", (post.text, current_user))
    conn.commit()
    conn.close()
    return post


# List Users
@app.get("/users/", response_model=List[User])
async def list_users():
    conn = sqlite3.connect("social_media.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users")
    users = [{"username": row[0]} for row in cursor.fetchall()]
    conn.close()
    return users


# List Posts
@app.get("/posts/", response_model=List[Post])
async def list_posts():
    conn = sqlite3.connect("social_media.db")
    cursor = conn.cursor()
    cursor.execute("SELECT text, username FROM posts ORDER BY timestamp DESC")
    posts = [{"text": row[0], "username": row[1]} for row in cursor.fetchall()]
    conn.close()
    return posts


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)

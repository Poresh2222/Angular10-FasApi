from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    username: str
    firstName: str
    lastName: str


class UserCreate(User):
    password: str    


class UserInDB(User):
    hashed_password: str
    uid: str    


class UserLogin(BaseModel):
    username: str
    password: str    


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None    
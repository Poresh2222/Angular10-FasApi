import random
import string

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from jose import JWTError,jwt
from passlib.context import CryptContext

from app.schemas import users as users_schemas
from app.utils.users_depends import get_current_user
from databases.firestore.firestoredb import ref


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"


def get_random_string(length=12):
        return ''.join(random.choice(string.ascii_letters) for _ in range(length))


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)    


async def create_user(user: users_schemas.UserCreate):
    hashedPassword = get_password_hash(user.password)
    uid = get_random_string()

    data = {
        u'username': user.username,
        u'hashed_password': hashedPassword,
        u'firstName': user.firstName,
        u'lastName': user.lastName,
        u'uid': uid,
    }

    doc_ref = ref.document(user.username).set(data)


async def getAllusers():
    docs = ref.stream()

    for doc in docs:
        user_dict = doc.to_dict()
        firstNames = user_dict.get(u'firstNames')
        lastNames = user_dict.get(u'lastName')
        usernames = user_dict.get(u'username')
        uid = user_dict.get(u'uid')
        password = user_dict.get(u'hashed_password')
        return {'firstName': firstNames, 'lastName': lastNames, 'username': usernames, 'id': uid, 'password': password}



async def get_user_by_username(username: str):
    db_user = ref.document(username).get().to_dict()
    return db_user     


async def get_user(username: str):
    user = ref.document(username).get().to_dict()
    return users_schemas.UserInDB(**user)    


async def authenticate_user(username: str, password: str):
    user = await get_user(username)

    if not user:
        return False

    if not verify_password(password, user.hashed_password):
        return False

    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt    
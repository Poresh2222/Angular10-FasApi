from datetime import datetime, timedelta
from typing import Optional, List, Union
from jose import JWTError, jwt

from fastapi import Depends, FastAPI, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext

from app.schemas import users as users_schemas
from app.utils import users as users_utils
from app.utils import users_depends


router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 30


@router.post('/users/register')  
async def user_register(user: users_schemas.UserCreate):
    db_user = await users_utils.get_user_by_username(user.username)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail='Username is already exist'
        )

    return await users_utils.create_user(user)


@router.post('/users/authenticate')
async def login_for_access_token(user: users_schemas.UserLogin):
    User = await users_utils.authenticate_user(user.username, user.password)
    if not User:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = users_utils.create_access_token(
        data={'sub': user.username}, expires_delta=access_token_expires
    )
        
    db_user = await users_utils.get_user(user.username)
    password = db_user.hashed_password

    return [{'username': user.username, 'firstName': db_user.firstName, 'lastName': db_user.lastName, 'password': password}, {'access_token': access_token, 'token_type': 'bearer'}]
    

@router.get('/users')
async def get_all_users():
    return await users_utils.getAllusers()
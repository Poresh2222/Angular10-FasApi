from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt

from app.schemas import users as users_schemas
from app.utils import users as users_utils


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='authenticate')
SECRET_KEY = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
ALGORITHM = 'HS256'


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = users_schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await users_utils.get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user
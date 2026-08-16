import os
from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from ...storage.database import get_db
from ...storage.repositories.user_repository import UserRepository

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    api_key: str = Depends(API_KEY_HEADER),
    db: AsyncSession = Depends(get_db),
):
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")

    repo = UserRepository(db)
    user = await repo.get_by_api_key(api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY", "fallback"), algorithm="HS256")
    return encoded_jwt

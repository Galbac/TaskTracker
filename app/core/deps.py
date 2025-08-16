import os

import jwt
from dotenv import load_dotenv
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import RedirectResponse
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


async def get_current_user(request: Request, db: AsyncSession):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get('sub'))

    except JWTError:
        return None

    result = await  db.execute(select(User).where(User.id == user_id))
    return result.scalar()


def redirect_if_not_authenticated(user: User):
    if user is None:
        return RedirectResponse("/login", status_code=303)

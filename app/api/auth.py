from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password, create_access_token
from app.database import get_db
from app.models.users import User
from app.schema.auth import UserSchema

auth_router = APIRouter()


@auth_router.get("/register")
async def register_form(request: Request):
    return request.app.templates.TemplateResponse(
        request=request, name="register.html", context={"request": request}
    )


@auth_router.post("/register")
async def register(
    request: Request, user_reg: UserSchema = Form(), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == user_reg.email))
    user = result.scalar()
    if user:
        request.app.templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Пользователь с таким email уже существует",
            },
        )
    user_dict = User(
        email=user_reg.email, hashed_password=get_password_hash(user_reg.password)
    )
    db.add(user_dict)
    await db.commit()
    return RedirectResponse("/login", status_code=303)


@auth_router.get("/login")
async def login_form(request: Request):
    return request.app.templates.TemplateResponse(
        request=request, name="login.html", context={"request": request}
    )


@auth_router.post("/login")
async def login(user_login: UserSchema = Form(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_login.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(user_login.password, user.hashed_password):
        return RedirectResponse("/login?error=invalid", status_code=303)
    access_token = create_access_token({"sub": str(user.id)})
    response = RedirectResponse("/", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

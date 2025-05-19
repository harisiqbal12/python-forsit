from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from app.core.jwt import create_access_token
from app.schema import UserCreate
from app.models.users import User as UserModel
from app.api.dependencies import get_db, get_redis
from app.core.security import get_password_hash, rate_limiting, verify_password
from redis import Redis

from app.schema.auth import LoginRequest


router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)


@router.post("/register")
async def register(
    req: UserCreate,
    db: Session = Depends(get_db),
    redis_client: Redis = Depends(get_redis),
    request: Request = None,
):

    ip = request.client.host if request else "unknown"
    rate_limiting(ip, "registeration", redis_client)

    existing_user = (
        db.query(UserModel)
        .filter((UserModel.email == req.email) | (UserModel.username == req.username))
        .first()
    )

    if existing_user:
        raise HTTPException(status_code=400, detail="invalid email or password")

    hashed_password = get_password_hash(req.password)

    user = UserModel(
        email=req.email,
        username=req.username,
        name=req.name,
        avatar=req.avatar,
        password=hashed_password,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "name": str(user.name),
            "username": str(user.username),
        }
    )

    redis_client.set(f"session:{user.id}", str(access_token), 60 * 60)
    return {"message": "Successfully registered", "access_token": access_token}


@router.post("/login")
async def login(
    req: LoginRequest,
    db: Session = Depends(get_db),
    redis_client: Redis = Depends(get_redis),
    request: Request = None,
):
    ip = request.client.host if request else "unknown"
    rate_limiting(ip, "registeration", redis_client)

    if req.email:
        user = db.query(UserModel).filter(UserModel.email == req.email).first()

    if req.username:
        user = db.query(UserModel).filter(UserModel.password == req.password).first()

    if not user:
        raise HTTPException(status_code=400, detail="invalid email or password")

    is_matched = verify_password(req.password, user.password)

    if not is_matched:
        raise HTTPException(status_code=400, detail="invalid email or password")

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "name": str(user.name),
            "username": str(user.username),
        }
    )

    redis_client.set(f"session:{user.id}", str(access_token), 60 * 60)
    return {"message": "success", "access_token": access_token}

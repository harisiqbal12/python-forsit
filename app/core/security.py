import bcrypt
from fastapi import HTTPException
from redis import Redis

from app.core.config import settings


def get_password_hash(password: str) -> str:
    """Hash a password string"""
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """verify password hashed"""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def rate_limiting(ip: str, module: str, redis_client: Redis) -> None:
    key = f"{module}:rate:{ip}"
    attempts = redis_client.get(key)
    if attempts and int(attempts) >= settings.HTTP_MAX_ATTEMPTS:
        raise HTTPException(
            status_code=429,
            detail=f"Too many {module} attempts. Please try again later.",
        )
    pipe = redis_client.pipeline()
    pipe.incr(key, 1)
    pipe.expire(key, settings.HTTP_ATTEMPT_COOLDOWN)
    pipe.execute()
    return

from fastapi import Depends, HTTPException, Header
from redis import Redis
from app.db.session import get_db
from app.db.redis import get_redis
from app.core.jwt import decode_jwt_token


def get_current_user(
    authorization: str = Header(..., alias="Authorization"),
    redis_client: Redis = Depends(get_redis),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = authorization.split(" ")[1]
    payload = decode_jwt_token(token)
    user_id = payload["sub"]
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    session_key = f"session:{user_id}"
    redis_token = redis_client.get(session_key)
    if not redis_token or redis_token.decode() != token:
        raise HTTPException(status_code=401, detail="session expired or invalid")

    return payload


__all__ = ["get_db", "get_redis", "get_current_user"]

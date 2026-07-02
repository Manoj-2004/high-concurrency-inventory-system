from jose import jwt

from app.config import settings
from app.redis_client import redis_client


def blacklist_token(token: str) -> None:
    payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm],
    )

    exp = payload.get("exp")

    if exp is None:
        return

    ttl = exp - int(__import__("time").time())

    if ttl > 0:
        redis_client.setex(
            f"blacklist:{token}",
            ttl,
            "true",
        )


def is_token_blacklisted(token: str) -> bool:
    return redis_client.exists(f"blacklist:{token}") == 1
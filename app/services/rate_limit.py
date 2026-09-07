from fastapi import HTTPException, Request, status
from redis import Redis
from app.config import settings
from app.services.security import decode_access_token

redis_client = Redis.from_url(settings.redis_url, decode_responses=True)

RATE_LIMIT_MAX_REQUESTS = 10
RATE_LIMIT_WINDOW_SECONDS = 60 * 60  # 1 hour


def _get_identifier(request: Request) -> str:
    """Identify the caller by user id when authenticated, else by IP."""
    auth_header = request.headers.get("Authorization")

    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
        user_id = decode_access_token(token)
        if user_id is not None:
            return f"user:{user_id}"

    client_host = request.client.host if request.client else "unknown"
    return f"ip:{client_host}"


async def enforce_rate_limit(request: Request) -> None:
    """FastAPI dependency: raises 429 if the caller has exceeded the rate limit."""
    identifier = _get_identifier(request)
    key = f"rate_limit:{identifier}:{request.scope['path']}"

    current_count = redis_client.incr(key)

    if current_count == 1:
        # First request in this window — start the clock.
        redis_client.expire(key, RATE_LIMIT_WINDOW_SECONDS)

    if current_count > RATE_LIMIT_MAX_REQUESTS:
        ttl = redis_client.ttl(key)
        retry_after = ttl if ttl and ttl > 0 else RATE_LIMIT_WINDOW_SECONDS
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later.",
            headers={"Retry-After": str(retry_after)},
        )
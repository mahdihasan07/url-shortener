from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .routers import urls

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="URL Shortener API",
    description="Shorten URLs, track clicks, and view analytics.",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Register routers
# Order matters: stats route must be registered before the generic /{code} redirect
app.include_router(urls.router)


@app.get("/health")
def health():
    return {"status": "ok"}
import os
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from .. import models, schemas
from ..database import get_db
from ..utils import generate_short_code
from ..cache import get_cache

router = APIRouter(tags=["urls"])
limiter = Limiter(key_func=get_remote_address)

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


@router.post("/shorten", response_model=schemas.URLOut)
@limiter.limit("10/minute")
def shorten_url(
    request: Request,
    payload: schemas.URLCreate,
    db: Session = Depends(get_db),
):
    """
    Accept a long URL, generate a unique short code, store it, return the short URL.
    Rate limited to 10 requests per minute per IP address.
    """
    original_url = str(payload.original_url)

    for attempt in range(5):
        code = generate_short_code()
        existing = db.query(models.URL).filter(
            models.URL.short_code == code
        ).first()
        if not existing:
            break
    else:
        raise HTTPException(status_code=500, detail="Could not generate a unique short code")

    new_url = models.URL(short_code=code, original_url=original_url)
    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    return {
        "id": new_url.id,
        "short_code": new_url.short_code,
        "original_url": new_url.original_url,
        "short_url": f"{BASE_URL}/{new_url.short_code}",
        "created_at": new_url.created_at,
    }

@router.get("/{code}")
def redirect_to_url(
    code: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    cache=Depends(get_cache),
):
    """
    Look up the short code and redirect.
    Cache hit  → Redis lookup (sub-millisecond, no DB query)
    Cache miss → Postgres query, then cache the result for 1 hour
    Click is logged asynchronously after the response is sent.
    """
    cache_key = f"url:{code}"

    # Step 1: check Redis first
    cached_url = cache.get(cache_key)

    if cached_url:
        original_url = cached_url
        url_id = None          # we'll need the id for click logging
    else:
        # Step 2: cache miss — query Postgres
        url_obj = db.query(models.URL).filter(
            models.URL.short_code == code
        ).first()

        if not url_obj:
            raise HTTPException(status_code=404, detail="Short URL not found")

        original_url = url_obj.original_url
        url_id = url_obj.id

        # Step 3: store in Redis for 1 hour (3600 seconds)
        cache.setex(cache_key, 3600, original_url)

    # Step 4: schedule click logging to run after response is sent
    if url_id:
        background_tasks.add_task(
            log_click,
            db=db,
            url_id=url_id,
            referrer=request.headers.get("referer"),
            user_agent=request.headers.get("user-agent"),
        )

    return RedirectResponse(url=original_url, status_code=302)
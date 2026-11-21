
import os

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import URLCreate, URLResponse
from app.services.url_service import create_short_url
import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from redis.exceptions import RedisError

from app.database import get_db
from app.models import URL,Click
from app.redis_client import redis_client

router = APIRouter()
def to_utc(dt):
    if dt is None:
        return None

    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)
def get_cache_ttl(expires_at):
    default_ttl = 3600
    expires_at = to_utc(expires_at)

    if expires_at is None:
        return default_ttl

    remaining_seconds = int(
        (expires_at - datetime.now(timezone.utc)).total_seconds()
    )

    return min(default_ttl, remaining_seconds)
def record_click(db: Session, url_id: int, request: Request):
    ip_address = request.client.host if request.client else None

    click = Click(
        url_id=url_id,
        ip_address=ip_address
    )

    db.add(click)
    db.commit()

@router.post(
    "/shorten",
    response_model=URLResponse,
    status_code=201
)
def shorten_url(
    request: URLCreate,
    db: Session = Depends(get_db)
):

    try:

        new_url = create_short_url(
            db=db,
            original_url=str(request.original_url),
            custom_alias=request.custom_alias,
            expires_at=request.expires_at
        )

    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail=str(e)
        )

    base_url = os.getenv(
        "BASE_URL",
        "http://localhost:8000"
    )

    return URLResponse(
        original_url=new_url.original_url,
        short_code=new_url.short_code,
        short_url=f"{base_url}/{new_url.short_code}",
        created_at=new_url.created_at,
        expires_at=new_url.expires_at
    )

@router.get("/{short_code}")
def redirect_url(short_code: str,request:Request,db: Session = Depends(get_db)):

    cache_key = f"url:{short_code}" #main thing
    cached_data = None

    # STEP 1: Check Redis
    try:
        cached_data = redis_client.get(cache_key)
    except RedisError:
        # Redis unavailable: continue using PostgreSQL
        pass

    # STEP 2: Cache hit
    if cached_data:
        try:
            data = json.loads(cached_data)

            if not data.get("is_active", True):
                raise HTTPException(
                    status_code=410,
                    detail="This URL is no longer active"
                )

            expires_at = (
                datetime.fromisoformat(data["expires_at"])
                if data.get("expires_at")
                else None
            )

            if expires_at and expires_at <= datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=410,
                    detail="This short URL has expired"
                )
            record_click(db,data["url_id"],request)

            return RedirectResponse(
                url=data["original_url"],
                status_code=302
            )

        except HTTPException:
            raise
        except (ValueError, KeyError, TypeError):
            # Invalid cache entry: fall back to PostgreSQL
            pass

    # STEP 3: Cache miss — query PostgreSQL
    url = db.query(URL).filter(
        URL.short_code == short_code
    ).first()

    if not url:
        raise HTTPException(
            status_code=404,
            detail="Short URL not found"
        )

    if not url.is_active:
        raise HTTPException(
            status_code=410,
            detail="This URL is no longer active"
        )

    if url.expires_at and url.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=410,
            detail="This short URL has expired"
        )

    # STEP 4: Populate Redis
    ttl = get_cache_ttl(url.expires_at)

    if ttl > 0:
        cache_data = {
            "url_id":url.id,
            "original_url": url.original_url,
            "expires_at": (
                url.expires_at.isoformat()
                if url.expires_at
                else None
            ),
            "is_active": url.is_active
        }

        try:
            redis_client.set(
                cache_key,
                json.dumps(cache_data),
                ex=ttl
            )
        except RedisError:
            # Caching failure should not prevent redirection
            pass
    #STEP 5: Record Click
    record_click(db,url.id,request)

    # STEP 6: Redirect
    return RedirectResponse(
        url=url.original_url,
        status_code=302
    )

@router.get("/analytics/{short_code}")
def get_url_analytics(
    short_code: str,
    db: Session = Depends(get_db)
):
    url = db.query(URL).filter(
        URL.short_code == short_code
    ).first()

    if not url:
        raise HTTPException(
            status_code=404,
            detail="Short URL not found"
        )

    total_clicks = db.query(Click).filter(
        Click.url_id == url.id
    ).count()

    return {
        "short_code": url.short_code,
        "original_url": url.original_url,
        "total_clicks": total_clicks,
        "created_at": url.created_at,
        "expires_at": url.expires_at
    }

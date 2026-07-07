# URL Shortener with Click Analytics

A production-ready URL shortener built with FastAPI, PostgreSQL, and Redis.
Short codes are randomly generated. Every redirect is tracked asynchronously.
Lookups are cached in Redis for sub-millisecond response times.

## Features
- Shorten any URL to a 7-character code
- Redirect with click tracking (referrer, user agent)
- Per-code click analytics
- Redis cache-aside for fast redirects
- Rate limiting on URL creation (10/minute per IP)
- Docker Compose for one-command local setup

## Quick start

    cp .env.example .env
    docker compose up --build

API docs: http://localhost:8000/docs

## API

| Method | Endpoint | Description |
|---|---|---|
| POST | /shorten | Create a short URL |
| GET | /{code} | Redirect to original URL |
| GET | /stats/{code} | View click analytics |

## Run tests

    docker compose up db redis -d
    pytest tests/ -v
from fastapi import FastAPI, Depends, status
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
from typing import List

from .models import Item, ItemsResponse
from .deps import get_settings, Settings

app = FastAPI(title="Homelab Demo API")

# In-memory "databáze"
ITEMS: List[Item] = []

# Prometheus metriky
REQUEST_COUNT = Counter(
    "demo_api_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "demo_api_request_latency_seconds",
    "Request latency",
    ["endpoint"],
)


def track_request(endpoint: str):
    def decorator(handler):
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                response = await handler(*args, **kwargs)
                status_code = response.status_code
                return response
            finally:
                duration = time.time() - start
                REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
                REQUEST_COUNT.labels(
                    method=endpoint, endpoint=endpoint, status=status_code
                ).inc()

        return wrapper

    return decorator


@app.get("/livez", tags=["health"])
async def livez():
    # jednoduchý liveness – pokud proces běží, vrátí 200
    return {"status": "ok"}


@app.get("/healthz", tags=["health"])
async def healthz(settings: Settings = Depends(get_settings)):
    # zde bys na pohovoru mohl zmínit check na DB/Redis atd.
    return {
        "status": "ok",
        "env": settings.env,
        "version": settings.version,
    }


@app.get("/version", tags=["meta"])
async def version(settings: Settings = Depends(get_settings)):
    return {"version": settings.version, "env": settings.env}


@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return JSONResponse(
        content=data,
        media_type=CONTENT_TYPE_LATEST,
        status_code=status.HTTP_200_OK,
    )


@app.get("/items", response_model=ItemsResponse, tags=["items"])
@track_request("/items")
async def list_items():
    return ItemsResponse(items=ITEMS)


@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED, tags=["items"])
@track_request("/items")
async def create_item(item: Item):
    ITEMS.append(item)
    return item

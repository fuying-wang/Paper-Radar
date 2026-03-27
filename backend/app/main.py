from fastapi import FastAPI

from app.api.v1.router import api_router
from app.db.init_db import init_db
from app.services.scheduler import start_scheduler, stop_scheduler


app = FastAPI(title="Paper Discovery API", version="0.1.0")
app.include_router(api_router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    start_scheduler()


@app.on_event("shutdown")
def on_shutdown() -> None:
    stop_scheduler()

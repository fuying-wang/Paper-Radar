from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.daily_update import run_daily_update


logger = logging.getLogger(__name__)
_scheduler: BackgroundScheduler | None = None


def run_scheduled_daily_update() -> None:
    db = SessionLocal()
    try:
        result = run_daily_update(db=db, limit=settings.daily_update_limit)
        logger.info("daily update finished: %s", result)
    except Exception:
        logger.exception("daily update failed")
    finally:
        db.close()


def start_scheduler() -> None:
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        return
    _scheduler = BackgroundScheduler(timezone="UTC")
    _scheduler.add_job(
        run_scheduled_daily_update,
        trigger="cron",
        hour=settings.daily_update_hour,
        minute=settings.daily_update_minute,
        id="daily-paper-update",
        replace_existing=True,
    )
    _scheduler.start()
    if settings.run_daily_update_on_startup:
        run_scheduled_daily_update()


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is None:
        return
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
    _scheduler = None

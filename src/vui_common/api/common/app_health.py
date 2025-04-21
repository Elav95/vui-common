from fastapi import APIRouter
from vui_common.api.common.routers import health

appHealth = APIRouter()
appHealth.include_router(health.router)

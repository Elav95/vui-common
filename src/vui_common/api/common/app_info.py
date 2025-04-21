from fastapi import APIRouter

from vui_common.api.common.routers import info

appInfo = APIRouter()

appInfo.include_router(info.router)


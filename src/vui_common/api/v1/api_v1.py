from fastapi import Depends, APIRouter

from vui_common.security.routers import authentication, user
from vui_common.security.authentication.auth_service import get_current_active_user

from vui_common.configs.config_proxy import config_app


v1 = APIRouter()

if config_app.app.auth_enabled:

    v1.include_router(authentication.router)

    v1.include_router(user.router,
                      dependencies=[Depends(get_current_active_user)])

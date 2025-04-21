from fastapi.responses import JSONResponse

from vui_common.schemas.response.successful_request import SuccessfulRequest

from vui_common.database.db_connection import SessionLocal

from vui_common.configs.config_proxy import config_app

from vui_common.service.app_version import last_tags_from_github_service
from vui_common.service.architecture import identify_architecture_service
from vui_common.service.app_compatibility import ui_compatibility_service


async def identify_architecture_handler():
    payload = await identify_architecture_service()

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def get_origins_handler():
    payload = config_app.security.get_origins()

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def last_tags_from_github_handler(force_refresh: bool, db: SessionLocal):
    payload = await last_tags_from_github_service(db,
                                                  force_refresh=force_refresh,
                                                  check_version=True)

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def last_tag_velero_from_github_handler(force_refresh: bool, db: SessionLocal):
    payload = await last_tags_from_github_service(db,
                                                  force_refresh=force_refresh,
                                                  check_version=True,
                                                  only_velero=True)

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def ui_compatibility_handler(version):
    payload = await ui_compatibility_service(version)

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)

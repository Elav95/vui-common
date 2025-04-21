from fastapi.responses import JSONResponse

from vui_common.schemas.response.successful_request import SuccessfulRequest

from vui_common.service.k8s import get_k8s_online_service


async def get_k8s_online_handler():
    payload = await get_k8s_online_service()

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)

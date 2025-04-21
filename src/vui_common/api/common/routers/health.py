from fastapi import APIRouter, Depends, status

from datetime import datetime

from vui_common.utils.swagger import route_description
from vui_common.utils.exceptions import handle_exceptions_endpoint

from vui_common.security.helpers.rate_limiter import LimiterRequests
from vui_common.security.helpers.rate_limiter import RateLimiter

from vui_common.schemas.response.successful_request import SuccessfulRequest

from vui_common.controllers.health import get_k8s_online_handler

router = APIRouter()


tag_name = 'Common Health'

endpoint_limiter = LimiterRequests(tags=tag_name,
                                   default_key='L1')

# ------------------------------------------------------------------------------------------------
#             GET UTC
# ------------------------------------------------------------------------------------------------


limiter_utc = endpoint_limiter.get_limiter_cust('health_utc')
route = '/utc'


@router.get(path=route,
            tags=[tag_name],
            summary='UTC time',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_utc.max_request,
                                          limiter_seconds=limiter_utc.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_utc.seconds,
                                              max_requests=limiter_utc.max_request))],
            response_model=dict,
            status_code=status.HTTP_200_OK
            )
@handle_exceptions_endpoint
async def get_utc() -> dict:
    return {'timestamp': datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')}


# ------------------------------------------------------------------------------------------------
#             GET KUBERNETES HEALTH
# ------------------------------------------------------------------------------------------------


limiter_k8s = endpoint_limiter.get_limiter_cust('health_k8s')
route = '/k8s'


@router.get(path=route,
            tags=[tag_name],
            summary='Get K8s connection an api status',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_k8s.max_request,
                                          limiter_seconds=limiter_k8s.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_k8s.seconds,
                                              max_requests=limiter_k8s.max_request))],
            response_model=SuccessfulRequest,
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_k8s_health():
    return await get_k8s_online_handler()

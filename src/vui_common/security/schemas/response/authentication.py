from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from vui_common.logger.logger_proxy import logger


class AuthenticationResponse:

    def is_response(self, response):
        logger.debug(f"is_response")
        return isinstance(response, (Response,
                                     HTMLResponse,
                                     JSONResponse,
                                     RedirectResponse))

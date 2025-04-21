from functools import wraps
import json

from vui_common.contexts.context import current_user_var
from vui_common.ws.ws_manager_proxy import ws_manager

from vui_common.logger.logger_proxy import logger


def trace_k8s_async_method(description):
    def decorator(fn):
        @wraps(fn)
        async def wrapper(*args, **kw):
            message = f"k8s {description}"
            # await manager.broadcast(message)
            try:
                user = current_user_var.get(None)
                if user is None:
                    logger.warning(f"No user found in context, message: {message}")
                else:
                    logger.debug(f"user:{user}, message:{message}")
                    response = {'type': 'k8s_tracker', 'message': message}
                    await ws_manager.send_personal_message(str(user.id), json.dumps(response))
            except Exception as Ex:
                logger.warning(f"{str(Ex)}, message:{message}")
                pass
            return await fn(*args, **kw)

        return wrapper

    return decorator

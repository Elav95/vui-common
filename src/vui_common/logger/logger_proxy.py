import logging

from vui_common.configs.config_proxy import config_app
from vui_common.logger.logger import ColoredLogger, LEVEL_MAPPING

logger = ColoredLogger.get_logger(__name__, level=LEVEL_MAPPING.get(config_app.logger.debug_level, logging.INFO))

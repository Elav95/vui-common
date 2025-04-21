from typing import Optional
import uvicorn

from vui_common.app_data import __version__, __app_name__
from vui_common.database.db_connection import SessionLocal
from vui_common.security.authentication.built_in_authentication.users import create_default_user
from vui_common.logger.logger_proxy import logger

# logger filter
from vui_common.configs.config_proxy import config_app
from vui_common.uvicorn_filter import uvicorn_logger # noqa

from vui_common.kubernetes_boot import config # noqa

# import sentry_sdk
#
# sentry_sdk.init(
#     dsn="http://b9ec3373cc7ef4345b891b8bc728614d@127.0.0.1:9009/2",
#     # Set traces_sample_rate to 1.0 to capture 100%
#     # of transactions for performance monitoring.
#     traces_sample_rate=1.0,
#     release=os.getenv('BUILD_VERSION', 'dev'),
#     environment=os.getenv('BUILD_VERSION', 'dev'),
# )


def run_api(
    app_module: str = "app:app",
    create_user: bool = True,
    reload: Optional[bool] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    log_level: Optional[str] = None,
    workers: int = 1,
    limit_concurrency: Optional[int] = None,
):
    """
    Start a uvicorn API server with base boot logic.
    Can be called by agent, core, or other modules.
    """

    logger.info('VUI API starting...')
    logger.info('loading config...')

    config_app.create_env_variables()

    if config_app.validate_env_variables():
        exit(200)

    logger.debug(f"App name: {__app_name__}, Version={__version__}")
    logger.debug(f"Uvicorn target app: {app_module}")
    logger.debug(f"Reload mode: {reload or config_app.app.uvicorn_reload}")
    logger.debug(f"Host: {host or config_app.api.endpoint_url}")
    logger.debug(f"Port: {port or config_app.api.endpoint_port}")
    logger.debug(f"Log level: {log_level or config_app.logger.debug_level}")
    logger.debug(f"Limit concurrency: {limit_concurrency or config_app.security.limit_concurrency}")

    # logger.debug(f"App name: {__app_name__}, Version={__version__}")
    # logger.debug(f"run server at url:{config_app.api.endpoint_url}, port={config_app.api.endpoint_port}")
    # logger.debug(
    #     f"uvicorn log level:{config_app.logger.debug_level}, limit concurrency : "
    #     f"{config_app.security.limit_concurrency}")
    # logger.debug(f"uvicorn reload: {config_app.app.uvicorn_reload}")

    #
    # init database and default user (if not exits)
    #
    if create_user:
        # create database session
        db = SessionLocal()
        logger.debug("Open database connection for check default user")
        # Create default user
        create_default_user(db)

        # Close
        db.close()
        logger.debug("Close database connection")

    # def start_uvicorn():
    uvicorn.run(app=app_module,
                host=config_app.api.endpoint_url,
                port=config_app.api.endpoint_port,
                reload=config_app.app.uvicorn_reload,
                log_level=config_app.logger.debug_level,
                workers=workers,
                limit_concurrency=config_app.security.limit_concurrency,
                log_config=None
                )

    # server_process = Process(target=start_uvicorn)
    # server_process.start()
    # time.sleep(2)


if __name__ == '__main__':
    run_api(app_module='vui_common.app:app')

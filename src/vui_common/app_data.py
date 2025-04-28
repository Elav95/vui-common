from vui_common.configs.config_proxy import config_app

__version__ = config_app.app.build_version
__date__ = config_app.app.build_date
__app_name__ = 'vui-common'
__app_summary__ = 'VUI-Common is part of the VUI Project'
__admin_email__ = config_app.app.admin_email
# __app_description__ = "<br>".join("{}: <b>{}</b>".format(k, v) for k, v in env.items())
__app_description__ = ''
__helm_version__ = config_app.helm.version
__helm_app_version__ = config_app.helm.app_version
__helm_api__ = config_app.helm.api
__helm_ui__ = config_app.helm.ui
__helm_watchdog__ = config_app.helm.watchdog
__helm_core__ = config_app.helm.core

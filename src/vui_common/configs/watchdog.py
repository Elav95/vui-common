import os

class WatchdogConfig:
    def __init__(self):
        self.url = self._get_watchdog_url()
        self.report_cronjob_name = os.getenv('WATCHDOG_REPORT_CRONJOB_NAME', f"{os.getenv('HELM_RELEASE_NAME')}-report-cronjob")

    @staticmethod
    def _get_watchdog_url():
        """Determines the Watchdog URL based on K8s mode."""
        watchdog_url = os.getenv('WATCHDOG_URL', '127.0.0.1').strip()
        watchdog_port = os.getenv('WATCHDOG_PORT', '8002').strip()
        return f"{watchdog_url}:{watchdog_port}"

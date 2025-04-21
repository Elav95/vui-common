from kubernetes import config

from vui_common.configs.config_proxy import config_app

from vui_common.logger.logger_proxy import logger


# Load Kubernetes configuration
try:
    config.load_incluster_config()
    logger.info("Kubernetes in cluster mode....")
except config.ConfigException:
    # Use local kubeconfig file if running locally
    config.load_kube_config(config_file=config_app.k8s.kube_config)
    logger.info("Kubernetes load local kube config...")

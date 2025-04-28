from kubernetes import client
from datetime import datetime

from vui_common.logger.logger_proxy import logger
from vui_common.utils.k8s_tracer import trace_k8s_async_method


async def _get_node_list(only_problem=False):
    """
    Obtain K8S nodes
    :param only_problem:
    :return: List of nodes
    """
    try:
        total_nodes = 0
        retrieved_nodes = 0
        add_node = True
        nodes = {}
        active_context = ''
        # Listing the cluster nodes
        node_list = client.CoreV1Api().list_node()
        for node in node_list.items:
            total_nodes += 1
            node_details = {}

            node_details['context'] = active_context
            node_details['name'] = node.metadata.name
            if 'kubernetes.io/role' in node.metadata.labels:
                node_details['role'] = node.metadata.labels['kubernetes.io/role']
                node_details['role'] = 'core'

            version = node.status.node_info.kube_proxy_version
            node_details['version'] = version

            node_details['architecture'] = node.status.node_info.architecture

            node_details['operating_system'] = node.status.node_info.operating_system

            node_details['kernel_version'] = node.status.node_info.kernel_version

            node_details['os_image'] = node.status.node_info.os_image

            node_details['addresses'] = node.status.addresses
            condition = {}
            for detail in node.status.conditions:
                condition[detail.reason] = detail.status

                if only_problem:
                    if add_node:
                        if detail.reason == 'KubeletReady':
                            if not bool(detail.status):
                                add_node = False
                        else:
                            if bool(detail.status):
                                add_node = False
                else:
                    add_node = True
            node_details['conditions'] = condition

            if add_node:
                retrieved_nodes += 1
                nodes[node.metadata.name] = node_details

        return total_nodes, retrieved_nodes, nodes

    except Exception as Ex:
        return 0, 0, None


@trace_k8s_async_method(description="Get k8s online status")
async def get_k8s_online_service():
    ret = False
    total_nodes = 0
    retr_nodes = 0
    try:
        total_nodes, retr_nodes, nodes = await _get_node_list(only_problem=True)
        if nodes is not None:
            ret = True

    except Exception as Ex:
        ret = False

    output = {'cluster_online': ret, 'nodes': {'total': total_nodes, 'in_error': retr_nodes},

              'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')}
    return output

@trace_k8s_async_method(description="Get configmap")
async def get_config_map_service(namespace, configmap_name):
    # Kubernetes API client
    core_api = client.CoreV1Api()

    try:
        # Retrieve the ConfigMap
        configmap = core_api.read_namespaced_config_map(name=configmap_name, namespace=namespace)
        # Access the data in the ConfigMap
        data = configmap.data
        if not data:
            return None
        kv = {}
        # Print out the data
        for key, value in data.items():
            if (key.startswith('SECURITY_TOKEN_KEY') or key.startswith('EMAIL_PASSWORD') or
                    key.startswith('TELEGRAM_TOKEN')):
                value = value[0].ljust(len(value) - 1, '*')
            kv[key] = value
        return kv
    except client.exceptions.ApiException as e:
        logger.warning(f"Exception when calling CoreV1Api->read_namespaced_config_map: {e}")
        # raise HTTPException(status_code=400, detail=f"Exception when calling "
        #                                             f"CoreV1Api->read_namespaced_config_map: {e}")
        return None

import os
import consul


def run_consul_diagnostics():
    import warnings
    from urllib3.exceptions import InsecureRequestWarning
    import requests
    result = {}  # Always initialize at the top
    # Setup Consul connection and variables
    skip_verify = os.environ.get('CONSUL_HTTP_SSL_VERIFY', 'true').lower()
    if skip_verify in ['0', 'false', 'no']:
        warnings.simplefilter('ignore', InsecureRequestWarning)
        verify = False
    else:
        verify = True
    consul_addr = os.environ.get('CONSUL_HTTP_ADDR', 'http://127.0.0.1:8500')
    scheme = 'http'
    addr = consul_addr
    if consul_addr.startswith('http://'):
        scheme = 'http'
        addr = consul_addr[len('http://'):]
    elif consul_addr.startswith('https://'):
        scheme = 'https'
        addr = consul_addr[len('https://'):]
    addr = addr.rstrip('/')
    if ':' in addr:
        host, port = addr.split(':', 1)
        port = int(port)
    else:
        host = addr
        port = 8500
    os.environ['CONSUL_HTTP_ADDR'] = f"{host}:{port}"
    verify = True
    skip_verify = os.environ.get('CONSUL_HTTP_SSL_VERIFY', 'true').lower()
    if skip_verify in ['0', 'false', 'no']:
        verify = False
    # Pass verify param to python-consul only if using HTTPS, else ignore
    if scheme == 'https':
        c = consul.Consul(host=host, port=port, scheme=scheme, verify=verify)
    else:
        c = consul.Consul(host=host, port=port, scheme=scheme)

    # Cluster state (members)
    try:
        members = c.agent.members()
        if members:
            result['members'] = members
    except Exception as e:
        result['members'] = f"Error: {e}"
    # Raft peers
    try:
        peers = c.status.peers()
        if peers:
            result['raft_peers'] = peers
    except Exception as e:
        result['raft_peers'] = f"Error: {e}"
    # Leader
    try:
        leader = c.status.leader()
        if leader:
            result['leader'] = leader
    except Exception as e:
        result['leader'] = f"Error: {e}"
    # Catalog nodes (pretty-print if tuple)
    try:
        nodes = c.catalog.nodes()
        if isinstance(nodes, tuple) and len(nodes) == 2 and isinstance(nodes[1], list):
            result['catalog_nodes'] = nodes[1]
        else:
            result['catalog_nodes'] = nodes
    except Exception as e:
        result['catalog_nodes'] = f"Error: {e}"
    # Autopilot Configuration
    try:
        autopilot_url = f"http://{host}:{port}/v1/operator/autopilot/configuration"
        if scheme == 'https':
            autopilot_url = f"https://{host}:{port}/v1/operator/autopilot/configuration"
        headers = {}
        consul_token = os.environ.get('CONSUL_HTTP_TOKEN')
        if consul_token:
            headers['X-Consul-Token'] = consul_token
        resp = requests.get(autopilot_url, headers=headers, verify=verify)
        if resp.ok:
            result['autopilot_configuration'] = resp.json()
        else:
            result['autopilot_configuration'] = f"Error: {resp.status_code} {resp.text}"
    except Exception as e:
        result['autopilot_configuration'] = f"Error: {e}"
    # Autopilot Health
    try:
        autopilot_health_url = f"http://{host}:{port}/v1/operator/autopilot/health"
        if scheme == 'https':
            autopilot_health_url = f"https://{host}:{port}/v1/operator/autopilot/health"
        headers = {}
        consul_token = os.environ.get('CONSUL_HTTP_TOKEN')
        if consul_token:
            headers['X-Consul-Token'] = consul_token
        resp = requests.get(autopilot_health_url, headers=headers, verify=verify)
        if resp.ok:
            result['autopilot_health'] = resp.json()
        else:
            result['autopilot_health'] = f"Error: {resp.status_code} {resp.text}"
    except Exception as e:
        result['autopilot_health'] = f"Error: {e}"
    # Autopilot State
    autopilot_state_url = f"http://{host}:{port}/v1/operator/autopilot/state"
    if scheme == 'https':
        autopilot_state_url = f"https://{host}:{port}/v1/operator/autopilot/state"
    headers = {}
    consul_token = os.environ.get('CONSUL_HTTP_TOKEN')
    if consul_token:
        headers['X-Consul-Token'] = consul_token
    try:
        resp = requests.get(autopilot_state_url, headers=headers, verify=verify)
        if resp.ok:
            result['autopilot_state'] = resp.json()
        else:
            result['autopilot_state'] = f"Error: {resp.status_code} {resp.text}"
    except Exception as e:
        result['autopilot_state'] = f"Error: {e}"
    # Datacenters List
    try:
        datacenters_url = f"http://{host}:{port}/v1/catalog/datacenters"
        if scheme == 'https':
            datacenters_url = f"https://{host}:{port}/v1/catalog/datacenters"
        headers = {}
        consul_token = os.environ.get('CONSUL_HTTP_TOKEN')
        if consul_token:
            headers['X-Consul-Token'] = consul_token
        resp = requests.get(datacenters_url, headers=headers, verify=verify)
        if resp.ok:
            result['datacenters_list'] = resp.json()
        else:
            result['datacenters_list'] = f"Error: {resp.status_code} {resp.text}"
    except Exception as e:
        result['datacenters_list'] = f"Error: {e}"
    # License Report
    try:
        license_url = f"http://{host}:{port}/v1/operator/license"
        if scheme == 'https':
            license_url = f"https://{host}:{port}/v1/operator/license"
        headers = {}
        consul_token = os.environ.get('CONSUL_HTTP_TOKEN')
        if consul_token:
            headers['X-Consul-Token'] = consul_token
        resp = requests.get(license_url, headers=headers, verify=verify)
        if resp.ok:
            result['license_report'] = resp.json()
        else:
            result['license_report'] = f"Error: {resp.status_code} {resp.text}"
    except Exception as e:
        result['license_report'] = f"Error: {e}"

    # Operator Usage
    try:
        usage_url = f"http://{host}:{port}/v1/operator/usage"
        if scheme == 'https':
            usage_url = f"https://{host}:{port}/v1/operator/usage"
        headers = {}
        consul_token = os.environ.get('CONSUL_HTTP_TOKEN')
        if consul_token:
            headers['X-Consul-Token'] = consul_token
        resp = requests.get(usage_url, headers=headers, verify=verify)
        if resp.ok:
            result['operator_usage'] = resp.json()
        else:
            result['operator_usage'] = f"Error: {resp.status_code} {resp.text}"
    except Exception as e:
        result['operator_usage'] = f"Error: {e}"
    # Remove empty or error fields if they are just empty strings
    cleaned = {k: v for k, v in result.items() if v not in [None, '', {}, []]}
    return cleaned

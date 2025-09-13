
import os
import nomad

def run_nomad_diagnostics():
    # Suppress urllib3 InsecureRequestWarning if skip verify is set
    import warnings
    from urllib3.exceptions import InsecureRequestWarning
    import requests
    result = {}  # Always initialize at the top
    skip_verify = os.environ.get('NOMAD_SKIP_VERIFY', 'true').lower()
    if skip_verify in ['0', 'false', 'no']:
        warnings.simplefilter('ignore', InsecureRequestWarning)
    nomad_addr = os.environ.get('NOMAD_ADDR', 'http://127.0.0.1:4646')
    addr = nomad_addr
    scheme = 'http'
    if addr.startswith('http://'):
        scheme = 'http'
        addr = addr[len('http://'):]
    elif addr.startswith('https://'):
        scheme = 'https'
        addr = addr[len('https://'):]
    addr = addr.rstrip('/')
    if ':' in addr:
        host, port = addr.split(':', 1)
        port = int(port)
    else:
        host = addr
        port = 4646
    os.environ['NOMAD_ADDR'] = f"{host}:{port}"
    verify = not (skip_verify in ['0', 'false', 'no'])
    n = nomad.Nomad(host=host, port=port, verify=verify)
    try:
        import json
        # Autopilot Configuration
        try:
            autopilot_url = f"{scheme}://{host}:{port}/v1/operator/autopilot/configuration"
            resp = requests.get(autopilot_url, verify=verify)
            if resp.ok:
                result['autopilot_configuration'] = resp.json()
            else:
                result['autopilot_configuration'] = f"Error: {resp.status_code} {resp.text}"
        except Exception as e:
            result['autopilot_configuration'] = f"Error: {e}"

        # Autopilot Health
        try:
            autopilot_health_url = f"{scheme}://{host}:{port}/v1/operator/autopilot/health"
            resp = requests.get(autopilot_health_url, verify=verify)
            if resp.ok:
                result['autopilot_health'] = resp.json()
            else:
                result['autopilot_health'] = f"Error: {resp.status_code} {resp.text}"
        except Exception as e:
            result['autopilot_health'] = f"Error: {e}"

        # Raft Configuration
        try:
            raft_url = f"{scheme}://{host}:{port}/v1/operator/raft/configuration"
            resp = requests.get(raft_url, verify=verify)
            if resp.ok:
                result['raft_configuration'] = resp.json()
            else:
                result['raft_configuration'] = f"Error: {resp.status_code} {resp.text}"
        except Exception as e:
            result['raft_configuration'] = f"Error: {e}"

        # License Info
        try:
            license_url = f"{scheme}://{host}:{port}/v1/operator/license"
            resp = requests.get(license_url, verify=verify)
            if resp.ok:
                result['license_info'] = resp.json()
            else:
                result['license_info'] = f"Error: {resp.status_code} {resp.text}"
        except Exception as e:
            result['license_info'] = f"Error: {e}"

        # Leader (update to use /v1/status/leader)
        try:
            leader_url = f"{scheme}://{host}:{port}/v1/status/leader"
            resp = requests.get(leader_url, verify=verify)
            if resp.ok:
                result['leader'] = resp.json() if resp.headers.get('content-type','').startswith('application/json') else resp.text.strip()
            else:
                result['leader'] = f"Error: {resp.status_code} {resp.text}"
        except Exception as e:
            result['leader'] = f"Error: {e}"

        # List Peers
        try:
            peers_url = f"{scheme}://{host}:{port}/v1/status/peers"
            resp = requests.get(peers_url, verify=verify)
            if resp.ok:
                result['list_peers'] = resp.json()
            else:
                result['list_peers'] = f"Error: {resp.status_code} {resp.text}"
        except Exception as e:
            result['list_peers'] = f"Error: {e}"

        # Scheduler configuration (new logic)
        try:
            scheduler_url = f"{scheme}://{host}:{port}/v1/operator/scheduler/configuration"
            resp = requests.get(scheduler_url, verify=verify)
            if resp.ok:
                result['scheduler'] = resp.json()
            else:
                result['scheduler'] = f"Error: {resp.status_code} {resp.text}"
        except Exception as e:
            result['scheduler'] = f"Error: {e}"

    # ...existing code...

    # ...existing code...
    except Exception as e:
        result['error'] = f"Nomad connection or authentication failed: {e}"
    # Remove empty or error fields if they are just empty strings
    cleaned = {k: v for k, v in result.items() if v not in [None, '', {}, []]}
    return cleaned

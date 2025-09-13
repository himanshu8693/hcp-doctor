
import os
import requests
import glob
import json
import dateutil.parser

"""Nomad health checks"""
def check_nomad_health(addr=None, token=None, profile='auto'):
    NOMAD_ADDR = addr or os.environ.get("NOMAD_ADDR", "http://127.0.0.1:4646")
    NOMAD_TOKEN = token or os.environ.get("NOMAD_TOKEN", None)
    headers = {"X-Nomad-Token": NOMAD_TOKEN} if NOMAD_TOKEN else {}
    results = {"status": "ok", "details": [], "warnings": []}

    # --- Autopilot Operator State ---

    # --- Raft Configuration ---
    try:
        r = requests.get(f"{NOMAD_ADDR}/v1/operator/raft/configuration", headers=headers, timeout=5)
        if r.status_code == 200:
            results['details'].append({'raft_configuration': r.json()})
        else:
            results['warnings'].append(f"Raft configuration API error: {r.status_code}")
    except Exception as e:
        results['warnings'].append(f"Raft configuration check error: {e}")

    # --- Peers ---
    try:
        r = requests.get(f"{NOMAD_ADDR}/v1/status/peers", headers=headers, timeout=5)
        if r.status_code == 200:
            results['details'].append({'peers': r.json()})
        else:
            results['warnings'].append(f"Peers API error: {r.status_code}")
    except Exception as e:
        results['warnings'].append(f"Peers check error: {e}")
    results = {"status": "ok", "details": [], "warnings": []}
    # ...existing logic from both functions, merged here, using the profile argument as needed...
    # Version and uptime check
    try:
    # datetime is imported at the top
        r = requests.get(f"{NOMAD_ADDR}/v1/agent/self", headers=headers, timeout=5)
        if r.status_code == 200:
            agent = r.json().get('config', {})
            version = agent.get('Version')
            if version:
                results['details'].append({'nomad_version': version})
                try:
                    vparts = [int(x) for x in version.split('.')]
                    if vparts[0] < 1 or (vparts[0] == 1 and vparts[1] < 5):
                        results['warnings'].append(f"Nomad version {version} is EOL or unsupported!")
                except Exception:
                    pass
            # Uptime: use 'start_time' if available
            if 'start_time' in agent:
                try:
                    # dateutil.parser is imported at the top
                    start = dateutil.parser.isoparse(agent['start_time']).timestamp()
                    now = datetime.datetime.utcnow().timestamp()
                    uptime = now - start
                    results['details'].append({'nomad_uptime_seconds': uptime})
                except Exception:
                    pass
    except Exception as e:
        results['warnings'].append(f"Nomad version/uptime check error: {e}")
    # Config file validation (nomad.hcl or nomad.json)
    # glob and json are imported at the top
    try:
        config_files = glob.glob('/etc/nomad.d/nomad.*') + glob.glob('./nomad.*')
        found = False
        for f in config_files:
            if f.endswith('.json'):
                with open(f) as jf:
                    try:
                        cfg = json.load(jf)
                        found = True
                        # Example: check if server is enabled but no bootstrap_expect
                        if cfg.get('server', {}).get('enabled', False) and not cfg.get('server', {}).get('bootstrap_expect'):
                            results['warnings'].append(f"Config file {f}: server enabled but no bootstrap_expect set!")
                        if cfg.get('disable_update_check', False):
                            results['warnings'].append(f"Config file {f}: update check is disabled!")
                    except Exception as e:
                        results['warnings'].append(f"Config file {f}: JSON parse error: {e}")
            elif f.endswith('.hcl'):
                try:
                    import hcl2
                    with open(f, 'r') as hf:
                        cfg = hcl2.load(hf)
                        found = True
                        if 'server' in cfg and cfg['server'].get('enabled', False) and not cfg['server'].get('bootstrap_expect'):
                            results['warnings'].append(f"Config file {f}: server enabled but no bootstrap_expect set!")
                        if cfg.get('disable_update_check', False):
                            results['warnings'].append(f"Config file {f}: update check is disabled!")
                except ImportError:
                    results['warnings'].append(f"Config file {f}: hcl2 module not installed, skipping HCL parse.")
                except Exception as e:
                    results['warnings'].append(f"Config file {f}: HCL parse error: {e}")
        if not found:
            results['warnings'].append("No Nomad config file found for validation.")
    except Exception as e:
        results['warnings'].append(f"Nomad config file validation error: {e}")
    """
    Perform Nomad health checks using the Nomad HTTP API.
    Accepts addr and token as arguments, falling back to NOMAD_ADDR and NOMAD_TOKEN env vars.
    """
    # os and requests are imported at the top
    NOMAD_ADDR = addr or os.environ.get("NOMAD_ADDR", "http://127.0.0.1:4646")
    NOMAD_TOKEN = token or os.environ.get("NOMAD_TOKEN", None)
    headers = {"X-Nomad-Token": NOMAD_TOKEN} if NOMAD_TOKEN else {}
    results = {"status": "ok", "details": []}
    # Scheduler/leader health
    try:
        r = requests.get(f"{NOMAD_ADDR}/v1/status/leader", headers=headers, timeout=5)
        if r.status_code == 200:
            try:
                leader = r.json() if r.text else None
            except Exception as e:
                results["status"] = "fail"
                results["details"].append(f"Leader API returned invalid JSON: {e}")
                leader = None
            if not leader:
                results["status"] = "fail"
                results["details"].append("No Nomad leader detected!")
            else:
                results["details"].append({"leader": leader})
        elif r.status_code in (401, 403):
            results["status"] = "fail"
            results["details"].append(f"Leader API permission error: {r.status_code}. Check NOMAD_TOKEN.")
        else:
            results["status"] = "fail"
            results["details"].append(f"Leader API error: {r.status_code}")
    except requests.exceptions.Timeout:
        results["status"] = "fail"
        results["details"].append("Leader API request timed out.")
    except requests.exceptions.ConnectionError:
        results["status"] = "fail"
        results["details"].append("Could not connect to Nomad at " + NOMAD_ADDR)
    except Exception as e:
        results["status"] = "fail"
        results["details"].append(f"Leader check exception: {e}")

    # Job allocations across clients
    try:
        r = requests.get(f"{NOMAD_ADDR}/v1/allocations", headers=headers, timeout=5)
        if r.status_code == 200:
            allocs = r.json()
            if not allocs:
                results["details"].append("No job allocations found.")
            else:
                failed = [a for a in allocs if a.get("ClientStatus") != "running"]
                if failed:
                    results["status"] = "fail"
                    results["details"].append(f"Failed allocations: {len(failed)}")
        else:
            results["details"].append(f"Allocations API error: {r.status_code}")
    except Exception as e:
        results["details"].append(f"Allocations check exception: {e}")

    # Plugin status (CSI, CNI)
    try:
        r = requests.get(f"{NOMAD_ADDR}/v1/plugins", headers=headers, timeout=5)
        if r.status_code == 200:
            plugins = r.json()
            for plugin in plugins:
                if plugin.get("State") != "running":
                    results["status"] = "fail"
                    results["details"].append(f"Plugin not running: {plugin.get('Name')}")
        else:
            results["details"].append(f"Plugins API error: {r.status_code}")
    except Exception as e:
        results["details"].append(f"Plugin check exception: {e}")

    return results

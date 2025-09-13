import os
import requests
import glob
import json
import datetime
"""Vault health checks"""
def check_vault_health(addr=None, token=None, profile='auto'):
    results = {"status": "ok", "details": [], "warnings": []}
    VAULT_ADDR = addr or os.environ.get("VAULT_ADDR", "http://127.0.0.1:8200")
    VAULT_TOKEN = token or os.environ.get("VAULT_TOKEN", None)
    headers = {"X-Vault-Token": VAULT_TOKEN} if VAULT_TOKEN else {}

    # --- DR & PR Replication Status ---
    try:
        r = requests.get(f"{VAULT_ADDR}/v1/sys/replication/performance/status", headers=headers, timeout=5)
        if r.status_code == 200:
            results['details'].append({'replication_performance_status': r.json()})
        else:
            results['warnings'].append(f"Performance replication status API error: {r.status_code}")
    except Exception as e:
        results['warnings'].append(f"Performance replication status check error: {e}")

    try:
        r = requests.get(f"{VAULT_ADDR}/v1/sys/replication/dr/status", headers=headers, timeout=5)
        if r.status_code == 200:
            results['details'].append({'replication_dr_status': r.json()})
        else:
            results['warnings'].append(f"DR replication status API error: {r.status_code}")
    except Exception as e:
        results['warnings'].append(f"DR replication status check error: {e}")

    # --- Raft (Integrated Storage) Checks ---
    try:
        r = requests.get(f"{VAULT_ADDR}/v1/sys/storage/raft/configuration", headers=headers, timeout=5)
        if r.status_code == 200:
            results['details'].append({'raft_configuration': r.json()})
        else:
            results['warnings'].append(f"Raft configuration API error: {r.status_code}")
    except Exception as e:
        results['warnings'].append(f"Raft configuration check error: {e}")

    try:
        r = requests.get(f"{VAULT_ADDR}/v1/sys/storage/raft/autopilot/state", headers=headers, timeout=5)
        if r.status_code == 200:
            results['details'].append({'raft_autopilot_state': r.json()})
        else:
            results['warnings'].append(f"Raft autopilot state API error: {r.status_code}")
    except Exception as e:
        results['warnings'].append(f"Raft autopilot state check error: {e}")

    try:
        r = requests.get(f"{VAULT_ADDR}/v1/sys/storage/raft/autopilot/configuration", headers=headers, timeout=5)
        if r.status_code == 200:
            results['details'].append({'raft_autopilot_config': r.json()})
        else:
            results['warnings'].append(f"Raft autopilot config API error: {r.status_code}")
    except Exception as e:
        results['warnings'].append(f"Raft autopilot config check error: {e}")

    # --- HA Status ---
    try:
        r = requests.get(f"{VAULT_ADDR}/v1/sys/ha/status", headers=headers, timeout=5)
        if r.status_code == 200:
            results['details'].append({'ha_status': r.json()})
        else:
            results['warnings'].append(f"HA status API error: {r.status_code}")
    except Exception as e:
        results['warnings'].append(f"HA status check error: {e}")
    # ...existing code for all checks, properly indented inside this function...
    # Version and uptime check
    try:
        r = requests.get(f"{VAULT_ADDR}/v1/sys/health", headers=headers, timeout=5)
        if r.status_code == 200:
            health = r.json()
            version = health.get('version')
            if version:
                results['details'].append({'vault_version': version})
                # Example: warn if version is < 1.10.0
                try:
                    vparts = [int(x) for x in version.split('+')[0].split('.')]
                    if vparts[0] < 1 or (vparts[0] == 1 and vparts[1] < 10):
                        results['warnings'].append(f"Vault version {version} is EOL or unsupported!")
                except Exception:
                    pass
            # Uptime: use server_time_utc if available
            if 'server_time_utc' in health:
                try:
                    now = datetime.datetime.utcnow().timestamp()
                    uptime = now - health['server_time_utc']
                    results['details'].append({'vault_uptime_seconds': uptime})
                except Exception:
                    pass
    except Exception as e:
        results['warnings'].append(f"Vault version/uptime check error: {e}")
    # Config file validation (vault.hcl or vault.json)
    try:
        config_files = glob.glob('/etc/vault.d/vault.*') + glob.glob('./vault.*')
        found = False
        for f in config_files:
            if f.endswith('.json'):
                with open(f) as jf:
                    try:
                        cfg = json.load(jf)
                        found = True
                        # Example: check if storage is inmem
                        if cfg.get('storage', {}).get('inmem') is not None:
                            results['warnings'].append(f"Config file {f}: storage backend is in-memory!")
                        if cfg.get('disable_mlock', False):
                            results['warnings'].append(f"Config file {f}: mlock is disabled!")
                    except Exception as e:
                        results['warnings'].append(f"Config file {f}: JSON parse error: {e}")
            elif f.endswith('.hcl'):
                try:
                    import hcl2
                    with open(f, 'r') as hf:
                        cfg = hcl2.load(hf)
                        found = True
                        # Example: check if storage is inmem
                        if 'storage' in cfg and 'inmem' in cfg['storage']:
                            results['warnings'].append(f"Config file {f}: storage backend is in-memory!")
                        if cfg.get('disable_mlock', False):
                            results['warnings'].append(f"Config file {f}: mlock is disabled!")
                except ImportError:
                    results['warnings'].append(f"Config file {f}: hcl2 module not installed, skipping HCL parse.")
                except Exception as e:
                    results['warnings'].append(f"Config file {f}: HCL parse error: {e}")
        if not found:
            results['warnings'].append("No Vault config file found for validation.")
    except Exception as e:
        results['warnings'].append(f"Vault config file validation error: {e}")
    """
    Perform Vault health checks using the Vault HTTP API.
    Accepts addr and token as arguments, falling back to VAULT_ADDR and VAULT_TOKEN env vars.
    """
    return results


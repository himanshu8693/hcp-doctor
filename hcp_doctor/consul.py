import os
import requests
import glob
import json
"""Consul health checks"""
def check_consul_health(addr=None, token=None, profile='auto'):
    results = {"status": "ok", "details": [], "warnings": []}
    CONSUL_HTTP_ADDR = addr or os.environ.get("CONSUL_HTTP_ADDR", "http://127.0.0.1:8500")
    CONSUL_HTTP_TOKEN = token or os.environ.get("CONSUL_HTTP_TOKEN", None)
    headers = {"X-Consul-Token": CONSUL_HTTP_TOKEN} if CONSUL_HTTP_TOKEN else {}
    # --- Autopilot Health & State ---
    try:
        r = requests.get(f"{CONSUL_HTTP_ADDR}/v1/operator/autopilot/health", headers=headers, timeout=5)
        results['details'].append({
            'endpoint': '/v1/operator/autopilot/health',
            'status_code': r.status_code,
            'response': r.text
        })
        if r.status_code == 200:
            results['details'].append({'autopilot_health': r.json()})
        else:
            results['warnings'].append(f"Autopilot health API error: {r.status_code}")
    except Exception as e:
        results['warnings'].append(f"Autopilot health check error: {e}")
    # ...add similar blocks for other Consul API checks as needed...
    return results
    # --- Autopilot Health & State ---
    try:
        r = requests.get(f"{CONSUL_HTTP_ADDR}/v1/operator/autopilot/health", headers=headers, timeout=5)
        if r.status_code == 200:
            results['details'].append({'autopilot_health': r.json()})
        else:
            results['warnings'].append(f"Autopilot health API error: {r.status_code}")
    except Exception as e:
        results['warnings'].append(f"Autopilot health check error: {e}")
    # ...existing code...
    # (Paste all code from the original consul.py, lines 11 to end, here, with correct indentation)
    # ...existing code...

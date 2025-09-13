import os
import hvac

def run_vault_diagnostics():
    # You can set VAULT_ADDR and VAULT_TOKEN as env vars or pass them here
    vault_addr = os.environ.get('VAULT_ADDR', 'http://127.0.0.1:8200')
    vault_token = os.environ.get('VAULT_TOKEN', None)
    if not vault_addr.startswith('http://') and not vault_addr.startswith('https://'):
        vault_addr = f'http://{vault_addr}'
    skip_verify = os.environ.get('VAULT_SKIP_VERIFY', 'false').lower() in ['1', 'true', 'yes']
    client = hvac.Client(url=vault_addr, token=vault_token, verify=not skip_verify)
    result = {}
    try:
        # HA_STATUS
        try:
            ha_resp = client.adapter.get('/v1/sys/ha-status')
            if ha_resp and isinstance(ha_resp, dict):
                result['ha_status'] = ha_resp
            else:
                result['ha_status'] = 'No HA status information returned.'
        except Exception as e:
            result['ha_status'] = f"Error: {e}"
        # SYSTEM_HEALTH
        try:
            health_resp = client.adapter.get('/v1/sys/health')
            if health_resp and isinstance(health_resp, dict):
                result['system_health'] = health_resp
            else:
                result['system_health'] = 'No health information returned.'
        except Exception as e:
            result['system_health'] = f"Error: {e}"
        # TOKEN_LOOKUP_SELF
        try:
            token_info = client.auth.token.lookup_self()
            if token_info:
                result['token_lookup_self'] = token_info
        except Exception as e:
            msg = str(e)
            if 'permission denied' in msg or 'invalid token' in msg:
                result['token_lookup_self'] = 'Permission denied or invalid token. Please check your Vault token.'
            else:
                result['token_lookup_self'] = f"Error: {msg}"
        # SEAL_STATUS
        try:
            seal_status = client.sys.read_seal_status()
            if seal_status:
                result['seal_status'] = seal_status
        except Exception as e:
            result['seal_status'] = f"Error: {e}"
        # LEADER
        try:
            leader = client.sys.read_leader_status()
            if leader:
                result['leader'] = leader
        except Exception as e:
            result['leader'] = f"Error: {e}"
        # LICENSE
        try:
            license_resp = client.adapter.get('/v1/sys/license/status')
            if license_resp and isinstance(license_resp, dict) and 'data' in license_resp:
                result['license'] = license_resp['data']
            else:
                license_info = client.sys.read_license()
                if license_info and isinstance(license_info, dict):
                    if 'data' in license_info:
                        result['license'] = license_info['data']
                    else:
                        result['license'] = license_info
                else:
                    result['license'] = 'No license information returned (Vault OSS or insufficient permissions).'
        except Exception as e:
            msg = str(e) or 'No license information returned (Vault OSS or insufficient permissions).'
            result['license'] = f"Error: {msg}"
        # REPLICATION_STATUS
        try:
            rep_summary = {}
            dr_resp = client.adapter.get('/v1/sys/replication/dr/status')
            if dr_resp and isinstance(dr_resp, dict) and 'data' in dr_resp:
                rep_summary['dr'] = dr_resp['data']
            else:
                rep_summary['dr'] = dr_resp
            perf_resp = client.adapter.get('/v1/sys/replication/performance/status')
            if perf_resp and isinstance(perf_resp, dict) and 'data' in perf_resp:
                rep_summary['performance'] = perf_resp['data']
            else:
                rep_summary['performance'] = perf_resp
            top_resp = client.adapter.get('/v1/sys/replication/status')
            if top_resp and isinstance(top_resp, dict) and 'data' in top_resp:
                rep_summary['summary'] = top_resp['data']
            else:
                rep_summary['summary'] = top_resp
            result['replication_status'] = rep_summary
        except Exception as e:
            msg = str(e) or 'No replication status returned (feature not enabled or insufficient permissions).'
            result['replication_status'] = f"Error: {msg}"
        # CONFIG
        try:
            config_resp = client.adapter.get('/v1/sys/config/state/sanitized')
            if config_resp and isinstance(config_resp, dict) and 'data' in config_resp:
                result['config'] = config_resp['data']
            else:
                result['config'] = config_resp
        except Exception as e:
            result['config'] = f"Error: {e}"
        # AUTOPILOT
        try:
            autopilot_resp = client.adapter.get('/v1/sys/storage/raft/autopilot/state')
            if autopilot_resp and isinstance(autopilot_resp, dict):
                if 'errors' in autopilot_resp:
                    result['autopilot'] = f"Error: {autopilot_resp['errors']} (This endpoint is only available for Raft/Integrated Storage)"
                else:
                    result['autopilot'] = autopilot_resp
            else:
                result['autopilot'] = 'Autopilot not enabled or not available (OSS or insufficient permissions).'
        except Exception as e:
            msg = str(e)
            result['autopilot'] = f"Error: {msg} (Autopilot endpoint failed or not available)"
        # RATE_LIMIT_QUOTAS
        try:
            quotas_resp = client.adapter.get('/v1/sys/quotas/config')
            if quotas_resp and isinstance(quotas_resp, dict) and 'data' in quotas_resp:
                result['rate_limit_quotas'] = quotas_resp['data']
            else:
                result['rate_limit_quotas'] = quotas_resp
        except Exception as e:
            result['rate_limit_quotas'] = f"Error: {e}"

        # LEASE_COUNT_QUOTA
        try:
            lease_quota_resp = client.adapter.get('/v1/sys/quotas/lease-count/global-lease-count-quota')
            # If Vault returns {"errors":[]} it means no quota is set
            if lease_quota_resp and isinstance(lease_quota_resp, dict):
                if 'errors' in lease_quota_resp and lease_quota_resp['errors'] == []:
                    result['lease_count_quota'] = 'No global lease count quota set.'
                else:
                    result['lease_count_quota'] = lease_quota_resp
            else:
                result['lease_count_quota'] = lease_quota_resp
        except Exception as e:
            result['lease_count_quota'] = f"Error: {e}"
    except Exception as e:
        result['error'] = f"Vault connection or authentication failed: {e}"
    cleaned = {k: v for k, v in result.items() if v not in [None, '', {}, []]}
    return cleaned

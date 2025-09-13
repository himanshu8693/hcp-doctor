from typing import Any

def get_section_state(section: str, value: Any) -> str:
    """
    Determine the health/state of a diagnostic section based on its value.
    Args:
        section (str): The section name.
        value (Any): The value to evaluate.
    Returns:
        str: The state ('Good', 'Failed', 'Healthy', 'Unhealthy', 'Unknown').
    """
    # Consul Autopilot Health/State logic
    if section == 'autopilot_health' and isinstance(value, dict):
        if value.get('Healthy') is True:
            return 'Healthy'
        elif value.get('Healthy') is False:
            return 'Unhealthy'
        else:
            return 'Unknown'
    if section == 'autopilot_state' and isinstance(value, dict):
        if value.get('Healthy') is True:
            return 'Healthy'
        elif value.get('Healthy') is False:
            return 'Unhealthy'
        else:
            return 'Unknown'
    if section == 'license_report' and isinstance(value, dict):
        if value.get('Valid') is True:
            return 'Good'
        elif value.get('Valid') is False:
            return 'Failed'
        else:
            return 'Unknown'
    if section == 'raft_peers':
        if isinstance(value, list) and len(value) > 0:
            return 'Good'
        else:
            return 'Failed'
    if section == 'leader':
        if isinstance(value, str) and value:
            return 'Good'
        elif isinstance(value, dict) and (value.get('ha_enabled') is False or value.get('is_self') or value.get('leader_address')):
            return 'Good'
        else:
            return 'Failed'
    if section == 'members':
        if isinstance(value, list) and len(value) > 0:
            return 'Good'
        else:
            return 'Failed'
    if section == 'ha_status' and isinstance(value, dict):
        nodes = value.get('nodes') or value.get('data', {}).get('nodes')
        if nodes and any(n.get('active_node') for n in nodes if isinstance(n, dict)):
            return 'Good'
        else:
            return 'Failed'
    if section == 'system_health' and isinstance(value, dict):
        if value.get('initialized') and not value.get('sealed') and not value.get('standby'):
            return 'Good'
        elif value.get('sealed'):
            return 'Failed'
        else:
            return 'Unknown'
    if section == 'seal_status' and isinstance(value, dict):
        if value.get('sealed') is False:
            return 'Good'
        elif value.get('sealed') is True:
            return 'Failed'
        else:
            return 'Unknown'
    if section == 'license' and isinstance(value, dict):
        if 'autoloaded' in value or 'expiration_time' in value:
            return 'Good'
        else:
            return 'Unknown'
    if section == 'replication_status' and isinstance(value, dict):
        for k in ['dr', 'performance', 'summary']:
            v = value.get(k, {})
            if isinstance(v, dict) and v.get('mode') not in ['unsupported', None]:
                return 'Good'
        return 'Unknown'
    if section == 'autopilot':
        if isinstance(value, dict) and not value.get('errors'):
            return 'Good'
        elif isinstance(value, str) and 'not enabled' in value.lower():
            return 'Unknown'
        elif isinstance(value, str) and 'error' in value.lower():
            return 'Failed'
        else:
            return 'Unknown'
    if section == 'rate_limit_quotas' and isinstance(value, dict):
        return 'Good' if value else 'Unknown'
    if section == 'lease_count_quota':
        if isinstance(value, str) and 'no global lease count quota set' in value.lower():
            return 'Unknown'
        elif isinstance(value, dict) and value:
            return 'Good'
        elif isinstance(value, str) and 'error' in value.lower():
            return 'Failed'
        else:
            return 'Unknown'
    if section == 'token_lookup_self' and isinstance(value, dict):
        if value.get('data', {}).get('id'):
            return 'Good'
        elif 'permission denied' in str(value).lower() or 'invalid token' in str(value).lower():
            return 'Failed'
        else:
            return 'Unknown'
    if section == 'catalog_nodes' and isinstance(value, list):
        if value:
            return 'Good'
        else:
            return 'Failed'
    if section == 'acl_bootstrap':
        if isinstance(value, dict) and value.get('ID'):
            return 'Good'
        elif isinstance(value, str) and 'not available' in value.lower():
            return 'Unknown'
        elif isinstance(value, str) and 'error' in value.lower():
            return 'Failed'
        else:
            return 'Unknown'
    if section == 'jobs' and isinstance(value, list):
        if value:
            return 'Good'
        else:
            return 'Failed'
    if section == 'plugins':
        if isinstance(value, str) and 'not available' in value.lower():
            return 'Unknown'
        elif isinstance(value, dict) and value:
            return 'Good'
        else:
            return 'Unknown'
    if section == 'cpu_percent':
        if isinstance(value, (int, float)) and value < 90:
            return 'Good'
        elif isinstance(value, (int, float)) and value >= 90:
            return 'Failed'
        else:
            return 'Unknown'
    if section == 'memory' and isinstance(value, dict):
        if value.get('percent', 0) < 90:
            return 'Good'
        elif value.get('percent', 0) >= 90:
            return 'Failed'
        else:
            return 'Unknown'
    if section == 'disk' and isinstance(value, dict):
        if value.get('percent', 0) < 90:
            return 'Good'
        elif value.get('percent', 0) >= 90:
            return 'Failed'
        else:
            return 'Unknown'
    if section == 'os' and isinstance(value, str):
        return 'Good' if value else 'Unknown'
    if section == 'upgrade_precheck':
        if isinstance(value, str) and 'no upgrade blockers' in value.lower():
            return 'Good'
        else:
            return 'Unknown'
    if section == 'snapshot_validation':
        if isinstance(value, str) and 'not implemented' in value.lower():
            return 'Unknown'
        elif isinstance(value, str) and 'valid' in value.lower():
            return 'Good'
        else:
            return 'Unknown'
    if section == 'error':
        return 'Failed'
    return 'Unknown'

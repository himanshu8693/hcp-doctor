import click
import json
import os

from hashicorp_doctor.vault.diagnostics import run_vault_diagnostics
from hashicorp_doctor.consul_diag.diagnostics import run_consul_diagnostics
from hashicorp_doctor.nomad_diag.diagnostics import run_nomad_diagnostics
from hashicorp_doctor.utils import get_section_state

def print_section(title, data, pdf=None):
    click.secho(f"\n{'='*60}", fg='cyan')
    click.secho(f"{title}", fg='green', bold=True)
    click.secho(f"{'='*60}", fg='cyan')


    if isinstance(data, dict):
        for key, value in data.items():
            state = get_section_state(key, value)
            # Special color and label for Consul Autopilot Health/State
            if key in ['autopilot_health', 'autopilot_state']:
                if state == 'Healthy':
                    state_color = 'green'
                elif state == 'Unhealthy':
                    state_color = 'red'
                else:
                    state_color = 'white'
                click.secho(f"\n  {key.upper()} -- {state}", fg=state_color, bold=True)
            else:
                state_color = {'Good': 'green', 'Failed': 'red', 'Unknown': 'white'}.get(state, 'white')
                click.secho(f"\n  {key.upper()} - {state}", fg=state_color, bold=True)
            click.secho(f"  {'-'*len(key)}", fg='yellow')
            if isinstance(value, dict) or isinstance(value, list):
                click.echo(json.dumps(value, indent=4, default=str))
            else:
                click.echo(f"  {value}")
            if pdf is not None:
                from fpdf.enums import XPos, YPos
                def safe_line(line):
                    # Replace all non-ASCII, non-printable, and problematic whitespace with '?'
                    return ''.join((c if 32 <= ord(c) <= 126 else '?') for c in line.replace('\t', ' ').replace('\n', ' '))
                pdf.set_font("Courier", size=10)
                pdf.cell(0, 8, f"{key.upper()} - {state}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font("Courier", size=8)
                text = json.dumps(value, indent=2, default=str)
                for line in text.splitlines():
                    safe = safe_line(line)
                    if not safe.strip():
                        continue
                    # FPDFException workaround: forcibly break every character if needed
                    i = 0
                    while i < len(safe):
                        chunk = safe[i:i+90]
                        if not chunk.strip():
                            i += 90
                            continue
                        pdf.multi_cell(0, 5, chunk)
                        i += 90
                pdf.ln(2)
    elif isinstance(data, list):
        click.echo(json.dumps(data, indent=2, default=str))
        if pdf is not None:
            def safe_line(line):
                return ''.join((c if 32 <= ord(c) <= 126 else '?') for c in line.replace('\t', ' ').replace('\n', ' '))
            pdf.set_font("Courier", size=8)
            text = json.dumps(data, indent=2, default=str)
            for line in text.splitlines():
                safe = safe_line(line)
                if not safe.strip():
                    continue
                i = 0
                while i < len(safe):
                    chunk = safe[i:i+90]
                    if not chunk.strip():
                        i += 90
                        continue
                    pdf.multi_cell(0, 5, chunk)
                    i += 90
            pdf.ln(2)
    else:
        click.echo(str(data))
        if pdf is not None:
            def safe_line(line):
                return ''.join((c if 32 <= ord(c) <= 126 else '?') for c in line.replace('\t', ' ').replace('\n', ' '))
            pdf.set_font("Courier", size=8)
            text = str(data)
            for line in text.splitlines():
                safe = safe_line(line)
                if not safe.strip():
                    continue
                i = 0
                while i < len(safe):
                    chunk = safe[i:i+90]
                    if not chunk.strip():
                        i += 90
                        continue
                    pdf.multi_cell(0, 5, chunk)
                    i += 90
            pdf.ln(2)


@click.group(context_settings=dict(help_option_names=['--help']))
@click.option('--vault-addr', type=str, help='Vault address (http(s)://host:port, overrides VAULT_ADDR env)')
@click.option('--vault-token', type=str, help='Vault token (overrides VAULT_TOKEN env)')
@click.option('--consul-addr', type=str, default=None, help='Consul address as http(s)://host:port or host:port (overrides CONSUL_HTTP_ADDR env, default: http://localhost:8500)')
@click.option('--consul-token', type=str, help='Consul token (overrides CONSUL_HTTP_TOKEN env)')
@click.option('--nomad-addr', type=str, help='Nomad address (http(s)://host:port, overrides NOMAD_ADDR env)')
@click.option('--nomad-token', type=str, help='Nomad token (overrides NOMAD_TOKEN env)')
@click.option('--profile', type=click.Choice(['auto', 'dev', 'prod', 'custom']), default='auto', show_default=True, help='Check profile: auto, dev, prod, custom')
@click.pass_context
def cli(ctx, vault_addr, vault_token, consul_addr, consul_token, nomad_addr, nomad_token, profile):
    """HCP Doctor: Cluster Health Diagnostics"""
    # Set env vars for diagnostics modules
    if vault_addr:
        os.environ['VAULT_ADDR'] = vault_addr
    if vault_token:
        os.environ['VAULT_TOKEN'] = vault_token
    # Determine Consul address: env > CLI > default
    consul_env = os.environ.get('CONSUL_HTTP_ADDR')
    if consul_env:
        os.environ['CONSUL_HTTP_ADDR'] = consul_env
    else:
        addr = consul_addr or 'http://localhost:8500'
        # Accept http(s)://host:port or host:port
        if not addr.startswith('http://') and not addr.startswith('https://'):
            addr = f'http://{addr}'
        os.environ['CONSUL_HTTP_ADDR'] = addr
    if consul_token:
        os.environ['CONSUL_HTTP_TOKEN'] = consul_token
    if nomad_addr:
        os.environ['NOMAD_ADDR'] = nomad_addr
    if nomad_token:
        os.environ['NOMAD_TOKEN'] = nomad_token
    ctx.ensure_object(dict)
    ctx.obj['profile'] = profile


# Add individual product commands to the CLI
@cli.command()
@click.option('--html', type=click.Path(), help='Generate HTML report at the given path')
@click.pass_context
def vault(ctx, html):
    """Run Vault diagnostics only."""
    click.secho('\n[Vault Diagnostics]', fg='yellow', bold=True)
    try:
        vault_diag = run_vault_diagnostics()
        print_section('Vault', vault_diag)
        if html:
            import os
            html_path = html
            if os.path.isdir(html):
                html_path = os.path.join(html, 'vault_diagnostics_report.html')
            html_lines = ["""
<html><head><meta charset='utf-8'><title>Vault Diagnostics Report</title><style>body { font-family: Arial, sans-serif; margin: 2em; } h1 { color: #2d5fa4; } h2 { color: #1a3d6d; border-bottom: 1px solid #ccc; } pre { background: #f8f8f8; border: 1px solid #ddd; padding: 8px; overflow-x: auto; }</style></head><body><h1>Vault Diagnostics Report</h1>
"""]
            html_lines.append(f"<pre>{json.dumps(vault_diag, indent=4, default=str)}</pre>")
            html_lines.append("</body></html>")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.writelines(html_lines)
            click.secho(f"\nHTML report generated at: {html_path}", fg='green', bold=True)
    except Exception as e:
        print(f'ERROR: Vault diagnostics failed: {e}')

@cli.command()
@click.option('--html', type=click.Path(), help='Generate HTML report at the given path')
@click.pass_context
def consul(ctx, html):
    """Run Consul diagnostics only."""
    click.secho('\n[Consul Diagnostics]', fg='yellow', bold=True)
    try:
        consul_diag = run_consul_diagnostics()
        print_section('Consul', consul_diag)
        if html:
            import os
            html_path = html
            if os.path.isdir(html):
                html_path = os.path.join(html, 'consul_diagnostics_report.html')
            html_lines = ["""
<html><head><meta charset='utf-8'><title>Consul Diagnostics Report</title><style>body { font-family: Arial, sans-serif; margin: 2em; } h1 { color: #2d5fa4; } h2 { color: #1a3d6d; border-bottom: 1px solid #ccc; } pre { background: #f8f8f8; border: 1px solid #ddd; padding: 8px; overflow-x: auto; }</style></head><body><h1>Consul Diagnostics Report</h1>
"""]
            html_lines.append(f"<pre>{json.dumps(consul_diag, indent=4, default=str)}</pre>")
            html_lines.append("</body></html>")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.writelines(html_lines)
            click.secho(f"\nHTML report generated at: {html_path}", fg='green', bold=True)
    except Exception as e:
        print(f'ERROR: Consul diagnostics failed: {e}')

@cli.command()
@click.option('--html', type=click.Path(), help='Generate HTML report at the given path')
@click.pass_context
def nomad(ctx, html):
    """Run Nomad diagnostics only."""
    click.secho('\n[Nomad Diagnostics]', fg='yellow', bold=True)
    try:
        nomad_diag = run_nomad_diagnostics()
        print_section('Nomad', nomad_diag)
        if html:
            import os
            html_path = html
            if os.path.isdir(html):
                html_path = os.path.join(html, 'nomad_diagnostics_report.html')
            html_lines = ["""
<html><head><meta charset='utf-8'><title>Nomad Diagnostics Report</title><style>body { font-family: Arial, sans-serif; margin: 2em; } h1 { color: #2d5fa4; } h2 { color: #1a3d6d; border-bottom: 1px solid #ccc; } pre { background: #f8f8f8; border: 1px solid #ddd; padding: 8px; overflow-x: auto; }</style></head><body><h1>Nomad Diagnostics Report</h1>
"""]
            html_lines.append(f"<pre>{json.dumps(nomad_diag, indent=4, default=str)}</pre>")
            html_lines.append("</body></html>")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.writelines(html_lines)
            click.secho(f"\nHTML report generated at: {html_path}", fg='green', bold=True)
    except Exception as e:
        print(f'ERROR: Nomad diagnostics failed: {e}')



@cli.command(help="Run diagnostic test for all runtime products.")
@click.option('--html', type=click.Path(), help='Generate HTML report at the given path')
@click.pass_context
def doctor(ctx, html):
    print('DEBUG: doctor command started')
    """Run diagnostics across all runtime products (Vault, Consul, Nomad, General)."""
    html_writer = None
    html_lines = []
    if html:
        html_writer = True
        html_lines.append("""
<html><head><meta charset='utf-8'><title>HashiCorp Doctor Report</title>
<style>
body { font-family: Arial, sans-serif; margin: 2em; }
h1 { color: #2d5fa4; }
h2 { color: #1a3d6d; border-bottom: 1px solid #ccc; }
.section { margin-bottom: 2em; }
.state-good { color: green; font-weight: bold; }
.state-failed { color: red; font-weight: bold; }
.state-unknown { color: #888; font-weight: bold; }
.state-healthy { color: green; font-weight: bold; }
.state-unhealthy { color: red; font-weight: bold; }
pre { background: #f8f8f8; border: 1px solid #ddd; padding: 8px; overflow-x: auto; }
</style></head><body>
<h1>HashiCorp Doctor Diagnostics Report</h1>
""")
    print(f'DEBUG: HTML report requested at {html}')
    def html_section(title, data):
        html_lines.append(f"<div class='section'><h2>{title}</h2>")
        if isinstance(data, dict):
            for key, value in data.items():
                state = get_section_state(key, value)
                state_class = {
                    'Good': 'state-good',
                    'Healthy': 'state-healthy',
                    'Failed': 'state-failed',
                    'Unhealthy': 'state-unhealthy',
                    'Unknown': 'state-unknown'
                }.get(state, 'state-unknown')
                html_lines.append(f"<div><span class='{state_class}'>{key.upper()} - {state}</span></div>")
                html_lines.append(f"<pre>{json.dumps(value, indent=4, default=str)}</pre>")
        elif isinstance(data, list):
            html_lines.append(f"<pre>{json.dumps(data, indent=2, default=str)}</pre>")
        else:
            html_lines.append(f"<pre>{str(data)}</pre>")
        html_lines.append("</div>")
    print('DEBUG: Running Vault diagnostics')
    click.secho('\n[Vault Diagnostics]', fg='yellow', bold=True)
    try:
        vault_diag = run_vault_diagnostics()
        print('DEBUG: Vault diagnostics complete')
        print_section('Vault', vault_diag)
        if html_writer: html_section('Vault', vault_diag)
    except Exception as e:
        print(f'ERROR: Vault diagnostics failed: {e}')
    print('DEBUG: Running Consul diagnostics')
    click.secho('\n[Consul Diagnostics]', fg='yellow', bold=True)
    try:
        consul_diag = run_consul_diagnostics()
        print('DEBUG: Consul diagnostics complete')
        print_section('Consul', consul_diag)
        if html_writer: html_section('Consul', consul_diag)
    except Exception as e:
        print(f'ERROR: Consul diagnostics failed: {e}')
    print('DEBUG: Running Nomad diagnostics')
    click.secho('\n[Nomad Diagnostics]', fg='yellow', bold=True)
    try:
        nomad_diag = run_nomad_diagnostics()
        print('DEBUG: Nomad diagnostics complete')
        print_section('Nomad', nomad_diag)
        if html_writer: html_section('Nomad', nomad_diag)
    except Exception as e:
        print(f'ERROR: Nomad diagnostics failed: {e}')
    if html_writer:
        print('DEBUG: Writing HTML report')
        html_lines.append("</body></html>")
        import os
        html_path = html
        if os.path.isdir(html):
            html_path = os.path.join(html, 'hcp_doctor_report.html')
        try:
            with open(html_path, 'w', encoding='utf-8') as f:
                f.writelines(html_lines)
            click.secho(f"\nHTML report generated at: {html_path}", fg='green', bold=True)
        except Exception as e:
            click.secho(f"HTML report failed: {e}", fg='red', bold=True)

@cli.command(help="Launch the web UI for visualized diagnostics and HTML report download.")
@click.option('--host', default='127.0.0.1', help='Host for the web UI (default: 127.0.0.1)')
@click.option('--port', default=5000, help='Port for the web UI (default: 5000)')
@click.pass_context
def web(ctx, host, port):
    """Launch the web UI for visualized diagnostics and HTML report download."""
    from hashicorp_doctor.web import app
    import webbrowser
    url = f"http://{host}:{port}/"
    print(f"Starting web UI at {url}")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    app.run(host=host, port=port, debug=False)

# Place Click CLI entrypoint at the end of the file
if __name__ == '__main__':
    cli()


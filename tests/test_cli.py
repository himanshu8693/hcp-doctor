import subprocess
import sys
import os
import pytest

def run_cli(args, env=None):
    cmd = [sys.executable, '-m', 'hashicorp_doctor.cli'] + args
    return subprocess.run(cmd, capture_output=True, text=True, env=env or os.environ.copy())

def test_vault_cli():
    result = run_cli(['vault'])
    assert result.returncode == 0
    assert '[Vault Diagnostics]' in result.stdout

def test_consul_cli():
    result = run_cli(['consul'])
    assert result.returncode == 0
    assert '[Consul Diagnostics]' in result.stdout

def test_nomad_cli():
    result = run_cli(['nomad'])
    assert result.returncode == 0
    assert '[Nomad Diagnostics]' in result.stdout


def test_doctor_cli():
    result = run_cli(['doctor'])
    assert result.returncode == 0
    assert '[Vault Diagnostics]' in result.stdout or '[Consul Diagnostics]' in result.stdout

def test_doctor_html(tmp_path):
    html_path = tmp_path / 'doctor_report.html'
    result = run_cli(['doctor', '--html', str(html_path)])
    assert result.returncode == 0
    assert html_path.exists()
    content = html_path.read_text()
    assert '<html>' in content and 'HashiCorp Doctor Diagnostics Report' in content

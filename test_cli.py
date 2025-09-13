
import subprocess
import os
import sys
import pytest

def test_doctor_cli_runs():
    result = subprocess.run([
        sys.executable, '-m', 'hashicorp_doctor.cli', 'doctor',
    ], capture_output=True, text=True)
    assert result.returncode == 0
    assert '[Vault Diagnostics]' in result.stdout or '[Consul Diagnostics]' in result.stdout or '[Nomad Diagnostics]' in result.stdout or '[General System Checks]' in result.stdout

def test_doctor_cli_html_report(tmp_path):
    html_path = tmp_path / 'doctor_report.html'
    result = subprocess.run([
        sys.executable, '-m', 'hashicorp_doctor.cli', 'doctor', '--html', str(html_path)
    ], capture_output=True, text=True)
    assert result.returncode == 0
    assert html_path.exists()
    content = html_path.read_text()
    assert '<html>' in content and 'HashiCorp Doctor Diagnostics Report' in content

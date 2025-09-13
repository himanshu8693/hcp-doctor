from flask import Flask, render_template_string, jsonify, send_file
import json
import io
from hashicorp_doctor.utils import get_section_state
from hashicorp_doctor.vault.diagnostics import run_vault_diagnostics
from hashicorp_doctor.consul_diag.diagnostics import run_consul_diagnostics
from hashicorp_doctor.nomad_diag.diagnostics import run_nomad_diagnostics

app = Flask(__name__)

@app.route('/report/html')
def report_html():
    html_lines = []
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
    def html_section(title, data):
        html_lines.append(f"<div class='section'><h2>{title}</h2>")
        if isinstance(data, dict):
            for key, value in data.items():
                state = get_section_state(key, value)
                state_class = {
                    'Good': 'state-good', 'Healthy': 'state-healthy',
                    'Failed': 'state-failed', 'Unhealthy': 'state-unhealthy',
                    'Unknown': 'state-unknown'
                }.get(state, 'state-unknown')
                html_lines.append(f"<div><span class='{state_class}'>{key.upper()} - {state}</span></div>")
                html_lines.append(f"<pre>{json.dumps(value, indent=4, default=str)}</pre>")
        elif isinstance(data, list):
            html_lines.append(f"<pre>{json.dumps(data, indent=2, default=str)}</pre>")
        else:
            html_lines.append(f"<pre>{str(data)}</pre>")
        html_lines.append("</div>")
    html_section('Vault', run_vault_diagnostics())
    html_section('Consul', run_consul_diagnostics())
    html_section('Nomad', run_nomad_diagnostics())
    html_lines.append("</body></html>")
    html_str = ''.join(html_lines)
    return html_str, 200, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/report/html/download')
def report_html_download():
    html_lines = []
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
    def html_section(title, data):
        html_lines.append(f"<div class='section'><h2>{title}</h2>")
        if isinstance(data, dict):
            for key, value in data.items():
                state = get_section_state(key, value)
                state_class = {
                    'Good': 'state-good', 'Healthy': 'state-healthy',
                    'Failed': 'state-failed', 'Unhealthy': 'state-unhealthy',
                    'Unknown': 'state-unknown'
                }.get(state, 'state-unknown')
                html_lines.append(f"<div><span class='{state_class}'>{key.upper()} - {state}</span></div>")
                html_lines.append(f"<pre>{json.dumps(value, indent=4, default=str)}</pre>")
        elif isinstance(data, list):
            html_lines.append(f"<pre>{json.dumps(data, indent=2, default=str)}</pre>")
        else:
            html_lines.append(f"<pre>{str(data)}</pre>")
        html_lines.append("</div>")
    html_section('Vault', run_vault_diagnostics())
    html_section('Consul', run_consul_diagnostics())
    html_section('Nomad', run_nomad_diagnostics())
    html_lines.append("</body></html>")
    html_bytes = ''.join(html_lines).encode('utf-8')
    html_io = io.BytesIO(html_bytes)
    html_io.seek(0)
    return send_file(html_io, mimetype='text/html', as_attachment=True, download_name='hcp_doctor_report.html')
@app.route('/report/txt')
def report_txt():
    import tempfile, os
    txt_lines = []
    txt_lines.append("HashiCorp Doctor Diagnostics Report\n")
    def txt_section(title, data):
        txt_lines.append(f"\n{'='*60}\n{title}\n{'='*60}\n")
        if isinstance(data, dict):
            for key, value in data.items():
                state = get_section_state(key, value)
                txt_lines.append(f"  {key.upper()} - {state}\n  {'-'*len(key)}\n")
                txt_lines.append(json.dumps(value, indent=4, default=str) + "\n")
        elif isinstance(data, list):
            txt_lines.append(json.dumps(data, indent=2, default=str) + "\n")
        else:
            txt_lines.append(str(data) + "\n")
    txt_section('Vault', run_vault_diagnostics())
    txt_section('Consul', run_consul_diagnostics())
    txt_section('Nomad', run_nomad_diagnostics())
    with tempfile.NamedTemporaryFile('w+', delete=False, encoding='utf-8', suffix='.txt') as f:
        f.writelines(txt_lines)
        temp_path = f.name
    return send_file(temp_path, mimetype='text/plain', as_attachment=True, download_name='hcp_doctor_report.txt')

def generate_pdf_report():
    from fpdf import FPDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Courier", size=12)
    pdf.cell(0, 10, "HashiCorp Doctor Diagnostics Report", ln=True, align='C')
    sections = [
        ("Vault", run_vault_diagnostics()),
        ("Consul", run_consul_diagnostics()),
        ("Nomad", run_nomad_diagnostics()),
    ]
    for title, data in sections:
        pdf.set_font("Courier", size=12)
        pdf.cell(0, 10, f"[{title} Diagnostics]", new_x=None, new_y=None)
        if isinstance(data, dict):
            for key, value in data.items():
                state = get_section_state(key, value)
                pdf.set_font("Courier", size=10)
                pdf.multi_cell(0, 6, f"{key.upper()} - {state}")
                pdf.set_font("Courier", size=8)
                text = json.dumps(value, indent=2, default=str)
                for line in text.splitlines():
                    i = 0
                    while i < len(line):
                        chunk = line[i:i+90]
                        pdf.multi_cell(0, 5, chunk)
                        i += 90
        elif isinstance(data, list):
            pdf.set_font("Courier", size=8)
            text = json.dumps(data, indent=2, default=str)
            for line in text.splitlines():
                i = 0
                while i < len(line):
                    chunk = line[i:i+90]
                    pdf.multi_cell(0, 5, chunk)
                    i += 90
        else:
            pdf.set_font("Courier", size=8)
            text = str(data)
            for line in text.splitlines():
                i = 0
                while i < len(line):
                    chunk = line[i:i+90]
                    pdf.multi_cell(0, 5, chunk)
                    i += 90
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return io.BytesIO(pdf_bytes)

@app.route('/report/pdf')
def report_pdf():
    pdf_io = generate_pdf_report()
    pdf_io.seek(0)
    return send_file(pdf_io, mimetype='application/pdf', as_attachment=True, download_name='hcp_doctor_report.pdf')

@app.route('/')
def index():
    return render_template_string('''
    <h1>HashiCorp Doctor</h1>
    <ul>
    <li><a href="/vault">Vault Diagnostics</a></li>
    <li><a href="/consul">Consul Diagnostics</a></li>
    <li><a href="/nomad">Nomad Diagnostics</a></li>
    <li><a href="/report/html" target="_blank"><b>View HTML Report</b></a></li>
    <li><a href="/report/html/download" download><b>Download HTML Report</b></a></li>
    </ul>
    ''')


def render_diagnostics(title, data):
    # Render HTML with section states and pretty JSON
    html = f'<h2>{title} Diagnostics</h2>'
    if isinstance(data, dict):
        for key, value in data.items():
            state = get_section_state(key, value)
            color = {'Good': 'green', 'Healthy': 'green', 'Failed': 'red', 'Unhealthy': 'red', 'Unknown': 'gray'}.get(state, 'gray')
            html += f'<div style="margin-bottom:1em;">'
            html += f'<b style="color:{color};">{key.upper()} - {state}</b><br>'
            html += f'<pre style="background:#f8f8f8;border:1px solid #ddd;padding:8px;">{json.dumps(value, indent=4, default=str)}</pre>'
            html += '</div>'
    else:
        html += f'<pre>{json.dumps(data, indent=4, default=str)}</pre>'
    html += '<a href="/">Back</a>'
    return html

@app.route('/vault')
def vault():
    data = run_vault_diagnostics()
    return render_template_string(render_diagnostics('Vault', data))

@app.route('/consul')
def consul():

    data = run_consul_diagnostics()
    return render_template_string(render_diagnostics('Consul', data))

@app.route('/nomad')
def nomad():
    data = run_nomad_diagnostics()
    return render_template_string(render_diagnostics('Nomad', data))

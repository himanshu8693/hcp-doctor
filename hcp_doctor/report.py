from fpdf import FPDF
import datetime

def generate_pdf_report(filename, vault_result, consul_result, nomad_result, general_result):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "HCP Doctor Cluster Diagnostics Report", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Generated: {datetime.datetime.now().isoformat()}", ln=True)
    pdf.ln(5)

    def section(title, result):
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, title, ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 8, f"Status: {result.get('status', 'unknown')}", ln=True)
        if result.get('warnings'):
            pdf.set_text_color(255, 140, 0)
            pdf.cell(0, 8, f"Warnings: {', '.join(result['warnings'])}", ln=True)
            pdf.set_text_color(0, 0, 0)
        if result.get('details'):
            for d in result['details']:
                pdf.multi_cell(0, 7, str(d))
        pdf.ln(3)

    section("Vault", vault_result)
    section("Consul", consul_result)
    section("Nomad", nomad_result)
    section("General", general_result)

    pdf.output(filename)

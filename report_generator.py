from fpdf import FPDF
import unicodedata

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
        self.set_doc_option('core_fonts_encoding', 'utf-8')

    def header(self):
        self.set_font('DejaVu', 'B', 12)
        self.cell(0, 10, 'Plagiarism Analysis Report', 0, 1, 'C')
    
    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def safe_text(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'replace').decode()

def generate_plagiarism_report(text, analysis, filename):
    pdf = PDF()
    pdf.add_page()
    
    # Document Preview
    pdf.set_font('DejaVu', 'B', 14)
    pdf.cell(0, 10, 'Document Preview', 0, 1)
    pdf.set_font('DejaVu', '', 10)
    pdf.multi_cell(0, 8, safe_text(text[:2000]))
    
    # Analysis Results
    pdf.add_page()
    pdf.set_font('DejaVu', 'B', 14)
    pdf.cell(0, 10, 'Detailed Analysis', 0, 1)
    
    # Direct Quotes
    pdf.set_font('DejaVu', 'B', 12)
    pdf.cell(0, 10, 'Direct Quotes:', 0, 1)
    pdf.set_font('DejaVu', '', 10)
    for quote in analysis['direct_quotes']:
        pdf.multi_cell(0, 8, safe_text(f'"{quote["text"]}"\nSources: {", ".join(quote["sources"])}'))
        pdf.ln(5)
    
    # Paraphrased Content
    pdf.add_page()
    pdf.set_font('DejaVu', 'B', 12)
    pdf.cell(0, 10, 'Paraphrased Content:', 0, 1)
    pdf.set_font('DejaVu', '', 10)
    for para in analysis['paraphrased']:
        pdf.multi_cell(0, 8, safe_text(f'Text: {para["text"][:200]}...\nSources: {", ".join(para["sources"])}'))
        pdf.ln(5)
    
    # References
    pdf.add_page()
    pdf.set_font('DejaVu', 'B', 12)
    pdf.cell(0, 10, 'Reference Validation:', 0, 1)
    pdf.set_font('DejaVu', '', 10)
    for ref in analysis['references']:
        status = "Valid" if ref['valid'] else "Invalid"
        pdf.multi_cell(0, 8, safe_text(f'[{status}] {ref["reference"]}'))
    
    report_path = f"reports/{filename}_report.pdf"
    pdf.output(report_path)
    return report_path
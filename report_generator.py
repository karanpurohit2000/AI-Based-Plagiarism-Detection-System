from fpdf import FPDF
import unicodedata
import datetime

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        # Add the regular DejaVuSans font (no bold)
        self.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
        
        # Get the current date and time for report generation
        self.generation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def header(self):
        self.set_font('DejaVu', '', 10)  # Use regular font (not bold)
        self.cell(0, 10, f'Report Generated: {self.generation_date}', 0, 1, 'L')
        self.set_font('DejaVu', '', 14)  # Use regular font (not bold)
        self.cell(0, 10, 'Plagiarism Analysis Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', '', 8)  # Use regular font for footer
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def safe_text(text):
    return unicodedata.normalize('NFKD', text).encode('latin-1', 'replace').decode('latin-1')

def generate_plagiarism_report(text, analysis, filename):
    pdf = PDF()
    pdf.add_page()
    
    # Score Display (using regular font)
    pdf.set_font('DejaVu', '', 16)  # Use regular font (not bold)
    pdf.cell(0, 10, f'Final Plagiarism Score: {analysis["plagiarism_score"]}%', 0, 1)
    pdf.ln(10)
    
    # Document Preview Section
    pdf.set_font('DejaVu', 'U', 12)  # Underlined, but regular font (not bold)
    pdf.cell(0, 10, 'Document Overview', 0, 1)
    pdf.set_font('DejaVu', '', 10)  # Use regular font
    preview_text = text[:2000] + (" [...]" if len(text) > 2000 else "")
    pdf.multi_cell(0, 8, safe_text(preview_text))
    pdf.add_page()

    # Analysis Details
    pdf.set_font('DejaVu', 'U', 12)  # Underlined, but regular font (not bold)
    pdf.cell(0, 10, 'Detailed Findings', 0, 1)
    pdf.ln(5)

    # Direct Quotes Section
    pdf.set_font('DejaVu', '', 12)  # Use regular font (not bold)
    pdf.cell(0, 10, 'Direct Matches Found:', 0, 1)
    for i, quote in enumerate(analysis['direct_quotes'], 1):
        pdf.set_font('DejaVu', '', 10)  # Use regular font (not bold)
        pdf.cell(0, 8, f'Match {i}:', 0, 1)
        pdf.multi_cell(0, 8, safe_text(f'"{quote["text"]}"'))
        pdf.cell(0, 8, f'Sources: {", ".join(quote["sources"][:2])}', 0, 1)
        pdf.ln(3)
    
    # Paraphrased Content
    pdf.add_page()
    pdf.set_font('DejaVu', '', 12)  # Use regular font (not bold)
    pdf.cell(0, 10, 'Paraphrased Content:', 0, 1)
    pdf.set_font('DejaVu', '', 10)
    for para in analysis['paraphrased']:
        pdf.multi_cell(0, 8, safe_text(f'Text: {para["text"][:200]}...\nSources: {", ".join(para["sources"])}'))
        pdf.ln(5)
    
    # References
    pdf.add_page()
    pdf.set_font('DejaVu', '', 12)  # Use regular font (not bold)
    pdf.cell(0, 10, 'Reference Validation:', 0, 1)
    pdf.set_font('DejaVu', '', 10)
    for ref in analysis['references']:
        status = "Valid" if ref['valid'] else "Invalid"
        pdf.multi_cell(0, 8, safe_text(f'[{status}] {ref["reference"]}'))
    
    report_path = f"reports/{filename}_report.pdf"
    pdf.output(report_path)
    return report_path

from fpdf import FPDF
import io
import os
from datetime import datetime
import re

class PDFReport(FPDF):
    def header(self):
        # Header background color
        self.set_fill_color(0, 102, 204) 
        self.rect(0, 0, 210, 40, 'F')
        
        # Title
        self.set_text_color(255, 255, 255)
        self.set_font('helvetica', 'B', 20)
        self.set_xy(10, 10) # Reset X and Y
        self.cell(0, 10, 'ANTIGRAVITY ILAC ANALIZ', ln=True, align='C')
        self.set_font('helvetica', 'I', 10)
        self.set_x(10) # Ensure X is at margin
        self.cell(0, 10, 'Saglikli Yasam ve Bilgi Asistani', ln=True, align='C')
        self.set_xy(10, 45) # Move cursor below header

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Sayfa {self.page_no()} / {{nb}} - Rapor Tarihi: {datetime.now().strftime("%d.%m.%Y")}', align='C')

def clean_for_helvetica(text: str) -> str:
    """Türkçe karakterleri düzeltir ve Helvetica'nın desteklemediği emojileri/karakterleri temizler."""
    replacements = {
        'ı': 'i', 'İ': 'I', 'ğ': 'g', 'Ğ': 'G', 'ü': 'u', 'Ü': 'U',
        'ş': 's', 'Ş': 'S', 'ö': 'o', 'Ö': 'O', 'ç': 'c', 'Ç': 'C',
    }
    for search, replace in replacements.items():
        text = text.replace(search, replace)
    
    # Emoji ve diğer latin-1 dışı karakterleri temizle
    # Sadece yazdırılabilir ASCII karakterlerini tutar
    return text.encode('ascii', 'ignore').decode('ascii')

def generate_pdf_report(drug_name: str, analysis_text: str) -> bytes:
    """Analiz sonucunu PDF olarak oluştur ve bytes döndür."""
    pdf = PDFReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Font setup
    font_family = "helvetica"
    # Note: Unicode fonts require .ttf files in assets/
    # If font files exist, we could use them here.
    
    # Title Section
    pdf.set_font(font_family, 'B', 16)
    pdf.set_text_color(0, 102, 204)
    pdf.set_x(10)
    display_name = clean_for_helvetica(drug_name).upper()
    pdf.cell(190, 10, f"ILAC ANALIZ RAPORU: {display_name}", ln=True)
    pdf.set_draw_color(0, 102, 204)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    # Disclaimer Box
    pdf.set_fill_color(255, 243, 205)
    pdf.set_text_color(133, 100, 4)
    pdf.set_font(font_family, 'B', 9)
    pdf.set_x(10)
    warning = "YASAL UYARI: Bu rapor yapay zeka tarafindan olusturulmustur. Tibbi tavsiye degildir."
    pdf.multi_cell(190, 8, warning, border=1, fill=True, align='C')
    pdf.ln(10)

    # Parsing and Writing Content
    pdf.set_text_color(0, 0, 0)
    
    # Split text into lines to handle markdown basics
    lines = analysis_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(2)
            continue
            
        # Clean for Helvetica
        line = clean_for_helvetica(line)
        
        # Headers
        if line.startswith('## '):
            pdf.ln(4)
            pdf.set_x(10)
            pdf.set_font(font_family, 'B', 13)
            pdf.set_text_color(0, 51, 102)
            pdf.cell(190, 10, line.replace('## ', '').replace('**',''), ln=True)
            pdf.set_font(font_family, '', 11)
            pdf.set_text_color(0, 0, 0)
        elif line.startswith('### '):
            pdf.ln(2)
            pdf.set_x(10)
            pdf.set_font(font_family, 'B', 11)
            pdf.cell(190, 8, line.replace('### ', '').replace('**',''), ln=True)
            pdf.set_font(font_family, '', 11)
        # Lists
        elif line.startswith('- ') or line.startswith('* '):
            pdf.set_font(font_family, '', 11)
            pdf.set_x(10)
            # Remove symbols and handle bold markers
            clean_line = line[2:].replace('**', '')
            pdf.multi_cell(190, 7, f" @ {clean_line}")
        else:
            # Regular text, remove bold markers
            clean_line = line.replace('**', '').strip()
            if clean_line:
                pdf.set_x(10)
                pdf.set_font(font_family, '', 11)
                pdf.multi_cell(190, 7, clean_line)

    # Output as sequence of bytes
    return pdf.output()

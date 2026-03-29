from fpdf import FPDF
import io
import os
from datetime import datetime

def normalize_turkish(text: str) -> str:
    replacements = {
        'ı': 'i', 'İ': 'I',
        'ğ': 'g', 'Ğ': 'G',
        'ü': 'u', 'Ü': 'U',
        'ş': 's', 'Ş': 'S',
        'ö': 'o', 'Ö': 'O',
        'ç': 'c', 'Ç': 'C',
    }
    for search, replace in replacements.items():
        text = text.replace(search, replace)
    return text

def generate_pdf_report(drug_name: str, analysis_text: str) -> bytes:
    """
    Analiz sonucunu PDF olarak oluştur ve bytes döndür.
    """
    pdf = FPDF()
    pdf.add_page()
    
    font_name = "Helvetica"
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        font_path = os.path.join(base_dir, "assets", "DejaVuSans.ttf")
        bold_font_path = os.path.join(base_dir, "assets", "DejaVuSans-Bold.ttf")
        if os.path.exists(font_path) and os.path.exists(bold_font_path):
            pdf.add_font("DejaVu", "", font_path, uni=True)
            pdf.add_font("DejaVu", "B", bold_font_path, uni=True)
            font_name = "DejaVu"
    except:
        pass

    if font_name == "Helvetica":
        drug_name = normalize_turkish(drug_name)
        analysis_text = normalize_turkish(analysis_text)

    # Başlık
    pdf.set_font(font_name, "B", 16)
    title_text = f"İlaç Analiz Raporu: {drug_name}" if font_name == "DejaVu" else f"Ilac Analiz Raporu: {drug_name}"
    pdf.cell(0, 12, title_text, ln=True, align="C")
    pdf.set_font(font_name, "", 10)
    
    date_text = f"Oluşturulma: {datetime.now().strftime('%d.%m.%Y %H:%M')}" if font_name == "DejaVu" else f"Olusturulma: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    pdf.cell(0, 8, date_text, ln=True, align="C")
    pdf.ln(5)

    # Uyarı kutusu
    pdf.set_fill_color(255, 243, 205)
    pdf.set_font(font_name, "B", 10)
    warning_text = "! BU RAPOR BILGILENDIRME AMACLIDIR. TIBBI TAVSIYE DEGILDIR. ILAC KULLANMADAN ONCE DOKTORUNUZA DANISINIZ."
    if font_name == "DejaVu":
        warning_text = "⚠️ BU RAPOR BİLGİLENDİRME AMAÇLIDIR. TIBBİ TAVSİYE DEĞİLDİR. İLAÇ KULLANMADAN ÖNCE DOKTORUNUZA DANIŞINIZ."
        
    pdf.multi_cell(0, 8, warning_text, fill=True)
    pdf.ln(5)

    # Analiz içeriği
    pdf.set_font(font_name, "", 11)
    clean_text = analysis_text.replace("##", "").replace("**", "").replace("*", "")
    
    # Emoji ve özel karakterleri temizle (fpdf Helvetica desteklemez)
    if font_name == "Helvetica":
        clean_text = clean_text.encode('ascii', 'ignore').decode('ascii')
        
    pdf.multi_cell(0, 7, clean_text)

    # PDF'i bytes olarak döndür.
    # fpdf2'de .output() bytearray döndürür.
    return bytes(pdf.output())

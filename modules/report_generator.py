from fpdf import FPDF
import io
from datetime import datetime

def generate_pdf_report(drug_name: str, analysis_text: str) -> bytes:
    """
    Analiz sonucunu PDF olarak oluştur ve bytes döndür.
    """
    pdf = FPDF()
    pdf.add_page()

    # Türkçe karakter desteği için font (Yerel sistemde font olmayabilir, standart fontlara dönülebilir veya hata yönetimi eklenebilir)
    # Varsayılan olarak Arial kullanılırsa Türkçe karakterler bozulabilir. 
    # Ancak fpdf2 ile 'helvetica' kullanıp 'latin-1' encoding ile deniyoruz.
    
    try:
        # Load local DejaVu font if placed in assets/
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        font_path = os.path.join(base_dir, "assets", "DejaVuSans.ttf")
        bold_font_path = os.path.join(base_dir, "assets", "DejaVuSans-Bold.ttf")
        if os.path.exists(font_path) and os.path.exists(bold_font_path):
            pdf.add_font("DejaVu", "", font_path, uni=True)
            pdf.add_font("DejaVu", "B", bold_font_path, uni=True)
            font_name = "DejaVu"
        else:
            font_name = "Helvetica"
    except:
        font_name = "Helvetica"

    # Başlık
    pdf.set_font(font_name, "B" if font_name == "DejaVu" else "B", 16)
    pdf.cell(0, 12, f"İlaç Analiz Raporu: {drug_name}", ln=True, align="C")
    pdf.set_font(font_name, "" if font_name == "DejaVu" else "", 10)
    pdf.cell(0, 8, f"Oluşturulma: {datetime.now().strftime('%d.%m.%Y %H:%M')}", ln=True, align="C")
    pdf.ln(5)

    # Uyarı kutusu
    pdf.set_fill_color(255, 243, 205)
    pdf.set_font(font_name, "B" if font_name == "DejaVu" else "B", 10)
    pdf.multi_cell(0, 8,
        "⚠️ BU RAPOR BİLGİLENDİRME AMAÇLIDIR. TIBBİ TAVSİYE DEĞİLDİR. "
        "İLAÇ KULLANMADAN ÖNCE DOKTORUNUZA DANIŞINIZ.",
        fill=True)
    pdf.ln(5)

    # Analiz içeriği
    pdf.set_font(font_name, "" if font_name == "DejaVu" else "", 11)
    # Markdown başlıklarını temizle
    clean_text = analysis_text.replace("##", "").replace("**", "").replace("*", "")
    pdf.multi_cell(0, 7, clean_text)

    # PDF'i bytes olarak döndür
    pdf_output = pdf.output(dest="S")
    if isinstance(pdf_output, str):
        return pdf_output.encode("latin-1")
    return bytes(pdf_output)

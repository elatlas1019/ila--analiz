import easyocr
import numpy as np
from PIL import Image
import streamlit as st
import sys
import os

class SuppressPrint:
    def __enter__(self):
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        sys.stdout = open(os.devnull, 'w', encoding='utf-8')
        sys.stderr = open(os.devnull, 'w', encoding='utf-8')
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr

@st.cache_resource
def get_ocr_reader():
    """EasyOCR reader'ı bir kez yükle, cache'le."""
    try:
        with SuppressPrint():
            return easyocr.Reader(['tr', 'en'], gpu=False)
    except Exception:
        return easyocr.Reader(['tr', 'en'], gpu=False)

def extract_text_from_image(image: Image.Image) -> str:
    """
    PIL Image'dan metin çıkar.
    EasyOCR kullanarak Türkçe + İngilizce destekler.
    """
    try:
        reader = get_ocr_reader()
        img_array = np.array(image)
        with SuppressPrint():
            results = reader.readtext(img_array, detail=0, paragraph=True)
        extracted = " ".join(results).strip()
        return extracted if extracted else ""
    except Exception as e:
        # Avoid crashing when printing error if charmap issues happen
        e_str = str(e).encode('ascii', 'ignore').decode('ascii')
        return f"OCR okunamadi: {e_str}"

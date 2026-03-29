from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """Sen deneyimli bir eczacı ve tıp bilgi asistanısın.
Kullanıcıya ilaçlar hakkında bilgi verirsin.
MUTLAKA her cevabın sonuna şu uyarıyı ekle:

⚠️ UYARI: Bu bilgiler genel bilgilendirme amaçlıdır. Tıbbi tavsiye değildir.
Herhangi bir ilaç kullanmadan önce mutlaka doktorunuza veya eczacınıza danışınız.
Kendi kendinize ilaç kullanmayınız.
"""

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        return None
    return Groq(api_key=api_key)

def analyze_drug(
    drug_name: str,
    active_ingredient: str,
    web_info: str,
    language: str = "tr"
) -> str:
    """
    Groq LLM ile ilaç analizi yap.
    Anahtar yoksa fallback olarak Web araması sonucunu biçimlendirir.
    """
    client = get_groq_client()
    
    # KULLANICI API GİRMEDİYSE:
    if not client:
        fallback_msg = f"## 💊 {drug_name} - İlaç Hakkında Bilgiler (Otomatik Web Özeti)\n\n"
        fallback_msg += "*(Not: Sistemde Groq(LLM) API anahtarı girili olmadığı için doğrudan web arama sonuçları gösterilmektedir.)*\n\n"
        if web_info and "Web'de bilgi bulunamadı" not in web_info:
            fallback_msg += f"### 🌐 İnternetten Bulunan Veriler:\n{web_info}\n\n"
        else:
            fallback_msg += f" {drug_name} ({active_ingredient}) için web üzerinde hızlı bir bilgi bulunamadı.\n\n"
        fallback_msg += "---\n⚠️ **UYARI**: Bu bilgiler otomatik çekilmiştir ve tıbbi tavsiye değildir. Lütfen doktorunuza veya eczacınıza danışınız."
        return fallback_msg

    prompt = f"""
İlaç Adı: {drug_name}
Etken Madde: {active_ingredient}

Web'den bulunan bilgiler:
{web_info[:3000] if web_info else "Web bilgisi bulunamadı."}

Lütfen şu başlıkları Türkçe olarak kapsamlı şekilde açıkla:

## 💊 İlaç Hakkında Genel Bilgi

## 🎯 Hangi Hastalıklara İyi Gelir (Endikasyonlar)

## ⚗️ Etken Madde ve Etki Mekanizması

## ⚠️ Yan Etkiler
- Yaygın yan etkiler
- Ciddi yan etkiler (varsa)

## 🚫 Kimler Kullanmamalı (Kontrendikasyonlar)

## 💊 Doz Bilgisi (Genel)

## 🔄 Muadil / Eşdeğer İlaçlar
(Aynı etken maddeyi içeren veya benzer etkili ilaçlar)

## 💡 Önemli Notlar

Bilgi bulunamayan bölümlerde etken maddeye göre genel yorumda bulun.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2048,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"LLM analiz hatası: {str(e)}"


def quick_ingredient_analysis(ingredients_text: str) -> str:
    """
    Sadece etken madde listesinden hızlı analiz.
    Anahtar yoksa uyarı döndürür.
    """
    client = get_groq_client()
    if not client:
        return f"## Hızlı Etken Madde Analizi\n\nOkunan Metin: {ingredients_text[:200]}\n\n(Not: Groq API key eksik olduğu için detaylı analiz yapılamıyor.)"

    prompt = f"""
Aşağıdaki etken madde/ilaç bilgilerini analiz et:

{ingredients_text[:2000]}

Kısa ve net şekilde:
1. Bu maddeler/ilaç ne için kullanılır?
2. Başlıca yan etkileri neler?
3. Kimler dikkatli olmalı?
4. Muadil alternatifleri neler?
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Analiz hatası: {str(e)}"

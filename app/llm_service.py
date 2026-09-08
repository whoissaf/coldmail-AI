import os
import json
import re
import logging
from dotenv import load_dotenv
import google.generativeai as genai
from groq import Groq
from openai import OpenAI

load_dotenv()
logger = logging.getLogger(__name__)

# Konfigurasi API Keys dari .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Nama Model Terverifikasi
GEMINI_MODEL = "gemini-3.6-flash"
GROQ_MODEL = "llama-3.3-70b-versatile"
OPENROUTER_MODEL = "google/gemini-3.6-flash"

def _clean_json_output(text: str) -> dict:
    """Membersihkan output LLM dari markdown block agar valid JSON"""
    clean_text = re.sub(r'^```json\s*', '', text, flags=re.IGNORECASE)
    clean_text = re.sub(r'\s*```$', '', clean_text, flags=re.IGNORECASE)
    return json.loads(clean_text.strip())

def generate_email_content(prospect_data: dict) -> dict:
    """
    Menghasilkan konten email dengan mekanisme fallback otomatis:
    Gemini 3.6 Flash -> Groq -> OpenRouter -> Mock (Garansi Anti-Crash)
    """
    personal_hook = ", ".join(prospect_data.get("personal_points", [])) or "your recent achievements"
    pain_hook = ", ".join(prospect_data.get("pain_points", [])) or "scaling your outbound"
    full_name = prospect_data.get("full_name", "there")
    
    prompt = f"""
    Act as an expert B2B sales copywriter. Write a highly personalized cold email.
    Prospect Name: {full_name}
    Personal Hook: {personal_hook}
    Pain Point: {pain_hook}
    
    Rules:
    1. Subject line: Max 60 characters, intriguing, lowercase preferred.
    2. Opening: 1-2 sentences directly referencing the personal hook.
    3. Body: Connect their pain point to ColdGenius AI naturally.
    4. CTA: Soft, low-friction question (e.g., "Open to a 15-min chat?").
    5. Tone: Professional, friendly, concise (under 150 words total).
    
    Output STRICTLY in JSON format only:
    {{
      "subject": "...",
      "body": "..."
    }}
    """

    # --- PRIORITAS 1: Gemini 3.6 Flash ---
    try:
        logger.info("🔄 Attempting LLM: Gemini 3.6 Flash...")
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        result = _clean_json_output(response.text)
        logger.info("✅ SUCCESS: Generated via Gemini 3.6 Flash")
        return result
    except Exception as e:
        logger.warning(f"⚠️ Gemini 3.6 Flash failed ({str(e)[:50]}...). Trying Groq...")

    # --- PRIORITAS 2: Groq ---
    try:
        logger.info("🔄 Attempting LLM: Groq...")
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        result = _clean_json_output(response.choices[0].message.content)
        logger.info("✅ SUCCESS: Generated via Groq")
        return result
    except Exception as e:
        logger.warning(f"⚠️ Groq failed ({str(e)[:50]}...). Trying OpenRouter...")

    # --- PRIORITAS 3: OpenRouter ---
    try:
        logger.info("🔄 Attempting LLM: OpenRouter...")
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )
        response = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        result = _clean_json_output(response.choices[0].message.content)
        logger.info("✅ SUCCESS: Generated via OpenRouter")
        return result
    except Exception as e:
        logger.error(f"⚠️ OpenRouter failed ({str(e)[:50]}...). Falling back to Mock AI...")

    # --- FALLBACK TERAKHIR: Mock AI (Garansi Sistem Tidak Crash) ---
    logger.info("🛡️ Using Mock AI as final fallback to ensure system stability.")
    return {
        "subject": f"Quick question about {personal_hook[:30]}...",
        "body": f"Hi {full_name},\n\nI noticed your work regarding {personal_hook}.\n\nGiven your focus on {pain_hook}, I thought ColdGenius AI could help increase your reply rates by 3-5x.\n\nAre you open to a 15-min chat next week?\n\nBest,\nColdGenius Team"
    }

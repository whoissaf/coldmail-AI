import os
import resend
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "onboarding@resend.dev")

def send_real_email(to_email: str, subject: str, body: str) -> dict:
    """
    Mengirim email sungguhan menggunakan Resend API.
    """
    try:
        params = {
            "from": f"ColdGenius AI <{SENDER_EMAIL}>",
            "to": [to_email],
            "subject": subject,
            "html": body.replace("\n", "<br>"), # Konversi newline ke HTML sederhana
            "text": body
        }
        email = resend.Emails.send(params)
        return {"status": "success", "email_id": email.get("id")}
    except Exception as e:
        print(f"❌ Resend API Error: {str(e)}")
        return {"status": "failed", "error": str(e)}

import time
import re

# Daftar domain email sementara/disposable yang umum digunakan untuk spam
DISPOSABLE_DOMAINS = {
    "tempmail.com", "yopmail.com", "mailinator.com", 
    "guerrillamail.com", "10minutemail.com", "throwaway.email"
}

def validate_email_address(email: str) -> dict:
    """
    Mock ZeroBounce / Hunter.io Email Validation.
    Mengembalikan: {"status": "valid" | "invalid" | "risky", "reason": str}
    """
    # Simulasi delay jaringan API eksternal (sangat ringan, 0.2 detik)
    time.sleep(0.2)
    
    # 1. Validasi Format Regex Dasar
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        return {"status": "invalid", "reason": "Invalid email format"}
    
    domain = email.split('@')[1].lower()
    
    # 2. Cek Domain Disposable (Hard Block)
    if domain in DISPOSABLE_DOMAINS:
        return {"status": "invalid", "reason": "Disposable/temporary email domain detected"}
    
    # 3. Cek Domain Gratisan (Risky untuk B2B Cold Email, tapi diizinkan dengan peringatan)
    if domain in ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]:
        return {"status": "risky", "reason": "Free email provider (B2B domain recommended for higher deliverability)"}
    
    # 4. Default: Valid (Domain perusahaan/kustom)
    return {"status": "valid", "reason": "Mailbox exists and is deliverable"}

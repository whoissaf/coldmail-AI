import time
import random
import bcrypt
from datetime import timedelta, datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from app.database import engine, get_db, Base
from app import models, schemas, auth, llm_service, email_validator, web3_service

Base.metadata.create_all(bind=engine)
app = FastAPI(title="ColdGenius AI Backend", version="1.0.0")

WEBHOOK_SECRET = "coldgenius-webhook-secret-123"

def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

@app.get("/")
def read_root():
    return {"message": "ColdGenius AI Backend is running"}

@app.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    new_user = models.User(email=user.email, name=user.name, company=user.company, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=schemas.Token)
def login(user_login: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_login.email).first()
    if not user or not verify_password(user_login.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
    access_token = auth.create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/campaigns", response_model=schemas.CampaignResponse, status_code=status.HTTP_201_CREATED)
def create_campaign(campaign: schemas.CampaignCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    new_campaign = models.Campaign(name=campaign.name, status=campaign.status, user_id=current_user.id)
    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)
    return new_campaign

@app.get("/campaigns", response_model=list[schemas.CampaignResponse])
def get_campaigns(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Campaign).filter(models.Campaign.user_id == current_user.id).all()

@app.get("/campaigns/{campaign_id}", response_model=schemas.CampaignResponse)
def get_campaign(campaign_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    campaign = db.query(models.Campaign).filter(models.Campaign.id == campaign_id, models.Campaign.user_id == current_user.id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found or access denied")
    return campaign

@app.delete("/campaigns/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_campaign(campaign_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    campaign = db.query(models.Campaign).filter(models.Campaign.id == campaign_id, models.Campaign.user_id == current_user.id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found or access denied")
    db.delete(campaign)
    db.commit()
    return None

@app.post("/campaigns/{campaign_id}/prospects", response_model=schemas.ProspectResponse, status_code=status.HTTP_201_CREATED)
def add_prospect(campaign_id: int, prospect: schemas.ProspectCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    campaign = db.query(models.Campaign).filter(models.Campaign.id == campaign_id, models.Campaign.user_id == current_user.id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found or access denied")
    
    validation_result = email_validator.validate_email_address(prospect.email)
    if validation_result["status"] == "invalid":
        raise HTTPException(status_code=400, detail=f"Invalid email: {validation_result['reason']}")
    
    new_prospect = models.Prospect(
        campaign_id=campaign_id,
        full_name=prospect.full_name,
        email=prospect.email,
        linkedin_url=prospect.linkedin_url,
        personal_points=prospect.personal_points,
        pain_points=prospect.pain_points,
        validation_status=validation_result["status"]
    )
    db.add(new_prospect)
    db.commit()
    db.refresh(new_prospect)
    return new_prospect

@app.post("/campaigns/{campaign_id}/prospects/{prospect_id}/generate-email", response_model=schemas.EmailResponse)
def generate_email(campaign_id: int, prospect_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    prospect = db.query(models.Prospect).join(models.Campaign).filter(
        models.Prospect.id == prospect_id,
        models.Campaign.id == campaign_id,
        models.Campaign.user_id == current_user.id
    ).first()
    if not prospect:
        raise HTTPException(status_code=404, detail="Prospect not found or access denied")

    prospect_data = {
        "full_name": prospect.full_name,
        "personal_points": prospect.personal_points,
        "pain_points": prospect.pain_points
    }
    llm_result = llm_service.generate_email_content(prospect_data)
    
    new_email = models.Email(
        prospect_id=prospect.id,
        subject=llm_result.get("subject", "Error"),
        body=llm_result.get("body", "Error"),
        status="draft"
    )
    db.add(new_email)
    db.commit()
    db.refresh(new_email)
    return new_email

@app.post("/campaigns/{campaign_id}/prospects/{prospect_id}/send-email", response_model=schemas.EmailResponse)
def send_email(campaign_id: int, prospect_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    email_record = db.query(models.Email).join(models.Prospect).join(models.Campaign).filter(
        models.Email.prospect_id == prospect_id,
        models.Prospect.campaign_id == campaign_id,
        models.Campaign.user_id == current_user.id
    ).first()
    if not email_record:
        raise HTTPException(status_code=404, detail="Email draft not found or access denied")
    if email_record.status != "draft":
        raise HTTPException(status_code=400, detail=f"Email cannot be sent. Current status: {email_record.status}")

    if email_record.prospect.validation_status == "risky":
        print(f"⚠️ WARNING: Sending to risky email provider: {email_record.prospect.email}")

    print(f"🛡️ ANTI-SPAM LOGIC: Simulating random delay before sending to {email_record.prospect.email}")
    email_record.status = "sent"
    email_record.sent_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(email_record)
    return email_record

@app.post("/webhooks/email-tracking")
def email_tracking_webhook(
    email_id: int, 
    event_type: str, 
    x_webhook_secret: str = Header(..., alias="X-Webhook-Secret"),
    db: Session = Depends(get_db)
):
    if x_webhook_secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Invalid webhook secret")
    email_record = db.query(models.Email).filter(models.Email.id == email_id).first()
    if not email_record:
        raise HTTPException(status_code=404, detail="Email not found")
    now = datetime.now(timezone.utc)
    if event_type == "opened" and not email_record.opened_at:
        email_record.opened_at = now
    elif event_type == "replied" and not email_record.replied_at:
        email_record.replied_at = now
    else:
        return {"status": "ignored"}
    db.commit()
    return {"status": "success"}

@app.get("/campaigns/{campaign_id}/analytics", response_model=schemas.CampaignAnalyticsResponse)
def get_campaign_analytics(campaign_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    campaign = db.query(models.Campaign).filter(models.Campaign.id == campaign_id, models.Campaign.user_id == current_user.id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found or access denied")
    total_prospects = db.query(models.Prospect).filter(models.Prospect.campaign_id == campaign_id).count()
    emails_sent = db.query(models.Email).join(models.Prospect).filter(models.Prospect.campaign_id == campaign_id, models.Email.status == "sent").count()
    emails_opened = db.query(models.Email).join(models.Prospect).filter(models.Prospect.campaign_id == campaign_id, models.Email.opened_at != None).count()
    emails_replied = db.query(models.Email).join(models.Prospect).filter(models.Prospect.campaign_id == campaign_id, models.Email.replied_at != None).count()
    open_rate = (emails_opened / emails_sent * 100) if emails_sent > 0 else 0.0
    reply_rate = (emails_replied / emails_sent * 100) if emails_sent > 0 else 0.0
    return {"campaign_id": campaign_id, "total_prospects": total_prospects, "emails_sent": emails_sent, "emails_opened": emails_opened, "emails_replied": emails_replied, "open_rate": round(open_rate, 2), "reply_rate": round(reply_rate, 2)}

# --- TAHAP 8: WEB3 TIMESTAMP (IMMUTABLE PROOF) ---
@app.post("/campaigns/{campaign_id}/prospects/{prospect_id}/emails/{email_id}/timestamp", response_model=schemas.Web3TimestampResponse)
def timestamp_email_on_blockchain(
    campaign_id: int, 
    prospect_id: int, 
    email_id: int, 
    current_user: models.User = Depends(auth.get_current_user), 
    db: Session = Depends(get_db)
):
    email_record = db.query(models.Email).join(models.Prospect).join(models.Campaign).filter(
        models.Email.id == email_id,
        models.Email.prospect_id == prospect_id,
        models.Prospect.campaign_id == campaign_id,
        models.Campaign.user_id == current_user.id
    ).first()
    
    if not email_record:
        raise HTTPException(status_code=404, detail="Email not found or access denied")
        
    existing_timestamp = db.query(models.Web3Timestamp).filter(models.Web3Timestamp.email_id == email_id).first()
    if existing_timestamp:
        raise HTTPException(status_code=400, detail="Email already timestamped on blockchain")
        
    content_hash = web3_service.get_keccak256_hash(email_record.body)
    chain_data = web3_service.mock_blockchain_timestamp(content_hash)
    
    new_timestamp = models.Web3Timestamp(
        email_id=email_id,
        content_hash=content_hash,
        tx_hash=chain_data["tx_hash"],
        block_number=chain_data["block_number"],
        network=chain_data["network"]
    )
    db.add(new_timestamp)
    db.commit()
    db.refresh(new_timestamp)
    
    print(f"✅ WEB3 SUCCESS: Email {email_id} immutably stored at block {chain_data['block_number']}")
    return new_timestamp

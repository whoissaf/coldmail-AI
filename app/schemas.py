from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    email: str
    name: str
    company: Optional[str] = None
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    company: Optional[str]
    plan: str
    created_at: datetime
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class CampaignCreate(BaseModel):
    name: str
    status: Optional[str] = "draft"

class CampaignResponse(BaseModel):
    id: int
    user_id: int
    name: str
    status: str
    created_at: datetime
    class Config:
        from_attributes = True

class ProspectCreate(BaseModel):
    full_name: str
    email: str
    linkedin_url: Optional[str] = None
    personal_points: Optional[List[str]] = None
    pain_points: Optional[List[str]] = None

class ProspectResponse(BaseModel):
    id: int
    campaign_id: int
    full_name: str
    email: str
    linkedin_url: Optional[str]
    personal_points: Optional[List[str]]
    pain_points: Optional[List[str]]
    validation_status: str
    created_at: datetime
    class Config:
        from_attributes = True

class EmailResponse(BaseModel):
    id: int
    prospect_id: int
    subject: str
    body: str
    status: str
    sent_at: Optional[datetime]
    opened_at: Optional[datetime]
    replied_at: Optional[datetime]
    class Config:
        from_attributes = True

class CampaignAnalyticsResponse(BaseModel):
    campaign_id: int
    total_prospects: int
    emails_sent: int
    emails_opened: int
    emails_replied: int
    open_rate: float
    reply_rate: float

class Web3TimestampResponse(BaseModel):
    id: int
    email_id: int
    content_hash: str
    tx_hash: str
    block_number: int
    network: str
    timestamped_at: datetime
    class Config:
        from_attributes = True

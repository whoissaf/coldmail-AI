from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    company = Column(String, nullable=True)
    plan = Column(String, default="Free Trial")
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    campaigns = relationship("Campaign", back_populates="user")

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, default="draft")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="campaigns")
    prospects = relationship("Prospect", back_populates="campaign")

class Prospect(Base):
    __tablename__ = "prospects"
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    linkedin_url = Column(Text, nullable=True)
    personal_points = Column(JSON, nullable=True)
    pain_points = Column(JSON, nullable=True)
    validation_status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    campaign = relationship("Campaign", back_populates="prospects")
    emails = relationship("Email", back_populates="prospect")

class Email(Base):
    __tablename__ = "emails"
    id = Column(Integer, primary_key=True, index=True)
    prospect_id = Column(Integer, ForeignKey("prospects.id"), nullable=False)
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    status = Column(String, default="draft")
    sent_at = Column(DateTime(timezone=True), nullable=True)
    opened_at = Column(DateTime(timezone=True), nullable=True)
    replied_at = Column(DateTime(timezone=True), nullable=True)
    prospect = relationship("Prospect", back_populates="emails")

class Web3Timestamp(Base):
    __tablename__ = "web3_timestamps"
    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id"), unique=True, nullable=False)
    content_hash = Column(String, nullable=False)
    tx_hash = Column(String, nullable=False)
    block_number = Column(Integer, nullable=False)
    network = Column(String, nullable=False)
    timestamped_at = Column(DateTime(timezone=True), server_default=func.now())
    
    email = relationship("Email")

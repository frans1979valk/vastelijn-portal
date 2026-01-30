from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="customer")  # admin/customer
    created_at = Column(DateTime, default=datetime.utcnow)

    devices = relationship("Device", back_populates="owner")


class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    label = Column(String, nullable=False)
    mode = Column(String, nullable=False)  # kiosk|fallback (legacy)
    config_key = Column(String, default="vastelijn_alleen")  # vastelijn_alleen|vastelijn_telegram|vastelijn_whatsapp
    status = Column(String, default="pending")  # pending|enrolled|online|offline
    qr_payload = Column(Text, default="")  # Headwind QR enrollment URL
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="devices")


class DownloadLog(Base):
    __tablename__ = "download_logs"
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    downloaded_at = Column(DateTime, default=datetime.utcnow)

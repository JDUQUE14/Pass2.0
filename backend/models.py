from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    cards = relationship("Card", back_populates="owner")
    access_logs = relationship("AccessLog", back_populates="user")


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    card_number = Column(String, unique=True, nullable=False, index=True)
    institution_name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    nfc_payload = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    owner = relationship("User", back_populates="cards")
    logs = relationship("AccessLog", back_populates="card")


class AccessLog(Base):
    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True, index=True)
    # Calculamos la hora actual UTC y le restamos 5 horas exactas para obtener la hora de Colombia
    timestamp = Column(DateTime, default=lambda: datetime.utcnow())
    location = Column(String, nullable=False)
    status = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    card_id = Column(Integer, ForeignKey("cards.id"))

    user = relationship("User", back_populates="access_logs")
    card = relationship("Card", back_populates="logs")
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

# Esquemas de Autenticación
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Esquemas de Carnets
class CardBase(BaseModel):
    card_number: str
    institution_name: str
    role: str

class CardResponse(CardBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class CardDetailResponse(CardResponse):
    nfc_payload: str

class LinkCardRequest(BaseModel):
    card_number: str

# ---------------------------------------------------------
# NUEVO: Esquema básico para mostrar el carnet dentro del log
# ---------------------------------------------------------
class CardBasicResponse(BaseModel):
    card_number: str
    institution_name: str

    class Config:
        from_attributes = True

# Esquema de Historial de Accesos (Actualizado con el carnet)
class AccessLogResponse(BaseModel):
    id: int
    timestamp: datetime
    location: str
    status: str
    card: Optional[CardBasicResponse] = None  # <--- Agregamos esto para incluir la info del carnet

    class Config:
        from_attributes = True
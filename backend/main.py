from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from database import engine, get_db
import models, schemas, auth_utils

# Crea las tablas en la BD automáticamente al iniciar
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pass API",
    version="1.0.0",
    description="API REST para la app Pass aplicando buenas prácticas"
)


# 1. Endpoint: Login (Autenticación)
@app.post("/api/v1/auth/login", response_model=schemas.TokenResponse, tags=["Auth"])
def login(credentials: schemas.LoginRequest, db: Session = Depends(get_db)):
    # 1. Buscar el usuario en la base de datos por su correo
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    
    # Si el usuario no existe en la base de datos
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Si la contraseña no coincide con el hash guardado
    if not auth_utils.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña incorrecta"
        )
        
    # Si todo es correcto, generamos el token de acceso
    access_token = auth_utils.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

# 2. Endpoint: Obtener Carnets (Pantalla Inicio / Wallet)
@app.get("/api/v1/cards", response_model=List[schemas.CardResponse], tags=["Cards"])
def get_user_cards(
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Card).filter(models.Card.user_id == current_user.id).all()

# 3. Endpoint: Detalle del Carnet y Payload NFC (Pantalla Detalle)
@app.get("/api/v1/cards/{card_id}", response_model=schemas.CardDetailResponse, tags=["Cards"])
def get_card_detail(
    card_id: int,
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(get_db)
):
    card = db.query(models.Card).filter(
        models.Card.id == card_id,
        models.Card.user_id == current_user.id
    ).first()
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carnet no encontrado"
        )
    return card

# 4. Endpoint: Vincular Carnet (Pantalla Registro)
@app.post("/api/v1/cards/link", response_model=schemas.CardResponse, status_code=status.HTTP_201_CREATED, tags=["Cards"])
def link_card(
    payload: schemas.LinkCardRequest,
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(get_db)
):
    card = db.query(models.Card).filter(models.Card.card_number == payload.card_number).first()
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Número de carnet no existente en el sistema"
        )
    if card.user_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este carnet ya está vinculado a un usuario"
        )
    card.user_id = current_user.id
    db.commit()
    db.refresh(card)
    return card

# 5. Endpoint: Historial de Accesos (Pantalla Historial)
@app.get("/api/v1/access-logs", response_model=List[schemas.AccessLogResponse], tags=["Logs"])
def get_access_logs(
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.AccessLog).filter(models.AccessLog.user_id == current_user.id).all()

# 6. Endpoint: Registrar Acceso NFC (Pantalla Detalle NFC)
class AccessLogCreate(BaseModel):
    location: str
    status: str
    card_id: int  # Incluimos el ID del carnet para relacionarlo

@app.post("/api/v1/access-logs", response_model=schemas.AccessLogResponse, status_code=status.HTTP_201_CREATED, tags=["Logs"])
def create_access_log(
    payload: AccessLogCreate,
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(get_db)
):
    # Verificamos que el carnet pertenezca al usuario actual
    card = db.query(models.Card).filter(
        models.Card.id == payload.card_id,
        models.Card.user_id == current_user.id
    ).first()

    if not card:
        raise HTTPException(
            status_code=status_code.HTTP_404_NOT_FOUND,
            detail="El carnet especificado no existe o no te pertenece"
        )

    new_log = models.AccessLog(
        location=payload.location,
        status=payload.status,
        user_id=current_user.id,
        card_id=payload.card_id
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log
from database import SessionLocal
import models, auth_utils

db = SessionLocal()

# Verificar si ya existe el usuario de prueba
existing_user = db.query(models.User).filter(models.User.email == "estudiante@pass.com").first()

if not existing_user:
    # 1. Crear usuario de prueba (Contraseña: 123456)
    hashed_pwd = auth_utils.get_password_hash("123456")
    user = models.User(
        email="estudiante@pass.com", 
        hashed_password=hashed_pwd, 
        full_name="Juan Jose"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 2. Crear un carnet de prueba vinculado al usuario
    card = models.Card(
        card_number="CARD-2026-001",
        institution_name="Institución Universitaria",
        role="Estudiante",
        nfc_payload="NFC_SECURE_TOKEN_ABC123",
        user_id=user.id
    )
    db.add(card)
    db.commit()
    print("¡Usuario y carnet de prueba creados exitosamente!")
else:
    print("El usuario de prueba ya existe en la base de datos.")

db.close()
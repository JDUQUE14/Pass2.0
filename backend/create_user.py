from database import SessionLocal, engine, Base
import models
from passlib.context import CryptContext

# Asegura que las tablas existan en pass_app.db según tus modelos
Base.metadata.create_all(bind=engine)

# Configuración de hashing para la contraseña
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = SessionLocal()

# Datos del usuario real que deseas agregar
correo = "juan@gmail.com"
password_plana = "1234"
nombre_completo = "Juan Jose Castro Duque"

# Verificar si el usuario ya existe
user_existente = db.query(models.User).filter(models.User.email == correo).first()

if user_existente:
    print(f"⚠️ El usuario con correo '{correo}' ya se encuentra registrado.")
else:
    # Generar hash de la contraseña y crear la instancia
    hashed_pw = pwd_context.hash(password_plana)
    nuevo_usuario = models.User(
        email=correo,
        hashed_password=hashed_pw,
        full_name=nombre_completo,
        is_active=True
    )

    db.add(nuevo_usuario)
    db.commit()
    print(f"✅ ¡Usuario real '{nombre_completo}' creado exitosamente en la base de datos!")

db.close()
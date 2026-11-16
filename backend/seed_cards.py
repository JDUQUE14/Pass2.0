from database import SessionLocal
import models

def registrar_carnet_previo(card_number, institution_name, role, nfc_payload):
    db = SessionLocal()
    
    # Verificar si ya existe
    existing_card = db.query(models.Card).filter(models.Card.card_number == card_number).first()
    
    if not existing_card:
        new_card = models.Card(
            card_number=card_number,
            institution_name=institution_name,
            role=role,
            nfc_payload=nfc_payload,
            is_active=True,
            user_id=None # Libre para ser reclamado
        )
        db.add(new_card)
        db.commit()
        print(f"✅ ¡Éxito! Carnet {card_number} ({institution_name}) registrado y listo para vincular.")
    else:
        print(f"⚠️ El carnet {card_number} ya se encontraba registrado en el sistema.")
        
    db.close()

if __name__ == "__main__":
    # Aquí puedes agregar todos los carnets que quieras precargar:
    registrar_carnet_previo("cdf-123", "ITM", "Estudiante", "PAYLOAD_SECRETO_ITM_123")
    registrar_carnet_previo("cdf-456", "Pascual Bravo", "Estudiante", "PAYLOAD_SECRETO_PASCUAL_456")
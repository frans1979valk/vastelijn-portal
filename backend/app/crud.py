from sqlalchemy.orm import Session
from .models import User, Device
from .auth import hash_pw, verify_pw
from .headwind_client import get_headwind_client, CONFIGURATIONS


def create_user(db: Session, email: str, password: str, role: str = "customer"):
    u = User(email=email.lower().strip(), password_hash=hash_pw(password), role=role)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def authenticate(db: Session, email: str, password: str):
    u = db.query(User).filter(User.email == email.lower().strip()).first()
    if not u or not verify_pw(password, u.password_hash):
        return None
    return u


def list_devices(db: Session, owner_id: int):
    return (
        db.query(Device)
        .filter(Device.owner_id == owner_id)
        .order_by(Device.id.desc())
        .all()
    )


def create_device(db: Session, owner_id: int, label: str, config_key: str):
    """Maak een nieuw device aan met Headwind QR provisioning URL"""
    # Valideer config_key
    if config_key not in CONFIGURATIONS:
        config_key = "vastelijn_alleen"

    # Haal de QR URL op van Headwind
    client = get_headwind_client()
    config = CONFIGURATIONS[config_key]
    qr_payload = f"https://android.vastelijn.eu/#/qr/{config['qr_key']}"

    # Mode is nu gebaseerd op config (legacy support)
    mode = "kiosk"

    d = Device(
        owner_id=owner_id,
        label=label,
        mode=mode,
        config_key=config_key,
        qr_payload=qr_payload,
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


def get_device(db: Session, owner_id: int, device_id: int):
    return (
        db.query(Device)
        .filter(Device.owner_id == owner_id, Device.id == device_id)
        .first()
    )

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
import os
import hashlib
import base64
import subprocess
import json

from .db import Base, engine, get_db
from .settings import APP_NAME
from .crud import create_user, authenticate
from .auth import create_token, get_current_user
from .models import User, DownloadLog

Base.metadata.create_all(bind=engine)

app = FastAPI(title=APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory voor APK opslag
APK_DIR = "/app/data/apk"
CONFIG_FILE = "/app/data/config.json"
os.makedirs(APK_DIR, exist_ok=True)

def load_config():
    """Laad de huidige configuratie"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {
        "apk_filename": None,
        "apk_url": "https://portal.vastelijn.eu/api/public/apk",
        "checksum": "Ytae8RlFLC6/iaNh93mGXLyB8tnayAGrgYSKnsXNbTQ=",
        "package_name": "com.vastelijnphone",
        "admin_receiver": "com.vastelijnphone/.admin.VasteLijnDeviceAdminReceiver",
    }


def to_url_safe_base64(checksum: str) -> str:
    """
    Converteer standaard Base64 naar URL-safe Base64 voor Android provisioning.
    - Vervang + door -
    - Vervang / door _
    - Verwijder = padding
    """
    if not checksum:
        return checksum
    return checksum.replace("+", "-").replace("/", "_").rstrip("=")

def save_config(config):
    """Sla configuratie op"""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


class RegisterIn(BaseModel):
    email: EmailStr
    password: str


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class ConfigUpdate(BaseModel):
    apk_url: Optional[str] = None
    checksum: Optional[str] = None
    package_name: Optional[str] = None
    admin_receiver: Optional[str] = None


# ============ PUBLIEKE ENDPOINTS (geen login nodig) ============

@app.get("/api/health")
def health():
    return {"ok": True, "name": APP_NAME}


@app.get("/api/public/provisioning")
def get_provisioning():
    """
    Publiek endpoint - Haalt de QR provisioning data op.
    Dit is zichtbaar voor iedereen zonder login.
    """
    config = load_config()

    if not config.get("apk_url") or not config.get("checksum"):
        return {
            "configured": False,
            "message": "APK nog niet geconfigureerd. Admin moet eerst een APK uploaden.",
            "qr_json": None,
            "instructions": [],
        }

    # Converteer checksum naar URL-safe Base64 (Android vereiste)
    url_safe_checksum = to_url_safe_base64(config["checksum"])

    # Bouw de QR JSON payload (Variant B - direct APK download)
    qr_payload = {
        "android.app.extra.PROVISIONING_DEVICE_ADMIN_COMPONENT_NAME": config["admin_receiver"],
        "android.app.extra.PROVISIONING_DEVICE_ADMIN_PACKAGE_DOWNLOAD_LOCATION": config["apk_url"],
        "android.app.extra.PROVISIONING_DEVICE_ADMIN_SIGNATURE_CHECKSUM": url_safe_checksum,
        "android.app.extra.PROVISIONING_SKIP_ENCRYPTION": True,
        "android.app.extra.PROVISIONING_LEAVE_ALL_SYSTEM_APPS_ENABLED": True,
    }

    instructions = [
        "1. Factory reset het Android apparaat",
        "2. Kies taal en verbind met WiFi",
        "3. Tik 6x op het welkomstscherm om QR setup te starten",
        "4. Scan de QR code hieronder",
        "5. Wacht tot de app is gedownload en geinstalleerd",
        "6. De VasteLijn app start automatisch in kiosk mode",
    ]

    return {
        "configured": True,
        "qr_json": json.dumps(qr_payload),
        "qr_payload": qr_payload,
        "apk_url": config["apk_url"],
        "instructions": instructions,
    }


@app.get("/api/public/apk")
def download_apk(request: Request, db: Session = Depends(get_db)):
    """Publiek endpoint - Download de APK"""
    config = load_config()
    if not config.get("apk_filename"):
        raise HTTPException(404, "Geen APK beschikbaar")

    apk_path = os.path.join(APK_DIR, config["apk_filename"])
    if not os.path.exists(apk_path):
        raise HTTPException(404, "APK bestand niet gevonden")

    # Log de download
    log_entry = DownloadLog(
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", "")[:500],
    )
    db.add(log_entry)
    db.commit()

    return FileResponse(
        apk_path,
        media_type="application/vnd.android.package-archive",
        filename=config["apk_filename"],
    )


# ============ AUTH ENDPOINTS ============

@app.post("/api/auth/register")
def register(body: RegisterIn, db: Session = Depends(get_db)):
    existing = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
    if existing and existing > 0:
        raise HTTPException(403, "Registratie is uitgeschakeld. Admin account bestaat al.")
    u = create_user(db, body.email, body.password, role="admin")
    return {"id": u.id, "email": u.email, "role": u.role}


@app.post("/api/auth/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    u = authenticate(db, body.email, body.password)
    if not u:
        raise HTTPException(401, "Onjuiste login")
    return {"access_token": create_token(u.id, u.role), "token_type": "bearer"}


@app.get("/api/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "role": user.role}


# ============ ADMIN ENDPOINTS (login vereist) ============

@app.get("/api/admin/config")
def get_config(user: User = Depends(get_current_user)):
    """Admin: Haal huidige configuratie op"""
    return load_config()


@app.put("/api/admin/config")
def update_config(body: ConfigUpdate, user: User = Depends(get_current_user)):
    """Admin: Update configuratie (APK URL, checksum, etc)"""
    config = load_config()

    if body.apk_url is not None:
        config["apk_url"] = body.apk_url
    if body.checksum is not None:
        config["checksum"] = body.checksum
    if body.package_name is not None:
        config["package_name"] = body.package_name
    if body.admin_receiver is not None:
        config["admin_receiver"] = body.admin_receiver

    save_config(config)
    return config


@app.post("/api/admin/upload-apk")
async def upload_apk(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    """
    Admin: Upload een nieuwe APK.
    De checksum wordt automatisch berekend als apksigner beschikbaar is.
    """
    if not file.filename.endswith(".apk"):
        raise HTTPException(400, "Bestand moet een .apk zijn")

    # Sla APK op
    apk_path = os.path.join(APK_DIR, file.filename)
    content = await file.read()

    with open(apk_path, "wb") as f:
        f.write(content)

    # Bereken SHA-256 van het bestand (voor verificatie)
    file_hash = hashlib.sha256(content).hexdigest()

    # Probeer signing certificate checksum te berekenen met apksigner
    cert_checksum = None
    try:
        result = subprocess.run(
            ["apksigner", "verify", "--print-certs", apk_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            # Zoek SHA-256 digest in output
            for line in result.stdout.split("\n"):
                if "SHA-256 digest" in line:
                    hex_hash = line.split(":")[-1].strip()
                    # Converteer hex naar bytes en dan naar base64
                    hash_bytes = bytes.fromhex(hex_hash)
                    cert_checksum = base64.b64encode(hash_bytes).decode()
                    break
    except Exception as e:
        print(f"apksigner niet beschikbaar of fout: {e}")

    # Update config
    config = load_config()
    config["apk_filename"] = file.filename
    config["file_hash"] = file_hash
    if cert_checksum:
        config["checksum"] = cert_checksum
    save_config(config)

    return {
        "filename": file.filename,
        "file_hash": file_hash,
        "cert_checksum": cert_checksum,
        "message": "APK geupload" + (" en checksum berekend" if cert_checksum else ". Voer handmatig de checksum in."),
    }


@app.delete("/api/admin/apk")
def delete_apk(user: User = Depends(get_current_user)):
    """Admin: Verwijder de huidige APK"""
    config = load_config()

    if config.get("apk_filename"):
        apk_path = os.path.join(APK_DIR, config["apk_filename"])
        if os.path.exists(apk_path):
            os.remove(apk_path)

    config["apk_filename"] = None
    config["file_hash"] = None
    save_config(config)

    return {"message": "APK verwijderd"}


@app.get("/api/admin/stats")
def get_stats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Admin: Haal download statistieken op"""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)

    total_downloads = db.query(func.count(DownloadLog.id)).scalar() or 0
    today_downloads = db.query(func.count(DownloadLog.id)).filter(
        DownloadLog.downloaded_at >= today_start
    ).scalar() or 0
    week_downloads = db.query(func.count(DownloadLog.id)).filter(
        DownloadLog.downloaded_at >= week_start
    ).scalar() or 0

    # Laatste 10 downloads
    recent = db.query(DownloadLog).order_by(
        DownloadLog.downloaded_at.desc()
    ).limit(10).all()

    return {
        "total_downloads": total_downloads,
        "today_downloads": today_downloads,
        "week_downloads": week_downloads,
        "recent_downloads": [
            {
                "id": r.id,
                "ip_address": r.ip_address,
                "downloaded_at": r.downloaded_at.isoformat() if r.downloaded_at else None,
            }
            for r in recent
        ],
    }

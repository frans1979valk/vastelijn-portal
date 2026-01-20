"""
Headwind MDM API Client voor VasteLijn Portal
Haalt QR provisioning payloads op voor device enrollment.
"""
import httpx
from typing import Optional
from .settings import HEADWIND_BASE_URL, HEADWIND_ADMIN_USER, HEADWIND_ADMIN_PASS

# Beschikbare configuraties met hun QR keys
CONFIGURATIONS = {
    # === KLANT POLICIES ===
    "vastelijn_alleen": {
        "id": 3,
        "name": "VasteLijn - Alleen app",
        "description": "Kiosk mode met alleen de VasteLijn app",
        "qr_key": "b44353a7b7e8cf6a6ee6371e05067c46",
    },
    "vastelijn_telegram": {
        "id": 4,
        "name": "VasteLijn + Telegram",
        "description": "Kiosk mode met VasteLijn en Telegram",
        "qr_key": "61f688e2dfa81c0c4ad3eb135ca6d18d",
    },
    "vastelijn_whatsapp": {
        "id": 5,
        "name": "VasteLijn + WhatsApp",
        "description": "Kiosk mode met VasteLijn en WhatsApp",
        "qr_key": "38e1d91bfbc7d67ef34541fee64fce17",
    },
    # === ONTWIKKELING POLICIES ===
    "dev_ontwikkel": {
        "id": 6,
        "name": "DEV – Ontwikkeltoestel",
        "description": "NIET VOOR KLANTEN - USB debugging en Developer Options beschikbaar. Android Studio compatible.",
        "qr_key": "43db0b45a30f539cba65059ab332bcba",
    },
    "productie_kiosk": {
        "id": 7,
        "name": "VasteLijn – Productie Kiosk",
        "description": "ALLEEN KLANTEN - Volledig vergrendeld, geen ontsnapping, USB debugging geblokkeerd.",
        "qr_key": "7990654e1981baba208392101ebec9d6",
    },
    "kiosk_dev": {
        "id": 8,
        "name": "VasteLijn – Kiosk DEV",
        "description": "ONTWIKKELING - Kiosk mode AAN maar USB debugging toegestaan. Zet Developer Options AAN vóór enrollment!",
        "qr_key": "0435096ed832d7622605c45a3db6c729",
    },
}


class HeadwindClient:
    """Client voor Headwind MDM REST API"""

    def __init__(self):
        self.base_url = HEADWIND_BASE_URL.rstrip("/")
        self.username = HEADWIND_ADMIN_USER
        self.password = HEADWIND_ADMIN_PASS
        self._token: Optional[str] = None

    async def _login(self) -> str:
        """Login naar Headwind en krijg JWT token"""
        async with httpx.AsyncClient(verify=False) as client:
            # Headwind gebruikt MD5 hash van wachtwoord voor login
            import hashlib
            password_hash = hashlib.md5(self.password.encode()).hexdigest()

            response = await client.post(
                f"{self.base_url}/rest/public/jwt/login",
                json={"login": self.username, "password": password_hash},
                timeout=10.0,
            )
            if response.status_code == 200:
                data = response.json()
                self._token = data.get("token")
                return self._token
            else:
                raise Exception(f"Headwind login failed: {response.status_code} - {response.text}")

    async def get_token(self) -> str:
        """Get of refresh de JWT token"""
        if not self._token:
            await self._login()
        return self._token

    async def get_qr_provisioning_url(self, config_key: str) -> str:
        """
        Genereer de QR provisioning URL voor een configuratie.

        Args:
            config_key: Een van 'vastelijn_alleen', 'vastelijn_telegram', 'vastelijn_whatsapp'

        Returns:
            De volledige URL voor QR code scanning
        """
        if config_key not in CONFIGURATIONS:
            raise ValueError(f"Onbekende configuratie: {config_key}")

        config = CONFIGURATIONS[config_key]
        qr_key = config["qr_key"]

        # Headwind QR URL formaat
        return f"{self.base_url}/#/qr/{qr_key}"

    async def get_qr_payload(self, config_key: str) -> dict:
        """
        Haal de volledige QR provisioning payload op voor een configuratie.

        Returns:
            Dict met enrollment_url, qr_content, en installatie instructies
        """
        if config_key not in CONFIGURATIONS:
            raise ValueError(f"Onbekende configuratie: {config_key}")

        config = CONFIGURATIONS[config_key]
        qr_key = config["qr_key"]

        # Bouw de provisioning payload
        # Dit is het formaat dat Android Enterprise QR provisioning verwacht
        enrollment_url = f"{self.base_url}/#/qr/{qr_key}"

        # Android Enterprise provisioning payload
        # Ref: https://developers.google.com/android/management/provision-device
        provisioning_payload = {
            "android.app.extra.PROVISIONING_DEVICE_ADMIN_COMPONENT_NAME":
                "com.hmdm.launcher/com.hmdm.launcher.AdminReceiver",
            "android.app.extra.PROVISIONING_DEVICE_ADMIN_PACKAGE_DOWNLOAD_LOCATION":
                f"{self.base_url}/files/hmdm-{config['id']}.apk",
            "android.app.extra.PROVISIONING_LEAVE_ALL_SYSTEM_APPS_ENABLED": True,
            "android.app.extra.PROVISIONING_ADMIN_EXTRAS_BUNDLE": {
                "com.hmdm.DEVICE_ID": "",
                "com.hmdm.BASE_URL": self.base_url,
                "com.hmdm.SERVER_PROJECT": qr_key,
            }
        }

        return {
            "config_id": config["id"],
            "config_name": config["name"],
            "config_description": config["description"],
            "enrollment_url": enrollment_url,
            "qr_content": enrollment_url,  # Voor simpele QR code
            "provisioning_payload": provisioning_payload,
            "instructions": [
                "1. Factory reset het Android apparaat",
                "2. Tik 6x op het welkomstscherm om QR setup te starten",
                "3. Verbind met WiFi",
                "4. Scan de QR code",
                "5. Volg de installatie instructies",
                "6. Het apparaat wordt automatisch geconfigureerd",
            ],
        }

    def list_configurations(self) -> list:
        """Lijst alle beschikbare configuraties"""
        return [
            {
                "key": key,
                "id": config["id"],
                "name": config["name"],
                "description": config["description"],
            }
            for key, config in CONFIGURATIONS.items()
        ]


# Singleton instance
_client: Optional[HeadwindClient] = None


def get_headwind_client() -> HeadwindClient:
    """Get de singleton Headwind client"""
    global _client
    if _client is None:
        _client = HeadwindClient()
    return _client

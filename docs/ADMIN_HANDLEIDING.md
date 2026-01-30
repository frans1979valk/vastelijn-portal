# VasteLijn Portal - Admin Handleiding

Deze handleiding legt uit hoe je de VasteLijn Portal instelt en beheert.

## Inhoudsopgave

1. [Eerste keer inloggen](#eerste-keer-inloggen)
2. [APK uploaden](#apk-uploaden)
3. [Configuratie aanpassen](#configuratie-aanpassen)
4. [Download statistieken](#download-statistieken)
5. [Apparaat provisionen](#apparaat-provisionen)
6. [Problemen oplossen](#problemen-oplossen)

---

## Eerste keer inloggen

### Admin account aanmaken

Als er nog geen admin account bestaat, maak deze aan via de command line:

```bash
curl -X POST http://localhost:8008/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@jouwdomein.nl","password":"SterkWachtwoord123!"}'
```

**Let op:** Registratie is alleen mogelijk als er nog geen gebruiker bestaat.

### Inloggen

1. Ga naar de portal URL (bijv. `https://portal.vastelijn.eu`)
2. Klik op **"Admin Login"** rechtsboven
3. Vul je email en wachtwoord in
4. Klik op **"Login"**

---

## APK uploaden

### Stap 1: APK bestand selecteren

1. Log in op het admin panel
2. Zoek de sectie **"APK Uploaden"**
3. Klik op **"Bestand kiezen"** en selecteer je `.apk` bestand

### Stap 2: Uploaden

1. Klik op **"Upload APK"**
2. Wacht tot de upload compleet is
3. De checksum wordt automatisch berekend (als `apksigner` beschikbaar is)

### Checksum handmatig invoeren

Als de checksum niet automatisch wordt berekend:

1. Bereken de checksum op je computer:
   ```bash
   apksigner verify --print-certs app.apk | grep "SHA-256 digest"
   ```
2. Converteer de hex naar Base64
3. Vul dit in bij **"Signing Certificate Checksum"**

---

## Configuratie aanpassen

### APK Download URL

Dit is de URL waar Android apparaten de APK downloaden. Opties:

- **Portal URL:** `https://portal.vastelijn.eu/api/public/apk` (standaard)
- **Eigen hosting:** Als je de APK elders host

### Package Name

De Android package naam van je app:
- Standaard: `com.vastelijnphone`

### Device Admin Receiver

De volledige class naam van de Device Admin receiver:
- Standaard: `com.vastelijnphone/.admin.VasteLijnDeviceAdminReceiver`

### Configuratie opslaan

1. Pas de velden aan
2. Klik op **"Configuratie Opslaan"**
3. De QR code wordt automatisch bijgewerkt

---

## Download statistieken

Het admin panel toont:

| Statistiek | Beschrijving |
|------------|--------------|
| **Totaal downloads** | Alle downloads sinds het begin |
| **Vandaag** | Downloads van vandaag |
| **Afgelopen 7 dagen** | Downloads van de afgelopen week |
| **Recente downloads** | Lijst met laatste 10 downloads (tijd + IP) |

---

## Apparaat provisionen

### Voorbereiding

1. Zorg dat de APK is geüpload
2. Controleer dat **"QR Ready"** op **"Ja"** staat
3. Zorg dat het apparaat WiFi-verbinding heeft

### Stappen voor de gebruiker

1. **Factory reset** het Android apparaat
2. Kies taal en verbind met **WiFi**
3. Op het welkomstscherm: **tik 6x snel achter elkaar** op het scherm
4. De QR scanner opent
5. **Scan de QR code** van de portal
6. Wacht tot de app is gedownload en geïnstalleerd
7. De VasteLijn app start automatisch in kiosk mode

### Belangrijke tips

- Het apparaat moet een **schone factory reset** hebben
- De QR scanner werkt alleen op het **eerste welkomstscherm**
- Zorg voor een **stabiele WiFi verbinding**

---

## Problemen oplossen

### QR scanner start niet

**Probleem:** Na 6x tikken gebeurt er niets.

**Oplossingen:**
- Tik sneller en precies 6x achter elkaar
- Probeer op verschillende plekken op het scherm
- Sommige apparaten vereisen 7x of 8x tikken
- Zorg dat het de eerste keer opstarten is na factory reset

### Installatie mislukt

**Probleem:** APK download of installatie faalt.

**Controleer:**
- Is de APK correct geüpload? (Status: groen)
- Is de checksum correct?
- Heeft het apparaat internet?
- Is de APK URL bereikbaar?

Test de APK URL:
```bash
curl -I https://portal.vastelijn.eu/api/public/apk
```

### Device Owner: false

**Probleem:** App is geïnstalleerd maar niet in Device Owner mode.

**Oorzaak:** Apparaat was niet volledig gereset.

**Oplossing:**
1. Verwijder de app
2. Doe een **volledige factory reset**
3. Probeer opnieuw vanaf het begin

### Checksum fout

**Probleem:** Android weigert de APK vanwege checksum mismatch.

**Controleer:**
- Is de checksum in Base64 formaat? (niet hex)
- Is het de checksum van het **signing certificate** (niet van het APK bestand)?
- Gebruik `apksigner verify --print-certs` om de juiste checksum te krijgen

---

## Wachtwoord resetten

Als je het admin wachtwoord bent vergeten:

```bash
docker exec vastelijn-portal-api python -c "
from app.db import SessionLocal
from app.models import User
from app.auth import hash_pw

db = SessionLocal()
user = db.query(User).filter(User.email == 'admin@jouwdomein.nl').first()
user.password_hash = hash_pw('NieuwWachtwoord123!')
db.commit()
print('Wachtwoord gereset!')
db.close()
"
```

---

## Contact

Bij vragen of problemen, neem contact op met de beheerder.

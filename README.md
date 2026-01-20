# VasteLijn Portal (v1)

Dit pakket is een **startklare v1** van jouw klantinterface:

- Klant (of jij) logt in
- Klant maakt een apparaat-installatie aan
- Klant kiest **Kiosk** of **Fallback**
- Portaal toont installatie-instructies en een (nu nog) placeholder “QR/payload”

## Wat dit nu al doet
- Backend (FastAPI) met JWT-login
- SQLite database in `./data/portal.db`
- Frontend (static) met:
  - Login
  - Mijn apparaten
  - Nieuw apparaat toevoegen
  - Detailpagina met instructies + payload

## Wat dit nog niet doet (bewust)
- Geen betalingen, geen abonnementen
- Geen echte Headwind MDM integratie (QR/policies)
- Geen multi-tenant rollenmodel (alleen 1 admin in v1)

## Technologie
- Backend: FastAPI + SQLAlchemy + SQLite
- Frontend: plain HTML/CSS/JS
- Deployment: Docker Compose

## Snel starten
1) Zet `.env` klaar:

```bash
cp .env.example .env
nano .env
```

2) Start:

```bash
docker compose up -d --build
```

3) Open:
- Frontend: `http://<server-ip>:8088`
- API health: `http://<server-ip>:8008/api/health`

## Eerste admin aanmaken (1 keer)
In deze v1 is registratie alleen toegestaan zolang er nog **geen** user bestaat.

```bash
curl -X POST http://localhost:8008/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"jij@jouwdomein.nl","password":"SterkWachtwoord"}'
```

Daarna log je in via de web UI.

## Volgende stap
Lees `CLAUDE_PROMPT.md` om Claude Code de Headwind-koppeling te laten afmaken.

# VasteLijn Portal

Een self-service portal voor het provisionen van Android apparaten in Device Owner (kiosk) modus via QR codes.

## Functionaliteiten

- **Publieke QR pagina** - Gebruikers kunnen de QR code scannen om hun apparaat te provisionen
- **Admin panel** - APK uploaden, configuratie beheren, download statistieken bekijken
- **Automatische checksum** - APK signing certificate checksum wordt automatisch berekend
- **Download tracking** - Houdt bij hoeveel keer de APK is gedownload

## Technologie

| Component | Technologie |
|-----------|-------------|
| Backend | FastAPI + SQLAlchemy + SQLite |
| Frontend | Plain HTML/CSS/JavaScript |
| Deployment | Docker Compose |

## Snelle start

### 1. Clone en configureer

```bash
git clone https://github.com/JOUW_USERNAME/vastelijn-portal.git
cd vastelijn-portal
cp .env.example .env
nano .env
```

### 2. Start de containers

```bash
docker compose up -d --build
```

### 3. Maak de eerste admin aan

```bash
curl -X POST http://localhost:8008/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@jouwdomein.nl","password":"SterkWachtwoord123!"}'
```

### 4. Open de portal

- **Publieke pagina:** http://localhost:8088
- **Admin panel:** http://localhost:8088/#admin
- **API health:** http://localhost:8008/api/health

## Poorten

| Service | Interne poort | Externe poort |
|---------|---------------|---------------|
| API | 8000 | 8008 |
| Frontend | 80 | 8088 |

## Mapstructuur

```
vastelijn-portal/
├── backend/
│   ├── app/
│   │   ├── main.py        # FastAPI endpoints
│   │   ├── models.py      # Database modellen
│   │   ├── auth.py        # JWT authenticatie
│   │   ├── crud.py        # Database operaties
│   │   └── db.py          # Database configuratie
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── index.html
│   │   ├── app.js         # Frontend logica
│   │   └── styles.css
│   ├── nginx.conf
│   └── Dockerfile
├── data/                   # Persistente data (gemount volume)
│   ├── portal.db          # SQLite database
│   ├── config.json        # APK configuratie
│   └── apk/               # Geüploade APK bestanden
├── docker-compose.yml
├── .env.example
└── README.md
```

## API Endpoints

### Publiek (geen login)

| Method | Endpoint | Beschrijving |
|--------|----------|--------------|
| GET | `/api/health` | Health check |
| GET | `/api/public/provisioning` | QR provisioning data |
| GET | `/api/public/apk` | Download de APK |

### Auth

| Method | Endpoint | Beschrijving |
|--------|----------|--------------|
| POST | `/api/auth/register` | Registreer (alleen als er nog geen user is) |
| POST | `/api/auth/login` | Login, krijg JWT token |
| GET | `/api/me` | Huidige gebruiker info |

### Admin (login vereist)

| Method | Endpoint | Beschrijving |
|--------|----------|--------------|
| GET | `/api/admin/config` | Huidige configuratie |
| PUT | `/api/admin/config` | Update configuratie |
| POST | `/api/admin/upload-apk` | Upload nieuwe APK |
| DELETE | `/api/admin/apk` | Verwijder APK |
| GET | `/api/admin/stats` | Download statistieken |

## Productie deployment

Voor productie met HTTPS, plaats een reverse proxy (nginx/Caddy/Traefik) voor de containers:

```nginx
# Voorbeeld nginx config
server {
    listen 443 ssl;
    server_name portal.jouwdomein.nl;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8088;
    }

    location /api {
        proxy_pass http://127.0.0.1:8008;
    }
}
```

## Omgevingsvariabelen

Zie `.env.example` voor alle beschikbare variabelen:

```bash
SECRET_KEY=jouw-geheime-sleutel-hier
APP_NAME=VasteLijn Portal
```

## Licentie

MIT

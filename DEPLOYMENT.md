# Deployment (server)

## Vereisten
- Docker + Docker Compose
- Poorten open (of reverse proxy):
  - 8088 (portal web)
  - 8008 (API)

## Installatie
1) Upload de map `vastelijn-portal/` naar je server.
2) Maak `.env`:

```bash
cp .env.example .env
nano .env
```

3) Build en start:

```bash
docker compose up -d --build
```

4) Check:
- Web: `http://<server-ip>:8088`
- API: `http://<server-ip>:8008/api/health`

## Eerste admin-account (1 keer)
Zolang de `users` tabel leeg is, kun je 1 admin registreren:

```bash
curl -X POST http://localhost:8008/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"jij@jouwdomein.nl","password":"SterkWachtwoord"}'
```

Daarna staat registratie dicht.

## Data/backup
- Database staat in `./data/portal.db`
- Backup: kopieer de volledige `data/` map.

## Reverse proxy (optioneel)
Laat je dit achter Caddy of Nginx draaien, dan proxy je:
- `/` naar `web:80`
- `/api` naar `api:8000` (of op subdomein)

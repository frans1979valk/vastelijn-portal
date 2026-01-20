# Deployment checklist (v1)

## Benodigd
- Docker + Docker Compose
- Poorten open (of reverse proxy):
  - 8088 → web
  - 8008 → api

## Installatie
```bash
cp .env.example .env
nano .env

docker compose up -d --build
```

## Test
```bash
curl http://localhost:8008/api/health
```

Open de UI:
- `http://<server-ip>:8088`

## Tips voor productie
- Zet de API het liefst **niet publiek** open: alleen intern of achter reverse proxy.
- Gebruik een **sterke JWT_SECRET**.
- Zet CORS strakker als je op domeinen gaat draaien.

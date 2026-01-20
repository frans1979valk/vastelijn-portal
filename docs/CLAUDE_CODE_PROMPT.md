# Claude Code prompt: Headwind integratie (afmaken)

Plak dit in Claude Code (of een andere coding agent) binnen dit project.

```txt
Je werkt in repo "vastelijn-portal". Doel: Headwind MDM integratie toevoegen zodat de QR/payload per device echt een Android Enterprise provisioning QR wordt en de juiste policy/app wordt toegepast.

Context:
- Portal v1 draait al: frontend (nginx static) + backend (FastAPI) + SQLite.
- Backend endpoints bestaan al: POST /api/devices en GET /api/devices/{id} met qr_payload placeholder.
- We willen 2 modes:
  1) kiosk: volledige lockdown (device owner / fully managed) via QR provisioning
  2) fallback: app-only (best effort)

Taken:
1) Voeg in backend/app/ een module headwind_client.py toe die Headwind admin login doet en REST calls kan doen.
2) Vervang in crud.create_device() de placeholder qr_payload door echte Headwind provisioning payload voor kiosk.
   - Maak/zoek een policy "VasteLijn Kiosk" en koppel app package "eu.vastelijn.phone" (voorbeeld) aan de policy.
   - Stel kiosk/launcher opties in via Headwind zoals mogelijk.
3) Voeg mapping toe in database:
   - table headwind_mapping: device_id, headwind_device_id, created_at
4) Voeg endpoint toe: POST /api/devices/{id}/refresh-qr om QR opnieuw te genereren.
5) Houd security netjes:
   - Headwind credentials alleen via env (.env)
   - Timeouts + foutafhandeling + duidelijke errors
6) Update de frontend deviceView: vervang placeholder tekst door echte QR-code weergave.
   - Genereer een QR als SVG client-side uit de payload string (mag via een kleine embedded JS QR lib of minimal QR generator).
   - Zorg dat het ook werkt als payload groot is.

Belangrijk:
- Geen redesign. Alleen functioneel afmaken.
- Alles moet blijven werken via docker compose.
- Geef mij daarna een korte deployment checklist.
```

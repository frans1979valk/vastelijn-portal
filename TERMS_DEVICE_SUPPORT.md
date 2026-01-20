# Voorwaarden & toestel-ondersteuning (concept)

## Installatie-opties
Wij bieden twee installatiemethodes:

1) **Volledige Kiosk (aanbevolen)**
- Factory reset vereist
- Tijdens de eerste Android setup wordt een QR-code gescand
- Doel: toestel volledig vergrendeld, VasteLijn automatisch geïnstalleerd

2) **Fallback / App-only (best-effort)**
- Als QR / device-owner modus niet lukt door toestelbeperkingen
- Doel: VasteLijn app werkt, maar vergrendeling kan beperkter zijn

## Ondersteunde toestellen (praktisch)
- **Aanbevolen:** Samsung toestellen (beste compatibiliteit)
- **Minimum:** Android 7+ voor QR provisioning (praktijkadvies: Android 9+)

## Geen garantie op BYOD (eigen toestellen)
Bij gebruik van een eigen toestel (BYOD) kunnen merkspecifieke beperkingen (firmware, enterprise-features, policies) zorgen dat volledige kiosk niet mogelijk is. In dat geval leveren we fallback-modus.

## Belangrijk om helder te communiceren
- Volledige kiosk = alleen mogelijk wanneer toestel als “device owner” geprovisioned kan worden.
- Lukt dat niet, dan is “alles dicht” technisch niet volledig afdwingbaar.

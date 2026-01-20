# Wat ik heb gebouwd (en waarom)

## Het doel
Jij wilt een simpele omgeving waar:
- een klant kan inloggen
- een toestel kan toevoegen
- de klant een duidelijke keuze krijgt:
  - **Kiosk (aanbevolen)**: factory reset + QR enrollment
  - **Fallback**: als toestel/merk moeilijk doet

## Waarom deze aanpak
1) **Eerst UX/flow live** → jij kunt al verkopen/testen zonder te wachten op perfecte MDM.
2) **Headwind later integreren** → voorkomt dat je nu al vastloopt op merk/OS uitzonderingen.
3) **Minimaal, maar uitbreidbaar** → je kunt later:
   - accounts door admin laten aanmaken
   - multi-tenant uitbreiden (admin ziet alle klanten)
   - Headwind mapping + policies

## Wat v1 wél doet
- JWT login
- Devices aanmaken met `mode` (kiosk/fallback)
- Device detailpagina met instructies + QR payload placeholder

## Wat v1 nog niet doet
- Headwind API calls
- echte Android Enterprise provisioning QR payload
- policies/apps automatisch koppelen
- device status synchroniseren (online/offline) uit Headwind

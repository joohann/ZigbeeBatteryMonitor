# 🔋 Zigbee Battery Monitor

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)
[![HA Version](https://img.shields.io/badge/Home%20Assistant-2023.1%2B-blue.svg)](https://www.home-assistant.io)

Een Home Assistant HACS integratie voor het bewaken van alle Zigbee apparaat batterijen, met configureerbare drempelwaarden en notificaties via de HA mobiele app.

---

## ✨ Functies

- 📊 **Automatisch alle batterij-entiteiten detecteren** – geen handmatige configuratie nodig
- 🔴🟠🟡 **Drie drempelwaarden** – kritiek, laag en waarschuwing, volledig instelbaar
- 🔔 **Directe notificatie** bij kritieke batterij
- 📅 **Dagelijks rapport** voor lage batterijen
- 📆 **Wekelijks rapport** met volledig overzicht
- 📱 **Meerdere apparaten** notificeren via komma-gescheiden notify services
- 🎛️ **Volledig configureerbaar** via de HA UI (geen YAML nodig)
- 🔧 **6 sensoren** die je in automaties en dashboards kunt gebruiken

---

## 📦 Installatie via HACS

### Methode 1 – HACS Custom Repository (aanbevolen)

1. Ga naar **HACS → Integraties**
2. Klik op de **3 puntjes** rechtsboven → **Aangepaste repositories**
3. Vul in:
   - **URL**: `https://github.com/jouw-gebruikersnaam/zigbee-battery-monitor`
   - **Categorie**: `Integratie`
4. Klik **Toevoegen**
5. Zoek op **"Zigbee Battery Monitor"** en installeer
6. **Herstart Home Assistant**

### Methode 2 – Handmatig

1. Download de map `custom_components/zigbee_battery_monitor`
2. Kopieer naar je HA `config/custom_components/` map
3. **Herstart Home Assistant**

---

## ⚙️ Configuratie

1. Ga naar **Instellingen → Apparaten & Diensten → Integratie toevoegen**
2. Zoek op **"Zigbee Battery Monitor"**
3. Vul in het formulier in:

| Instelling | Standaard | Omschrijving |
|---|---|---|
| Kritieke drempel | 10% | Directe notificatie onder dit niveau |
| Lage drempel | 20% | Dagelijkse notificatie onder dit niveau |
| Waarschuwingsdrempel | 30% | Wekelijkse notificatie onder dit niveau |
| Notify services | *(leeg)* | Komma-gescheiden lijst van notify services |
| Scan interval | 30 min | Hoe vaak batterijen worden gecheckt |

### Notify services vinden

Ga naar **Ontwikkelaarstools → Services** en zoek op `notify`. Je ziet dan services zoals:
- `notify.mobile_app_samsung_s24`
- `notify.mobile_app_iphone_van_jan`

Voer in het veld in: `notify.mobile_app_samsung_s24, notify.mobile_app_iphone_van_jan`

---

## 📊 Sensoren

Na installatie worden de volgende sensoren aangemaakt:

| Sensor | Omschrijving |
|---|---|
| `sensor.zigbee_batterij_kritieke_batterijen` | Aantal apparaten onder kritieke drempel |
| `sensor.zigbee_batterij_lage_batterijen` | Aantal apparaten onder lage drempel |
| `sensor.zigbee_batterij_batterij_waarschuwingen` | Aantal apparaten onder waarschuwingsdrempel |
| `sensor.zigbee_batterij_batterijen_ok` | Aantal apparaten met goede batterij |
| `sensor.zigbee_batterij_niet_beschikbaar` | Aantal offline apparaten |
| `sensor.zigbee_batterijen_totaal` | Totaal aantal gemonitorde apparaten |

Elke sensor heeft ook een attribuut `apparaten` met een lijst van de betrokken apparaten.

---

## 🗺️ Dashboard

Gebruik het meegeleverde `lovelace_dashboard.yaml` bestand:

1. Ga naar **Instellingen → Dashboards → Nieuw dashboard**
2. Klik op de **3 puntjes → Bewerken via YAML**
3. Plak de inhoud van `lovelace_dashboard.yaml`

> **Let op:** Vereist de HACS frontend-integratie [auto-entities](https://github.com/thomasloven/lovelace-auto-entities)

---

## 🤖 Automaties

De integratie regelt notificaties automatisch. Je kunt de sensoren ook gebruiken in je eigen automaties:

```yaml
trigger:
  - platform: numeric_state
    entity_id: sensor.zigbee_batterij_kritieke_batterijen
    above: 0
action:
  - service: notify.mobile_app_mijn_telefoon
    data:
      message: "Er zijn kritieke batterijen!"
```

---

## 📝 Licentie

MIT License – vrij te gebruiken en aan te passen.

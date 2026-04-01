# P-Count Parking - Home Assistant Integration

Eine Custom Integration für [Home Assistant](https://www.home-assistant.io/), die Parkplatz-Auslastungsdaten aus dem [P-Count Parkleitsystem](https://p-count.de/) bereitstellt.

## Was macht diese Integration?

Die Integration verbindet sich mit der P-Count API (von Steinberg Verkehrstechnik) und stellt die aktuelle Parkplatz-Belegung als Sensoren in Home Assistant bereit. So kannst du z.B. Automationen erstellen, die dich warnen, wenn nur noch wenige Parkplätze frei sind.

## Sensoren

### Gesamt-Sensoren (über alle Parkbereiche)

| Sensor | Beschreibung |
|--------|-------------|
| Gesamt freie Plätze | Anzahl freier Plätze über alle Bereiche |
| Gesamt belegte Plätze | Anzahl belegter Plätze über alle Bereiche |
| Gesamt Plätze | Gesamtkapazität aller Bereiche |
| Letzte Aktualisierung | Zeitstempel der letzten Messung |

### Pro Parkbereich (z.B. P1+2, P3, ...)

| Sensor | Beschreibung |
|--------|-------------|
| Freie Plätze | Anzahl freier Plätze im Bereich |
| Belegte Plätze | Anzahl belegter Plätze im Bereich |
| Plätze gesamt | Gesamtkapazität des Bereichs |
| Auslastung | Prozentuale Auslastung des Bereichs |

## Installation

### Manuell

1. Kopiere den Ordner `custom_components/p_count` in dein Home Assistant `config/custom_components/` Verzeichnis.
2. Starte Home Assistant neu.
3. Gehe zu **Einstellungen** > **Geräte & Dienste** > **Integration hinzufügen** und suche nach "P-Count Parking".

### HACS (Custom Repository)

1. Öffne HACS in Home Assistant.
2. Gehe zu **Integrationen** > **3-Punkte-Menü** > **Benutzerdefinierte Repositories**.
3. Füge `https://github.com/manuveli/p-count-ha-integration` als Repository hinzu (Kategorie: Integration).
4. Installiere "P-Count Parking" und starte Home Assistant neu.

## Einrichtung

Bei der Einrichtung werden zwei Werte abgefragt:

- **Parkerfassungssystem (Benutzer)**: Die System-ID / der Benutzername für dein P-Count System
- **Zugangscode (Passwort)**: Das Passwort / der Zugangscode

Diese Zugangsdaten erhältst du vom Betreiber deines Parkleitsystems.

## Beispiel-Automation: Warnung bei wenig freien Plätzen

```yaml
automation:
  - alias: "Warnung: Wenige Parkplätze frei"
    trigger:
      - platform: numeric_state
        entity_id: sensor.deutsche_leasing_1_total_free
        below: 10
    action:
      - service: notify.mobile_app
        data:
          title: "Parkplatz-Warnung"
          message: "Nur noch {{ states('sensor.deutsche_leasing_1_total_free') }} Parkplätze frei!"
```

## Technische Details

- Die Integration nutzt die P-Count REST-API mit HTTP Basic Authentication.
- Das Polling-Intervall wird automatisch vom Server vorgegeben (typisch: 30 Sekunden).
- IoT-Klasse: `cloud_polling`

## Lizenz

MIT

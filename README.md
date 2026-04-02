<h1 align="center">P-Count Parking</h1>

<p align="center">
  <strong>Parkplatz-Auslastung aus dem P-Count Parkleitsystem — direkt in Home Assistant.</strong>
</p>

<p align="center">
  <a href="https://github.com/hacs/integration"><img src="https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge" alt="HACS Custom"></a>
  <a href="https://github.com/manuveli/p-count-ha-integration/releases"><img src="https://img.shields.io/github/v/release/manuveli/p-count-ha-integration?style=for-the-badge" alt="GitHub Release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge" alt="License: MIT"></a>
  <a href="https://www.home-assistant.io/"><img src="https://img.shields.io/badge/HA-2024.1+-blue?style=for-the-badge" alt="Home Assistant 2024.1+"></a>
</p>

<p align="center">
  Diese Custom Integration verbindet sich mit der <a href="https://p-count.de/">P-Count API</a> (Steinberg Verkehrstechnik) und stellt die aktuelle Parkplatz-Belegung als Sensoren in Home Assistant bereit.<br>
  So kannst du Automationen erstellen, die dich warnen, wenn nur noch wenige Parkplätze frei sind — oder Dashboards bauen, die die Auslastung in Echtzeit anzeigen.
</p>

---

## 📑 Inhaltsverzeichnis

- [✨ Features](#-features)
- [📥 Installation](#-installation)
- [⚙️ Einrichtung](#️-einrichtung)
- [📊 Sensoren](#-sensoren)
- [💡 Beispiel-Automationen](#-beispiel-automationen)
- [🔧 Fehlerbehebung](#-fehlerbehebung)
- [📄 Lizenz](#-lizenz)

---

## ✨ Features

- 🅿️ **Echtzeit-Parkdaten** — Freie Plätze, belegte Plätze, Gesamtkapazität und Auslastung in Prozent
- 📊 **Gesamt- & Bereichs-Sensoren** — Aggregierte Werte über alle Parkbereiche sowie Einzelwerte pro Bereich (z.B. P1, P2, P3)
- ⏱️ **Automatisches Polling** — Das Abfrageintervall wird vom P-Count Server vorgegeben (typisch: 30 Sekunden)
- 🔐 **Sichere Authentifizierung** — HTTP Basic Auth mit System-ID und Zugangscode
- 🖥️ **Einfache Einrichtung** — Vollständig über die Home Assistant UI konfigurierbar (Config Flow)
- ☁️ **Cloud Polling** — IoT-Klasse `cloud_polling` für zuverlässige API-Abfragen

---

## 📥 Installation

### Voraussetzungen

> 🏠 **Home Assistant 2024.1** oder neuer

### HACS (Empfohlen)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=manuveli&repository=p-count-ha-integration&category=integration)

1. Stelle sicher, dass [HACS](https://hacs.xyz/) installiert ist
2. Klicke auf den Badge oben — oder gehe zu **HACS → Integrationen → ⋮ → Benutzerdefinierte Repositories** und füge hinzu:
   ```
   https://github.com/manuveli/p-count-ha-integration
   ```
   mit der Kategorie **Integration**
3. Suche nach **P-Count Parking** und klicke **Installieren**
4. **Starte** Home Assistant neu
5. Gehe zu **Einstellungen → Geräte & Dienste → Integration hinzufügen** und suche nach **P-Count Parking**

### Manuelle Installation

1. Lade das neueste Release von der [Releases-Seite](https://github.com/manuveli/p-count-ha-integration/releases) herunter
2. Kopiere den Ordner `custom_components/p_count` in dein `config/custom_components/` Verzeichnis
3. **Starte** Home Assistant neu
4. Gehe zu **Einstellungen → Geräte & Dienste → Integration hinzufügen** und suche nach **P-Count Parking**

---

## ⚙️ Einrichtung

Die Integration wird vollständig über die UI eingerichtet. Es werden zwei Werte abgefragt:

| Option | Beschreibung |
|--------|-------------|
| **Parkerfassungssystem (Benutzer)** | Die System-ID / der Benutzername für dein P-Count System |
| **Zugangscode (Passwort)** | Das Passwort / der Zugangscode |

> 💡 **Tipp:** Diese Zugangsdaten erhältst du vom Betreiber deines Parkleitsystems.

Nach der Einrichtung werden automatisch alle verfügbaren Parkbereiche erkannt und als Sensoren angelegt.

---

## 📊 Sensoren

### Gesamt-Sensoren (über alle Parkbereiche)

| Sensor | Beschreibung | Icon |
|--------|-------------|------|
| Gesamt freie Plätze | Anzahl freier Plätze über alle Bereiche | `mdi:car-parking-lights` |
| Gesamt belegte Plätze | Anzahl belegter Plätze über alle Bereiche | `mdi:car` |
| Gesamt Plätze | Gesamtkapazität aller Bereiche | `mdi:parking` |
| Letzte Aktualisierung | Zeitstempel der letzten Messung | `mdi:clock-outline` |

### Pro Parkbereich (z.B. P1, P2, P3, …)

| Sensor | Beschreibung | Icon |
|--------|-------------|------|
| Freie Plätze | Anzahl freier Plätze im Bereich | `mdi:car-parking-lights` |
| Belegte Plätze | Anzahl belegter Plätze im Bereich | `mdi:car` |
| Plätze gesamt | Gesamtkapazität des Bereichs | `mdi:parking` |
| Auslastung | Prozentuale Auslastung des Bereichs | `mdi:chart-donut` |

---

## 💡 Beispiel-Automationen

### 🔔 Warnung bei wenig freien Plätzen

```yaml
automation:
  - alias: "Parkplatz: Wenige Plätze frei"
    trigger:
      - platform: numeric_state
        entity_id: sensor.p_count_total_free
        below: 10
    action:
      - service: notify.mobile_app
        data:
          title: "🅿️ Parkplatz-Warnung"
          message: "Nur noch {{ states('sensor.p_count_total_free') }} Parkplätze frei!"
```

### 📈 Benachrichtigung bei hoher Auslastung (über 90%)

```yaml
automation:
  - alias: "Parkplatz: Hohe Auslastung"
    trigger:
      - platform: numeric_state
        entity_id: sensor.p_count_p1_occupancy_percent
        above: 90
    action:
      - service: notify.mobile_app
        data:
          title: "🅿️ Parkplatz fast voll"
          message: "Bereich P1 ist zu {{ states('sensor.p_count_p1_occupancy_percent') }}% ausgelastet!"
```

---

## 🔧 Fehlerbehebung

<details>
<summary><strong>❌ "Verbindung fehlgeschlagen" / Timeout</strong></summary>

- Prüfe, ob der P-Count Server unter `https://p-count.de` erreichbar ist
- Stelle sicher, dass dein Home Assistant eine Internetverbindung hat
- Prüfe die Home Assistant Logs unter **Einstellungen → System → Protokolle**
</details>

<details>
<summary><strong>❌ "Ungültige Zugangsdaten"</strong></summary>

- Überprüfe System-ID und Zugangscode
- Kontaktiere den Betreiber deines Parkleitsystems, um die korrekten Zugangsdaten zu erhalten
- Nutze die Reauthentifizierung unter **Einstellungen → Geräte & Dienste → P-Count Parking → Neu konfigurieren**
</details>

<details>
<summary><strong>❌ Sensoren werden nicht angezeigt</strong></summary>

- Starte Home Assistant nach der Installation neu
- Prüfe, ob die Integration unter **Einstellungen → Geräte & Dienste** korrekt eingerichtet ist
- Überprüfe die Logs auf Fehlermeldungen der `p_count` Integration
</details>

<details>
<summary><strong>⏱️ Wie oft werden die Daten aktualisiert?</strong></summary>

Das Polling-Intervall wird automatisch vom P-Count Server vorgegeben (typisch: 30 Sekunden). Die Integration passt sich dynamisch an den vom Server zurückgemeldeten Wert an.
</details>

---

## 📄 Lizenz

Dieses Projekt steht unter der [MIT-Lizenz](LICENSE).

---

<p align="center">
  Made with ❤️ for the Home Assistant Community<br>
  <a href="https://github.com/manuveli/p-count-ha-integration">github.com/manuveli/p-count-ha-integration</a>
</p>

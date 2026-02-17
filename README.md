# MVG CLI

Eine inoffizielle Command-Line-Interface für die Münchner Verkehrsgesellschaft (MVG).

## Features

- 🚇 **Station suchen** - Finde Stationen nach Name
- ⏰ **Echtzeit-Abfahrten** - Aktuelle Abfahrten mit Verspätungsanzeige
- 🗺️ **Verbindungssuche** - Routen zwischen Stationen
- 📍 **Nahbereichssuche** - Stationen in der Nähe bestimmter Koordinaten  
- ⚠️ **Störungsmeldungen** - Aktuelle Betriebsstörungen
- 🚊 **Linienübersicht** - Alle verfügbaren Linien nach Verkehrsmittel

## Installation

```bash
# Dependencies: nur Python stdlib + requests
pip install requests

# CLI verwenden
python3 mvg_cli.py --help
```

## Nutzung

### Stationen suchen
```bash
python3 mvg_cli.py search "Marienplatz"
```

### Abfahrten anzeigen
```bash
python3 mvg_cli.py departures "Marienplatz"
python3 mvg_cli.py departures "Marienplatz" --limit 20
python3 mvg_cli.py departures "Marienplatz" --type ubahn,sbahn
python3 mvg_cli.py departures "Marienplatz" --offset 5  # +5min Fußweg
```

### Verbindungen suchen
```bash
python3 mvg_cli.py route "Marienplatz" "Garching"
python3 mvg_cli.py route "Marienplatz" "Garching" --arrive
python3 mvg_cli.py route "Marienplatz" "Garching" --time "18:00"
```

### Stationen in der Nähe
```bash
python3 mvg_cli.py nearby                    # Default: Lars' Position
python3 mvg_cli.py nearby 48.1351 11.5820    # Bestimmte Koordinaten
```

### Störungsmeldungen
```bash
python3 mvg_cli.py alerts
python3 mvg_cli.py alerts --station "Marienplatz"
```

### Linien auflisten
```bash
python3 mvg_cli.py lines
python3 mvg_cli.py lines --type ubahn
```

## JSON Output

Alle Commands unterstützen das `--json` Flag für maschinenlesbare Ausgabe:

```bash
python3 mvg_cli.py --json search "Marienplatz"
python3 mvg_cli.py --json departures "Marienplatz"
```

## Verkehrsmittel

| Typ | Emoji | Filter |
|-----|-------|---------|
| U-Bahn | 🔵 | `ubahn` |
| S-Bahn | 🟢 | `sbahn` |
| Bus | 🚌 | `bus` |
| Tram | 🚋 | `tram` |
| Regionalzug | 🚆 | `bahn` |

## API

Nutzt die inoffizielle MVG API unter `https://www.mvg.de/api/bgw-pt/v3/`:
- `/locations` - Stationen suchen
- `/departures` - Echtzeit-Abfahrten  
- `/routes` - Verbindungssuche
- `/lines` - Alle Linien
- `/messages` - Störungsmeldungen

## Features im Detail

### Farbkodierte Verspätungen
- ✅ **Pünktlich** - grün
- 🟡 **Bis 5 min Verspätung** - gelb  
- 🔴 **Über 5 min Verspätung** - rot

### Automatische Stationsauflösung
Gib einfach den Stationsnamen ein - die CLI löst automatisch zur korrekten `globalId` auf.

### Zeitzonen
Alle Zeiten werden in lokaler Zeit (Europe/Berlin) angezeigt.

### Unicode-Boxen
Hübsche Terminal-Ausgabe mit Unicode-Zeichnungen für bessere Lesbarkeit.

## Limitierungen

- **Inoffizielle API**: Kann sich jederzeit ändern
- **Keine Authentifizierung**: Kein API-Key nötig
- **Read-Only**: Nur Abfragen, keine Buchungen/Tickets

## Entwickelt mit ❤️ in München

Inspiriert von anderen CLI-Tools im Workspace - pure Python, keine externen Dependencies außer `requests`.
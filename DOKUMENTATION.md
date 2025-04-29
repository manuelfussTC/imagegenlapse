# ImagegeneratorGPT4o - Dokumentation

## Inhalt
1. [Überblick](#überblick)
2. [Installation](#installation)
3. [Befehlszeilenparameter](#befehlszeilenparameter)
4. [Anwendungsbeispiele](#anwendungsbeispiele)
5. [Iterationsprozess verstehen](#iterationsprozess-verstehen)
6. [Tipps und Fehlerbehebung](#tipps-und-fehlerbehebung)

## Überblick

ImagegeneratorGPT4o ist ein Python-Tool, das Bilder mit OpenAI's GPT-Image-1 Modell verarbeitet. Das Tool nimmt ein Ausgangsbild und wendet wiederholt (iterativ) den Prompt "create the exact replica of this image, don't change a thing" an. Das Ergebnis jeder Iteration wird als Eingabe für die nächste Iteration verwendet.

Dies ermöglicht die Beobachtung, wie sich das Bild über mehrere Generationen der "exakten Replikation" verändert - ein interessantes Experiment zur Untersuchung kleiner Veränderungen und Interpretationen durch das KI-Modell.

## Installation

### Voraussetzungen
- Python 3.7 oder höher
- OpenAI API-Schlüssel
- Verifizierte OpenAI-Organisation mit Business-Status (für den Zugriff auf gpt-image-1)

> **WICHTIG:** GPT-Image-1 erfordert eine vollständig verifizierte OpenAI-Organisation mit validiertem Business-Status. Privatkonten haben in der Regel keinen Zugriff auf dieses Modell.

### Schritte

1. Repository klonen oder Dateien herunterladen
2. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```
3. API-Key einrichten:
   ```bash
   cp .env.example .env
   # Bearbeite .env und füge deinen eigenen API-Schlüssel ein
   ```
   > **WICHTIG:** Commit niemals deine `.env`-Datei! Sie ist bereits in `.gitignore` eingetragen.

## Befehlszeilenparameter

Das Tool bietet mehrere Parameter zur Anpassung des Generierungsprozesses:

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `--initial-image` | String | "images/IMG_3831.JPG" | Pfad zum Ausgangsbild |
| `--iterations` | Integer | 5 | Anzahl der zu durchlaufenden Iterationen (1-100) |
| `--size` | String | "1024x1024" | Größe der generierten Bilder (Format: "BreitexHöhe") |
| `--keep-aspect-ratio` | Flag | False | Bei Angabe wird das Seitenverhältnis des Originalbildes beibehalten |
| `--continue` | Flag | False | Setzt die Verarbeitung mit der letzten generierten Iteration fort |

## Anwendungsbeispiele

### Basisanwendung
Generiert 5 Iterationen des Standardbilds:
```bash
python image_replicator.py
```

### Benutzerdefiniertes Bild verwenden
```bash
python image_replicator.py --initial-image pfad/zu/meinem/bild.jpg
```

### Mehr Iterationen durchführen
```bash
python image_replicator.py --iterations 20
```

### Seitenverhältnis beibehalten
```bash
python image_replicator.py --keep-aspect-ratio
```

### Mit einer früheren Iteration fortfahren
Wenn bereits Iterationen im `imagegen` Ordner existieren:
```bash
python image_replicator.py --continue --iterations 10
```

### Kombinierte Parameter
```bash
python image_replicator.py --initial-image meinbild.png --iterations 15 --keep-aspect-ratio
```

## Iterationsprozess verstehen

Der Iterationsprozess funktioniert wie folgt:

1. **Initialisierung**:
   - Das Ausgangsbild wird in ein optimiertes PNG-Format konvertiert
   - Die Bildorientierung wird basierend auf EXIF-Metadaten korrigiert
   - Optional wird das Seitenverhältnis beibehalten (mit `--keep-aspect-ratio`)

2. **Iterative Verarbeitung**:
   - Für jede Iteration wird das Bild an die OpenAI API gesendet
   - Der Prompt "create the exact replica of this image, don't change a thing" wird angewendet
   - Das generierte Bild wird als `iteration_N.png` gespeichert (wobei N die Iterationsnummer ist)
   - Das neue Bild wird als Eingabe für die nächste Iteration verwendet

3. **Fortsetzungsfunktion**:
   - Mit dem Parameter `--continue` sucht das Skript automatisch nach der letzten Iteration im Verzeichnis
   - Es setzt den Prozess mit der nächsthöheren Iterationsnummer fort
   - Dies ermöglicht, jederzeit weitere Iterationen hinzuzufügen, ohne von vorne beginnen zu müssen

### Beispielablauf:

```
Tag 1: python image_replicator.py --iterations 5 --keep-aspect-ratio
# Generiert iteration_1.png bis iteration_5.png

Tag 2: python image_replicator.py --continue --iterations 10 --keep-aspect-ratio
# Findet iteration_5.png und generiert iteration_6.png bis iteration_15.png
```

## Tipps und Fehlerbehebung

### Optimale Bildgröße
- GPT-Image-1 arbeitet am besten mit Bildern bis zu 1024x1024 Pixeln
- Größere Bilder werden automatisch skaliert
- Mit `--keep-aspect-ratio` vermeiden Sie Verzerrungen

### Häufige Fehler

1. **Organization not verified**:
   ```
   Your organization must be verified to use the model `gpt-image-1`
   ```
   **Lösung**: Verifizieren Sie Ihre OpenAI-Organisation unter [https://platform.openai.com/settings/organization/general](https://platform.openai.com/settings/organization/general). Beachten Sie, dass Sie einen validierte Business-Organisation benötigen - Privatkonten können dieses Modell in der Regel nicht nutzen.

2. **API-Schlüssel nicht gefunden**:
   ```
   Fehler: OPENAI_API_KEY nicht in der .env Datei gefunden oder nicht gesetzt.
   ```
   **Lösung**: Erstellen Sie eine .env-Datei basierend auf der .env.example-Datei mit Ihrem API-Schlüssel.

3. **Bildformat-Probleme**:
   Das Tool konvertiert automatisch Bilder in das PNG-Format mit korrekter Orientierung und Größe. Bei Problemen versuchen Sie, das Bild vorher in ein anderes Format zu konvertieren.

### Sicherheitshinweise
- Fügen Sie niemals Ihre echten API-Schlüssel in Dateien ein, die ins Git-Repository übertragen werden
- Die .env-Datei ist bereits in .gitignore eingetragen und wird nicht committed
- Verwenden Sie immer die .env.example als Vorlage und kopieren Sie diese zu .env für Ihre persönlichen Schlüssel

### Iterationszeit
- Jede Iteration dauert etwa 20-60 Sekunden, abhängig von der Serverauslastung und Bildgröße
- Planen Sie ausreichend Zeit für größere Iterationsmengen ein 
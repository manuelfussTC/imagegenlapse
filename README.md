# ImagegenLapse

Ein Tool zur iterativen Bildverarbeitung mit OpenAI's GPT-Image-1 Modell.

## Überblick

ImagegenLapse ist ein Python-Tool, das Bilder mit OpenAI's GPT-Image-1 Modell iterativ verarbeitet. Das Tool nimmt ein Ausgangsbild und wendet wiederholt den Prompt "create the exact replica of this image, don't change a thing" an. Jedes Ergebnis wird als Eingabe für die nächste Iteration verwendet.

Dies ermöglicht es, zu beobachten, wie sich das Bild über mehrere Generationen der "exakten Replikation" verändert - ein interessantes Experiment, um kleine Veränderungen und Interpretationen durch das KI-Modell zu untersuchen.

## Schnellstart

1. **Repository klonen:**
   ```bash
   git clone https://github.com/manuelfussTC/imagegenlapse.git
   cd imagegenlapse
   ```

2. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```

3. **API-Key einrichten:**
   Erstelle eine `.env`-Datei im Hauptverzeichnis mit:
   ```
   OPENAI_API_KEY=dein_openai_api_key
   ```

4. **Bilderverzeichnis erstellen:**
   Lege ein Bild in den Ordner `images/` oder verwende das vorhandene Beispielbild.

5. **Tool ausführen:**
   ```bash
   python image_replicator.py --keep-aspect-ratio
   ```

## Voraussetzungen

- Python 3.7 oder höher
- OpenAI API-Schlüssel
- Verifizierte OpenAI-Organisation (für den Zugriff auf gpt-image-1)

> **Wichtig:** Für die Verwendung des Modells `gpt-image-1` muss deine OpenAI-Organisation verifiziert sein. Dies kannst du unter [https://platform.openai.com/settings/organization/general](https://platform.openai.com/settings/organization/general) erledigen.

## Befehlszeilenparameter

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

### Seitenverhältnis beibehalten (empfohlen)
```bash
python image_replicator.py --keep-aspect-ratio
```

### Mit einer früheren Iteration fortfahren
Wenn bereits Iterationen im `imagegen` Ordner existieren:
```bash
python image_replicator.py --continue --iterations 10
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
   - Das generierte Bild wird als `iteration_N.png` im Ordner `imagegen/` gespeichert
   - Das neue Bild wird als Eingabe für die nächste Iteration verwendet

3. **Fortsetzungsfunktion**:
   - Mit dem Parameter `--continue` sucht das Skript automatisch nach der letzten Iteration
   - Es setzt den Prozess mit der nächsthöheren Iterationsnummer fort
   - Dies ermöglicht, jederzeit weitere Iterationen hinzuzufügen

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
   **Lösung**: Verifizieren Sie Ihre OpenAI-Organisation unter [https://platform.openai.com/settings/organization/general](https://platform.openai.com/settings/organization/general)

2. **API-Schlüssel nicht gefunden**:
   ```
   Fehler: OPENAI_API_KEY nicht in der .env Datei gefunden oder nicht gesetzt.
   ```
   **Lösung**: Erstellen Sie eine .env-Datei im Hauptverzeichnis mit Ihrem API-Schlüssel.

3. **Bildformat-Probleme**:
   Das Tool konvertiert automatisch Bilder in das PNG-Format mit korrekter Orientierung und Größe. Bei Problemen versuchen Sie, das Bild vorher in ein anderes Format zu konvertieren.

## Autor

Manuel Fuss # imagegenlapse

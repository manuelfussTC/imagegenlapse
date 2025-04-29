import os
import base64
from openai import OpenAI
from dotenv import load_dotenv
import time
import argparse
import sys
import requests
from PIL import Image, ExifTags
import io
import re
import glob

# Lade Umgebungsvariablen aus der .env Datei
load_dotenv()

def parse_arguments():
    parser = argparse.ArgumentParser(description="Bildreplikator mit OpenAI GPT-Image")
    parser.add_argument("--initial-image", default="images/IMG_3831.JPG", 
                      help="Pfad zum initialen Bild")
    parser.add_argument("--iterations", type=int, default=5, 
                      help="Anzahl der Iterationen (1-100)")
    parser.add_argument("--size", default="1024x1024", 
                      help="Größe der generierten Bilder")
    parser.add_argument("--keep-aspect-ratio", action="store_true", 
                      help="Seitenverhältnis des Ausgangsbildes beibehalten")
    parser.add_argument("--continue", action="store_true", dest="continue_last",
                      help="Mit der letzten Iteration fortfahren")
    return parser.parse_args()

def find_last_iteration(output_dir, prefix="iteration_", suffix=".png"):
    """Findet die letzte Iteration im Ausgabeverzeichnis"""
    pattern = os.path.join(output_dir, f"{prefix}*{suffix}")
    files = glob.glob(pattern)
    
    if not files:
        return None, 0
    
    # Extrahiere die Iterationsnummern aus den Dateinamen
    iterations = []
    for file in files:
        match = re.search(f"{prefix}(\\d+){suffix}", os.path.basename(file))
        if match:
            iterations.append((int(match.group(1)), file))
    
    if not iterations:
        return None, 0
    
    # Sortiere nach Iterationsnummer und nimm die höchste
    iterations.sort(reverse=True)
    return iterations[0][1], iterations[0][0]

def fix_image_orientation(image):
    """Korrigiert die Orientierung des Bildes basierend auf EXIF-Daten"""
    try:
        # Hole EXIF-Daten
        exif = image._getexif()
        if exif is None:
            return image
        
        # Finde den Orientierungs-Tag
        orientation_key = None
        for key, value in ExifTags.TAGS.items():
            if value == 'Orientation':
                orientation_key = key
                break
                
        if orientation_key is None or orientation_key not in exif:
            return image
            
        # Abhängig vom Orientierungswert das Bild drehen
        orientation = exif[orientation_key]
        
        if orientation == 1:  # Normal
            return image
        elif orientation == 2:  # Spiegelung horizontal
            return image.transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 3:  # 180° gedreht
            return image.transpose(Image.ROTATE_180)
        elif orientation == 4:  # Spiegelung vertikal
            return image.transpose(Image.FLIP_TOP_BOTTOM)
        elif orientation == 5:  # 90° im Uhrzeigersinn gedreht und horizontal gespiegelt
            return image.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_90)
        elif orientation == 6:  # 90° im Uhrzeigersinn gedreht
            return image.transpose(Image.ROTATE_270)
        elif orientation == 7:  # 90° gegen den Uhrzeigersinn gedreht und horizontal gespiegelt
            return image.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_270)
        elif orientation == 8:  # 90° gegen den Uhrzeigersinn gedreht
            return image.transpose(Image.ROTATE_90)
        
        return image
    except Exception as e:
        print(f"Warnung: Konnte Bildorientierung nicht korrigieren: {e}")
        return image

def resize_image_keep_aspect_ratio(img, max_size):
    """Skaliert ein Bild unter Beibehaltung des Seitenverhältnisses"""
    width, height = img.size
    
    # Berechne das Seitenverhältnis
    aspect_ratio = width / height
    
    # Bestimme die neue Größe unter Beibehaltung des Seitenverhältnisses
    if width > height:
        new_width = min(width, max_size)
        new_height = int(new_width / aspect_ratio)
    else:
        new_height = min(height, max_size)
        new_width = int(new_height * aspect_ratio)
        
    # Skaliere das Bild
    return img.resize((new_width, new_height), Image.LANCZOS)

def convert_to_png(image_path, output_path=None, max_size_mb=20, keep_aspect_ratio=True):
    """Konvertiert ein Bild in PNG-Format"""
    if output_path is None:
        output_path = os.path.splitext(image_path)[0] + ".png"
    
    try:
        # Öffne das Bild
        img = Image.open(image_path)
        
        # Korrigiere die Bildorientierung basierend auf EXIF-Daten
        img = fix_image_orientation(img)
        
        # Konvertiere zu RGB, falls es RGBA ist
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        # Reduziere die Größe, wenn das Bild zu groß ist
        original_size = img.size
        if max(img.width, img.height) > 1024:
            if keep_aspect_ratio:
                img = resize_image_keep_aspect_ratio(img, 1024)
                print(f"  Bild skaliert von {original_size} auf {img.size} (Seitenverhältnis beibehalten)")
            else:
                img = img.resize((1024, 1024), Image.LANCZOS)
                print(f"  Bild skaliert von {original_size} auf (1024, 1024) (quadratisches Format)")
        
        # Speichern als PNG mit Kompression
        img.save(output_path, "PNG", optimize=True, compress_level=6)
        
        # Prüfe die Dateigröße und reduziere die Auflösung weiter, falls nötig
        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        attempts = 0
        
        while file_size_mb > max_size_mb and attempts < 5:
            attempts += 1
            current_size = max(img.width, img.height)
            new_max_size = int(current_size * 0.8)  # 20% kleiner
            
            if keep_aspect_ratio:
                img = resize_image_keep_aspect_ratio(img, new_max_size)
            else:
                new_size = int(new_max_size)
                img = img.resize((new_size, new_size), Image.LANCZOS)
                
            img.save(output_path, "PNG", optimize=True, compress_level=6)
            file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"  Reduziere Bildgröße auf {img.size} Pixel, neue Dateigröße: {file_size_mb:.2f} MB")
        
        return output_path
    except Exception as e:
        print(f"Fehler bei der Konvertierung des Bildes: {e}")
        return None

def main():
    args = parse_arguments()
    
    # --- Konfiguration ---
    INITIAL_IMAGE_PATH = args.initial_image  # Pfad zum initialen Bild
    OUTPUT_DIR = "imagegen"  # Verzeichnis für die generierten Bilder
    PROMPT = "create the exact replica of this image, don't change a thing"  # Prompt für die Bildbearbeitung
    ITERATIONS = args.iterations  # Anzahl der Iterationen (1-100)
    MODEL = "gpt-image-1"  # Modell für die Bildbearbeitung - nur gpt-image-1
    SIZE = args.size  # Größe der generierten Bilder
    KEEP_ASPECT_RATIO = args.keep_aspect_ratio  # Seitenverhältnis beibehalten
    CONTINUE_LAST = args.continue_last  # Mit der letzten Iteration fortfahren
    OUTPUT_FILENAME_PREFIX = "iteration_"
    OUTPUT_FILENAME_SUFFIX = ".png"  # Dateiendung für die Ausgabe

    # --- Initialisierung ---
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Fehler: OPENAI_API_KEY nicht in der .env Datei gefunden oder nicht gesetzt.")
        print("Bitte erstellen Sie eine .env Datei im Hauptverzeichnis und fügen Sie Ihren Key hinzu:")
        print('OPENAI_API_KEY="sk-..."')
        sys.exit(1)

    try:
        client = OpenAI(api_key=api_key)
    except Exception as e:
        print(f"Fehler bei der Initialisierung des OpenAI Clients: {e}")
        sys.exit(1)

    # Stelle sicher, dass das Ausgabe-Verzeichnis existiert
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # --- Hauptlogik ---
    # Ermittle das Startbild und die Startiteration
    start_iteration = 1
    if CONTINUE_LAST:
        last_iteration_path, last_iteration_num = find_last_iteration(OUTPUT_DIR)
        if last_iteration_path:
            current_image_path = last_iteration_path
            start_iteration = last_iteration_num + 1
            print(f"Fortfahren mit Iteration {start_iteration} basierend auf Bild: {current_image_path}")
        else:
            print("Keine vorherigen Iterationen gefunden. Starte mit dem Originalbild.")
            current_image_path = INITIAL_IMAGE_PATH
    else:
        current_image_path = INITIAL_IMAGE_PATH

    # Konvertiere das Originalbild zu PNG, wenn wir nicht mit einer vorherigen Iteration fortfahren
    if not CONTINUE_LAST or current_image_path == INITIAL_IMAGE_PATH:
        print(f"Konvertiere Eingabebild nach PNG...")
        png_path = os.path.join(OUTPUT_DIR, "input.png")
        png_path = convert_to_png(current_image_path, png_path, keep_aspect_ratio=KEEP_ASPECT_RATIO)
        if png_path:
            current_image_path = png_path
            file_size_mb = os.path.getsize(current_image_path) / (1024 * 1024)
            print(f"  Bild konvertiert nach: {png_path} ({file_size_mb:.2f} MB)")
        else:
            print(f"Fehler: Konnte das Bild nicht nach PNG konvertieren.")
            sys.exit(1)

    # Überprüfen, ob wir auf gpt-image-1 zugreifen können
    try:
        # Versuche eine einfache Anfrage, um zu sehen, ob gpt-image-1 verfügbar ist
        client.models.retrieve("gpt-image-1")
    except Exception as e:
        if "must be verified" in str(e) or "organization must be verified" in str(e):
            print("Fehler: Ihre OpenAI-Organisation ist nicht für gpt-image-1 verifiziert.")
            print("Um gpt-image-1 zu verwenden, verifizieren Sie Ihre Organisation unter:")
            print("https://platform.openai.com/settings/organization/general")
            sys.exit(1)
        else:
            print(f"Fehler beim Zugriff auf gpt-image-1: {e}")
            sys.exit(1)

    print(f"Starte Bildreplikationsprozess für {ITERATIONS} Iterationen...")
    print(f"Initiales Bild: {current_image_path}")
    print(f"Ausgabeverzeichnis: {OUTPUT_DIR}")
    print(f"Prompt: '{PROMPT}'")
    print(f"Modell: {MODEL}")
    if KEEP_ASPECT_RATIO:
        print(f"Seitenverhältnis wird beibehalten")
    print("-" * 30)

    for i in range(start_iteration, start_iteration + ITERATIONS):
        start_time = time.time()
        print(f"Starte Iteration {i}/{start_iteration + ITERATIONS - 1}...")
        print(f"  Input Bild: {current_image_path}")

        output_filename = f"{OUTPUT_FILENAME_PREFIX}{i}{OUTPUT_FILENAME_SUFFIX}"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        try:
            # Verwende den images.edit Endpunkt für gpt-image-1
            with open(current_image_path, "rb") as image_file:
                response = client.images.edit(
                    model=MODEL,
                    image=image_file,
                    prompt=PROMPT,
                    n=1,
                    size=SIZE
                )
            
            # GPT-Image-1 gibt immer base64-kodierte Bilder zurück
            b64_data = response.data[0].b64_json
            image_data = base64.b64decode(b64_data)
            with open(output_path, "wb") as f:
                f.write(image_data)

            end_time = time.time()
            print(f"  Iteration {i} erfolgreich abgeschlossen.")
            print(f"  Generiertes Bild gespeichert als: {output_path}")
            print(f"  Dauer: {end_time - start_time:.2f} Sekunden")

            # Das gerade generierte Bild wird zum Input für die nächste Iteration
            current_image_path = output_path

        except FileNotFoundError:
            print(f"Fehler: Input-Bild '{current_image_path}' nicht gefunden.")
            sys.exit(1)
        except Exception as e:
            print(f"Fehler während Iteration {i}: {e}")
            print(f"Details: {str(e)}")
            sys.exit(1)

        print("-" * 30)

    print("Bildreplikationsprozess abgeschlossen.")

if __name__ == "__main__":
    main() 
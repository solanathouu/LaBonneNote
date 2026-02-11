"""
Script pour retirer l'arrière-plan de toutes les images de mascotte
Utilise rembg pour créer des PNG avec transparence
"""
import os
from pathlib import Path
from rembg import remove
from PIL import Image

def remove_background(input_path, output_path):
    """Retire l'arrière-plan d'une image"""
    print(f"Traitement: {input_path.name}...")

    # Ouvrir l'image
    with open(input_path, 'rb') as input_file:
        input_data = input_file.read()

    # Retirer l'arrière-plan
    output_data = remove(input_data)

    # Sauvegarder
    with open(output_path, 'wb') as output_file:
        output_file.write(output_data)

    print(f"OK - Sauvegarde: {output_path.name}")

def main():
    # Dossier des images
    mascot_dir = Path(__file__).parent.parent / "frontend" / "assets" / "mascot"

    # Créer un dossier temporaire pour les backups
    backup_dir = mascot_dir / "backup_with_bg"
    backup_dir.mkdir(exist_ok=True)

    print(f"Dossier: {mascot_dir}")
    print(f"Backup: {backup_dir}")
    print()

    # Trouver toutes les images PNG
    png_files = list(mascot_dir.glob("*.png"))
    print(f"Trouve {len(png_files)} images PNG")
    print()

    # Traiter chaque image
    for i, png_file in enumerate(png_files, 1):
        print(f"[{i}/{len(png_files)}] ", end="")

        # Créer backup de l'original
        backup_path = backup_dir / png_file.name
        if not backup_path.exists():
            import shutil
            shutil.copy2(png_file, backup_path)

        # Retirer le background et écraser l'original
        remove_background(png_file, png_file)

    print()
    print("Termine ! Tous les arriere-plans ont ete retires.")
    print(f"Les originaux sont sauvegardes dans: {backup_dir}")

if __name__ == "__main__":
    main()

import os
import shutil
import datetime
import eel
from backend.strategies import get_highest_confidence_image, get_clean_image, get_nth_images

MAX_DIR_SIZE = 1.9 * 1024 * 1024 * 1024

def notify(message):
    try:
        eel.extraction_message(message)()
    except Exception:
        pass

def clean_path(value):
    if not value:
        return ""
    return os.path.normpath(value.strip().strip('"').strip("'"))

def process_images(config):
    input_dir = clean_path(config.get("input_folder", ""))
    output_base_dir = clean_path(config.get("output_folder", ""))
    strategy = config["strategy"]
    nth = int(config.get("nth_image", 2))
    prefix = config.get("rename_prefix", "")
    limit_size = config.get("limit_size", False)
    delete_dirs = config.get("delete_subfolders", False)

    if not input_dir or not output_base_dir:
        notify("Geen invoer- of uitvoermap ingesteld.")
        eel.processing_complete()()
        return

    if not os.path.isdir(input_dir):
        notify(f"Invoermap bestaat niet of is niet bereikbaar:\n{input_dir}\n\n"
               "Controleer of het pad klopt en of OneDrive de map lokaal beschikbaar heeft (niet 'alleen online').")
        eel.processing_complete()()
        return

    subfolders = []
    walk_errors = []
    for root, dirs, files in os.walk(input_dir, onerror=walk_errors.append):
        if files:
            subfolders.append(root)

    total_folders = len(subfolders)
    processed_folders = 0

    if total_folders == 0:
        msg = (f"Geen mappen met bestanden gevonden in:\n{input_dir}\n\n"
               "Mogelijke oorzaken: de mappen zijn al verwerkt (bestanden zijn verplaatst), "
               "het verkeerde niveau is gekozen, of OneDrive heeft de inhoud nog niet gesynct.")
        if walk_errors:
            msg += f"\n\n{len(walk_errors)} map(pen) kon(den) niet gelezen worden (rechten/pad)."
        notify(msg)
        eel.processing_complete()()
        return

    active_output_dirs = {}
    category_sizes = {}
    moved_files = 0
    move_errors = []

    for folder in subfolders:
        rel_path = os.path.relpath(folder, input_dir)
        parts = rel_path.split(os.sep)
        category = parts[0] if parts else "extracted"

        if category not in active_output_dirs:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
            dir_name = f"{prefix}_{category}_{timestamp}" if prefix else f"{category}_{timestamp}"
            active_output_dirs[category] = os.path.join(output_base_dir, dir_name)
            os.makedirs(active_output_dirs[category], exist_ok=True)
            category_sizes[category] = 0

        selected_files = []
        
        if strategy == "highest":
            best = get_highest_confidence_image(folder)
            if best: 
                sub_name = os.path.basename(folder)
                selected_files.append((best, f"{sub_name}_{best}"))
                
        elif strategy == "clean": 
            # Zoekt specifiek naar clean.jpg
            clean_file = get_clean_image(folder, "clean.jpg") 
            if clean_file:
                sub_name = os.path.basename(folder)
                selected_files.append((clean_file, f"{sub_name}_{clean_file}"))
                
        elif strategy == "best":
            # Zoekt specifiek naar best.jpg
            best_file = get_clean_image(folder, "best.jpg")
            if best_file:
                sub_name = os.path.basename(folder)
                selected_files.append((best_file, f"{sub_name}_{best_file}"))
                
        elif strategy == "metadata":
            # NIEUW: Zoekt specifiek naar metadata.json
            metadata_file = get_clean_image(folder, "metadata.json")
            if metadata_file:
                sub_name = os.path.basename(folder)
                selected_files.append((metadata_file, f"{sub_name}_{metadata_file}"))
                
        elif strategy == "video":
            # NIEUW: Zoekt specifiek naar video.mp4
            video_file = get_clean_image(folder, "video.mp4")
            if video_file:
                sub_name = os.path.basename(folder)
                selected_files.append((video_file, f"{sub_name}_{video_file}"))
                
        elif strategy == "nth":
            nth_files = get_nth_images(folder, nth)
            sub_name = os.path.basename(folder)
            for f in nth_files:
                selected_files.append((f, f"{sub_name}_{f}"))

        for original_name, target_name in selected_files:
            source_path = os.path.join(folder, original_name)
            # Voegt de prefix toe als deze is ingevuld
            final_name = f"{prefix}_{target_name}" if prefix else target_name

            try:
                file_size = os.path.getsize(source_path)

                if limit_size and (category_sizes[category] + file_size) > MAX_DIR_SIZE:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
                    dir_name = f"{prefix}_{category}_{timestamp}" if prefix else f"{category}_{timestamp}"
                    active_output_dirs[category] = os.path.join(output_base_dir, dir_name)
                    os.makedirs(active_output_dirs[category], exist_ok=True)
                    category_sizes[category] = 0

                target_path = os.path.join(active_output_dirs[category], final_name)
                shutil.move(source_path, target_path)
                category_sizes[category] += file_size
                moved_files += 1
            except Exception as e:
                move_errors.append(f"{source_path}: {e}")

        if delete_dirs:
            try:
                if os.path.exists(folder):
                    shutil.rmtree(folder)
            except Exception as e:
                move_errors.append(f"{folder} (verwijderen): {e}")

        processed_folders += 1
        eel.update_progress(processed_folders, total_folders)()

    summary = f"Klaar: {moved_files} bestand(en) verplaatst uit {total_folders} map(pen)."
    if moved_files == 0:
        summary += ("\n\nLet op: er is niets verplaatst. De gekozen strategie vond geen passend "
                    "bestand in de mappen (bijv. strategie 'Highest Confidence' terwijl de bestanden "
                    "best.jpg/clean.jpg heten).")
    if move_errors:
        summary += f"\n\n{len(move_errors)} bestand(en) overgeslagen door fouten:\n" + "\n".join(move_errors[:10])
        if len(move_errors) > 10:
            summary += f"\n... en nog {len(move_errors) - 10} meer."
    notify(summary)

    eel.processing_complete()()

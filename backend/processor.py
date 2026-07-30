import os
import re
import shutil
import datetime
import eel
from backend.strategies import get_highest_confidence_image, get_clean_image, get_nth_images

MAX_DIR_SIZE = 1.9 * 1024 * 1024 * 1024

# Map waar verwerkte submappen naartoe gaan in plaats van dat ze verwijderd worden.
RECYCLE_BIN_NAME = "recycle_bin"

# Detectiemappen beginnen altijd met een datum: JJJJ-MM-DD, gevolgd door een
# willekeurige code. Alles wat hier niet aan voldoet blijft ongemoeid staan.
DETECTION_FOLDER_PATTERN = re.compile(r"^(\d{4})-(\d{2})-(\d{2})(?!\d)")

def notify(message):
    try:
        eel.extraction_message(message)()
    except Exception:
        pass

def clean_path(value):
    if not value:
        return ""
    return os.path.normpath(value.strip().strip('"').strip("'"))

def determine_category(folder_path, input_dir):
    parts = folder_path.split(os.sep)
    lower_parts = [p.lower() for p in parts]
    if "detections" in lower_parts:
        idx = lower_parts.index("detections")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    rel_parts = os.path.relpath(folder_path, input_dir).split(os.sep)
    if rel_parts and rel_parts[0] not in (os.curdir, ""):
        return rel_parts[0]
    return "extracted"

def is_detection_folder_name(name):
    """True als de mapnaam begint met een geldige datum (JJJJ-MM-DD)."""
    match = DETECTION_FOLDER_PATTERN.match(name)
    if not match:
        return False
    year, month, day = (int(part) for part in match.groups())
    try:
        datetime.date(year, month, day)
    except ValueError:
        return False
    return True

def unique_destination(path):
    """Voorkomt dat een eerdere map in de recycle_bin overschreven wordt."""
    if not os.path.exists(path):
        return path
    counter = 1
    while os.path.exists(f"{path}__{counter}"):
        counter += 1
    return f"{path}__{counter}"

def move_to_recycle_bin(folder, input_dir, recycle_root):
    """Verplaatst een verwerkte submap naar de recycle_bin, met behoud van de mapstructuur."""
    relative = os.path.relpath(folder, input_dir)
    destination = unique_destination(os.path.join(recycle_root, relative))
    parent = os.path.dirname(destination)
    if parent:
        os.makedirs(parent, exist_ok=True)
    shutil.move(folder, destination)
    return destination

def process_images(config):
    input_dir = clean_path(config.get("input_folder", ""))
    output_base_dir = clean_path(config.get("output_folder", ""))
    strategy = config["strategy"]
    nth = int(config.get("nth_image", 2))
    prefix = config.get("rename_prefix", "")
    limit_size = config.get("limit_size", False)
    copy_files = config.get("copy_files", False)
    recycle_dirs = config.get("delete_subfolders", False) and not copy_files

    if not input_dir or not output_base_dir:
        notify("Geen invoer- of uitvoermap ingesteld.")
        eel.processing_complete()()
        return

    if not os.path.isdir(input_dir):
        notify(f"Invoermap bestaat niet of is niet bereikbaar:\n{input_dir}\n\n"
               "Controleer of het pad klopt en of OneDrive de map lokaal beschikbaar heeft (niet 'alleen online').")
        eel.processing_complete()()
        return

    recycle_root = os.path.join(input_dir, RECYCLE_BIN_NAME)

    subfolders = []
    walk_errors = []
    for root, dirs, files in os.walk(input_dir, onerror=walk_errors.append):
        # De recycle_bin zelf nooit opnieuw verwerken.
        dirs[:] = [d for d in dirs if os.path.join(root, d) != recycle_root]
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
    recycled_folders = 0
    skipped_folders = []

    for folder in subfolders:
        if not os.path.isdir(folder):
            # Map is al meeverhuisd met een bovenliggende map naar de recycle_bin.
            processed_folders += 1
            eel.update_progress(processed_folders, total_folders)()
            continue

        category = determine_category(folder, input_dir)

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
                if copy_files:
                    shutil.copy2(source_path, target_path)
                else:
                    shutil.move(source_path, target_path)
                category_sizes[category] += file_size
                moved_files += 1
            except Exception as e:
                move_errors.append(f"{source_path}: {e}")

        if recycle_dirs:
            folder_name = os.path.basename(os.path.normpath(folder))
            if os.path.abspath(folder) == os.path.abspath(input_dir):
                skipped_folders.append(f"{folder} (hoofdmap wordt nooit verplaatst)")
            elif not is_detection_folder_name(folder_name):
                skipped_folders.append(f"{folder} (naam begint niet met JJJJ-MM-DD)")
            else:
                try:
                    os.makedirs(recycle_root, exist_ok=True)
                    move_to_recycle_bin(folder, input_dir, recycle_root)
                    recycled_folders += 1
                except Exception as e:
                    move_errors.append(f"{folder} (naar recycle_bin): {e}")

        processed_folders += 1
        eel.update_progress(processed_folders, total_folders)()

    verb = "gekopieerd" if copy_files else "verplaatst"
    summary = f"Klaar: {moved_files} bestand(en) {verb} uit {total_folders} map(pen)."
    if moved_files == 0:
        summary += ("\n\nLet op: er is niets verplaatst. De gekozen strategie vond geen passend "
                    "bestand in de mappen (bijv. strategie 'Highest Confidence' terwijl de bestanden "
                    "best.jpg/clean.jpg heten).")
    if recycle_dirs:
        summary += (f"\n\n{recycled_folders} map(pen) verplaatst naar de recycle_bin:\n{recycle_root}"
                    "\nEr wordt niets definitief verwijderd; leeg deze map zelf als je zeker weet dat "
                    "de inhoud weg mag.")
        if skipped_folders:
            summary += (f"\n\n{len(skipped_folders)} map(pen) bleven staan omdat de naam niet aan het "
                        "formaat JJJJ-MM-DD... voldoet:\n" + "\n".join(skipped_folders[:10]))
            if len(skipped_folders) > 10:
                summary += f"\n... en nog {len(skipped_folders) - 10} meer."
    if move_errors:
        summary += f"\n\n{len(move_errors)} bestand(en) overgeslagen door fouten:\n" + "\n".join(move_errors[:10])
        if len(move_errors) > 10:
            summary += f"\n... en nog {len(move_errors) - 10} meer."
    notify(summary)

    eel.processing_complete()()

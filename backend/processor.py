import os
import shutil
import datetime
import eel
from backend.strategies import get_highest_confidence_image, get_clean_image, get_nth_images # Functienaam aangepast

MAX_DIR_SIZE = 1.9 * 1024 * 1024 * 1024

def process_images(config):
    input_dir = config["input_folder"]
    output_base_dir = config["output_folder"]
    strategy = config["strategy"]
    nth = int(config.get("nth_image", 2))
    prefix = config.get("rename_prefix", "")
    target_filename = config.get("target_filename", "clean.jpg")
    limit_size = config.get("limit_size", False)
    delete_dirs = config.get("delete_subfolders", False)

    if not input_dir or not output_base_dir:
        return

    subfolders = []
    for root, dirs, files in os.walk(input_dir):
        if files:
            subfolders.append(root)

    total_folders = len(subfolders)
    processed_folders = 0

    active_output_dirs = {}
    category_sizes = {}

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
        elif strategy == "clean": # Aangepast van "exact" naar "clean" om te matchen met de UI
            clean_file = get_clean_image(folder, target_filename) # Functie aangeroepen
            if clean_file:
                sub_name = os.path.basename(folder)
                # Voegt submapnaam toe om overschrijven te voorkomen
                selected_files.append((clean_file, f"{sub_name}_{clean_file}"))
        elif strategy == "nth":
            nth_files = get_nth_images(folder, nth)
            sub_name = os.path.basename(folder)
            for f in nth_files:
                selected_files.append((f, f"{sub_name}_{f}"))

        for original_name, target_name in selected_files:
            source_path = os.path.join(folder, original_name)
            # Voegt de prefix toe als deze is ingevuld
            final_name = f"{prefix}_{target_name}" if prefix else target_name
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

        if delete_dirs:
            if os.path.exists(folder):
                shutil.rmtree(folder)

        processed_folders += 1
        eel.update_progress(processed_folders, total_folders)()

    eel.processing_complete()()

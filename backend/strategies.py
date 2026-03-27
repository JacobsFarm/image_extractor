import os
import re

def get_highest_confidence_image(folder_path):
    pattern = re.compile(r'_([0-9]+\.[0-9]+)\.(jpg|jpeg|png)$', re.IGNORECASE)
    highest_conf = -1.0
    best_file = None
    for file in os.listdir(folder_path):
        match = pattern.search(file)
        if match:
            conf = float(match.group(1))
            if conf > highest_conf:
                highest_conf = conf
                best_file = file
    return best_file

def get_exact_image(folder_path, target_name):
    for file in os.listdir(folder_path):
        if file.lower() == target_name.lower():
            return file
    return None

def get_nth_images(folder_path, n):
    valid_extensions = ('.jpg', '.jpeg', '.png')
    files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(valid_extensions)])
    return files[n-1::n] if n > 0 else []
import json
import os
import sys

def get_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SETTINGS_DIR = os.path.join(get_base_dir(), "settings")
CONFIG_PATH = os.path.join(SETTINGS_DIR, "config.json")

def load_config():
    if not os.path.exists(SETTINGS_DIR):
        os.makedirs(SETTINGS_DIR)
    if not os.path.exists(CONFIG_PATH):
        default_config = {
            "input_folder": "",
            "output_folder": "",
            "strategy": "highest",
            "nth_image": 2,
            "rename_prefix": "",
            "limit_size": False,
            "delete_subfolders": False
        }
        with open(CONFIG_PATH, "w") as f:
            json.dump(default_config, f, indent=4)
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_config(config_data):
    if not os.path.exists(SETTINGS_DIR):
        os.makedirs(SETTINGS_DIR)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config_data, f, indent=4)
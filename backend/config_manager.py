import json
import os

CONFIG_PATH = os.path.join("settings", "config.json")

def load_config():
    if not os.path.exists("settings"):
        os.makedirs("settings")
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
    if not os.path.exists("settings"):
        os.makedirs("settings")
    with open(CONFIG_PATH, "w") as f:
        json.dump(config_data, f, indent=4)
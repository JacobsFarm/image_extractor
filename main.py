import eel
import os
from tkinter import Tk, filedialog
from backend.config_manager import load_config, save_config
from backend.processor import process_images

eel.init('frontend/dist')

@eel.expose
def get_config():
    return load_config()

@eel.expose
def update_config(data):
    save_config(data)

@eel.expose
def select_directory():
    root = Tk()
    root.attributes("-topmost", True)
    root.withdraw()
    folder_path = filedialog.askdirectory()
    root.destroy()
    return folder_path

@eel.expose
def start_processing(config):
    update_config(config)
    process_images(config)

eel.start('index.html', size=(850, 750))
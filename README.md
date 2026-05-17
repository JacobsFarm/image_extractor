# Image Extractor

Explanation video
https://www.youtube.com/watch?v=vHgYNldPFcM

Image Extractor is a hybrid desktop application designed to scan deeply nested directory structures, extract specific files based on customizable strategies, and neatly organize them into designated output folders. 

It features a modern, lightweight graphical user interface built with Svelte and a file-processing backend written in Python. The application communicates via Eel and compiles into a single standalone `.exe` file for easy distribution.

## Features

* **Smart Directory Parsing:** Automatically scans through parent category folders and their timestamped subfolders to find files.
* **Category-Based Organization:** Groups extracted files into separate output folders based on their original parent category.
* **Automated Renaming:** Prepends the original subfolder's timestamp to the extracted file to prevent file overwriting.
* **Custom Prefixes:** Add a custom text prefix to both the generated output folders and the extracted files.
* **Smart Folder Chunking:** Optionally limit output folders to 1.9 GB. Once the limit is reached, the application automatically generates a new timestamped folder.
* **Cleanup Mode:** Optionally force-delete the original subfolders and their remaining contents after a successful extraction.
* **Persistent Settings:** Remembers your last used folders and preferences across sessions via an auto-generated configuration file.
* **Categorized UI:** An intuitive tabbed interface splitting extraction strategies into **Data** and **Media** categories.

## Extraction Strategies

The application offers several extraction strategies, divided into two main categories:

### 📊 Data Strategies
1. **Extract Highest Confidence:** Scans image filenames for YOLO-style confidence scores (e.g., `_0.881.jpg`) and extracts only the image with the highest score from each subfolder.
2. **Extract clean.jpg:** Specifically looks for and extracts an image named `clean.jpg` from every subfolder.
3. **Extract Every Nth Image:** Extracts images based on a customizable numerical interval (e.g., extracting every 2nd or 5th image).

### 🎬 Media Strategies
1. **Extract best.jpg:** Specifically looks for and extracts an image named `best.jpg` from every subfolder.
2. **Extract metadata.json:** Extracts the `metadata.json` file from each subfolder.
3. **Extract video.mp4:** Extracts the `video.mp4` file from each subfolder.****

   <img width="880" height="886" alt="image_extractr" src="https://github.com/user-attachments/assets/15618c1f-54f3-4852-81ed-9f263d277efc" />

# Image Extractor

Explanation video
https://www.youtube.com/watch?v=vHgYNldPFcM

Image Extractor is a hybrid desktop application designed to scan deeply nested directory structures, extract specific images based on customizable strategies, and neatly organize them into designated output folders. 

It features a modern, lightweight graphical user interface built with Svelte and a file-processing backend written in Python. The application communicates via Eel and compiles into a single standalone `.exe` file for easy distribution.

## Features

* **Smart Directory Parsing:** Automatically scans through parent category folders and their timestamped subfolders to find images.
* **Category-Based Organization:** Groups extracted images into separate output folders based on their original parent category.
* **Automated Renaming:** Prepends the original subfolder's timestamp to the extracted image to prevent file overwriting.
* **Custom Prefixes:** Add a custom text prefix to both the generated output folders and the extracted files.
* **Smart Folder Chunking:** Optionally limit output folders to 1.9 GB. Once the limit is reached, the application automatically generates a new timestamped folder.
* **Cleanup Mode:** Optionally force-delete the original subfolders and their remaining contents after a successful extraction.
* **Persistent Settings:** Remembers your last used folders and preferences across sessions via an auto-generated configuration file.

## Extraction Strategies

1. **Extract Specific File:** Looks for an exact filename inside every subfolder.
2. **Extract Highest Confidence:** Scans filenames for YOLO-style confidence scores and extracts only the image with the highest score from each subfolder.
3. **Extract Every Nth Image:** Extracts images based on a numerical interval.

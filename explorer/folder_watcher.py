# explorer/folder_watcher.py
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .models import WatchedFolder

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}

class FolderEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            process_folder(event.src_path)

def calculate_folder_stats(folder_path):
    total_images = 0
    total_size = 0

    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            if ext in IMAGE_EXTENSIONS:
                total_images += 1
            try:
                total_size += os.path.getsize(file_path)
            except OSError:
                pass  # skip files that can't be read

    return total_images, total_size

def process_folder(folder_path):
    folder_name = os.path.basename(folder_path)

    # Check if folder already in DB
    if WatchedFolder.objects.filter(name=folder_name).exists():
        return

    # Look for .pan file
    pan_file = None
    for file in os.listdir(folder_path):
        if file.endswith(".pan"):
            pan_file = file
            break

    # Calculate stats
    total_images, total_size = calculate_folder_stats(folder_path)

    # Save to DB
    WatchedFolder.objects.create(
        name=folder_name,
        completed=bool(pan_file),
        pan_file=pan_file,
        total_images=total_images,
        total_size=total_size
    )

def sync_folders(path_to_watch):
    existing_folder_names = set(os.listdir(path_to_watch))

    # Remove DB entries for folders that no longer exist
    for folder in WatchedFolder.objects.all():
        if folder.name not in existing_folder_names:
            folder.delete()

    # Add missing folders from disk
    for folder_name in existing_folder_names:
        folder_path = os.path.join(path_to_watch, folder_name)
        if os.path.isdir(folder_path):
            process_folder(folder_path)

def start_watching(path_to_watch):
    # --- Step 1: Sync existing folders ---
    sync_folders(path_to_watch)

    # --- Step 2: Start real-time watcher ---
    event_handler = FolderEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=False)
    observer.start()
    return observer

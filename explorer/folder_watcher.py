# explorer/folder_watcher.py
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .models import WatchedFolder

class FolderEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            process_folder(event.src_path)

def process_folder(folder_path):
    folder_name = os.path.basename(folder_path)

    # Check if folder already in DB
    if WatchedFolder.objects.filter(name=folder_name).exists():
        return

    # Look for .pan files
    pan_file = None
    for file in os.listdir(folder_path):
        if file.endswith(".pan"):
            pan_file = file
            break

    # Save to DB
    WatchedFolder.objects.create(
        name=folder_name,
        completed=bool(pan_file),
        pan_file=pan_file
    )


def sync_folders(path_to_watch):
    existing_folder_names = set(os.listdir(path_to_watch))
    
    for folder in WatchedFolder.objects.all():
        if folder.name not in existing_folder_names:
            folder.delete()
    
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
    print(f"👀 Watching folder: {path_to_watch}")
    return observer

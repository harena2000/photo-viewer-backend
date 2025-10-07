# explorer/folder_watcher.py
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from explorer.utils.parser import parse_file
from .models import ImageMetadata, ProjectFolder

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
ACCEPTED_DATA_FILES = {".pan", ".csv", ".cam"}


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
                pass

    return total_images, total_size


def process_folder(folder_path):
    folder_name = os.path.basename(folder_path)

    if ProjectFolder.objects.filter(name=folder_name).exists():
        return

    data_file = None
    for file in os.listdir(folder_path):
        ext = os.path.splitext(file)[1].lower()
        if ext in ACCEPTED_DATA_FILES:
            data_file = os.path.join(folder_path, file)
            break

    total_images, total_size = calculate_folder_stats(folder_path)

    print("✅ Processing folder:", folder_name)
    folder = ProjectFolder.objects.create(
        name=folder_name,
        completed=bool(data_file),
        total_images=total_images,
        total_size=total_size,
    )

    print("✅ Folder created:", folder)

    if data_file:
        print("✅ Data File:", data_file)
        metadata_list = parse_file(data_file)
        # print("✅ Metadata List :", metadata_list)
        for meta in metadata_list:
            # print("✅ Meta : ", meta.get("filename"))
            ImageMetadata.objects.create(folder=folder, **meta)


def sync_folders(path_to_watch):
    existing_folder_names = set(os.listdir(path_to_watch))

    for folder in ProjectFolder.objects.all():
        if folder.name not in existing_folder_names:
            folder.delete()

    for folder_name in existing_folder_names:
        folder_path = os.path.join(path_to_watch, folder_name)
        if os.path.isdir(folder_path):
            process_folder(folder_path)


def start_watching(path_to_watch):
    sync_folders(path_to_watch)

    event_handler = FolderEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=False)
    observer.start()
    return observer

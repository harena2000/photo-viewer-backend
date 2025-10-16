# import os
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler

# from project.utils.parser import parse_file
# from .models import ImageMetadata, ProjectFolder

# IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
# ACCEPTED_DATA_FILES = {".pan", ".csv", ".cam", ".ort", ".kml"}


# class FolderEventHandler(FileSystemEventHandler):
#     def on_created(self, event):
#         if event.is_directory:
#             process_folder(event.src_path)


# def calculate_folder_stats(folder_path):
#     total_images = 0
#     total_size = 0

#     for root, _, files in os.walk(folder_path):
#         for file in files:
#             file_path = os.path.join(root, file)
#             ext = os.path.splitext(file)[1].lower()
#             if ext in IMAGE_EXTENSIONS:
#                 total_images += 1
#             try:
#                 total_size += os.path.getsize(file_path)
#             except OSError:
#                 pass

#     return total_images, total_size


# def process_folder(project_path):
#     project_name = os.path.basename(project_path)

#     if ProjectFolder.objects.filter(name=project_name).exists():
#         return

#     data_file = None
#     for file in os.listdir(project_path):
#         ext = os.path.splitext(file)[1].lower()
#         if ext in ACCEPTED_DATA_FILES:
#             data_file = os.path.join(project_path, file)
#             break

#     total_images, total_size = calculate_folder_stats(project_path)

#     project = ProjectFolder.objects.create(
#         name=project_name,
#         completed=bool(data_file),
#         total_images=total_images,
#         total_size=total_size,
#     )

#     if data_file:
#         metadata_list = parse_file(data_file)
#         for meta in metadata_list:
#             ImageMetadata.objects.create(project=project, **meta)


# def sync_project(path_to_watch):
#     existing_project_names = set(os.listdir(path_to_watch))

#     for project in ProjectFolder.objects.all():
#         if project.name not in existing_project_names:
#             project.delete()

#     for project_name in existing_project_names:
#         project_path = os.path.join(path_to_watch, project_name)
#         if os.path.isdir(project_path):
#             process_folder(project_path)


# def start_watching(path_to_watch):
#     sync_project(path_to_watch)

#     event_handler = FolderEventHandler()
#     observer = Observer()
#     observer.schedule(event_handler, path_to_watch, recursive=False)
#     observer.start()
#     return observer

from django.apps import AppConfig
import threading
import os
from pathlib import Path


class FileExplorerConfig(AppConfig):

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'explorer'

    def ready(self):
        
        from .folder_watcher import start_watching
        ROOT_FOLDER = Path("/app/project");
        path_to_watch = str(ROOT_FOLDER);
        if os.path.exists(path_to_watch):
            thread = threading.Thread(target=start_watching, args=(path_to_watch,))
            thread.daemon = True
            thread.start()


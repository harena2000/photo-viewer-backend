from django.shortcuts import render
from environs import Env

import os
from pathlib import Path
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response

ROOT_FOLDER = Path("/app/project")

env = Env()
env.read_env()

class ListFiles(APIView):
    def get(self, request):
        """
        List all files and folders in ROOT_FOLDER.
        Optional query parameter:
        - path: relative path inside ROOT_FOLDER to explore subfolders
        """
        try:
            relative_path = request.query_params.get("path", "")
            folder_to_list = ROOT_FOLDER / relative_path
            print(folder_to_list)

            if not folder_to_list.exists() or not folder_to_list.is_dir():
                return Response({"error": "Folder does not exist"}, status=404)

            files = []
            for entry in folder_to_list.iterdir():
                files.append({
                    "name": entry.name,
                    "type": "folder" if entry.is_dir() else "file"
                })

            return Response({
                "current_path": str(folder_to_list.relative_to(ROOT_FOLDER)),
                "full_path": env.str('BACKEND_URL') + settings.MEDIA_URL + str(folder_to_list.relative_to(ROOT_FOLDER)),
                "files": files
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)

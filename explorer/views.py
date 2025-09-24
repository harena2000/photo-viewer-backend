from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.paginator import Paginator
from .models import WatchedFolder

class ListFiles(APIView):
    def get(self, request):
        try:
            page = int(request.query_params.get("page", 1))
            page_size = int(request.query_params.get("page_size", 10))

            # Query all folders from DB
            folders = WatchedFolder.objects.all().order_by("name")

            # Pagination
            paginator = Paginator(folders, page_size)
            paged_folders = paginator.get_page(page)

            # Serialize folders
            files_data = []
            for folder in paged_folders:
                files_data.append({
                    "name": folder.name,
                    "completed": folder.completed,
                    "pan_file": folder.pan_file,
                    "total_images": folder.total_images,
                    "total_size": folder.total_size,
                    "created_at": folder.created_at,
                })

            return Response({
                "projects": files_data,
                "pagination": {
                    "page": paged_folders.number,
                    "page_size": page_size,
                    "total_pages": paginator.num_pages,
                    "total_items": paginator.count,
                    "has_next": paged_folders.has_next(),
                    "has_previous": paged_folders.has_previous(),
                }
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)

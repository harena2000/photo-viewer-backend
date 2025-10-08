from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.paginator import Paginator
from .models import ImageMetadata, ProjectFolder
from rest_framework import status

class ProjectList(APIView):
    def get(self, request):
        try:
            page = int(request.query_params.get("page", 1))
            page_size = int(request.query_params.get("page_size", 10))

            projects = ProjectFolder.objects.all().order_by("name")

            # Pagination
            paginator = Paginator(projects, page_size)
            paged_projects = paginator.get_page(page)

            # Serialize folders
            projects_data = []
            for project in paged_projects:
                projects_data.append({
                    "name": project.name,
                    "completed": project.completed,
                    "project_id": project.id,
                    "total_images": project.total_images,
                    "total_size": project.total_size,
                    "created_at": project.created_at,
                })

            return Response({
                "projects": projects_data,
                "pagination": {
                    "page": paged_projects.number,
                    "page_size": page_size,
                    "total_pages": paginator.num_pages,
                    "total_items": paginator.count,
                    "has_next": paged_projects.has_next(),
                    "has_previous": paged_projects.has_previous(),
                }
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)

class ImageMetadataList(APIView):
    def get(self, request):
        try:
            project_id = request.query_params.get("project_id")
            page = int(request.query_params.get("page", 1))
            page_size = int(request.query_params.get("page_size", 10))
            
            if not project_id:
                return Response(
                    {"error": "Missing required parameter: project_id"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                project = ProjectFolder.objects.get(id=project_id)
            except ProjectFolder.DoesNotExist:
                return Response(
                    {"error": f"WatchedFolder with id={project_id} not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            images = ImageMetadata.objects.filter(project=project).order_by("id")
            images = ImageMetadataList.objects.all().order_by("name")

            # Pagination
            paginator = Paginator(images, page_size)
            paged_images = paginator.get_page(page)

            images_data = []
            for image in paged_images:
                images_data.append({
                    'filename': image.filename,
                    'timestamp': image.timestamp,
                    'x': image.x, 'y': image.y, 'z': image.z,
                    'roll': image.roll, 'pitch': image.pitch, 'yaw': image.yaw
                })

            return Response({
                "projects": images_data,
                "pagination": {
                    "page": paged_images.number,
                    "page_size": page_size,
                    "total_pages": paginator.num_pages,
                    "total_items": paginator.count,
                    "has_next": paged_images.has_next(),
                    "has_previous": paged_images.has_previous(),
                }
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)

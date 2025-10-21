import os
import re
from sys import stdout
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from core import settings
from .models import Project, Pathway, Position
from .utils.parser import parse_file
from django.core.paginator import Paginator

DOCKER_VOLUME_BASE = "/app/data"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
ACCEPTED_DATA_FILES = {".pan", ".csv", ".cam"}

# ---------------------------------------------------------------
# 🧩 Utility: Convert Windows path to Docker volume path
# ---------------------------------------------------------------
def windows_to_docker_path(windows_path: str) -> str:
    path = windows_path.replace("\\", "/")
    if ":" in path:
        _, relative = path.split(":", 1)
        path = relative.lstrip("/")
    return os.path.join(DOCKER_VOLUME_BASE, path)

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


# ---------------------------------------------------------------
# 1️⃣ Create a Project from a Windows Path
# ---------------------------------------------------------------
@api_view(["POST"])
def create_project_from_path(request):
    windows_path = request.data.get("filepath")
    if not windows_path:
        return Response({"error": "Missing 'filepath'."}, status=400)

    docker_path = windows_to_docker_path(windows_path)
    if not os.path.exists(docker_path):
        return Response({"error": f"Path not found: {docker_path}"}, status=404)

    match = re.match(
        r"^([A-Z]:)?[\\/]+([^\\/]+)[\\/]+(\d{4})[\\/]+([^\\/]+)[\\/]+([^\\/]+)$",
        windows_path.strip(),
        re.IGNORECASE,
    )
    if not match:
        return Response({"error": "Invalid path format. Expected: P:/<departement>/<year>/<project_number>/<project_name>"},
                        status=400)

    project_number = match.group(4)
    project_name = match.group(5)

    if Project.objects.filter(name=project_name).exists():
        return Response({"message": f"Project '{project_name}' already exists."}, status=200)

    project = Project.objects.create(
        number=project_number,
        name=project_name,
        folder=windows_path,
    )

    return Response(
        {
            "message": "Project created successfully.",
            "project": {
                "id": project.id,
                "number": project.number,
                "name": project.name,
                "folder": project.folder,
            },
        },
        status=status.HTTP_201_CREATED,
    )

# ---------------------------------------------------------------
# 2️⃣ Create Pathway and Positions (from image folder)
# ---------------------------------------------------------------
@api_view(["POST"])
def create_pathway_from_path(request):
    project_id = request.data.get("project_id")
    epsg = request.data.get("epsg")
    windows_path = request.data.get("filepath")

    if not project_id or not windows_path:
        return Response({"error": "Missing 'project_id' or 'filepath'."}, status=400)

    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response({"error": f"Project with id {project_id} not found."}, status=404)

    docker_path = windows_to_docker_path(windows_path)
    if not os.path.exists(docker_path):
        return Response({"error": f"Folder not found: {docker_path}"}, status=404)

    pathway_name = os.path.basename(docker_path)

    # Detect data file
    data_file = next(
        (f for f in os.listdir(docker_path)
         if os.path.splitext(f)[1].lower() in ACCEPTED_DATA_FILES),
        None
    )
    original_format = os.path.splitext(data_file)[1][1:].upper() if data_file else ""

    pathway = Pathway.objects.create(
        project=project,
        name=pathway_name,
        original_format=original_format,
        original_file=data_file or "",
        folder=pathway_name,
        epsg=epsg if epsg else None,
        full_folder_path=windows_path,
    )

    result = create_positions_from_pathway(pathway)
    
    # Now handle the plain result
    if isinstance(result, dict) and "error" in result:
        return Response({"error": result["error"]}, status=500)

    positions_created = result.get("positions_created", 0) if isinstance(result, dict) else result

    return Response(
        {
            "message": "✅ Pathway and image positions created successfully.",
            "project_id": project.id,
            "pathway_id": pathway.id,
            "positions_created": positions_created,
        },
        status=status.HTTP_201_CREATED,
    )

def create_positions_from_pathway(pathway):
    if not pathway or not pathway.id:
        return {"error": "Missing 'pathway_id'."}

    if not pathway.original_file:
        return {"error": "Pathway has no original file defined."}

    pathway_windows_path = os.path.join(pathway.full_folder_path, pathway.original_file)
    docker_path = windows_to_docker_path(pathway_windows_path)

    try:
        parsed_positions = parse_file(docker_path)
        positions_created = 0

        for idx, pos_data in enumerate(parsed_positions, start=1):
            Position.objects.create(
                pathway=pathway,
                number=idx,
                x=pos_data.get("x"),
                y=pos_data.get("y"),
                z=pos_data.get("z"),
                roll=pos_data.get("roll"),
                pitch=pos_data.get("pitch"),
                yaw=pos_data.get("yaw"),
                filename=pos_data.get("filename", ""),
                full_folder_path=os.path.join(pathway.full_folder_path, pos_data.get("filename", "")),
            )
            positions_created += 1
        return {"positions_created": positions_created}

    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------------
# 3️⃣ Update Pathway EPSG
# ---------------------------------------------------------------
@api_view(["PATCH"])
def update_pathway_epsg(request, pathway_id):
    """
    PATCH /api/pathway/<pathway_id>/update-epsg/
    Input:
    {
        "epsg": "2154"
    }
    """
    try:
        pathway = Pathway.objects.get(id=pathway_id)
    except Pathway.DoesNotExist:
        return Response({"error": f"Pathway with id {pathway_id} not found."}, status=404)

    epsg = request.data.get("epsg")
    if not epsg:
        return Response({"error": "Missing 'epsg' value."}, status=400)

    pathway.epsg = epsg
    pathway.save()

    return Response(
        {
            "message": f"EPSG updated successfully for pathway '{pathway.name}'.",
            "pathway_id": pathway.id,
            "new_epsg": pathway.epsg,
        },
        status=status.HTTP_200_OK,
    )

# ---------------------------------------------------------------
# 🧾 1️⃣ Get All Projects (Paginated)
# ---------------------------------------------------------------
@api_view(["GET"])
def get_project_list(request):
    """
    GET /api/project/list/?page=1&page_size=10
    Returns all projects with their associated pathways.
    """
    try:
        # Pagination setup
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

        projects = Project.objects.all().order_by("name")
        paginator = Paginator(projects, page_size)
        paged_projects = paginator.get_page(page)

        projects_data = []
        for project in paged_projects:
            # Fetch pathways related to this project
            pathways = Pathway.objects.filter(project=project).order_by("id")

            # Build pathway list
            pathways_data = [
                {
                    "id": p.id,
                    "name": p.name,
                    "original_format": p.original_format,
                    "original_file": p.original_file,
                    "folder": p.folder,
                    "epsg": p.epsg,
                    "full_folder_path": p.full_folder_path,
                }
                for p in pathways
            ]

            projects_data.append({
                "id": project.id,
                "number": project.number,
                "name": project.name,
                "folder": project.folder,
                "pathways": pathways_data,
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


# ---------------------------------------------------------------
# 🧭 2️⃣ Get All Pathways by Project ID (Paginated)
# ---------------------------------------------------------------
@api_view(["GET"])
def get_pathways_by_project(request, project_id):
    """
    GET /api/projects/<project_id>/pathways
    """
    try:
        pathways = Pathway.objects.filter(project_id=project_id).order_by("id")

        pathways_data = []
        for pathway in pathways:
            pathways_data.append({
                "id": pathway.id,
                "name": pathway.name,
                "original_format": pathway.original_format,
                "original_file": pathway.original_file,
                "folder": pathway.folder,
                "epsg": pathway.epsg,
                "full_folder_path": pathway.full_folder_path,
            })

        return Response(pathways_data)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


# ---------------------------------------------------------------
# 🧭 3️⃣ Get All Positions by Pathway ID (Paginated)
# ---------------------------------------------------------------
@api_view(["GET"])
def get_positions_by_pathway(request, pathway_id):
    """
    GET /api/pathway/<pathway_id>/positions/?page=1&page_size=10
    """
    try:
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

        positions = Position.objects.filter(pathway_id=pathway_id).order_by("number")

        paginator = Paginator(positions, page_size)
        paged_positions = paginator.get_page(page)

        positions_data = []
        for pos in paged_positions:
            docker_path = windows_to_docker_path(pos.full_folder_path)

            # Get only the relative path under MEDIA_ROOT
            relative_path = os.path.relpath(docker_path, settings.MEDIA_ROOT)

            # Build full URL to access the image
            image_url = request.build_absolute_uri(
                os.path.join(settings.MEDIA_URL, relative_path).replace("\\", "/")
            )
            positions_data.append({
                "id": pos.id,
                "number": pos.number,
                "x": pos.x,
                "y": pos.y,
                "z": pos.z,
                "roll": pos.roll,
                "pitch": pos.pitch,
                "yaw": pos.yaw,
                "filename": pos.filename,
                "imageUrl": image_url,
            })
            
        return Response({
            "positions": positions_data,
            "pagination": {
                "page": paged_positions.number,
                "page_size": page_size,
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "has_next": paged_positions.has_next(),
                "has_previous": paged_positions.has_previous(),
            }
        })
    except Exception as e:
        return Response({"error": str(e)}, status=500)

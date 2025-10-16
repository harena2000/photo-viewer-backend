from django.urls import path
from .views import (
    create_project_from_path,
    create_pathway_from_path,
    update_pathway_epsg,
    get_project_list,
    get_pathways_by_project,
    get_positions_by_pathway,
)

urlpatterns = [
    path("create/", create_project_from_path, name="create_project_from_path"),
    path("pathway/create/", create_pathway_from_path, name="create_pathway_from_path"),
    path("position/create/", create_pathway_from_path, name="create_pathway_from_path"),
    path("pathway/<int:pathway_id>/update-epsg/", update_pathway_epsg, name="update_pathway_epsg"),
    path("list/", get_project_list, name="get_projects"),
    path("<int:project_id>/pathways/", get_pathways_by_project, name="get_pathways_by_project"),
    path("pathways/<int:pathway_id>/positions/", get_positions_by_pathway, name="get_positions_by_pathway"),
]
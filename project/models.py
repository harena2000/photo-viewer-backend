from django.db import models


class Project(models.Model):
    number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    folder = models.CharField(max_length=512)

    def __str__(self):
        return f"{self.number} - {self.name}"


class Pathway(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="pathways")
    name = models.CharField(max_length=255)
    original_format = models.CharField(max_length=20, blank=True, null=True)
    original_file = models.CharField(max_length=255, blank=True, null=True)
    folder = models.CharField(max_length=512, blank=True, null=True)
    epsg = models.CharField(max_length=50, blank=True, null=True)
    full_folder_path = models.CharField(max_length=1024, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.project.name})"


class Position(models.Model):
    pathway = models.ForeignKey(
        "Pathway", on_delete=models.CASCADE, related_name="positions"
    )
    number = models.IntegerField()
    x = models.FloatField(blank=True, null=True)
    y = models.FloatField(blank=True, null=True)
    z = models.FloatField(blank=True, null=True)
    roll = models.FloatField(blank=True, null=True)  # Roll
    pitch = models.FloatField(blank=True, null=True)  # Pitch
    yaw = models.FloatField(blank=True, null=True)  # Yaw
    filename = models.CharField(max_length=512)
    full_folder_path = models.CharField(max_length=1024, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pathway.name} - Pos {self.number} ({self.path})"

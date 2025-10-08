from django.db import models

class ProjectFolder(models.Model):
    name = models.CharField(max_length=255, unique=True)
    completed = models.BooleanField(default=False)
    pan_file = models.CharField(max_length=255, null=True, blank=True)
    total_images = models.IntegerField(default=0)
    total_size = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({'Completed' if self.completed else 'Pending'})"

class ImageMetadata(models.Model):
    folder = models.ForeignKey(ProjectFolder, on_delete=models.CASCADE, related_name="images")
    filename = models.CharField(max_length=255)
    timestamp = models.DateTimeField(null=True, blank=True)
    x = models.FloatField(null=True, blank=True)
    y = models.FloatField(null=True, blank=True)
    z = models.FloatField(null=True, blank=True)
    roll = models.FloatField(null=True, blank=True)
    pitch = models.FloatField(null=True, blank=True)
    yaw = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.filename} ({self.folder.name})"
from django.db import models

class WatchedFolder(models.Model):
    name = models.CharField(max_length=255, unique=True)
    completed = models.BooleanField(default=False)
    pan_file = models.CharField(max_length=255, null=True, blank=True)
    total_images = models.IntegerField(default=0)
    total_size = models.BigIntegerField(default=0)  # size in bytes
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({'Completed' if self.completed else 'Pending'})"



from django.db import models

class Storage(models.Model):
    title = models.CharField(max_length=100)
    storage_image = models.URLField(null=True, blank=True)
    quantity = models.IntegerField()

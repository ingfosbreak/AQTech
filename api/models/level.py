from django.db import models

class Level(models.Model):
    levelName = models.CharField(max_length=50)

    def __str__(self):
        return self.levelName

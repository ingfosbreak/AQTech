from django.db import models

class Type(models.Model):
    typeName = models.CharField(max_length=50)

    def __str__(self):
        return self.typeName

from django.db import models

# Create your models here.
class category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

class subCategory(models.Model):
    id = models.AutoField(primary_key=True)
    category_id = models.IntegerField()
    name = models.CharField(max_length=50)
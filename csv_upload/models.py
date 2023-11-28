# csv_upload/models.py

from django.db import models

class CSVFile(models.Model):
    file = models.FileField(upload_to='csv_files/')

class Hotel(models.Model):
    name = models.CharField(max_length=255)
import uuid

from django.db import models


class HttpSource(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(unique=True)
    e_tag = models.CharField(max_length=64, null=True, blank=True)
    last_refreshed = models.DateTimeField()
    blob_path = models.CharField(max_length=256)

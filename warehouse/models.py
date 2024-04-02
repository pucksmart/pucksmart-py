import uuid

from django.db import models


class HttpSource(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(unique=True)
    e_tag = models.CharField(max_length=64, null=True, blank=True)
    last_refreshed = models.DateTimeField()
    blob_path = models.CharField(max_length=256)


class NhlPlayer(models.Model):
    nhl_id = models.IntegerField(unique=True)
    given_name = models.CharField(max_length=64)
    family_name = models.CharField(max_length=64)
    is_active = models.BooleanField(default=False)
    position = models.CharField(max_length=2)
    hall_of_fame = models.BooleanField(default=False)
    birth_date = models.DateField()
    birth_locality = models.CharField(max_length=64)
    birth_region = models.CharField(max_length=64, null=True, blank=True)
    birth_country = models.CharField(max_length=3)
    handedness = models.CharField(max_length=1, null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)

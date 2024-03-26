from datetime import timezone, timedelta, datetime

import boto3
import requests
from botocore.config import Config
from celery import shared_task

from warehouse.models import HttpSource


s3 = boto3.resource("s3",
                    endpoint_url="http://localhost:9000",
                    config=Config(signature_version="s3v4"),
                    aws_access_key_id="accesskey",
                    aws_secret_access_key="secretkey",
                    aws_session_token=None,
                    verify=False)


@shared_task
def load_play_by_play(game_id: int):
    url = "https://api-web.nhle.com/v1/gamecenter/%d/play-by-play" % game_id
    try:
        source = HttpSource.objects.get(url=url)
    except HttpSource.DoesNotExist:
        source = HttpSource(url=url)

    if not source.last_refreshed or source.last_refreshed + timedelta(days=1) < datetime.now(timezone.utc):
        e_tag = ""
        if source.e_tag:
            r = requests.head(source.url, allow_redirects=True)
            e_tag = r.headers.get("ETag")
        if not source.e_tag or e_tag != source.e_tag:
            r = requests.get(source.url, allow_redirects=True)
            source.e_tag = r.headers.get("ETag")
            source.last_refreshed = datetime.now(timezone.utc)
            source.blob_path = "game/%d/play-by-play" % game_id
            s3.Object("pucksmart", source.blob_path).put(Body=r.content)
    source.save()


@shared_task
def load_shifts(game_id: int):
    url = "https://api.nhle.com/stats/rest/en/shiftcharts?cayenneExp=gameId=%d" % game_id
    try:
        source = HttpSource.objects.get(url=url)
    except HttpSource.DoesNotExist:
        source = HttpSource(url=url)

    if not source.last_refreshed or source.last_refreshed + timedelta(days=1) < datetime.now(timezone.utc):
        e_tag = ""
        if source.e_tag:
            r = requests.head(source.url, allow_redirects=True)
            e_tag = r.headers.get("ETag")
        if not source.e_tag or e_tag != source.e_tag:
            r = requests.get(source.url, allow_redirects=True)
            source.e_tag = r.headers.get("ETag")
            source.last_refreshed = datetime.now(timezone.utc)
            source.blob_path = "game/%d/shifts" % game_id
            s3.Object("pucksmart", source.blob_path).put(Body=r.content)
    source.save()

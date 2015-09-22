from __future__ import absolute_import
from argparse import Namespace
from celery import shared_task
from celery.utils.log import get_task_logger
from performanceplatform.collector.main import _run_collector
from django.conf import settings
from stagecraft.apps.collectors.libs.ga import CredentialStorage
from stagecraft.apps.collectors.models import Collector
import json

logger = get_task_logger(__name__)


@shared_task
def log(message):
    logger.info(message)


@shared_task
def run_collector(collector_slug, start_at=None, end_at=None, dry_run=False):
    def get_config(collector_slug, start, end):
        collector = Collector.objects.get(slug=collector_slug)
        config = Namespace(
            performanceplatform={
                "backdrop_url": settings.BACKDROP_WRITE_URL + '/data'
            },
            credentials=json.loads(collector.data_source.credentials),
            query={
                "data-set": {
                    "data-group": collector.data_set.data_group,
                    "data-type": collector.data_set.data_type
                },
                "query": collector.query,
                "options": collector.options
            },
            token={
                "token": collector.type.provider.slug
            },
            dry_run=dry_run,
            start_at=start,
            end_at=end
        )
        return collector.type.entry_point, config

    entry_point, args = get_config(collector_slug, start_at, end_at)
    _run_collector(entry_point, args)

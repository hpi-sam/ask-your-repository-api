from .elastic_syncer import ElasticSyncer
from flask import current_app


def resync_elasticsearch_eventually():
    current_app.sync_scheduler.add_job(ElasticSyncer.resync_everything())

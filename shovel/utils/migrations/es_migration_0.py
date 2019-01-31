import os

from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from shovel import task

load_dotenv()


@task
def migrate_indices_0():
    es = Elasticsearch(os.environ.get('ES_URL'))
    new_index_body = {
        "mappings": {
            "image": {
                "properties": {
                    "tags": {"type": "text"},
                    "file_url": {"type": "keyword"},
                    "team_id": {"type": "keyword"},
                    "file_date": {
                        "type": "date",
                        "format": "strict_date_optional_time||epoch_millis"
                    },
                    "created_at": {
                        "type": "date",
                        "format": "strict_date_optional_time||epoch_millis"
                    },
                    "updated_at": {
                        "type": "date",
                        "format": "strict_date_optional_time||epoch_millis"
                    }
                }
            }
        }
    }
    es.indices.create(index="new_artifact", ignore=400, body=new_index_body)
    es.reindex(refresh=True, body={
        "source": {
            "index": "artifact"
        },
        "dest": {
            "index": "new_artifact"
        }})
    es.indices.delete(index="artifact")
    es.indices.create(index="artifact", ignore=400, body=new_index_body)
    es.reindex(refresh=True, body={
        "source": {
            "index": "new_artifact"
        },
        "dest": {
            "index": "artifact"
        }})
    es.indices.delete(index="new_artifact")


if __name__ == '__main__':
    migrate_indices_0()
    print('lmao success')

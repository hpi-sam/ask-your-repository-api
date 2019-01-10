import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
load_dotenv()


def setup_indices():
    es = Elasticsearch(os.environ.get('ES_URL'))
    es.indices.create(index="artifact", ignore=400, body={
        "mappings": {
            "image": {
                "properties": {
                    "tags": {"type": "text"},
                    "file_url": {"type": "text"},
                    "team_id": {"type": "text"},
                    "file_date":  {
                        "type":   "date",
                        "format": "strict_date_optional_time||epoch_millis"
                    },
                    "created_at":  {
                        "type":   "date",
                        "format": "strict_date_optional_time||epoch_millis"
                    },
                    "updated_at":  {
                        "type":   "date",
                        "format": "strict_date_optional_time||epoch_millis"
                    }
                }
            }
        }
    })


if __name__ == '__main__':
    setup_indices()
    print('rofl success')

import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
load_dotenv()


def delete_indices():
    es = Elasticsearch(os.environ.get('ES_URL'))
    es.indices.delete(index="artifact")

if __name__ == '__main__':
    delete_indices()
    print('rofl success')

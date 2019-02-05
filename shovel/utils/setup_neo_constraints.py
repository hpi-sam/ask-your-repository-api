import os

from dotenv import load_dotenv
from shovel import task
from neomodel import install_labels
from neomodel import config


@task
def setup_neo_constraints():
    load_dotenv()
    config.ENCRYPTED_CONNECTION = False
    config.DATABASE_URL = os.environ.get('NEO4J_URL')
    #install_labels(Team)
    #install_labels(Tag)
    #install_labels(Artifact)
    print('success')


if __name__ == '__main__':
    setup_neo_constraints()
    print('xdd success')

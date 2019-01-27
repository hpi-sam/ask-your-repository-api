import os
from dotenv import load_dotenv
from py2neo import Graph, Database
load_dotenv()


def setup_neo_constraints():
    db = Database(os.environ.get('NEO4J_URL'))
    graph = db.default_graph
    graph.schema.create_uniqueness_constraint("NeoTag", "name")


if __name__ == '__main__':
    setup_neo_constraints()
    print('xdd success')
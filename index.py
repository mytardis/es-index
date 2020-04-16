import sys
import argparse
import os
import yaml
import json

from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from elasticsearch import Elasticsearch, helpers

from datafile import count_from_db, data_from_db, data_to_es


def init_es_index(index_name):

    with open("{}.json".format(index_name)) as f:
        config = json.load(f)

    es.indices.delete(
        index=index_name,
        ignore_unavailable=True
    )

    es.indices.create(
        index=index_name,
        body=config
    )


parser = argparse.ArgumentParser()
parser.add_argument(
    "--config",
    default="settings.yaml",
    help="Config file location."
)
parser.add_argument(
    "--rebuild",
    action="store_true",
    help="Delete and create index."
)

args = parser.parse_args()

if os.path.isfile(args.config):
    with open(args.config) as f:
        settings = yaml.load(f, Loader=yaml.Loader)
else:
    sys.exit("Can't find settings.")

try:
    con = connect(
        host=settings["database"]["host"],
        port=settings["database"]["port"],
        user=settings["database"]["username"],
        password=settings["database"]["password"],
        database=settings["database"]["database"]
    )
except Exception:
    sys.exit("Can't connect to the database.")


try:
    es_host = "{}:{}".format(
        settings["elasticsearch"]["host"],
        settings["elasticsearch"]["port"]
    )
    es = Elasticsearch([es_host])
except Exception:
    con.close()
    sys.exit("Can't connect to the Elasticsearch.")


cur = con.cursor(cursor_factory=RealDictCursor)

if args.rebuild:
    print("Rebuild index.")
    init_es_index(settings["index"]["name"])

start = 0
to_go = 1

while to_go > 0:

    to_go = count_from_db(cur, start)
    print("{:,} datafiles to index".format(to_go))

    if to_go > 0:
        (data, start) = data_from_db(cur, start, settings["index"]["limit"])
        helpers.bulk(es, data_to_es(settings["index"]["name"], data))

print("Completed.")
cur.close()
con.close()

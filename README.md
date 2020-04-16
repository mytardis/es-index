## Index MyTardis datafiles to Elasticsearch

This script will populate Elasticsearch index from MyTardis datafile records.

Out of the box Elasticsearch DSL library for Django was not robust enough to index large data. Indexing ~17 mil datafile records for Store.Monash was taking 3 days and required use of VM with high memory available (32GB RAM).

Script takes around 90 minutes in default pod configuration (when run in Kubernetes setup) to do the same job.

We will support MyTardis version 4.2+

### Technical details

Settings are available through default `setting.yaml` config file.

You must specify credentials to the database and location of Elasticsearch server. You can increase number of rows fetched per single bulk call.

Run from command line:

> `python index.py [--config mysetting.yaml] [--rebuild]`

`--config` will allow you to indicate location of settings file.

`--rebuild` will tell script to delete and create ES index before data population.

### Docker and Kubernetes

We build only [latest version of Docker image](https://hub.docker.com/repository/docker/mytardis/es-index) and publish on DockerHub with `mytardis/es-index:latest` image name.

Sample file `job.yaml` provide you with example of running an indexing job in Kubernetes.
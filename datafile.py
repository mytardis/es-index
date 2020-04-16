def count_from_db(cur, start_id):

    q = '''
        select count(id) as total
        from tardis_portal_datafile
        where id > %s
    '''

    cur.execute(q, [start_id])
    rows = cur.fetchall()

    return rows[0]["total"]


def data_from_db(cur, start_id, rows_bulk):

    q = '''
        select
            df.id as df_id,
            df.filename,
            df.created_time,
            df.modification_time,
            df.dataset_id,
            e.id as experiment_id,
            e.public_access,
            a."pluginId" as plugin_id,
            a."entityId" as entity_id
        from tardis_portal_datafile df
        left join tardis_portal_dataset ds
        on ds.id = df.dataset_id
        left join tardis_portal_dataset_experiments dse
        on dse.dataset_id = ds.id
        left join tardis_portal_experiment e
        on e.id = dse.experiment_id
        left join tardis_portal_objectacl a
        on a.content_type_id = 15 and a.object_id = e.id
        where df.id in (
            select id
            from tardis_portal_datafile
            where id > %s
            order by id
            limit %s
        )
    '''

    cur.execute(q, [start_id, rows_bulk])
    rows = cur.fetchall()

    data = {}
    start = start_id
    for row in rows:
        df_id = row["df_id"]
        if df_id > start:
            start = df_id
        if df_id not in data:
            data[df_id] = {
                'filename': row["filename"],
                'created_time': row["created_time"],
                'modification_time': row["modification_time"],
                'dataset': [{
                    'id': row["dataset_id"]
                }],
                'experiments': {}
            }
        experiment_id = row["experiment_id"]
        if experiment_id not in data[df_id]['experiments']:
            data[df_id]['experiments'][experiment_id] = {
                'id': row["experiment_id"],
                'public_access': row["public_access"],
                'objectacls': []
            }
        if row["plugin_id"] is not None:
            data[df_id]['experiments'][experiment_id]['objectacls'].append({
                'pluginId': row["plugin_id"],
                'entityId': row["entity_id"]
            })

    return (data, start)


def data_to_es(index_name, data):

    for df_id in data:

        doc = data[df_id]
        exp = doc["experiments"]

        doc["experiments"] = []
        for k, v in exp.items():
            doc["experiments"].append(v)

        yield {
            '_index': index_name,
            '_type': '_doc',
            '_id': df_id,
            '_source': doc
        }

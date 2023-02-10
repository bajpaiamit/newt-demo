from google.cloud import bigquery

bq_client = bigquery.Client()


def get_job_config(schema):
    return bigquery.LoadJobConfig(
        autodetect=False,
        schema=schema,
        create_disposition='CREATE_IF_NEEDED',
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1, # This should be configurable
        # allow_quoted_newlines=True,
    )


def load_table_from_df(df, bq_table_id, job_config):
    return bq_client.load_table_from_dataframe(df, bq_table_id, job_config=job_config)


def load_table_from_uri(uri, bq_table_id, job_config):
    return bq_client.load_table_from_uri(uri, bq_table_id, job_config=job_config)


def query_table(query_sql):
    query_job = bq_client.query(query_sql)
    res = query_job.result()
    return res


def create_table(bq_table, schema):
    table = bigquery.Table(bq_table, schema=schema)

    return bq_client.create_table(table)


def get_table(table_name):
    try:
        table = bq_client.get_table(table_name)

    except:
        table = None

    return table


def get_table_counts(table_id):
    sql = f"SELECT COUNT(1) as cnt from `{table_id}`"

    table = get_table(table_id)

    cnt = 0

    if table is not None:
        rows = query_table(sql)

        for row in rows:
            cnt = cnt + row['cnt']

    return cnt


def drop_table(output_project, output_dataset, output_table):

    table_id = f"{output_project}.{output_dataset}.{output_table}"
    table = get_table(table_id)
    if table is not None:
        bq_client.delete_table(table_id)

from google.cloud import logging
from util.google.bigquery import get_table_counts, query_table
from datetime import datetime


def init_logger(logger_name):
    logging_client = logging.Client()
    logger = logging_client.logger(logger_name)
    return logger


def get_metadata_query(source_table, destination_table, task):
    current_time = datetime.now()
    query = f"""
        INSERT INTO `{destination_table}`
        SELECT *,
                2844 as ParentSystemId,
                2845 as SystemId,
                '{task}' as CreateBy,
                cast("{current_time}" as TIMESTAMP) as CreateDate,
                '{task}' as CreateProcess,
                NULL as UpdateBy,
                NULL as UpdateDate,
                NULL as UpdateProcess,
                NULL as InactiveInd,
                NULL as InactiveDate,
                NULL as InactiveReason,
                '{task}' as LoadBy,
                cast("{current_time}" as TIMESTAMP) as LoadDate
        from  `{source_table}`
    """

    return query


def log_rows(project_id, dataset_id, table_id, logger):
    bq_table_id = f"{project_id}.{dataset_id}.{table_id}"
    curr_row_cnt = get_table_counts(bq_table_id)
    logger.log_text(f'Table {bq_table_id} has {str(curr_row_cnt)} rows.', severity="INFO")

    sql = f"""
    INSERT INTO `{project_id}.{dataset_id}.nexidia_row_logs`
    VALUES (CURRENT_DATETIME(), "{project_id}", "{dataset_id}", "{table_id}", {curr_row_cnt})
    """

    query_table(sql)


"""
CREATE TABLE eid-dw-dev-a5cf.EdwOdsStage.nexidia_row_logs (
log_date datetime,
project_id string,
dataset_id string,
table_id string,
row_count integer
)
"""


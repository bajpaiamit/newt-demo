
from util.google.storage import get_config
from util.google.pubsub import publish_message, get_message
from util.google.bigquery import query_table, drop_table
from util.google.datacatalog import get_info_types, get_tag_template, get_entry, apply_column_tags, parse_bq_summary
from util.google.dlp import get_dlp_job, get_dlp_job_request

from flask import Flask, request
import traceback
import time

from util.utility import init_logger

app = Flask(__name__)

task = "tag_results"
logger = init_logger(task)

CONF_KEY = task


@app.route("/", methods=["POST"])
def main():

    try:

        envelope = request.get_json()
        data = get_message(envelope)

        conf_path = data['conf_path']
        job_name = data['job_name']
        table_project = data['table_project']
        table_schema = data['table_schema']
        table_id = data['table_id']

        logger.log_text(f"Analyzing Job: {job_name}", severity="INFO")

        config = get_config(conf_path, CONF_KEY)

        project_id = config["project_id"]
        _info_types = config.get("info_types")

        next_topic = config.get("next_topic")
        tag_template = config["tag_template"]
        liklihood_vars = config['liklihood_vars']

        if not _info_types:
            _info_types = get_info_types()

        info_types = [
            {"name": info_type} for info_type in _info_types
        ]

        job_req = get_dlp_job_request(job_name)
        job = get_dlp_job(request=job_req)

        while job.state.name not in ['DONE', 'CANCELED', 'FAILED']:
            time.sleep(5)
            job = get_dlp_job(request=job_req)

        if job.state.name in ['CANCELED', 'FAILED']:
            raise f"DLP Job {job_name} failed with status {job.state.name}"

        with open('summary.sql') as d:
            temp_sql = d.read()

        action = job.inspect_details.requested_options.job_config.actions[0]
        output_project = action.save_findings.output_config.table.project_id
        output_dataset = action.save_findings.output_config.table.dataset_id
        output_table = action.save_findings.output_config.table.table_id

        fmt_sql = temp_sql.format(output_project, output_dataset, output_table, '","'.join(liklihood_vars), job_name)

        rows = query_table(fmt_sql)

        summary = parse_bq_summary(rows)

        # Create a Tag Template.
        tag_template = get_tag_template(project_id, tag_template, info_types)

        logger.log_text(f"TAG Template {tag_template}", severity="INFO")

        entry = get_entry(table_project, table_schema, table_id)

        apply_column_tags(entry, tag_template, summary)

        logger.log_text(f"Tagged Entry: {entry}", severity="INFO")

        # drop_table(output_project, output_dataset, output_table)

        if next_topic:
            data = {
                "conf_path": conf_path
            }
            publish_message(project_id, next_topic, data)

        return "Success", 200

    except Exception as e:
        err = traceback.format_exc()

        logger.log_text(f"Error {err}", severity="ERROR")
        return f"error: {str(e)} ", 200


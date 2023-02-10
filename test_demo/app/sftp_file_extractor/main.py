
from util.google.pubsub import get_message, publish_message
from util.google.storage import get_config, list_blobs, get_bucket
from util.sftp import make_sftp_connect

from datetime import datetime, timedelta
import fnmatch
from flask import Flask, request
import traceback

from util.utility import init_logger

app = Flask(__name__)

task = "sftp_file_extractor"

logger = init_logger(task)

CONF_KEY = task


@app.route("/", methods=["POST"])
def sftp_connect():

    try:
        sftp = None
        envelope = request.get_json()
        data = get_message(envelope)

        yesterday_fmt = data.get('date')
        yesterday_file_fmt = datetime.strptime(yesterday_fmt, "%Y-%m-%d") .strftime("%Y%m%d")

        if yesterday_fmt is None:
            yesterday_fmt = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
            yesterday_file_fmt = (datetime.utcnow() - timedelta(days=1)).strftime("%Y%m%d")

        conf_path = data['conf_path']
        logger.log_text(f'conf path: {str(conf_path)}')
        config = get_config(conf_path, CONF_KEY)

        sftp = make_sftp_connect(config)
        next_topic = config.get("next_topic")
        sftp_file_path = config['sftp_path']
        project_id = config["project_id"]
        output_bucket = config["output_bucket"]

        bucket = get_bucket(output_bucket)

        file_list = list_blobs(bucket, prefix=yesterday_fmt)
        processed_files = []
        for blob in file_list:
            b_name = blob.name.split("/")[-1]
            processed_files.append(b_name)

        files = []
        with sftp.open_sftp() as host:
            all_files = host.listdir(sftp_file_path)
            for file in all_files:
                if fnmatch.fnmatch(file, f"Nexidia_DEU_{yesterday_file_fmt}*.zip.asc"):
                    files.append(file)

        sftp.close()

        if next_topic:
            for file in files:
                if file not in processed_files:

                    data = {
                        "conf_path": conf_path,
                        "file": file
                    }
                    publish_message(project_id, next_topic, data)

                else:
                    # File has already been processed
                    logger.log_text(f"Skipping file: {file}")

        return "Success", 200

    except Exception as e:

        if sftp:
            sftp.close()
        err = traceback.format_exc()

        logger.log_text(f"Error {err}", severity="ERROR")
        return f"error: {str(e)} ", 200

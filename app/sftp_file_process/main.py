
from util.google.pubsub import get_message, publish_message
from util.google.storage import get_config, get_bucket
from util.sftp import make_sftp_connect

import os
from datetime import datetime, timedelta
from flask import Flask, request
import traceback
import shutil

from util.utility import init_logger

app = Flask(__name__)

task = "sftp_file_process"

logger = init_logger(task)

CONF_KEY = task


@app.route("/", methods=["POST"])
def sftp_process():

    yesterday_fmt = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    yesterday_file_fmt = (datetime.utcnow() - timedelta(days=1)).strftime("%Y%m%d")

    try:
        sftp = None
        envelope = request.get_json()
        data = get_message(envelope)

        conf_path = data['conf_path']
        file = data['file']
        logger.log_text(f'conf_path: {str(conf_path)}')
        config = get_config(conf_path, CONF_KEY)

        output_bucket = config["output_bucket"]
        next_topic = config.get("next_topic")
        sftp_file_path = config['sftp_path']
        project_id = config["project_id"]

        bucket = get_bucket(output_bucket)

        current_dir = os.getcwd()
        path = os.path.join(current_dir, str(yesterday_fmt))

        if not os.path.exists(path):
            os.mkdir(path)

        # Process the file
        logger.log_text(f"Processing file: {file}")
        file_name = os.path.basename(file)
        logger.log_text(f"file name before if: {file_name}")

        output_gcs_pathname = f"{yesterday_fmt}/{file_name}"
        output_os_path = os.path.join(current_dir, yesterday_fmt, file_name)

        sftp = make_sftp_connect(config)
        logger.log_text(f"connection successful")
        logger.log_text(f"file name: {file_name}")
        logger.log_text(f"sftp_file_path: {sftp_file_path}")
        logger.log_text(f"output_os_path: {output_os_path}")

        with sftp.open_sftp() as host:

            sftp_file_instance = host.open(f"{sftp_file_path}/{file_name}", 'r')
            with open(output_os_path, 'wb') as out_file:
                shutil.copyfileobj(sftp_file_instance, out_file)

            blob = bucket.blob(output_gcs_pathname)
            blob.upload_from_filename(output_os_path)
            os.remove(output_os_path)

        sftp.close()

        logger.log_text(f"Uploaded files to the bucket {str(bucket)}", severity="INFO")
        file_name = output_bucket + "/" + yesterday_fmt + "/" + file

        if next_topic:
            data = {
                "conf_path": conf_path,
                "file": file_name
            }
            publish_message(project_id, next_topic, data)

        return "Success", 200

    except Exception as e:

        if sftp:
            sftp.close()
        err = traceback.format_exc()

        logger.log_text(f"Final Error {err}", severity="ERROR")
        return f"error: {str(e)} ", 200

from util.google.storage import get_config, list_blobs
from util.google.pubsub import get_message, publish_message
import os
from flask import Flask, request
import subprocess
from datetime import datetime, timedelta
import traceback

from util.utility import init_logger

app = Flask(__name__)

task = "decrypt_and_extract"
logger = init_logger(task)

CONF_KEY = task

yesterday_fmt = (datetime.utcnow()-timedelta(days=1)).strftime("%Y-%m-%d")


@app.route("/", methods=["POST"])
def decrypt_and_extract():
    try:
        envelope = request.get_json()
        data = get_message(envelope)
        conf_path = data["conf_path"]
        file_process = data["file"]
        config = get_config(conf_path, CONF_KEY)
        output_bucket = config["bucket_name"]
        project_id = config["project_id"]
        secret_file_path = config["secret_key_file_path"]
        secret_version = config.get("secret_version", "latest")
        decrypt_secret_id = config["decrypt_secret_id"]
        next_topic = config.get("next_topic")

        my_env = os.environ.copy()

        my_env['BUCKET_NAME'] = output_bucket
        my_env['DECRYPT_SECRET_VERSION'] = secret_version
        my_env['SECRET_FILE_PATH'] = secret_file_path
        my_env['DECRYPT_SECRET_ID'] = decrypt_secret_id
        my_env['FILE_PROCESS'] = file_process

        proc = subprocess.run(['./decrypt_and_extract.sh'], env=my_env, shell=True)
        if proc.returncode != 0:
            logger.log_text(f"Returncode for {file_process} was {str(proc.returncode)} ", severity="ERROR")
            proc.check_returncode()

        if next_topic:
            file_folder = file_process.split("/")[-1].split(".")[0]

            blobs = list_blobs(bucket=output_bucket, prefix=f"Uncompressed_folders/{yesterday_fmt}/{file_folder}")
            for blob in blobs:
                if "csv" in blob.name:
                    data = {
                        "conf_path": conf_path,
                        "file_path": blob.name
                    }
                    publish_message(project_id, next_topic, data)
        return "Success", 200

    except Exception as e:
        err = traceback.format_exc()

        logger.log_text(f"Error {err}", severity="ERROR")
        return f"error: {str(e)} ", 200

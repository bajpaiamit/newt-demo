from util.google.pubsub import publish_message
import os


config_path = os.getenv('CONFIG_PATH')
project_id = os.getenv('PROJECT_ID')
staging_dataset = os.getenv('STAGING_DATASET')
table_name = os.getenv('TABLE_NAME')


def send_to_sftp_file_extract():
    topic_id = "sftp_file_extract"
    message = {
        "conf_path": config_path,
        "date": "2023-02-02"
    }
    publish_message(project_id, topic_id, message)


def send_to_sftp_file_process():
    topic_id = "sftp_file_process"
    message = {
        "conf_path": config_path
    }
    publish_message(project_id, topic_id, message)


def send_to_sftp():
    topic_id = "sftp_extract"
    message = {
        "conf_path": config_path
    }

    publish_message(project_id, topic_id, message)


def send_to_decrypt():
    topic_id = "decrypt_and_extract"
    message = {
        "conf_path": config_path
    }

    publish_message(project_id, topic_id, message)


def send_to_dlp():
    topic_id = "dlp_data_catalog"
    message = {
        "conf_path": config_path,
        "table_project": project_id,
        "table_schema": staging_dataset,
        "table_id": table_name
    }

    publish_message(project_id, topic_id, message)


def send_to_load_bq():
    topic_id = "gcs_to_bq"
    message = {
        "conf_path": config_path,
        "file_path": "Uncompressed_folders/2023-01-30/Nexidia_DEU_20230130_121323308/EvalsEvaluationCategory.csv"
    }

    publish_message(project_id, topic_id, message)


def send_to_tag():
    topic_id = "tag_results"
    message = {
        "conf_path": config_path,
        "job_name": "projects/eid-dw-dev-a5cf/locations/global/dlpJobs/i-3953803346615353123",
        "table_project": "eid-dw-dev-a5cf",
        "table_schema": "EdwOdsStage",
        "table_id": "Nexidia_AgentInventory"
    }

    publish_message(project_id, topic_id, message)


if __name__ == "__main__":
    # send_to_sftp()
    send_to_sftp_file_extract()
    # send_to_sftp_file_process()
    # send_to_dlp()
    # send_to_decrypt()
    # send_to_load_bq()
    # send_to_tag()


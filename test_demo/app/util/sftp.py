
import paramiko
from datetime import timedelta, datetime
from util.google.secretmanager import access_secret_version


yesterday_fmt = (datetime.utcnow()-timedelta(days=1)).strftime("%Y-%m-%d")


def make_sftp_connect(config):
    ssh_client = paramiko.SSHClient()
    project_id = config["project_id"]
    secret_id = config["secret_id"]
    version = config.get("secret_version", "latest")
    hostname = config["hostname"]
    port = config["sftp_port"]
    username = config["username"]

    creds = access_secret_version(project_id, secret_id, version)

    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname, port, username, creds, timeout=1800, compress=True)

    return ssh_client

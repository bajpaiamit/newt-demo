from google.cloud import pubsub
from util.utility import init_logger
import json
import base64

ps_client = pubsub.PublisherClient()
logger = init_logger('pubsub')


def publish_message(project_id, next_topic, data):
    topic_path = ps_client.topic_path(project_id, next_topic)
    data_str = json.dumps(data)
    # Data must be a bytestring
    data = data_str.encode("utf-8")
    # When you publish a message, the client returns a future.
    future = ps_client.publish(topic_path, data)
    future.result()


def get_message(envelope):
    if not envelope:
        msg = "no Pub/Sub message received"
        logger.log_text(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    if not isinstance(envelope, dict) or "message" not in envelope:
        msg = "invalid Pub/Sub message format"
        logger.log_text(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    pubsub_message = envelope["message"]

    if isinstance(pubsub_message, dict) and "data" in pubsub_message:
        data = json.loads(base64.b64decode(pubsub_message["data"]).decode("utf-8").strip())

    return data

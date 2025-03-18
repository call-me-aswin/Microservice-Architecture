import pika
import json
import logging
import os  # Add this import

def upload(f, fs, channel, access):
    try:
        logging.debug(f"Uploading file with filename: {f.filename}")
        fid = fs.put(f, filename=f.filename)  # Stream file directly to GridFS
        logging.debug(f"File uploaded successfully with fid: {fid}")
    except Exception as err:
        logging.error(f"Error during file upload: {err}")
        return "internal server error!", 500

    message = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": access["username"],
    }

    video_queue = os.environ.get("VIDEO_QUEUE")
    if not video_queue:
        logging.error("VIDEO_QUEUE environment variable is not set.")
        return "VIDEO_QUEUE environment variable is not set.", 500

    try:
        logging.debug(f"Publishing message to the queue '{video_queue}'")
        channel.basic_publish(
            exchange="",
            routing_key=video_queue,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
        logging.debug("Message published successfully")
    except Exception as err:
        logging.error(f"Error during message publishing: {err}")
        fs.delete(fid)
        return "internal server error", 500

    return None

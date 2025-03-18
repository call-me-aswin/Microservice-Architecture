import pika
import sys
import os
import json
from pymongo import MongoClient
import gridfs
from bson.objectid import ObjectId
from convert import to_mp3

def connect_to_mongo():
    """
    Connects to MongoDB, specifically the `video` and `mp3s` databases, and initializes GridFS.
    """
    minikube_ip = os.environ.get("MINIKUBE_IP")
    mongo_port = os.environ.get("MONGO_PORT")

    if not minikube_ip or not mongo_port:
        print("MINIKUBE_IP or MONGO_PORT environment variable is not set.")
        sys.exit(1)

    try:
        client = MongoClient(f"mongodb://root:example@{minikube_ip}:{mongo_port}/?authSource=admin")
        db_videos = client.video  # Updated to access the correct database, `video`
        db_mp3s = client.mp3s
        fs_videos = gridfs.GridFS(db_videos)
        fs_mp3s = gridfs.GridFS(db_mp3s)

        print(f"Connected to MongoDB at {minikube_ip}:{mongo_port}")
        print(f"Using database 'video' and 'mp3s'")
        return db_videos, db_mp3s, fs_videos, fs_mp3s
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        sys.exit(1)

def connect_to_rabbitmq():
    """
    Connects to RabbitMQ and initializes the channel.
    """
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
        channel = connection.channel()
        print("Connected to RabbitMQ")
        return connection, channel
    except Exception as e:
        print(f"Error connecting to RabbitMQ: {e}")
        sys.exit(1)

def main():
    """
    Main function that connects to MongoDB and RabbitMQ, and starts consuming messages from the queue.
    """
    db_videos, db_mp3s, fs_videos, fs_mp3s = connect_to_mongo()
    connection, channel = connect_to_rabbitmq()

    video_queue = os.environ.get("VIDEO_QUEUE")
    if not video_queue:
        print("VIDEO_QUEUE environment variable is not set.")
        sys.exit(1)
    channel.queue_declare(queue=video_queue, durable=True)
    print(f"Connected to RabbitMQ and declared queue '{video_queue}'")

    def callback(ch, method, properties, body):
        """
        Callback function for processing messages from the queue.
        """
        print("Received a message")
        try:
            message = json.loads(body)
            file_id = ObjectId(message.get("video_fid"))
            retries = message.get("retries", 0)
            print(f"Processing file with _id: {file_id}, attempt {retries + 1}")

            # Check if the file exists in GridFS
            if fs_videos.exists(file_id):
                print(f"File with _id {file_id} exists in GridFS")
                err = to_mp3.start(body, fs_videos, fs_mp3s, ch)
                if err:
                    print(f"Error converting file with _id {file_id}: {err}")
                    ch.basic_nack(delivery_tag=method.delivery_tag)
                else:
                    print(f"Successfully converted file with _id {file_id}")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                print(f"File with _id {file_id} does not exist in GridFS")
                ch.basic_nack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag)
        finally:
            print("Finished processing message.")

    try:
        channel.basic_consume(queue=video_queue, on_message_callback=callback)
        print("Waiting for messages. To exit press CTRL+C")
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Interrupted by user.")
    except Exception as e:
        print(f"Error during consuming: {e}")
    finally:
        connection.close()
        print("RabbitMQ connection closed.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program interrupted.")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

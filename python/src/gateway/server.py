import os, gridfs, pika, json, logging
from flask import Flask, request, send_file, jsonify
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util
from pymongo.errors import ConnectionFailure
from bson.objectid import ObjectId

# Configure logging
logging.basicConfig(level=logging.DEBUG)

server = Flask(__name__)
server.config["MONGO_URI_VIDEO"] = "mongodb://root:example@mongodb:27017/video?authSource=admin"
server.config["MONGO_URI_MP3"] = "mongodb://root:example@mongodb:27017/mp3s?authSource=admin"

logging.debug(f"Connecting to MongoDB with URIs: {server.config['MONGO_URI_VIDEO']} and {server.config['MONGO_URI_MP3']}")
mongo_video = PyMongo(server, uri=server.config["MONGO_URI_VIDEO"])
mongo_mp3 = PyMongo(server, uri=server.config["MONGO_URI_MP3"])

fs_videos = gridfs.GridFS(mongo_video.db)
fs_mp3s = gridfs.GridFS(mongo_mp3.db)

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()

# Set the VIDEO_QUEUE environment variable
os.environ["VIDEO_QUEUE"] = "video"

def check_mongo_connection():
    try:
        # Attempt to list databases to check the connection
        databases_video = mongo_video.cx.list_database_names()
        databases_mp3 = mongo_mp3.cx.list_database_names()
        logging.debug(f"Successfully connected to MongoDB. Video Databases: {databases_video}, MP3 Databases: {databases_mp3}")
    except ConnectionFailure as e:
        logging.error(f"Failed to connect to MongoDB: {e}")

# Call the function to check MongoDB connection
check_mongo_connection()

# login function
@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)

    if not err:
        return token
    else:
        return err

# uploading video to mongo db
@server.route("/upload", methods=["POST"])
def upload():
    try:
        access, err = validate.token(request)  # validating the token before uploading the video

        if err:
            logging.error(f"Token validation error: {err}")
            return err

        access = json.loads(access)

        if access["admin"]:
            if len(request.files) > 1 or len(request.files) < 1:
                return "exactly 1 file required", 400

            for _, f in request.files.items():
                err = util.upload(f, fs_videos, channel, access)

                if err:
                    logging.error(f"File upload error: {err}")
                    return err

            return "success!", 200
        else:
            return "not authorized", 401
    except Exception as e:
        logging.error(f"Error during upload: {e}")
        logging.debug(traceback.format_exc())
        return "internal server error !!!", 500

# downloading mp3 file
@server.route("/download", methods=["GET"])
def download():
    try:
        access, err = validate.token(request)

        if err:
            logging.error(f"Token validation error: {err}")
            return err

        access = json.loads(access)

        if access["admin"]:
            fid_string = request.args.get("fid")

            if not fid_string:
                return "fid is required", 400

            try:
                out = fs_mp3s.get(ObjectId(fid_string))
                return send_file(out, download_name=f"{fid_string}.mp3")
            except Exception as err:
                logging.error(f"Error during download: {err}")
                return "internal server error", 500

        return "not authorized", 401
    except Exception as e:
        logging.error(f"Error during download: {e}")
        return "internal server error !!!", 500

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)

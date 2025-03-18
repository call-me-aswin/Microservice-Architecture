import jwt, datetime, os
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from functools import wraps

app = Flask(__name__)

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'mariadb')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'auth_user')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'Auth123')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'auth')
app.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT", 3306))

mysql = MySQL(app)

def check_auth(username, password):
    print(f"Checking credentials: {username}, {password}")
    return username == 'aswinnnnn369@gmail.com' and password == 'Admin123'

def authenticate():
    return jsonify({"message": "Authentication required"}), 401

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth:
            print("No authorization header provided")
            return authenticate()
        print(f"Authorization header: {auth.username}, {auth.password}")
        if not check_auth(auth.username, auth.password):
            print("Invalid credentials")
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['POST'])
@requires_auth
def login():
    auth = request.authorization
    if not auth:
        return "missing credentials", 401

    try:
        # check db for username and password
        cur = mysql.connection.cursor()
        print(f"Executing query for username: {auth.username}")
        res = cur.execute(
            "SELECT email, password FROM user WHERE email=%s", (auth.username,)
        )
        print(f"Query executed, result: {res}")

        if res > 0:
            user_row = cur.fetchone()
            email = user_row[0]
            password = user_row[1]

            print(f"Database credentials: {email}, {password}")
            print(f"Provided credentials: {auth.username}, {auth.password}")

            if auth.username != email or auth.password != password:
                print("Invalid credentials from database")
                return "invalid credentials from db", 401
            else:
                return createJWT(auth.username, os.environ.get("JWT_SECRET"), True)
        else:
            print("No user found in database")
            return "No user found", 401
    except Exception as e:
        print(f"Error during database query: {e}")
        return f"Database query error: {e}", 500

@app.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers.get("Authorization")

    if not encoded_jwt:
        return "missing credentials", 401

    encoded_jwt = encoded_jwt.split(" ")[1]

    try:
        decoded = jwt.decode(
            encoded_jwt, os.environ.get("JWT_SECRET"), algorithms=["HS256"]
        )
    except jwt.ExpiredSignatureError:
        return "token expired", 403
    except jwt.InvalidTokenError:
        return "not authorized", 403

    return decoded, 200

def createJWT(username, secret, authz):
    return jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow(),
            "admin": authz,
        },
        secret,
        algorithm="HS256",
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
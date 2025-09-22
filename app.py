from flask import Flask, request, jsonify, Response, stream_with_context
import sqlite3, os, requests, jwt, datetime, json
from werkzeug.utils import secure_filename
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import boto3
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")

s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

jwt = JWTManager(app)
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'png','jpg','jpeg'}

app.config["UPLOAD_FOLDER"]=UPLOAD_FOLDER

def get_db():
    conn = sqlite3.connect("flaskapi.db")
    # conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row 
    return conn

users_db = get_db()
addinguser = users_db.cursor()
addinguser.execute('''CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT
);
''')
users_db.commit()
users_db.close()


# 1. Write a Flask endpoint to return all users.
# o URL: /users
# o Method: GET
@app.route('/users', methods=['GET'])
def allusers():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email FROM users")
    output = cur.fetchall()
    conn.close()
    users=[]
    for row in output:
        users.append({
        "id": row["id"],
        "username": row["name"],
        "email": row["email"],
        "message": "User created successfully"
    }), 201
    return jsonify(users), 200

# 2. Write a Flask endpoint to create a new user.
# o URL: /users
# o Method: POST
@app.route('/users', methods=['POST'])
def create_user():
    name = request.form['username']
    email = request.form['email']
    password = request.form['password']
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
                "INSERT INTO users(name, email, password) VALUES (?, ?, ?)",
                (name, email, password,)
                )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return jsonify({
        "id": user_id,
        "username": name,
        "email": email,
        "message": "User created successfully"
    }), 201


# 3. Write a Flask endpoint to update a user’s information by ID.
# o URL: /users/<int:user_id>
# o Method: PUT
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    name = data.get("username")
    # email = data.get("email")     
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET name = 'Krishna Boss' WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({
        "id": user_id,
        "username": name,
        # "email": email,
        "message": "User updated successfully"
    }), 200

# 4. Write a Flask endpoint to delete a user by ID.
# o URL: /users/<int:user_id>
# o Method: DELETE
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id): 
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({
        "message": "User deleted successfully"
    }), 200


# 5. Write a Flask endpoint that accepts query parameters to filter users by name.
# o URL: /users/search
# o Method: GET
# o Query parameter: name
@app.route('/users/search', methods=['GET'])
def search():
    name = request.args.get('name')
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE LOWER(name) LIKE LOWER(?)", (f"%{name}%",))
    output = cur.fetchall()
    conn.close()
    users = []
    for row in output:
        users.append({
            "id": row["id"],
            "username": row["name"],
            "email": row["email"]
        })

    return jsonify(users), 200

# 6. Write a Flask endpoint to return users with pagination (page and limit query parameters).
# o URL: /users/paginate
# o Method: GET
# o Query parameters: page, limit
@app.route('/users/paginate', methods=['GET'])
def pagination():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    
    offset = (page -1)*limit
    
    conn=get_db()
    cur= conn.cursor()
    cur.execute("select * from users limit ? offset ?", (limit, offset))
    rows=cur.fetchall()
    
    cur.execute("select count(*) from users")
    total_users= cur.fetchone()[0]
    
    cur.close()
    
    users=[]
    for row in rows:
        users.append({
            "id":row["id"],
            "username": row["name"],
            "email":row["email"]
        })

    return jsonify({
       "page": page,
            "limit": limit,
            "total_users": total_users,
            "total_pages": (total_users + limit - 1) // limit,  # ceiling division
            "users": users
    }), 200

# 7. Write a Flask endpoint to upload a profile picture for a user and save it locally.
# o URL: /users/<int:user_id>/upload
# o Method: POST
# o Form data: file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/users/<int:user_id>/upload', methods=['POST'])
def upload_profile_pic(user_id):
   file = request.files['file']
    
   if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
   if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
   if file and allowed_file(file.filename):
        filename = secure_filename(f"user_{user_id}_" + file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
  
        return jsonify({
            "user_id": user_id,
            "file_path": filepath,
            "message": "Profile picture uploaded successfully"
            }), 200
   
   return jsonify({"error": "File type not allowed"}), 400

# 8. Write a Flask endpoint that accepts JSON data to create a new user and validates the input.
# o URL: /users
# o Method: POST
# o JSON body: { "name": "John", "email": "john@example.com", "age": 25 }
@app.route('/users', methods=['POST'])
def json_data():
    data = request.get_json()
    name = data.get('username')
    email = data.get('email')
    password = data.get('password')
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
                "INSERT INTO users(name, email, password) VALUES (?, ?, ?)",
                (name, email, password,)
                )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return jsonify({
        "id": user_id,
        "username": name,
        "email": email,
        "password": password,
        "message": "User created successfully"
    }), 201

# 9. Write a Flask endpoint to authenticate a user using username and password.
# o URL: /login
# o Method: POST
# o JSON body: { "username": "john", "password": "secret" }
@app.route('/login', methods=['POST'])
def loginuser():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT email, password FROM users WHERE email=?", (email,))
    user = cur.fetchone()
    conn.close()
    
    message=[]
    if user:
        message.append({
            "message":"email Checked"
        })

    db_password = user

    if db_password != password:
        message.append({
            "message":"User authenticated"
        })

    return jsonify({
        "user": email,
        "messages" : message
        })

# 10. Write a Flask endpoint that returns a custom error message when a user is not found.
# o URL: /users/<int:user_id>
# o Method: GET
# o Return: 404 Not Found with message { "error": "User not found." }
@app.route('/users/<int:user_id>', methods=['GET'])
def error_message(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email FROM users WHERE id=?", (user_id,))
    output = cur.fetchone()
    conn.close()
    if not output:
        return jsonify({"error": "User not found."}), 404
    
    users = {
        "id": output[0],
        "username": output[1],
        "email": output[2]
        }
    return jsonify(users), 200

# 11. Write a Flask endpoint that integrates with an external API (e.g., GitHub) and returns combined user data.
# o URL: /external-data
# o Method: GET
@app.route('/external-data', methods=['GET'])
def externalapi():
    username = 'dishagitt'
    github = f'https://api.github.com/users/{username}'
    response = requests.get(github)
    
    if response.status_code !=200:
        return jsonify({
            "error": "Github user not found"
        }), 404
        
    github_data = response.json()
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    user = cur.fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "Local user not found"}), 404
    
    combined = {
        "id": user["id"],
        "username": user["name"],
        "email": user["email"],
        'password': user["password"],
        "github": {
            "name": github_data.get("name"),
            "repo": github_data.get("public_repos"),
            "followers": github_data.get("followers"),
            "following": github_data.get("following")
        }}
    
    return jsonify(combined), 200
    
# 12. Write a Flask endpoint that caches the response using a simple in-memory dictionary for faster access.
# o URL: /cached-users
# o Method: GET
cache = {}
@app.route('/cached-users', methods=['GET'])
def cache_response():
    if "user" in cache:
        return cache["user"]

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    conn.close()
    
    allusers=[]
    for row in users:
        allusers.append({
            "id": row["id"],
            "username": row["name"],
            "email": row["email"],
            'password': row["password"]
            })
        
    cache["user"]=allusers
    return allusers


# 13. Write a Flask endpoint that uses JWT authentication to restrict access to logged-in users.
# o URL: /protected
# o Method: GET
# o Header: Authorization: Bearer <token>
@app.route('/loginuser', methods=['POST'])
def loginuserjwt():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password') 
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, email, password FROM users WHERE email=?", (email,))
    user = cur.fetchone()
    conn.close()
    
    if not user:
        return jsonify({"error": "Invalid email"}), 401

    db_password = user[2]

    if db_password != password:
        return jsonify({"error": "Invalid password"}), 401
    
    access_token = create_access_token(identity=user[1])
    
    return jsonify({
        "message": "Login successful",
        "token": access_token
    }), 200

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    currentuser = get_jwt_identity()
    return jsonify({
        "message": "Protected Route Authorized",
        "user": currentuser
    }), 200

# 14. Write a Flask endpoint that handles file uploads and stores the files in cloud storage like AWS S3 or Google Cloud Storage.
# o URL: /files/upload
# o Method: POST
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/files/upload', methods=['POST'])
def aws():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
   
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        try:
            # Upload file to S3
            s3.upload_fileobj(
                file,
                AWS_BUCKET_NAME,
                filename,
                ExtraArgs={'ACL': 'private'}  # or 'public-read' if you want public access
            )

            file_url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{filename}"

            return jsonify({
                "file_name": filename,
                "file_url": file_url,
                "message": "File uploaded successfully to S3"
            }), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "File type not allowed"}), 400
  
# 15. Write a Flask endpoint that streams large datasets as a response using generators.
# o URL: /stream-data
# o Method: GET
def generate_json():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email FROM users")  # adjust table/columns
    try:
        for row in cur:
            yield json.dumps(dict(row)) + "\n"
    finally:
        conn.close()

@app.route('/stream-data', methods=['GET'])
def stream_data():
    return Response(
        stream_with_context(generate_json()),
        mimetype="application/x-ndjson"
    )


if __name__ == "__main__":
    app.run(debug=True)
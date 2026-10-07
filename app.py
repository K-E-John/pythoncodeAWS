from flask import Flask, render_template, request
import boto3
import pymysql
import os

app = Flask(__name__)

# -----------------------------
# Configuration
# -----------------------------

# S3 bucket name
bucket_name = os.environ.get("S3_BUCKET_NAME")

# RDS MySQL connection
db = pymysql.connect(
    host=os.environ.get("DB_HOST"),
    port=int(os.environ.get("DB_PORT", "3306")),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASSWORD"),
    database=os.environ.get("DB_NAME", "studentdb")
)


# -----------------------------
# Home page
# -----------------------------

@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# Student registration
# -----------------------------

@app.route("/register", methods=["POST"])
def register():

    name = request.form["name"]
    email = request.form["email"]
    course = request.form["course"]

    photo = request.files["photo"]

    # S3 client
    # AWS credentials are obtained from the EC2 IAM role
    s3 = boto3.client("s3")

    # Upload photo to S3
    s3.upload_fileobj(
        photo,
        bucket_name,
        photo.filename
    )

    # S3 object URL
    photo_url = (
        f"https://{bucket_name}.s3.amazonaws.com/{photo.filename}"
    )

    # Insert registration into RDS MySQL
    cursor = db.cursor()

    sql = """
        INSERT INTO students
        (name, email, course, photo_url)
        VALUES (%s, %s, %s, %s)
    """

    cursor.execute(
        sql,
        (name, email, course, photo_url)
    )

    db.commit()
    cursor.close()

    return "Student Registered Successfully"


# -----------------------------
# Local Flask testing
# -----------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )

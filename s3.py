from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

def upload_to_s3(file, bucket):
    """
    Upload a file to an S3 bucket using a fixed object name and return the public URL.

    :param file: File to upload
    :param bucket: Bucket to upload to
    :return: Public URL of the uploaded file or None if upload failed
    """
    # Use a fixed object name
    object_name = 'myusericon.jpg'
    region = os.getenv('AWS_REGION')  # Get the region from the environment

    # Create S3 client using credentials from environment variables
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),  # Fetch from environment
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),  # Fetch from environment
        region_name=region
    )
    
    try:
        # Upload the file
        s3_client.upload_fileobj(file, bucket, object_name)
        
        # Make the object public
        s3_client.put_object_acl(Bucket=bucket, Key=object_name, ACL='public-read')
        
        # Construct the public URL
        public_url = f"https://{bucket}.s3.{region}.amazonaws.com/{object_name}"
        return public_url
    except NoCredentialsError:
        return None

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    bucket_name = request.form.get('bucket_name')  # Ensure this matches the form field name
    if not bucket_name:
        return jsonify({"error": "No bucket name provided"}), 400

    file_url = upload_to_s3(file, bucket_name)

    if file_url:
        return jsonify({"message": "File uploaded successfully.", "url": file_url}), 200
    else:
        return jsonify({"error": "File upload failed"}), 500

if __name__ == '__main__':
    app.run(debug=True)

from injector import inject
from flask import Flask
import boto3
import os


class FileService:
    client = None  # @todo how to typehint this for the IDE?
    bucket: str

    @inject
    def __init__(self, app: Flask):
        self.client = boto3.client(
            's3',
            aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=app.config.get('AWS_SECRET_ACCESS_KEY')
        )
        self.bucket = app.config.get('AWS_BUCKET_NAME')

    def put(self, local_file, filename):
        print(
            "file.py:",
            "Pushing to S3:",
            os.path.abspath(local_file)
        )
        self.client.upload_file(
            local_file,
            self.bucket,
            filename,
            ExtraArgs={'ACL': 'public-read'}
        )

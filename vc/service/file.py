from injector import inject
from flask import Flask
import boto3
from botocore.client import BaseClient


class FileService:
    client: BaseClient
    bucket: str

    @inject
    def __init__(self, app: Flask):
        self.client = boto3.client(
            's3',
            aws_access_key_id=app.config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=app.config.AWS_SECRET_ACCESS_KEY
        )
        self.bucket = app.config.AWS_BUCKET_NAME

    def put(self, local_file, filename):
        self.client.upload_file(local_file, self.bucket, filename)

from datetime import datetime
from injector import inject
from flask import Flask
import boto3
import os
from vc.service.helper import DiagnosisHelper as dh


class FileService:
    URL_PATTERN = 'https://{bucket}.s3.{region}.amazonaws.com/{filename}'
    client = None  # @todo how to typehint this for the IDE?
    bucket: str
    region: str

    @inject
    def __init__(self, app: Flask):
        self.client = boto3.client(
            's3',
            aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=app.config.get('AWS_SECRET_ACCESS_KEY')
        )
        self.bucket = app.config.get('AWS_BUCKET_NAME')
        self.region = app.config.get('AWS_BUCKET_REGION')

    def put(self, local_file, filename):
        filename = self.get_filename(filename)
        url = self.URL_PATTERN.format(
            bucket=self.bucket,
            region=self.region,
            filename=filename
        )
        dh.debug("FileService", "put", os.path.abspath(local_file), url)
        self.client.upload_file(
            local_file,
            self.bucket,
            filename,
            ExtraArgs={'ACL': 'public-read'}
        )
        return url

    def get_filename(self, filename):
        now = datetime.now()
        return '%s-%s' % (
            now.strftime('%Y-%m-%d-%H-%M-%S'),
            filename
        )

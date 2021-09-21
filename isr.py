import os
<<<<<<< HEAD
from dataclasses import dataclass

import numpy as np
from ISR.models import RRDN
from PIL import Image
from injector import inject


input_dir = 'steps'
output_dir = 'steps-upscaled'
=======
from datetime import datetime

import dotenv
import boto3
import numpy as np
from ISR.models import RRDN
from PIL import Image


class FileUploader:
    def __init__(self):
        dotenv.load_dotenv()
        self.client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        self.bucket = os.getenv('AWS_BUCKET_NAME')
        self.region = os.getenv('AWS_BUCKET_REGION')

    def put(self, local_file):
        now = datetime.now()
        filename = '%s-%s' % (
            now.strftime('%Y-%m-%d-%H-%M-%S'),
            os.path.basename(local_file)
        )
        self.client.upload_file(
            local_file,
            self.bucket,
            filename,
            ExtraArgs={'ACL': 'public-read'}
        )


input_dir = 'usteps'
output_dir = 'ustepsu'
>>>>>>> d98ff10b0ce70510ca84b8694f317a44c9840030

for filename in os.listdir(input_dir):
    input_file = os.path.join(input_dir, filename)
    output_file = os.path.join(output_dir, filename)

    image = Image.open(input_file)
    image = image.convert('RGB')
    image_array = np.array(image)

    model = RRDN(weights='gans')
    result = model.predict(image_array)
    output = Image.fromarray(result)

    output.save(output_file)

<<<<<<< HEAD
=======
local_file = os.path.abspath('output-upscaled.mp4')
os.system(
    ' '.join(
        [
            'ffmpeg -y -i "%s/%%04d.png"' % output_dir,
            '-b:v 8M -c:v h264_nvenc -pix_fmt yuv420p -strict -2',
            '-filter:v "minterpolate=\'mi_mode=mci:mc_mode=aobmc:vsbmc=1:fps=60\'"',
            local_file
        ]
    )
)

uploader = FileUploader()
uploader.put(local_file)
>>>>>>> d98ff10b0ce70510ca84b8694f317a44c9840030

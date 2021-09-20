import os
from dataclasses import dataclass

import numpy as np
from ISR.models import RRDN
from PIL import Image
from injector import inject


input_dir = 'steps'
output_dir = 'steps-upscaled'

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


#!/bin/bash

python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
pip3 install Cython wheel decorator numpy
pip3 install torch==1.9.0+cu111 torchvision==0.10.0+cu111 torchaudio==0.9.0 -f https://download.pytorch.org/whl/torch_stable.html
pip3 install -r requirements.txt
git clone https://github.com/openai/CLIP
git clone https://github.com/CompVis/taming-transformers.git
mkdir checkpoints
curl -L -o checkpoints/vqgan_imagenet_f16_16384.yaml -C - 'http://mirror.io.community/blob/vqgan/vqgan_imagenet_f16_16384.yaml' #ImageNet 16384
curl -L -o checkpoints/vqgan_imagenet_f16_16384.ckpt -C - 'http://mirror.io.community/blob/vqgan/vqgan_imagenet_f16_16384.ckpt' #ImageNet 16384
inpainting/download.sh

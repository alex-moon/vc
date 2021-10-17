#!/bin/bash

if [[ ! -d "venv" ]]; then
  python3 -m venv venv
fi
source venv/bin/activate
python3 -m pip install --upgrade pip
pip3 install --no-cache-dir Cython wheel decorator numpy
pip3 install --no-cache-dir -r requirements.txt
pip3 install --no-cache-dir torch==1.9.0+cu111 torchvision==0.10.0+cu111 torchaudio==0.9.0 -f https://download.pytorch.org/whl/torch_stable.html

# VQGAN+CLIP
if [[ ! -d "CLIP" ]]; then
  git clone https://github.com/openai/CLIP
fi
if [[ ! -d "taming-transformers" ]]; then
  git clone https://github.com/CompVis/taming-transformers.git
fi

rm -rf ./taming-transformers/.git
rm -rf ./CLIP/.git

mkdir -p checkpoints

# VQGAN
file=checkpoints/vqgan_imagenet_f16_16384.yaml
if [[ ! -f "$file" ]]; then
  curl -L -o $file -C - 'http://mirror.io.community/blob/vqgan/vqgan_imagenet_f16_16384.yaml'
fi
file=checkpoints/vqgan_imagenet_f16_16384.ckpt
if [[ ! -f "$file" ]]; then
  curl -L -o $file -C - 'http://mirror.io.community/blob/vqgan/vqgan_imagenet_f16_16384.ckpt'
fi

# 3D Photo Inpainting
file=checkpoints/color-model.pth
if [[ ! -f "$file" ]]; then
  curl -L -o $file -C - https://filebox.ece.vt.edu/~jbhuang/project/3DPhoto/model/color-model.pth
fi

file=checkpoints/depth-model.pth
if [[ ! -f "$file" ]]; then
  curl -L -o $file -C - https://filebox.ece.vt.edu/~jbhuang/project/3DPhoto/model/depth-model.pth
fi

file=checkpoints/edge-model.pth
if [[ ! -f "$file" ]]; then
  curl -L -o $file -C - https://filebox.ece.vt.edu/~jbhuang/project/3DPhoto/model/edge-model.pth
fi

# MiDaS
file=checkpoints/midas.pt
if [[ ! -f "$file" ]]; then
  curl -L -o $file -C - https://github.com/intel-isl/DPT/releases/download/1_0/dpt_hybrid-midas-501f0c75.pt
fi

# ESRGAN
file=checkpoints/RealESRGAN_x4plus.pth
if [[ ! -f "$file" ]]; then
  curl -L -o $file -C - https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth
fi

# ABME
file=checkpoints/SBME_ckpt.pth
if [[ ! -f "$file" ]]; then
  curl -L -o $file -C - https://vc-ajmoon-uk.s3.eu-west-1.amazonaws.com/models/SBME_ckpt.pth
fi

file=checkpoints/ABMR_ckpt.pth
if [[ ! -f "$file" ]]; then
  curl -L -o $file -C - https://vc-ajmoon-uk.s3.eu-west-1.amazonaws.com/models/ABMR_ckpt.pth
fi

file=checkpoints/SynNet_ckpt.pth
if [[ ! -f "$file" ]]; then
  curl -L -o $file -C - https://vc-ajmoon-uk.s3.eu-west-1.amazonaws.com/models/SynNet_ckpt.pth
fi

echo "Done"

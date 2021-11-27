#!/bin/bash

if [[ ! -d "venv" ]]; then
  python3 -m venv venv
fi
source venv/bin/activate
python3 -m pip install --upgrade pip
pip3 install --no-cache-dir Cython wheel decorator numpy
pip3 install --no-cache-dir -r requirements.txt # @todo work out what's actually needed here and put in line above
pip3 install --no-cache-dir torch==1.9.0+cu111 torchvision==0.10.0+cu111 torchaudio==0.9.0 -f https://download.pytorch.org/whl/torch_stable.html
pip3 install --no-cache-dir -r requirements.txt

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
# NB: URLs have stop working recently, but there are replacements for all of these:
# @see https://www.reddit.com/r/bigsleep/comments/p96pnh/a_site_that_hosts_some_vqgan_models_isnt_working/
file=checkpoints/vqgan_imagenet_f16_16384.yaml
if [[ ! -f "$file" ]]; then
  curl -L -o $file -C - 'https://heibox.uni-heidelberg.de/d/a7530b09fed84f80a887/files/?p=%2Fconfigs%2Fmodel.yaml&dl=1'
fi
file=checkpoints/vqgan_imagenet_f16_16384.ckpt
if [[ ! -f "$file" ]]; then
  curl -L -o $file -C - 'https://heibox.uni-heidelberg.de/d/a7530b09fed84f80a887/files/?p=%2Fckpts%2Flast.ckpt&dl=1'
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
file=checkpoints/dpt_large-midas-2f21e586.pt
if [[ ! -f "$file" ]]; then
  curl -L -o $file -C - https://github.com/intel-isl/DPT/releases/download/1_0/dpt_large-midas-2f21e586.pt
fi

file=checkpoints/dpt_hybrid-midas-501f0c75.pt
if [[ ! -f "$file" ]]; then
  curl -L -o $file -C - https://github.com/intel-isl/DPT/releases/download/1_0/dpt_hybrid-midas-501f0c75.pt
fi

file=checkpoints/model-small-70d6b9c8.pt
if [[ ! -f "$file" ]]; then
  curl -L -o $file -C - https://github.com/intel-isl/MiDaS/releases/download/v2_1/model-small-70d6b9c8.pt
fi

file=checkpoints/model-f6b98070.pt
if [[ ! -f "$file" ]]; then
  curl -L -o $file -C - https://github.com/intel-isl/MiDaS/releases/download/v2_1/model-f6b98070.pt
fi

# ESRGAN
file=checkpoints/RealESRGAN_x4plus.pth
if [[ ! -f "$file" ]]; then
  curl -L -o $file -C - https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth
fi

# ABME (not used)
#file=checkpoints/SBME_ckpt.pth
#if [[ ! -f "$file" ]]; then
#  curl -L -o $file -C - https://vc-ajmoon-uk.s3.eu-west-1.amazonaws.com/models/SBME_ckpt.pth
#fi
#
#file=checkpoints/ABMR_ckpt.pth
#if [[ ! -f "$file" ]]; then
#  curl -L -o $file -C - https://vc-ajmoon-uk.s3.eu-west-1.amazonaws.com/models/ABMR_ckpt.pth
#fi
#
#file=checkpoints/SynNet_ckpt.pth
#if [[ ! -f "$file" ]]; then
#  curl -L -o $file -C - https://vc-ajmoon-uk.s3.eu-west-1.amazonaws.com/models/SynNet_ckpt.pth
#fi

# RIFE
file=checkpoints/flownet.pkl
if [[ ! -f "$file" ]]; then
  curl -L -o $file -C - https://vc-ajmoon-uk.s3.eu-west-1.amazonaws.com/models/flownet.pkl
fi

echo "Done"

#!/bin/bash

if [[ ! -d "venv" ]]; then
  python3 -m venv venv
fi
source venv/bin/activate

pip3 install --no-cache-dir Cython numpy
pip3 install --no-cache-dir torch==1.9.0+cu111 torchvision==0.10.0+cu111 torchaudio==0.9.0 -f https://download.pytorch.org/whl/torch_stable.html
pip3 install --no-cache-dir -r requirements.worker.txt

# VQGAN+CLIP
if [[ ! -d "CLIP" ]]; then
  git clone https://github.com/openai/CLIP
fi
#if [[ ! -d "taming-transformers" ]]; then
#  git clone https://github.com/CompVis/taming-transformers.git
#fi

rm -rf ./CLIP/.git
#rm -rf ./taming-transformers/.git

mkdir -p checkpoints

# VQGAN (not used)
# NB: URLs for other models can be found here:
# @see https://www.reddit.com/r/bigsleep/comments/p96pnh/a_site_that_hosts_some_vqgan_models_isnt_working/
#file=checkpoints/vqgan_imagenet_f16_16384.yaml
#if [[ ! -f "$file" ]]; then
#  curl -L -o $file -C - 'https://heibox.uni-heidelberg.de/d/a7530b09fed84f80a887/files/?p=%2Fconfigs%2Fmodel.yaml&dl=1'
#fi
#file=checkpoints/vqgan_imagenet_f16_16384.ckpt
#if [[ ! -f "$file" ]]; then
#  curl -L -o $file -C - 'https://heibox.uni-heidelberg.de/d/a7530b09fed84f80a887/files/?p=%2Fckpts%2Flast.ckpt&dl=1'
#fi

# Guided Diffusion
# @todo 512x512 (slower but higher quality...?)
#file=checkpoints/512x512_diffusion_uncond_finetune_008100.pt
#if [[ ! -f "$file" ]]; then
#  curl -OL --http1.1 -o $file 'https://the-eye.eu/public/AI/models/512x512_diffusion_unconditional_ImageNet/512x512_diffusion_uncond_finetune_008100.pt'
#fi

file=checkpoints/256x256_diffusion_uncond.pt
if [[ ! -f "$file" ]]; then
  curl -L -o $file https://openaipublic.blob.core.windows.net/diffusion/jul-2021/256x256_diffusion_uncond.pt
fi

# v1 not used
#file=checkpoints/secondary_model_imagenet.pth
#if [[ ! -f "$file" ]]; then
#  curl -L -o $file https://v-diffusion.s3.us-west-2.amazonaws.com/secondary_model_imagenet.pth
#fi

file=checkpoints/seconday_model_imagenet_2.pth
if [[ ! -f "$file" ]] ; then
  curl -L -o $file https://v-diffusion.s3.us-west-2.amazonaws.com/secondary_model_imagenet_2.pth
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

echo "Done [worker]"

FROM nvidia/cuda:11.4.0-devel-ubuntu18.04

WORKDIR /app

# @see https://pythonrepo.com/repo/nerdyrodent-VQGAN-CLIP-python-deep-learning

RUN python3 -m venv venv
RUN source venv/bin/activate

RUN pip install -r requirements.txt

RUN pip install torch==1.9.0+cu111 torchvision==0.10.0+cu111 torchaudio==0.9.0 -f https://download.pytorch.org/whl/torch_stable.html
RUN pip install ftfy regex tqdm omegaconf pytorch-lightning IPython kornia imageio imageio-ffmpeg einops

RUN git clone https://github.com/openai/CLIP
RUN git clone https://github.com/CompVis/taming-transformers.git

RUN mkdir checkpoints
RUN curl -L -o checkpoints/vqgan_imagenet_f16_16384.yaml -C - 'http://mirror.io.community/blob/vqgan/vqgan_imagenet_f16_16384.yaml' #ImageNet 16384
RUN curl -L -o checkpoints/vqgan_imagenet_f16_16384.ckpt -C - 'http://mirror.io.community/blob/vqgan/vqgan_imagenet_f16_16384.ckpt' #ImageNet 16384

CMD './local-wrapper.sh'

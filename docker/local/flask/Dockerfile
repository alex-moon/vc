# FROM pytorch/pytorch:1.9.0-cuda11.1-cudnn8-runtime
FROM ubuntu:20.04

WORKDIR /opt/vc

RUN apt update \
    && apt install -y software-properties-common \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt update

RUN apt install -y \
    python3.9 \
    python3-pip \
    python3-venv \
    git \
    wget \
    curl \
    ffmpeg \
    zip \
    redis-tools \
    supervisor \
    libsm6 \
    libxext6 \
    libxrender-dev \
    vim \
    less \
    nvidia-cuda-toolkit \
    python3-pyqt5 \
    libxcb-randr0-dev \
    libxcb-xtest0-dev \
    libxcb-xinerama0-dev \
    libxcb-shape0-dev \
    libxcb-xkb-dev

EXPOSE 5000
EXPOSE 5001

CMD './docker.flask.sh'

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
    vim \
    less \
    git \
    wget \
    curl \
    ffmpeg \
    zip \
    redis-tools

RUN pip3 install uwsgi

EXPOSE 5000

CMD './docker.flask.sh'

# VQGAN-CLIP

Forked from https://github.com/nerdyrodent/VQGAN-CLIP

## Set-up

1. Spin up the following EC2 instance a Deep Learning Base AMI (Ubuntu 18) - g4dn.xlarge - instance:
```
aws ec2 run-instances --image-id ami-0bdd0109e841ac9fc --count 1 --instance-type g4dn.xlarge --key-name MyKeyPair
```

Bear in mind this costs more than 50c an hour, i.e. £9 a day.

2. Add to ~/.ssh/config:

Host vc
    HostName 54.229.244.226
    User ubuntu
    IdentityFile path/to/your/key.pem

3. `ssh vc`
4. Set up work dir:
```
sudo mkdir /opt/vc
sudo chown ubuntu:ubuntu /opt/vc
cd /opt/vc
git clone https://github.com/alex-moon/vc.git .
sudo apt install -y python3-venv
./build.sh
```
6. Generate images:
./run.sh "view from a hill over a green valley at sunset on a warm summer evening unreal engine"


# Virtual Content

Virtual Content ("content" as in "manifest" vs "latent" "content") is a tiny JEMSCI
(job-event-manager-service-controller-injector) app, built on top of a collection of machine vision
libraries, which generates explorable dream worlds.

## Set-up

1. Spin up a `g4dn.xlarge` EC2 instance from the Deep Learning Base AMI (Ubuntu 18):
```
aws ec2 run-instances --image-id ami-0bdd0109e841ac9fc --count 1 --instance-type g4dn.xlarge --key-name MyKeyPair
```

Bear in mind this costs more than 50c an hour, i.e. £9 a day or £270 per month, as long as the
instance is running. All you need to do is stop the instance when you're not using it. It's a good
idea to [associate an Elastic IP](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/elastic-ip-addresses-eip.html)
to your instance.

2. Add to ~/.ssh/config:

Host vc
    HostName static.ip.goes.here
    User ubuntu
    IdentityFile path/to/your/key.pem

3. `ssh vc`
4. Set up work dir:
```
sudo mkdir /opt/vc
sudo chown ubuntu:ubuntu /opt/vc

echo >> ~/.bashrc
echo "cd /opt/vc" >> ~/.bashrc
echo "source venv/bin/activate" >> ~/.bashrc
echo >> ~/.bashrc

cd /opt/vc
git clone https://github.com/alex-moon/vc.git .
./build.sh
```
5. Visit https://static.ip.goes.here in your browser

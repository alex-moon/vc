# VC

VC ("virtual content") is a tiny JEMSCI app that generates explorable dream worlds. It's built on top
of the following machine vision libraries:

* VQGAN/CLIP: https://github.com/nerdyrodent/VQGAN-CLIP
* 3D Photo Inpainting: https://github.com/vt-vl-lab/3d-photo-inpainting

## Set-up

1. Spin up a `g4dn.xlarge` EC2 instance from the Deep Learning Base AMI (Ubuntu 18):
```
aws ec2 run-instances --image-id ami-0bdd0109e841ac9fc --count 1 --instance-type g4dn.xlarge --key-name MyKeyPair
```

Bear in mind this costs more than 50c an hour, i.e. £9 a day or £270 per month, as long as the
instance is running. All you need to do is stop the instance when you're not using it. It's a good
idea to [associate an Elastic IP](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/elastic-ip-addresses-eip.html)
to your instance.

2. Add your new box to `~/.ssh/config`:
```
Host vc
    HostName static.ip.goes.here
    User ubuntu
    IdentityFile path/to/your/key.pem
```
3. SSH into the box:
```
ssh vc
```
4. Set up your work dir:
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
5. This will prompt you for a database password. You can make this whatever you'd like. Whatever you
   choose, `cp .env.example .env` and then edit `.env` appropriately, e.g. if you chose
   `5up3r53cr37` as your DB password, your `.env` would look like this:
```bash
SQLALCHEMY_DATABASE_URI=postgresql://vc:5up3r53cr37@127.0.0.1:5432/vc
SQLALCHEMY_TRACK_MODIFICATIONS=False
RQ_DEFAULT_HOST=127.0.0.1
```
6. Move your nginx conf into place:
```
sudo cp nginx.unsecure.conf /etc/nginx/sites-enabled/vc.conf
sudo service nginx restart
```
6. Move your supervisor conf into place:
```
sudo cp supervisord.conf /etc/supervisor/conf.d/vc.conf
sudo service supervisor restart
```
7. Visit http://static.ip.goes.here in your browser

## SSL

It's advisable to set up SSL certificates for your server. This requires you to have DNS set up
and some familiarity with configuring nginx.

1. Set up your SSL certs:
```
sudo snap install core
sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
sudo certbot certonly --nginx
```
2. Copy the secure conf into place:
```
sudo cp nginx.conf /etc/nginx/sites-enabled/vc.conf
```
3. Modify `/etc/nginx/sites-enabled/vc.conf` to match your hostname and certificate filepaths.
4. Restart nginx:
```
sudo service nginx restart
```

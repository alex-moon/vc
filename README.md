# VC

VC ("virtual content") is a tiny JEMSCI app that generates explorable dream worlds. It's built on top
of the following machine vision libraries:

* VQGAN: https://github.com/CompVis/taming-transformers
* CLIP: https://github.com/openai/CLIP
* DPT (via MiDaS): https://github.com/isl-org/MiDaS
* 3D Photo Inpainting: https://github.com/vt-vl-lab/3d-photo-inpainting
* ESRGAN: https://github.com/xinntao/Real-ESRGAN
* RIFE: https://github.com/hzwer/arXiv2020-RIFE

## Set-up

0. A few things you're going to need to install if you haven't yet:

```bash
sudo snap install aws-cli --classic
sudo apt install jq postgresql-client redis-tools 
curl -sL https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.0/install.sh -o install_nvm.sh
bash install_nvm.sh
source ~/.bash_profile
nvm install 16.13.0 # (yes, not v17 - it has a problem with OpenSSL)
npm install -g npx
```

2. Spin up a `g4dn.xlarge` EC2 instance from the Deep Learning Base AMI (Ubuntu 18):
```
aws ec2 run-instances \
   --image-id ami-0bdd0109e841ac9fc \
   --count 1 \
   --instance-type g4dn.xlarge \
   --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=vc}]' \
   --key-name MyKeyPair
```

Bear in mind this costs more than 50c an hour, i.e. £9 a day or £270 per month, as long as the
instance is running. All you need to do is stop the instance when you're not using it. It's a good
idea to [associate an Elastic IP](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/elastic-ip-addresses-eip.html)
to your instance.

To stop/start your instance, simply:
```
make start
make stop
```

2. Create an S3 bucket for your results (the bucket name must be universally unique):
```
aws s3api create-bucket \
   --bucket unique-bucket-name \
   --region eu-west-1 \
   --create-bucket-configuration LocationConstraint=eu-west-1
```

3. Add your new box to `~/.ssh/config`:
```
Host vc
    HostName static.ip.goes.here
    User ubuntu
    IdentityFile path/to/your/key.pem
```

4. SSH into the box:
```
ssh vc
```

5. Set up your work dir:
```
sudo mkdir /opt/vc
sudo chown ubuntu:ubuntu /opt/vc

echo >> ~/.bashrc
echo "cd /opt/vc" >> ~/.bashrc
echo "source venv/bin/activate" >> ~/.bashrc
echo "export FLASK_APP=vc.app:app" >> ~/.bashrc
echo >> ~/.bashrc

cd /opt/vc
git clone https://github.com/alex-moon/vc.git .
./build.sh
```

6. This will prompt you for a database password. You can make this whatever you'd like. Whatever you
   choose, `cp .env.example .env` and then edit `.env` appropriately, e.g. if you chose
   `5up3r53cr37` as your DB password, the relevant line in your `.env` would look like this:
```bash
SQLALCHEMY_DATABASE_URI=postgresql://vc:5up3r53cr37@127.0.0.1:5432/vc
```

7. Don't forget to update the rest of your `.env` appropriately with your AWS credentials and unique
   bucket name.

7. Move your nginx conf into place:
```
sudo cp nginx.unsecure.conf /etc/nginx/sites-enabled/vc.conf
sudo service nginx restart
```

8. Move your supervisor conf into place:
```
sudo cp supervisor.api.conf /etc/supervisor/conf.d/vc.api.conf
sudo cp supervisor.worker.conf /etc/supervisor/conf.d/vc.worker.conf # if you want to run the worker
sudo service supervisor restart
```

9. Visit http://static.ip.goes.here in your browser

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
This should be as straightforward as replacing `vc.ajmoon.uk` with your domain name.

4. Restart nginx:
```
sudo service nginx restart
```

### Local development

If you want to work on the front-end locally, simply install node:
```
brew update
brew install node
npm install
```

And then run webpack:
```
make serve
```

And visit http://localhost:8000/ in your browser.

The typescript file that interacts with the API is `app/ts/manager.ts` - you'll
notice a variable `useDummyData` defined at the top. If this is `false`, you'll need use
a local proxy. To do so, simply replace `vc.ajmoon.uk` with your own domain name (as above)
in `webpack.config.js` in the project root.

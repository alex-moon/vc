FROM nginx:latest

RUN apt-get -y update
RUN apt-get -y install vim less curl gnupg apt-transport-https

COPY docker/local/nginx/conf/flask.conf /etc/nginx/nginx.conf
COPY docker/local/nginx/ssl/vc.local.crt /etc/ssl/vc.local.crt
COPY docker/local/nginx/ssl/vc.local.key /etc/ssl/vc.local.key

EXPOSE 80
EXPOSE 443

WORKDIR /etc/nginx

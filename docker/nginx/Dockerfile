FROM nginx:latest

RUN apt-get -y update
RUN apt-get -y install vim less curl gnupg apt-transport-https

COPY docker/nginx/conf/flask.conf /etc/nginx/nginx.conf

EXPOSE 80
EXPOSE 443

WORKDIR /etc/nginx

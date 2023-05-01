FROM nginx:latest

RUN apt-get -y update
RUN apt-get -y install vim less curl gnupg apt-transport-https

RUN curl https://raw.githubusercontent.com/nginx/nginx/master/conf/uwsgi_params -o /etc/nginx/uwsgi_params
COPY docker/nginx/conf/flask.conf /etc/nginx/nginx.conf

EXPOSE 80
EXPOSE 443

WORKDIR /etc/nginx

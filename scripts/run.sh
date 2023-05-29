#!/bin/bash

red="$(tput setaf 1)"
green="$(tput setaf 2)"
yellow="$(tput setaf 3)"
reset="$(tput sgr0)"
function red() { echo "${red}${@}${reset}"; }
function green() { echo "${green}${@}${reset}"; }
function yellow() { echo "${yellow}${@}${reset}"; }

service=$1
if [[ -z "$service" ]]; then
    service=flask
fi

green "Stopping docker containers"
docker-compose down

green "Starting docker containers"
docker-compose up -d

green "Obtaining shell for $service"
docker-compose exec $service bash -i

green "Your containers are still running"
echo "Do task sh to obtain another shell"
echo "Do task run to restart containers"

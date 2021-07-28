#!/bin/bash

# helper functions
function confirm() {
    while true; do
        read -p "[Y/n] " YESNO
        case "$YESNO" in
            [Yy]*|"" ) return 0;;
            [Nn]* ) return 1;;
            * ) printf "Try again hotshot. " ;;
        esac
    done
}

red="$(tput setaf 1)"
green="$(tput setaf 2)"
yellow="$(tput setaf 3)"
reset="$(tput sgr0)"
function red() { echo "${red}${@}${reset}"; }
function green() { echo "${green}${@}${reset}"; }
function yellow() { echo "${yellow}${@}${reset}"; }

# vars
machine=pcc

if [[ "$(docker-machine status $machine)" != "Running" ]]; then
    green "Starting docker machine"
    docker-machine start $machine
fi

eval $(docker-machine env $machine)

laravel_ip=$(grep laravel.local /etc/hosts | grep -o "[0-9.]*")
if [[ ! -z "$laravel_ip" ]]; then
    sed -i '' "s/laravel.local:[0-9.]*/laravel.local:$laravel_ip/g" docker-compose.yml
fi

green "Stopping docker containers"
docker-compose down

green "Starting docker containers"
docker-compose up -d

green "Obtaining shell"
docker-compose exec flask bash -l

green "Your containers are still running"
echo "Do make sh to obtain another shell"
echo "Do make run to restart containers"

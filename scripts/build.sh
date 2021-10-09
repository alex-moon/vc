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
machine=vc

echo "First let's get your root login cached..."
sudo echo "Done"

# let's do it!
if [[ -z "$(docker-machine ls -q | grep $machine)" ]]; then
    green "Creating docker machine"
    docker-machine create --driver virtualbox --virtualbox-memory 2048 $machine
fi

if [[ "$(docker-machine status $machine)" = "Error" ]]; then
    green "Rebuilding docker machine"
    docker-machine rm -f $machine
    docker-machine start $machine
fi

if [[ "$(docker-machine status $machine)" != "Running" ]]; then
    green "Starting docker machine"
    docker-machine start $machine
fi

# green "Regenerating certs"
yes | docker-machine regenerate-certs $machine

green "Mounting NFS"
docker-machine-nfs $machine -s=`pwd`

green "Loading env"
eval $(docker-machine env $machine)

green "Removing docker containers"
docker rm -f $(docker ps -a -q)

ip=$(docker-machine ip $machine)
green "Done - your IP is $ip - auto-adding to /etc/hosts..."
sudo sed -i '' '/vc.local/d' /etc/hosts
echo "$ip vc.local" | sudo tee -a /etc/hosts

docker-compose build vc

green Done

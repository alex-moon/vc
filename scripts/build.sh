#!/bin/bash

red="$(tput setaf 1)"
green="$(tput setaf 2)"
yellow="$(tput setaf 3)"
reset="$(tput sgr0)"
function red() { echo "${red}${@}${reset}"; }
function green() { echo "${green}${@}${reset}"; }
function yellow() { echo "${yellow}${@}${reset}"; }

green "Building images"
docker-compose build

green Done

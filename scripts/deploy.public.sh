#!/bin/bash

npx webpack build --node-env=public
rsync -av --delete public/ vos:/opt/vc/public/

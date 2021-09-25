start:
	scripts/aws.start.sh

stop:
	scripts/aws.stop.sh

build:
	npx webpack --node-env=local

serve: build
	npx webpack serve --node-env=local

deploy:
	scripts/deploy.sh

db:
	ssh -t vc "/opt/vc/db.sh"

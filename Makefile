start:
	scripts/aws.start.sh

stop:
	scripts/aws.stop.sh

build:
	npx webpack

serve: build
	npx webpack serve

deploy:
	scripts/deploy.sh

db:
	ssh -t vc "/opt/vc/db.sh"

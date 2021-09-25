start:
	scripts/aws.start.sh

stop:
	scripts/aws.stop.sh

build:
	npx webpack --node-env=local

serve: build
	npx webpack serve --node-env=local

deploy.private:
	scripts/deploy.private.sh

deploy.public:
	scripts/deploy.public.sh

deploy: deploy.private deploy.public

db:
	ssh -t vc "/opt/vc/db.sh"

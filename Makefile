start:
	scripts/aws.start.sh

stop:
	scripts/aws.stop.sh

build:
	npx webpack --node-env=local

serve: build
	npx webpack serve --node-env=local

deploy.backend:
	scripts/deploy.backend.sh

deploy.frontend:
	scripts/deploy.frontend.sh

deploy.public:
	scripts/deploy.public.sh

deploy: deploy.private deploy.public

db:
	ssh -t vc "/opt/vc/db.sh"

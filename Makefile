start:
	scripts/aws.start.sh

stop:
	scripts/aws.stop.sh

sh:
	scripts/sh.sh

build:
	-scripts/build.sh

run:
	scripts/run.sh

webpack:
	npx webpack --node-env=local

serve: webpack
	npx webpack serve --node-env=local

deploy.backend:
	scripts/deploy.backend.sh

deploy.frontend:
	scripts/deploy.frontend.sh

deploy.private: deploy.backend deploy.frontend

deploy.public:
	scripts/deploy.public.sh

deploy: deploy.private deploy.public

db:
	scripts/db.sh

dump:
	scripts/dump.sh

restore:
	scripts/db.sh < backup.sql

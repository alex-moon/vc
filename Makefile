start:
	scripts/aws.start.sh

stop:
	scripts/aws.stop.sh

serve:
	npx webpack && npx webpack serve

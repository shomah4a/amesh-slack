.PHONY: clean amesh

SIGNING_SECRET=$(shell cat slack_signing_secret)

python/bin/python3:
	python3 -m venv python

setup: python/bin/python3
	python/bin/pip3 install -r requirements.txt

amesh:
	python/bin/python3 amesh.py

package.zip: clean
	-mkdir dist
	cp amesh.py slackhandler.py dist
	cp -r python/lib/python*/site-packages/* dist
	cd dist && zip -r ../package.zip ./*

clean:
	-rm -rf dist

deploy: package.zip
	sam deploy --template-file sam-template.yml \
		--stack-name slack-command-stack \
		--capabilities CAPABILITY_IAM \
		--resolve-s3 \
		--parameter-overrides SlackSigningSecret=$(SIGNING_SECRET)

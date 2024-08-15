.PHONY: clean amesh

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
	cd dist && zip ../package.zip ./*

clean:
	-rm -rf dist

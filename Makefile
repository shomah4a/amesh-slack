python/bin/python3:
	python3 -m venv python

setup: python/bin/python3
	python/bin/pip3 install -r requirements.txt

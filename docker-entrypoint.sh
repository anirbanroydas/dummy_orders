#!/bin/sh
set -e

if [ "$ENV" = "DEV" ]; then
	echo "Running Development Application"
	pip install --no-deps -e .
	exec python orders/server.py

elif [ "$ENV" = "UNIT_TEST" ]; then
	echo "Running Unit Tests"
	pip install --no-deps -e .
	exec pytest -v -s --cov=./orders tests/unit 
	# exec tox -e unit

elif [ "$ENV" = "PROD" ]; then 
	echo "Running Production Application"
	pip install --no-deps .
	exec python orders/server.py

else
	echo "Please provide an environment"
	echo "Stopping"
fi

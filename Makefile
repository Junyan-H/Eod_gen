.PHONY: help setup dev prod build clean test

help:
	@echo "EOD Generator - Available Commands"
	@echo "=================================="
	@echo "setup     - Install dependencies and setup project"
	@echo "dev       - Start development server"
	@echo "prod      - Start production server"
	@echo "build     - Build TypeScript and prepare for production"
	@echo "clean     - Clean generated files"
	@echo "test      - Run application in test mode"
	@echo "cli       - Run original CLI version"

setup:
	python3 scripts/setup.py

dev:
	python3 scripts/dev.py

prod:
	@echo "Make sure to set SECRET_KEY environment variable:"
	@echo "export SECRET_KEY='your-secure-random-key'"
	@echo ""
	python3 scripts/prod.py

build:
	cd config && npm run build:prod

clean:
	cd config && npm run clean:all
	rm -rf __pycache__ src/__pycache__ config/__pycache__
	find . -name "*.pyc" -delete
	find . -name ".DS_Store" -delete

test:
	FLASK_ENV=testing python3 src/run_flask.py

cli:
	python3 src/app.py

install:
	pip install -r requirements.txt
	cd config && npm install
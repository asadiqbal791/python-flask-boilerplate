.PHONY: install dev test lint docker-dev docker-prod migrate seed

install:
	pip install -r requirements.txt

dev:
	FLASK_ENV=development python run.py

test:
	pytest

test-cov:
	pytest --cov=app --cov-report=html

lint:
	flake8 app tests --max-line-length 100
	black --check app tests

format:
	black app tests
	isort app tests

migrate-init:
	flask db init

migrate:
	flask db migrate -m "$(msg)"

upgrade:
	flask db upgrade

downgrade:
	flask db downgrade

docker-dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

docker-prod:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d

docker-down:
	docker-compose down -v

shell:
	FLASK_ENV=development flask shell

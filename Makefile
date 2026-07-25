.PHONY: install run test lint format-check type-check verify docker-up docker-down

install:
	python -m pip install -e ".[dev]"

run:
	uvicorn enterprise_ai_api.main:app --app-dir apps/api/src --reload

test:
	pytest --cov --cov-report=term-missing

lint:
	ruff check .

format-check:
	ruff format --check .

type-check:
	mypy

verify:
	./scripts/verify.sh

docker-up:
	docker compose up --build

docker-down:
	docker compose down

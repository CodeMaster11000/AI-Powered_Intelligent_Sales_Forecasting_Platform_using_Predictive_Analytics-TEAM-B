.PHONY: up build down logs test migrate

up:
	docker compose up -d --build

build:
	docker compose build

down:
	docker compose down

logs:
	docker compose logs -f backend frontend

migrate:
	docker compose run --rm backend alembic upgrade head

test:
	pytest -q

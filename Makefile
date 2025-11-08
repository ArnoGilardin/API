.PHONY: help build up down restart logs test clean init-db

help:
	@echo "B2B Lead Generation API - Make Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make build      - Build Docker images"
	@echo "  make up         - Start all services"
	@echo "  make down       - Stop all services"
	@echo "  make restart    - Restart all services"
	@echo "  make logs       - Show logs"
	@echo "  make test       - Run tests"
	@echo "  make init-db    - Initialize database"
	@echo "  make clean      - Clean up containers and volumes"
	@echo "  make shell      - Open shell in API container"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "API: http://localhost:8000"
	@echo "Docs: http://localhost:8000/docs"
	@echo "Flower: http://localhost:5555"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

logs-api:
	docker-compose logs -f api

logs-worker:
	docker-compose logs -f celery_worker

test:
	docker-compose exec api pytest -v

test-coverage:
	docker-compose exec api pytest --cov=app --cov-report=html

init-db:
	docker-compose exec api python -m app.utils.init_db

clean:
	docker-compose down -v
	docker system prune -f

shell:
	docker-compose exec api bash

db-shell:
	docker-compose exec db psql -U leadgen -d leadgen_db

migrate:
	docker-compose exec api alembic upgrade head

migrate-create:
	@read -p "Enter migration message: " msg; \
	docker-compose exec api alembic revision --autogenerate -m "$$msg"

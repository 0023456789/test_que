.PHONY: up down build logs shell migrate seed clean test health

# ── Lifecycle ─────────────────────────────────────────────────────────────────
up:
	docker compose up -d

build:
	docker compose up --build -d

down:
	docker compose down

clean:
	docker compose down -v --remove-orphans

restart-%:
	docker compose restart $*

rebuild-%:
	docker compose up --build -d $*

# ── Logs ──────────────────────────────────────────────────────────────────────
logs:
	docker compose logs -f

logs-%:
	docker compose logs -f $*

# ── Shell Access ──────────────────────────────────────────────────────────────
shell-%:
	docker compose exec $* bash

# ── Migrations ────────────────────────────────────────────────────────────────
migrate:
	@for svc in auth-service customer-service staff-service manager-service \
	            catalog-service book-service cart-service order-service \
	            ship-service pay-service comment-rate-service recommender-ai-service; do \
	  echo "==> Migrating $$svc..."; \
	  docker compose exec $$svc python manage.py migrate --noinput; \
	done

migrate-%:
	docker compose exec $* python manage.py migrate --noinput

# ── Health Check ──────────────────────────────────────────────────────────────
health:
	@echo "Checking all service health..."
	@curl -s http://localhost:8000/gateway/health/ | python3 -m json.tool

# ── Seed Data ─────────────────────────────────────────────────────────────────
seed:
	@echo "Creating admin user..."
	@curl -s -X POST http://localhost:8000/api/auth/register/ \
	  -H "Content-Type: application/json" \
	  -d '{"email":"admin@bookstore.com","username":"admin","first_name":"Admin","last_name":"User","password":"Admin123!","password_confirm":"Admin123!","role":"admin"}' \
	  | python3 -m json.tool
	@echo "\nCreating staff user..."
	@curl -s -X POST http://localhost:8000/api/auth/register/ \
	  -H "Content-Type: application/json" \
	  -d '{"email":"staff@bookstore.com","username":"staff1","first_name":"Staff","last_name":"Member","password":"Staff123!","password_confirm":"Staff123!","role":"staff"}' \
	  | python3 -m json.tool
	@echo "\nCreating customer..."
	@curl -s -X POST http://localhost:8000/api/auth/register/ \
	  -H "Content-Type: application/json" \
	  -d '{"email":"customer@example.com","username":"alice","first_name":"Alice","last_name":"Smith","password":"Alice123!","password_confirm":"Alice123!","role":"customer"}' \
	  | python3 -m json.tool

# ── Testing ───────────────────────────────────────────────────────────────────
test-auth:
	@echo "=== Testing Auth Service ==="
	@curl -s http://localhost:8000/health/ | python3 -m json.tool

test-flow:
	@echo "=== Full Customer Flow Test ==="
	@bash scripts/test_flow.sh

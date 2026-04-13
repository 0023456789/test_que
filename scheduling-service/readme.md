# scheduling-service

## Purpose
Owns investor availability templates and pitch slot status transitions.

## Base Paths
- /api/... and /... fallback

## Endpoints
### Availability Templates
- GET /api/availability-templates/
- POST /api/availability-templates/
- GET /api/availability-templates/{id}/
- PUT/PATCH /api/availability-templates/{id}/
- DELETE /api/availability-templates/{id}/
- GET /api/availability-templates/by_investor/?investor_id=<id>

### Pitch Slots
- GET /api/pitch-slots/
- POST /api/pitch-slots/
- GET /api/pitch-slots/{id}/
- PUT/PATCH /api/pitch-slots/{id}/
- DELETE /api/pitch-slots/{id}/
- PATCH /api/pitch-slots/{id}/update_status/
- GET /api/pitch-slots/stats/

### Health
- GET /api/health/

## Reliability Notes
- Idempotency middleware is enabled for write endpoints (Idempotency-Key).
- Outbox events are emitted for template/slot CRUD and slot status updates.
- Saga/correlation/idempotency metadata is propagated into outbox payload.

## Operations
- python manage.py migrate
- python manage.py runserver
- python manage.py run_outbox_processor
- python manage.py run_kafka_consumer

## Circuit Breaker Strategy
- Circuit breaker is implemented at caller side (BFF) for synchronous cross-service HTTP.

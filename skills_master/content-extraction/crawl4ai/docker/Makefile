# Crawl4AI Docker Makefile
# Usage: make <target>

.PHONY: build run stop logs clean prod gpu test

# Build the image
build:
	docker build -t crawl4ai:latest -f Dockerfile .

# Build GPU image
gpu: Dockerfile.gpu
	docker build -t crawl4ai:gpu -f Dockerfile.gpu .

# Start development environment
run:
	docker-compose up -d

# Start production environment
prod:
	docker-compose -f docker-compose.prod.yml up -d

# Start GPU environment
gpu-run:
	docker-compose -f docker-compose.gpu.yml up -d

# Stop all services
stop:
	docker-compose down
	docker-compose -f docker-compose.prod.yml down
	docker-compose -f docker-compose.gpu.yml down

# View logs
logs:
	docker-compose logs -f crawl4ai

# View all logs
all-logs:
	docker-compose logs -f
	docker-compose -f docker-compose.prod.yml logs -f

# Clean up
clean:
	docker-compose down -v
	docker-compose -f docker-compose.prod.yml down -v
	docker-compose -f docker-compose.gpu.yml down -v
	docker system prune -f

# Full rebuild
rebuild: clean build

# Run tests in container
test:
	docker run --rm crawl4ai:latest python -m pytest /app/tests/ -v

# Enter container shell
shell:
	docker exec -it crawl4ai-app /bin/bash

# View container status
status:
	docker-compose ps
	docker-compose -f docker-compose.prod.yml ps

# Health check
health:
	curl -s http://localhost:8000/health | jq .

# Prometheus targets
monitoring:
	@echo "Prometheus: http://localhost:9090/targets"
	@echo "Grafana: http://localhost:3000 (admin/admin)"
	@echo "Alertmanager: http://localhost:9093"

# Show help
help:
	@echo "Crawl4AI Docker Commands:"
	@echo ""
	@echo "  make build      - Build the Docker image"
	@echo "  make run        - Start development environment"
	@echo "  make prod       - Start production environment"
	@echo "  make gpu        - Build GPU image"
	@echo "  make gpu-run    - Start GPU environment"
	@echo "  make stop       - Stop all services"
	@echo "  make logs       - View crawler logs"
	@echo "  make clean      - Clean up containers and volumes"
	@echo "  make test       - Run tests in container"
	@echo "  make shell      - Enter container shell"
	@echo "  make health     - Check service health"
	@echo "  make monitoring - Show monitoring URLs"
	@echo "  make help       - Show this help"

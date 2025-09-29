.PHONY: help dev dev-info build run test install setup migrate clean frontend backend tree start

# Single source of truth for backend address (override with: HOST=0.0.0.0 PORT=8001 make run)
HOST ?= 127.0.0.1
PORT ?= 8001
ADDRESS := $(HOST):$(PORT)

help:
	@echo "Available commands:"
	@echo "  make setup      - Initial project setup (install dependencies, migrations)"
	@echo "  make install    - Install Python and Node.js dependencies"
	@echo "  make dev        - Start both frontend and backend development servers"
	@echo "  make dev-info   - Show development server commands (manual setup)"
	@echo "  make frontend   - Start frontend development server only"
	@echo "  make backend    - Start backend development server only"
	@echo "  make run        - Run Django development server (backend only)"
	@echo "      (override address: HOST=0.0.0.0 PORT=9000 make run)"
	@echo "  make start      - Build frontend, collect static, run Django (full project)"
	@echo "  make check-vite - Check Vite dev server availability"
	@echo "  make build      - Build frontend and collect static files"
	@echo "  make migrate    - Run Django migrations"
	@echo "  make test       - Run Django tests"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make tree       - Generate pretty repository tree structure"

setup: install migrate
	@echo "✅ Project setup complete!"
	@echo "Now run: make dev"

install:
	@echo "📦 Creating virtual environment (.venv) with uv..."
	uv venv .venv
	@echo "📦 Installing Python dependencies into .venv (uv) from requirements.txt..."
	uv pip install --python .venv/bin/python -r requirements.txt
	@echo "📦 Installing Python dev dependencies into .venv (uv) from requirements-dev.txt..."
	uv pip install --python .venv/bin/python -r requirements-dev.txt || true
	@echo "📦 Installing Node.js dependencies..."
	npm install --prefix apps/frontend
	@echo "✅ Dependencies installed!"

dev:
	@echo "🚀 Starting development servers..."
	@echo "Frontend: http://localhost:5173 (or next available port)"
	@echo "Backend:  http://$(ADDRESS)"
	@echo "Press Ctrl+C to stop both servers"
	@echo ""
	@make -j2 frontend backend

dev-info:
	@echo "🚀 To start development servers manually:"
	@echo ""
	@echo "Terminal 1 (Frontend):"
	@echo "  cd apps/frontend && npm run dev"
	@echo ""
	@echo "Terminal 2 (Backend):"
	@echo "  source .venv/bin/activate && cd apps/backend && python manage.py runserver $(ADDRESS)"
	@echo ""
	@echo "Frontend: http://localhost:5173 (or next available port)"
	@echo "Backend:  http://$(ADDRESS)"

frontend:
	@echo "🎨 Starting frontend development server..."
	cd apps/frontend && npm run dev

backend:
	@echo "⚙️ Starting backend development server..."
	source .venv/bin/activate && cd apps/backend && python manage.py runserver $(ADDRESS)

build:
	@echo "🏗️  Building frontend..."
	npm --prefix apps/frontend run build
	@echo "📋 Collecting static files..."
	source .venv/bin/activate && cd apps/backend && python manage.py collectstatic --noinput
	@echo "✅ Build complete!"

run:
	@echo "🚀 Starting Django development server..."
	source .venv/bin/activate && cd apps/backend && python manage.py runserver $(ADDRESS)

start: build
	@echo "🚀 Starting full project (prod-like preview) on http://$(ADDRESS)"
	source .venv/bin/activate && cd apps/backend && DJANGO_SETTINGS_MODULE=config.settings.prod python manage.py runserver $(ADDRESS)

migrate:
	@echo "🗃️  Running Django migrations..."
	source .venv/bin/activate && cd apps/backend && python manage.py migrate
	@echo "✅ Migrations complete!"

test:
	@echo "🧪 Running Django tests..."
	source .venv/bin/activate && cd apps/backend && python manage.py test -v 2

lint:
	@echo "🧹 Linting Python (ruff) and Frontend (eslint)..."
	@echo "Python:"
	ruff check .
	@echo "Frontend:"
	cd apps/frontend && npm run lint --silent || true

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf apps/frontend/dist/
	rm -rf apps/backend/staticfiles/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	@echo "✅ Clean complete!"

tree:
	@echo "🌳 Generating repository tree structure..."
	python scripts/tree.py --simple
	@echo ""
	@echo "💾 To save to file: python scripts/tree.py --simple -o TREE.md"

check-vite:
	@echo "🔎 Checking Vite dev server..."
	python apps/backend/manage.py check_vite || true

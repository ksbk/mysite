# 🚀 MySite - Full-Stack Django + TypeScript Website

[![CI](https://github.com/ksbk/mysite/actions/workflows/ci.yml/badge.svg)](https://github.com/ksbk/mysite/actions/workflows/ci.yml)
[![Quality Check](https://github.com/ksbk/mysite/actions/workflows/quality-check.yml/badge.svg)](https://github.com/ksbk/mysite/actions/workflows/quality-check.yml)
[![Deploy](https://github.com/ksbk/mysite/actions/workflows/deploy.yml/badge.svg)](https://github.com/ksbk/mysite/actions/workflows/deploy.yml)

A modern, production-ready web application built with Django backend and TypeScript frontend, featuring comprehensive testing, modern build pipeline, and clean architecture.

## ✨ Features

- **🏗️ Full-Stack Architecture**: Django 5.2.6 backend with TypeScript frontend
- **📧 Contact Form**: Complete AJAX-enabled contact system with validation
- **🧪 Comprehensive Testing**: 35 tests (17 Django + 18 TypeScript) with 100% pass rate
- **⚡ Modern Build Pipeline**: Vite integration with Django static files
- **🎯 Type Safety**: Full TypeScript coverage with proper validation
- **📱 Responsive Design**: Mobile-first approach with clean UI
- **🔧 Developer Experience**: Hot reload, comprehensive tooling, unified commands

## 🏃‍♂️ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- uv (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ksbk/mysite.git
   cd mysite
   ```

2. **Set up Python environment**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r pyproject.toml
   ```

3. **Install frontend dependencies**
   ```bash
   cd apps/frontend
   npm install
   cd ../..
   ```

4. **Set up database**
   ```bash
   make migrate
   ```

5. **Start development servers**
   ```bash
   make dev  # Starts both backend and frontend servers
   ```

Visit:
- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8000

## 🧪 Testing

Run the complete test suite:
```bash
make test        # Run all tests (Django + TypeScript)
make test-backend    # Django tests only
make test-frontend   # TypeScript tests only
```

**Test Coverage:**
- **Django**: 17 tests covering models, forms, views, API endpoints, integration
- **TypeScript**: 18 tests covering validation, DOM interaction, edge cases

## 🏗️ Project Structure

```
mysite/
├── apps/
│   ├── backend/           # Django application
│   │   ├── apps/
│   │   │   ├── contact/   # Contact form app
│   │   │   ├── core/      # Core functionality
│   │   │   ├── blog/      # Blog (coming soon)
│   │   │   └── projects/  # Projects showcase (coming soon)
│   │   ├── config/        # Django settings
│   │   └── templates/     # Django templates
│   └── frontend/          # TypeScript/Vite frontend
│       ├── src/
│       │   ├── components/    # TypeScript components
│       │   └── test/         # Frontend tests
│       └── package.json
├── Makefile              # Development commands
└── pyproject.toml       # Python dependencies
```

## 🛠️ Available Commands

| Command | Description |
|---------|-------------|
| `make dev` | Start both backend and frontend development servers |
| `make backend` | Start Django server only |
| `make frontend` | Start Vite dev server only |
| `make test` | Run all tests (Django + TypeScript) |
| `make build` | Build frontend assets and collect static files |
| `make migrate` | Run Django database migrations |
| `make shell` | Open Django shell |

## � Contact Form

The application includes a fully-featured contact form with:

- **Real-time validation** (TypeScript frontend)
- **Server-side validation** (Django backend)
- **AJAX submission** with fallback to traditional form
- **Comprehensive error handling**
- **Admin interface** for message management

## 🔧 Development

### Backend (Django)
- **Framework**: Django 5.2.6
- **Database**: SQLite (development), PostgreSQL-ready for production
- **Admin**: Django admin interface at `/admin/`
- **API**: RESTful endpoints for frontend integration

### Frontend (TypeScript)
- **Build Tool**: Vite for fast development and optimized builds
- **Language**: TypeScript for type safety
- **Testing**: Vitest with jsdom for DOM testing
- **Styling**: CSS with modern features

### Code Quality
- **Testing**: Comprehensive test suites for both backend and frontend
- **Type Safety**: Full TypeScript coverage
- **Static Analysis**: Pre-commit hooks with security scanning
- **Clean Architecture**: Separation of concerns with proper app structure

## 🚀 Production Deployment

The application is production-ready with:

- **Static file optimization** via Vite build pipeline
- **Environment-specific settings** (dev/staging/prod)
- **Security best practices** implemented
- **Scalable architecture** with proper app separation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## � License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎯 Roadmap

- [ ] **Blog Interface**: Complete blog system with admin
- [ ] **Projects Showcase**: Portfolio gallery with image uploads
- [ ] **User Authentication**: Login/signup system
- [ ] **Interactive Dashboard**: Admin dashboard with metrics
- [ ] **API Documentation**: OpenAPI/Swagger integration
- [ ] **Docker Support**: Containerized deployment

---

**Built with ❤️ using Django + TypeScript**

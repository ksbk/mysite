# MySite

A Django + Vite web application with a modern full-stack architecture.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### Setup

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd mysite
   ```

2. **Set up Python environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your specific values
   ```

4. **Set up the database**

   ```bash
   cd apps/backend
   python manage.py migrate
   python manage.py createsuperuser  # Optional: create admin user
   ```

5. **Set up frontend dependencies**

   ```bash
   cd apps/frontend
   npm install
   ```

## 🛠️ Development

### Running the Development Server

You have two options:

### Option C: Using Docker Compose

If you prefer containers, a dev compose is included to run both Django and Vite together.

```bash
# Copy environment file (adjust as needed)
cp .env.example .env

# Start the stack
docker compose -f docker-compose.dev.yml up --build

# Stop (Ctrl+C), then optionally clean up
docker compose -f docker-compose.dev.yml down
```

Services:

- Backend (Django): <http://localhost:8000>
- Frontend (Vite): <http://localhost:5173>

Optional: enable Postgres by uncommenting the service in `docker-compose.dev.yml` and set `DATABASE_URL` in `.env`.

### Option A: Using Makefile (Recommended)

```bash
# Start both frontend (Vite) and backend (Django) together
make dev

# Backend only
make run

# Override address per run (example)
HOST=0.0.0.0 PORT=9000 make run
```

### Option B: Manual

```bash
# Terminal 1: Start frontend dev server
cd apps/frontend
npm run dev

# Terminal 2: Start Django server
source .venv/bin/activate
cd apps/backend
python manage.py runserver 127.0.0.1:8001
```

### Available Commands

```bash
# Development
make dev          # Start both frontend and backend development servers
make run          # Run Django server only
make test         # Run Python tests

# Production
make build        # Build frontend and collect static files
```

## 📁 Project Structure

```text
mysite/
├── apps/
│   ├── backend/           # Django application
│   │   ├── apps/         # Django apps
│   │   │   ├── core/     # Core functionality
│   │   │   ├── pages/    # Static pages
│   │   │   ├── blog/     # Blog functionality
│   │   │   ├── projects/ # Projects showcase
│   │   │   └── contact/  # Contact forms
│   │   ├── config/       # Django settings
│   │   └── manage.py     # Django management
│   └── frontend/         # Vite + TypeScript
│       ├── src/          # Source files
│       ├── public/       # Static assets
│       └── dist/         # Build output (generated)
├── docs/                 # Documentation
├── infra/               # Infrastructure/deployment
├── scripts/             # Utility scripts
├── .env                 # Environment variables (local)
├── .env.example         # Environment template
├── requirements.txt     # Python dependencies
└── Makefile            # Development commands
```

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

- `SECRET_KEY`: Django secret key (generate a new one for production)
- `DEBUG`: Set to `False` in production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DATABASE_URL`: Database connection string
- `VITE_DEV_SERVER_URL`: Frontend dev server URL

### Django Settings

Settings are organized by environment:

- `base.py`: Common settings
- `dev.py`: Development settings (loads .env file)
- `prod.py`: Production settings
- `test.py`: Testing settings

## 🧪 Testing

```bash
# Run Django tests
make test

# Run specific app tests
cd apps/backend
python manage.py test apps.blog

# Run with verbose output
python manage.py test -v 2
```

## 📦 Deployment

### Production Setup

1. **Environment variables**

   - Set `DEBUG=False`
   - Configure proper `SECRET_KEY`
   - Set `ALLOWED_HOSTS` to your domain
   - Configure production database

2. **Build frontend**

   ```bash
   make build
   ```

3. **Collect static files**

   ```bash
   cd apps/backend
   python manage.py collectstatic --noinput
   ```

4. **Run migrations**

   ```bash
   python manage.py migrate
   ```

### Server Options

- **Development**: Django dev server (`python manage.py runserver`)
- **Production**: Gunicorn (`gunicorn config.wsgi:application`)

## 🔧 Development Tips

### Adding New Django Apps

1. Create the app:

   ```bash
   cd apps/backend
   python manage.py startapp myapp apps/myapp
   ```

2. Add to `INSTALLED_APPS` in `base.py`:

   ```python
   INSTALLED_APPS = [
       # ...
       "apps.myapp",
   ]
   ```

3. Update the app's `AppConfig` name to match the full path:

   ```python
   # apps/myapp/apps.py
   class MyAppConfig(AppConfig):
       name = 'apps.myapp'
   ```

### Frontend Development

- Vite dev server runs on `http://localhost:5173`
- Hot reloading is enabled for CSS and TypeScript
- Build output goes to `apps/frontend/dist/`

### Configure dev server address (HOST/PORT)

- The Makefile defines a single source of truth for the backend address:
  - `HOST ?= 127.0.0.1`
  - `PORT ?= 8001`
- VS Code launch/tasks also use `HOST`/`PORT` with the same defaults.
- You can override without editing files:

```bash
# Makefile targets
HOST=0.0.0.0 PORT=9000 make run

# VS Code: set environment variables HOST and PORT in your shell/session
export HOST=0.0.0.0
export PORT=9000
```

### Common Issues

1. **Import errors**: Make sure virtual environment is activated
2. **Database errors**: Run migrations (`python manage.py migrate`)
3. **Static files not loading**: Run `python manage.py collectstatic`
4. **Environment variables not loading**: Check `.env` file path and content

### Repository Structure

Generate a visual tree of the project structure:

```bash
# Quick tree view
make tree

# Generate documentation tree
./scripts/gentree --docs

# Custom tree with options
python scripts/tree.py --simple -d 3 -o structure.md
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

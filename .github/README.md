# GitHub Actions CI/CD Setup

This document describes the CI/CD pipeline setup for the MyStite project using GitHub Actions.

## 🏗️ Workflows Overview

### 1. **CI Workflow** (`ci.yml`)
- **Triggers**: Push to any branch, Pull requests
- **Jobs**:
  - **Python lint & test**: Runs Django tests, linting, and pre-commit hooks
  - **Frontend lint & build**: Runs TypeScript tests, linting, and Vite builds

### 2. **Quality Check** (`quality-check.yml`)
- **Triggers**: Weekly schedule, manual dispatch, main branch pushes
- **Features**: Comprehensive code quality analysis and reporting

### 3. **Deploy** (`deploy.yml`)
- **Triggers**: Main branch pushes, releases, manual dispatch
- **Environments**: Staging and Production deployments

### 4. **Test Matrix** (`test-matrix.yml`)
- **Triggers**: Weekly schedule, manual dispatch
- **Features**: Multi-OS and multi-version testing

### 5. **Dependency Updates** (`dependency-updates.yml`)
- **Triggers**: Weekly schedule, manual dispatch
- **Features**: Automated dependency updates with PRs

### 6. **Release** (`release.yml`)
- **Triggers**: Version tags, manual dispatch
- **Features**: Automated releases with changelog generation

## 🔐 Required Secrets

To use all features of the CI/CD pipeline, configure these secrets in your GitHub repository:

### Repository Secrets
Go to: `Settings` → `Secrets and variables` → `Actions`

#### **Deployment Secrets**
```
STAGING_SECRET_KEY          # Django secret key for staging
STAGING_DATABASE_URL        # Database URL for staging environment
PRODUCTION_SECRET_KEY       # Django secret key for production
PRODUCTION_DATABASE_URL     # Database URL for production environment
```

#### **Platform Integration**
```
RAILWAY_TOKEN              # Railway deployment token (if using Railway)
DO_APP_ID                  # DigitalOcean App Platform ID (if using DO)
HEROKU_API_KEY             # Heroku API key (if using Heroku)
```

#### **Notifications**
```
SLACK_WEBHOOK_URL          # Slack webhook for deployment notifications
DISCORD_WEBHOOK_URL        # Discord webhook for notifications
```

## 🌍 Environment Configuration

### Staging Environment
- **Name**: `staging`
- **URL**: Set in deployment workflow
- **Protection Rules**: None (auto-deploy from main)

### Production Environment
- **Name**: `production`
- **URL**: Set in deployment workflow
- **Protection Rules**:
  - Required reviewers: 1+
  - Restrict to main branch only

To set up environments:
1. Go to `Settings` → `Environments`
2. Create `staging` and `production` environments
3. Configure protection rules for production

## 📊 Status Badges

Add these badges to your README.md:

```markdown
[![CI](https://github.com/ksbk/mysite/actions/workflows/ci.yml/badge.svg)](https://github.com/ksbk/mysite/actions/workflows/ci.yml)
[![Quality Check](https://github.com/ksbk/mysite/actions/workflows/quality-check.yml/badge.svg)](https://github.com/ksbk/mysite/actions/workflows/quality-check.yml)
[![Deploy](https://github.com/ksbk/mysite/actions/workflows/deploy.yml/badge.svg)](https://github.com/ksbk/mysite/actions/workflows/deploy.yml)
```

## 🚀 Deployment Platforms

### Railway (Recommended)
1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Enable auto-deployments from main branch

### Heroku
1. Install Heroku CLI in workflow
2. Set up container deployment
3. Configure environment variables

### DigitalOcean App Platform
1. Use doctl CLI in workflow
2. Configure app specification
3. Set environment variables

## 🔄 Workflow Triggers

### Automatic Triggers
- **CI**: Every push and PR
- **Quality Check**: Weekly on Mondays
- **Dependency Updates**: Weekly on Mondays
- **Deploy**: Pushes to main branch
- **Release**: Version tags (v*)

### Manual Triggers
All workflows can be triggered manually via:
- GitHub Actions tab → Choose workflow → "Run workflow"

## 📈 Monitoring and Notifications

### Coverage Reports
- Backend coverage uploaded to Codecov
- Reports available in workflow artifacts

### Security Scanning
- Bandit for Python security issues
- Semgrep for general security patterns
- npm audit for frontend vulnerabilities

### Performance Testing
- Lighthouse CI for web performance
- Django performance tests
- Load testing capabilities

## 🛠️ Local Development

To run the same checks locally:

```bash
# Install dependencies
uv pip install -e .[dev]
cd apps/frontend && npm install

# Run tests
make test                    # All tests
make test-backend           # Django tests only
make test-frontend          # TypeScript tests only

# Run quality checks
uv run pre-commit run --all-files
uv run ruff check .
cd apps/frontend && npm run lint

# Build production assets
make build
```

## 🐛 Troubleshooting

### Common Issues

1. **Secret not found**: Ensure all required secrets are set in repository settings
2. **Environment not accessible**: Check environment protection rules
3. **Tests failing**: Run locally first to debug issues
4. **Build failures**: Check dependency versions and compatibility

### Debug Tips

1. Enable debug logging by setting `ACTIONS_STEP_DEBUG=true` secret
2. Use `continue-on-error: true` for non-critical steps
3. Check workflow logs for detailed error messages
4. Validate YAML syntax using GitHub's workflow validator

## 📚 Further Reading

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Environment Protection Rules](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [Secrets Management](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

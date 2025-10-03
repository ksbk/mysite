#!/bin/bash

# GitHub Repository Setup Script for CI/CD
# This script helps set up environments and provides guidance for secrets

set -e

echo "🔧 GitHub Repository CI/CD Setup"
echo "================================="

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed. Please install it first."
    echo "   Visit: https://cli.github.com/"
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree &> /dev/null; then
    echo "❌ Not in a git repository"
    exit 1
fi

echo "📋 Current repository:"
gh repo view --json owner,name,url --template '{{.owner.login}}/{{.name}} - {{.url}}'
echo ""

echo "🌍 Setting up GitHub Environments..."

# Create staging environment
echo "Creating staging environment..."
gh api repos/:owner/:repo/environments/staging \
  --method PUT \
  --field wait_timer=0 \
  --field prevent_self_review=false \
  --field reviewers='[]' \
  --field deployment_branch_policy='{"protected_branches":false,"custom_branch_policies":true}' \
  2>/dev/null || echo "  ✓ Staging environment already exists"

# Create production environment with protection rules
echo "Creating production environment with protection rules..."
gh api repos/:owner/:repo/environments/production \
  --method PUT \
  --field wait_timer=0 \
  --field prevent_self_review=true \
  --field reviewers='[]' \
  --field deployment_branch_policy='{"protected_branches":true,"custom_branch_policies":false}' \
  2>/dev/null || echo "  ✓ Production environment already exists"

echo "✅ Environments created successfully!"
echo ""

echo "🔐 Repository Secrets Setup Guide"
echo "================================="
echo ""
echo "Please add the following secrets to your repository:"
echo "Go to: https://github.com/$(gh repo view --json owner,name --template '{{.owner.login}}/{{.name}}')/settings/secrets/actions"
echo ""

echo "📦 Required Secrets:"
echo ""
echo "## Deployment Secrets"
echo "STAGING_SECRET_KEY          # Django secret key for staging"
echo "STAGING_DATABASE_URL        # Database URL for staging (e.g., postgresql://...)"
echo "PRODUCTION_SECRET_KEY       # Django secret key for production"
echo "PRODUCTION_DATABASE_URL     # Database URL for production"
echo ""

echo "## Platform Integration (choose one)"
echo "RAILWAY_TOKEN               # Railway deployment token"
echo "HEROKU_API_KEY             # Heroku API key"
echo "DO_APP_ID                  # DigitalOcean App Platform ID"
echo ""

echo "## Notifications (optional)"
echo "SLACK_WEBHOOK_URL          # Slack webhook for deployment notifications"
echo "DISCORD_WEBHOOK_URL        # Discord webhook for notifications"
echo ""

echo "🔑 Secret Value Examples:"
echo ""
echo "STAGING_SECRET_KEY:"
echo "  python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'"
echo ""
echo "DATABASE_URL examples:"
echo "  PostgreSQL: postgresql://username:password@host:port/database_name"
echo "  SQLite:     sqlite:///path/to/database.db"
echo ""

echo "🚀 Testing the Pipeline"
echo "======================"
echo ""
echo "1. Push this commit to trigger CI/CD:"
echo "   git push origin main"
echo ""
echo "2. View workflow runs:"
echo "   gh run list"
echo ""
echo "3. Watch a specific run:"
echo "   gh run watch"
echo ""
echo "4. View in browser:"
echo "   gh repo view --web"
echo "   Then go to 'Actions' tab"
echo ""

echo "✅ Setup guide complete!"
echo ""
echo "Next steps:"
echo "1. Add the required secrets to your repository"
echo "2. Configure your deployment platform (Railway/Heroku/DigitalOcean)"
echo "3. Push code to trigger the CI/CD pipeline"
echo "4. Check the Actions tab for workflow results"
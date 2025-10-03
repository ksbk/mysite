# Site Configuration System (sitecfg)

A comprehensive Django site configuration system with validation, caching, and version control.

## Overview

The `sitecfg` system provides a centralized way to manage site-wide configuration settings with:

- **Database-backed configuration** - Store settings in the database for easy updates
- **Pydantic validation** - Type-safe configuration with automatic validation
- **Multi-layer caching** - Efficient caching with automatic invalidation
- **Template integration** - Easy access to configuration in Django templates
- **Management commands** - CLI tools for initialization, export, and validation
- **Audit logging** - Track all configuration changes with full audit trail

## Configuration Types

The system manages four main configuration categories:

### 1. Site Configuration (`SiteConfig`)

- Site name, description, and contact information
- Domain and timezone settings
- Feature flags and maintenance mode
- Navigation menu structure

### 2. SEO Configuration (`SEOConfig`)

- Meta titles, descriptions, and keywords
- Open Graph and Twitter Card settings
- Google Analytics and Search Console integration
- Structured data (JSON-LD) configuration

### 3. Theme Configuration (`ThemeConfig`)

- Color scheme (primary, secondary, accent colors)
- Typography settings (font family, base size)
- Dark mode support
- Custom CSS injection

### 4. Content Configuration (`ContentConfig`)

- Posts per page and pagination settings
- Comment system configuration
- Search and categorization features
- Date formatting and author display

## Configuration Precedence

Settings are resolved in the following order (highest to lowest priority):

1. **Database values** - Stored in Django models, editable via admin
2. **Environment variables** - For deployment-specific overrides
3. **Schema defaults** - Fallback values defined in Pydantic schemas

## Caching Strategy

The system uses a multi-layer caching approach:

- **Per-config-type caching**: `config:site`, `config:seo`, etc.
- **TTL-based expiration**: 5-minute default cache timeout
- **Automatic invalidation**: Cache cleared on model save/delete via Django signals
- **Fallback handling**: Graceful degradation when cache is unavailable

### Cache Keys

````python

```python
CACHE_PREFIX = "config:"
# Examples:
# config:site - SiteConfig data
# config:seo - SEOConfig data
# config:theme - ThemeConfig data
# config:content - ContentConfig data
````

## Template Access

Configuration is available in Django templates through two mechanisms:

### 1. Context Processor

All templates automatically have access to configuration via the `config` context variable:

```html
<!-- Site name and description -->
<h1>{{ config.site.site_name }}</h1>
<p>{{ config.site.site_description }}</p>

<!-- SEO meta tags -->
<title>{{ config.seo.default_title }}</title>
<meta name="description" content="{{ config.seo.default_description }}" />

<!-- Theme colors -->
<style>
  :root {
    --primary-color: {{ config.theme.primary_color }};
    --secondary-color: {{ config.theme.secondary_color }};
  }
</style>
```

### 2. Template Tags

For more advanced configuration rendering:

```html
{% load core_site %}

<!-- Render structured data -->
{% render_json_ld config.seo.structured_data %}

<!-- Check feature flags -->
{% if config.site.feature_flags.enable_comments %}
<!-- Comments section -->
{% endif %}
```

## API Endpoints

The system provides REST API endpoints for configuration management:

### Validation Endpoints

- `GET /admin/config/validate/<config_type>/` - Validate specific configuration
- `POST /admin/config/validate/<config_type>/` - Validate configuration data

### Health Check

- `GET /admin/config/health/` - System health and connectivity check

### Cache Management

- `DELETE /admin/config/cache/` - Clear all configuration caches
- `DELETE /admin/config/cache/<config_type>/` - Clear specific configuration cache
- `POST /admin/config/cache/` - Warm all configuration caches
- `POST /admin/config/cache/<config_type>/` - Warm specific configuration cache

**Note**: All endpoints require staff-level authentication.

## Management Commands

### Initialize Configuration

```bash
python manage.py init_sitecfg --site-name "My Site" --domain "example.com" --email "admin@example.com"
```

### Export Configuration

```bash
# Export all configuration
python manage.py export_sitecfg --output config_backup.json --pretty

# Export specific type
python manage.py export_sitecfg --config-type site --output site_config.json
```

### Validate Configuration

```bash
# Validate all configuration
python manage.py validate_sitecfg --verbose

# Validate and fix errors
python manage.py validate_sitecfg --config-type seo --fix

# Validate specific type
python manage.py validate_sitecfg --config-type theme
```

### Legacy Comprehensive Command

The original `sitecfg` command is still available with all operations:

```bash
python manage.py sitecfg backup --output backup.json
python manage.py sitecfg restore backup.json
python manage.py sitecfg validate --config-type site
python manage.py sitecfg cache clear
python manage.py sitecfg audit --limit 10
```

## Python API Usage

### Basic Configuration Access

```python
from apps.core.sitecfg.loader import get_config, resolve_config

# Get all configuration
config = get_config()

# Get specific configuration type
site_config = get_config('site')

# Get configuration optimized for templates (with request context)
template_config = resolve_config(request)
```

### Configuration Loader

```python
from apps.core.sitecfg.loader import ConfigLoader

loader = ConfigLoader()

# Get configuration with caching
config = loader.get_config('site')

# Invalidate cache
loader.invalidate_cache('site')

# Warm cache
loader.warm_cache()
```

### Validation and Normalization

```python
from apps.core.sitecfg.normalize import normalize_config_dict

# Validate and normalize configuration data
raw_config = {'site': {'site_name': '  My Site  '}}
normalized = normalize_config_dict(raw_config)
# Result: {'site': {'site_name': 'My Site'}}
```

## Database Models

The configuration system uses four main Django models:

- `apps.core.models.SiteConfig` - Site-wide settings
- `apps.core.models.SEOConfig` - SEO and metadata
- `apps.core.models.ThemeConfig` - Visual theme settings
- `apps.core.models.ContentConfig` - Content display settings

All models use singleton patterns to ensure only one instance exists per type.

## Audit and Versioning

Configuration changes are automatically tracked:

- **ConfigAudit** - Records all create/update/delete operations
- **ConfigVersion** - Maintains versioned snapshots of configuration
- **Automatic logging** - All changes logged with user, timestamp, and IP address

## Security Considerations

- All API endpoints require staff-level authentication
- Configuration data is validated using Pydantic schemas
- File uploads and custom CSS are sanitized to prevent XSS
- Audit trail maintains complete change history
- Environment variable overrides allow secure deployment configuration

## Development and Testing

### Running Tests

```bash
# Test the configuration system
python -m pytest apps/core/tests/test_sitecfg_*.py -v

# Test with coverage
python -m pytest apps/core/tests/test_sitecfg_*.py --cov=apps.core.sitecfg
```

### Adding New Configuration Types

1. Create a new Django model in `apps/core/models/sitecfg/`
2. Add corresponding Pydantic schema in `apps/core/sitecfg/schemas.py`
3. Update the loader's `schema_map` in `apps/core/sitecfg/loader.py`
4. Create migrations and update admin registration
5. Add tests for the new configuration type

## Performance Notes

- Configuration is cached aggressively to minimize database queries
- Cache invalidation happens automatically via Django signals
- Template context processor adds minimal overhead (~1ms per request)
- Pydantic validation is fast and runs only during updates
- Database queries are optimized with proper indexes

## Migration and Deployment

When deploying configuration changes:

1. Run migrations to update database schema
2. Use management commands to validate existing configuration
3. Clear caches after deployment to ensure fresh data
4. Monitor audit logs for any unexpected changes
5. Use environment variables for deployment-specific overrides

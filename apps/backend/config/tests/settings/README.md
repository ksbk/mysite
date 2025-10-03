# Django Settings Test Suite

This directory contains comprehensive test cases for the Django settings configuration.

## Test Structure

### Test Files

1. **`test_env_validation.py`** - Tests for environment settings validation (env.py)
   - Pydantic validation testing
   - Field validation and bounds checking
   - URL normalization
   - Secret string redaction
   - Cached settings loading

2. **`test_django_settings.py`** - Tests for Django settings modules
   - Base settings structure validation
   - Required settings presence
   - Middleware ordering
   - Template configuration
   - Database and cache configuration

3. **`test_environment_settings.py`** - Tests for environment-specific settings
   - Development settings (dev.py)
   - Production settings (prod.py)
   - Staging settings (staging.py)
   - Test settings (test.py)
   - Conditional feature loading

4. **`test_request_id.py`** - Tests for request ID middleware and logging
   - Request ID generation and uniqueness
   - Thread-local storage isolation
   - Logging integration
   - Middleware functionality

## Running Tests

### Option 1: Using Django's Test Runner

```bash
# From the backend directory
cd apps/backend
python manage.py test config.settings.tests
```

### Option 2: Using the Custom Test Runner

```bash
# From the tests directory
cd config/settings/tests
python run_tests.py
```

### Option 3: Using pytest

```bash
# Install pytest if not already installed
pip install pytest pytest-django

# Run all settings tests
pytest config/settings/tests/

# Run specific test file
pytest config/settings/tests/test_env_validation.py

# Run with verbose output
pytest -v config/settings/tests/
```

## Test Categories

### Unit Tests
- Environment settings validation
- Individual component testing
- Isolated functionality testing

### Integration Tests
- Django settings module loading
- Middleware integration
- Logging system integration

### Configuration Tests
- Environment-specific behavior
- Conditional loading
- Settings consistency

## Test Coverage Areas

### Environment Settings (env.py)
- ✅ Default values validation
- ✅ Field parsing and normalization
- ✅ Bounds checking (HSTS, email ports)
- ✅ TLS/SSL exclusivity validation
- ✅ URL normalization
- ✅ Secret string redaction
- ✅ Cached loading behavior

### Django Settings Integration
- ✅ Required settings presence
- ✅ Middleware ordering
- ✅ App configuration
- ✅ Database setup
- ✅ Template configuration
- ✅ Static files configuration
- ✅ Security settings

### Environment-Specific Settings
- ✅ Development overrides
- ✅ Production security hardening
- ✅ Staging configuration balance
- ✅ Test optimizations
- ✅ Conditional feature loading

### Request ID System
- ✅ Unique ID generation
- ✅ Thread isolation
- ✅ Middleware integration
- ✅ Logging correlation
- ✅ Format validation

## Expected Test Results

All tests should pass in a properly configured environment. Common issues:

1. **Missing Dependencies**: Ensure `pydantic`, `pydantic-settings` are installed
2. **Django Setup**: Tests require Django to be properly configured
3. **Environment Variables**: Some tests may require specific environment variables

## Test Output Examples

### Successful Run
```
......................................................................
----------------------------------------------------------------------
Ran 70 tests in 0.234s

OK
All settings tests passed!
```

### Failed Test Example
```
FAIL: test_email_tls_ssl_exclusivity (config.settings.tests.test_env_validation.TestEnvironmentSettings)
----------------------------------------------------------------------
AssertionError: ValidationError not raised

FAILED (failures=1)
```

## Extending Tests

When adding new settings or functionality:

1. Add corresponding test cases to the appropriate test file
2. Ensure both positive and negative test cases
3. Test edge cases and boundary conditions
4. Add integration tests for complex interactions
5. Update this README with new test coverage

## Maintenance

- Review and update tests when settings change
- Ensure test coverage remains comprehensive
- Update documentation for new test patterns
- Regular test performance review

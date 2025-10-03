# Core app tests

A small, pragmatic test layout that stays lean for v1 and scales cleanly as features grow.

## Layout

- test_models/
  - test_base_mixins.py — TimeStampedModel, SingletonModel, VersionedSingletonModel, OrderedModel
- test_config/
  - test_loader.py — config loader + cache invalidation

Add new files by concern (models, config, templates, context, admin). Keep names obvious and searchable.

## Conventions

- Group by feature/subject, not only by test type.
- One clear subject per test class; descriptive test names.
- Prefer Arrange–Act–Assert; avoid hidden setup.
- Use the lightest base class needed:
  - SimpleTestCase — no DB (pure functions, template rendering without ORM)
  - TestCase — default for ORM interactions
  - TransactionTestCase — only when testing transactions or schema ops
- Avoid JSON/YAML fixtures. Create data inline; introduce factories later if needed.

## Data setup

- Inline `Model.objects.create(...)` for clarity in simple tests.
- If object creation becomes repetitive, consider:
  - model_bakery (lowest ceremony)
  - factory_boy (when you need more control)
- Keep helpers local to this app (add `helpers/` when reuse appears 3+ times).

## Dynamic model pattern (used in mixin tests)

- Define small test-only models inside the test module.
- Set `class Meta: app_label = "core"` and a unique `db_table`.
- Do not use `schema_editor` — Django’s test runner creates these tables for the test DB.
- Use `TestCase` so each test runs in a clean transaction and remains fast.

## Caching and settings

- Use `override_settings` in a test when you need one-off variations.
- Clear cache or use a dedicated alias when testing caching logic.
- Keep email backend to locmem and use a fast password hasher in `settings/test.py`.

## When to add structure

- Start flat, add folders as areas get crowded (e.g., `test_templates/`, `test_context/`).
- Promote shared helpers to `tests/helpers/` when repeated across 3+ files.

## Running tests

From the backend app root:

```bash
# Run core app tests
python manage.py test apps.core -v 2

# Run a specific module
python manage.py test apps.core.tests.test_models.test_base_mixins -v 2

# Run a single test case
python manage.py test apps.core.tests.test_models.test_base_mixins.SingletonModelTests -v 2
```

## Style

- Keep assertions specific; avoid overly broad `assertTrue` when `assertEqual` would be clearer.
- Prefer deterministic checks over time-based sleeps.
- Keep tests independent; no shared mutable state.

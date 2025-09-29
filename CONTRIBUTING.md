# Contributing

Thanks for contributing! This project uses pre-commit to enforce formatting, linting, and security checks across Python, Django templates, and the frontend.

-   Install deps: `make install`
-   Run all hooks locally: `pre-commit run --all-files`
-   Lint Python: `ruff check .`
-   Type-check: `mypy --config-file pyproject.toml`
-   Frontend lint: `npm run lint --prefix apps/frontend`
-   Tests (backend): `make test`

We follow Conventional Commits for commit messages. Pre-commit validates commit messages.

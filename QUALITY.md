# 🧭 Project Quality Framework

This document defines the **living quality baseline** for the project.
It covers **code, performance, security, accessibility, UX, and business impact**, with clear criteria, tools, and scoring.
Every release must be assessed against this framework.

---

## 📊 Quality Criteria

### 1. Code Quality & Standards

- **Semantic HTML**: Use correct HTML5 elements.
- **Template Structure**: Base → Components → Pages.
- **Consistency**: Naming, formatting, lint rules.
- **Validation**: Pass W3C HTML/CSS validators.
- **Tools**:
  - Ruff (`ruff check`, `ruff format --check`)
  - MyPy (`mypy --config-file mypy.ini`)
  - djLint (`djlint --profile=django --lint`)
  - Prettier (`prettier --check`)

### 2. Performance

- **Budgets**:
  - JS ≤ 200KB gz
  - CSS ≤ 100KB gz
  - Images total ≤ 800KB per page
  - LCP ≤ 2.5s, CLS ≤ 0.1, TBT ≤ 200ms
- **Practices**: lazy loading, compression, CDN-ready.
- **Tools**: Lighthouse CI, WebPageTest, Vite bundle analyzer.

### 3. Security

- **Headers**: CSP, HSTS, X-Frame, X-Content-Type, Referrer-Policy.
- **Protection**: XSS escaping, CSRF tokens, HTTPS enforced.
- **Secrets**: No secrets in git (`detect-secrets`).
- **Tools**: Semgrep, Bandit, Trivy (Docker/infra), Django `check --deploy`.

### 4. Accessibility (WCAG 2.1 AA)

- **Keyboard Navigation**: Full tab flow.
- **Screen Readers**: ARIA landmarks, alt text.
- **Contrast**: AA contrast ratios.
- **Focus Management**: Visible outlines.
- **Tools**: axe-core, pa11y CI, Lighthouse a11y score.

### 5. Usability & UX

- **Navigation**: Intuitive menus, skip links.
- **Readability**: Typography, spacing.
- **Feedback**: Clear CTAs, error/success states.
- **Forms**: Accessible labels, errors.
- **Testing**: Manual UX review + user feedback.

### 6. Content & SEO

- **Meta tags**: title, description, keywords.
- **Open Graph & Twitter Cards**: social share optimization.
- **Structured Data**: schema.org markup where relevant.
- **URLs**: clean, semantic, canonical.
- **Tools**: Lighthouse SEO, Google Search Console.

### 7. Maintainability

- **Documentation**: README, ADRs, inline comments.
- **Modularity**: Components, apps, DRY patterns.
- **Config**: Env-based settings (via Pydantic v2).
- **Testing**: Unit, integration, E2E with Playwright.
- **Coverage**: Target ≥ 85%.

### 8. Scalability & Ops

- **Template Architecture**: Block/component hierarchy.
- **Caching**: Django template fragment caching.
- **CDN-ready**: Static/media assets.
- **Monitoring**: Sentry (errors), Prometheus/Grafana (metrics).
- **Reliability**: Migrations tested, rollback plan defined.

### 9. Analytics & Insights

- **Tracking**: Analytics scripts gated by cookie consent.
- **Conversion**: Goals/events tracked.
- **A/B Testing**: Feature flags ready via LaunchDarkly/Unleash.

### 10. Internationalization (i18n)

- **Language Support**: Django i18n, JSON translations.
- **RTL Support**: Bidirectional layout support.
- **Locale Formatting**: Dates, numbers, currencies localized.

### 11. Progressive Web App (PWA)

- **Service Worker**: Offline caching.
- **Web App Manifest**: Installable experience.
- **Push Notifications**: Optional engagement.
- **Tools**: Lighthouse PWA score.

---

## ⚖️ Scoring Framework

### Scoring Bands

- **10**: Production Excellence (best practices met)
- **8–9**: Professional Grade (minor improvements possible)
- **6–7**: Good Foundation (needs several fixes)
- **4–5**: Basic (major gaps)
- **1–3**: Critical Issues

### Category Weights

| Category          | Weight |
| ----------------- | ------ |
| Accessibility     | 0.15   |
| Security          | 0.15   |
| Performance       | 0.15   |
| SEO               | 0.10   |
| Maintainability   | 0.10   |
| Usability         | 0.10   |
| Responsive Design | 0.10   |
| Code Quality      | 0.08   |
| Analytics         | 0.04   |
| PWA               | 0.03   |

**Formula**:

```text
overall_score = Σ (category_score × weight)
```

---

## 📈 Reporting & Evidence

Every release must include:

- **Automated reports**: Lighthouse, axe, Ruff, MyPy, djLint, Prettier, Semgrep.
- **Manual checks**: UX, accessibility keyboard nav, privacy/data governance.
- **Artifacts**: Store reports under `tests/reports/` and link in release notes.

**Example JSON report**:

```json
{
    "commit": "abc123",
    "date": "2025-09-29",
    "overall": 8.8,
    "categories": {
        "performance": { "score": 8, "evidence": ["lighthouse/report.html"] },
        "security": { "score": 8, "evidence": ["semgrep.sarif"] },
        "accessibility": { "score": 9, "evidence": ["axe.json"] }
    }
}
```

---

## 🤖 Automation

Quality automation is driven by the `quality-check` GitHub Actions workflow. It:

1. Runs the backend toolchain (`ruff`, `mypy`, `djlint`, `bandit`, `detect-secrets`).
2. Runs the frontend toolchain (`eslint`, `prettier --check`, `vite build`).
3. Spins up the production preview and audits it with Lighthouse (HTML + JSON reports) and axe-core (accessibility JSON).
4. Generates machine-readable reports under `tests/reports/`, appending each run to `tests/reports/history.jsonl` for long-term tracking.
5. Publishes the `quality-summary.json` artifact (plus supporting reports) for auditing and trend analysis.

Trigger the workflow on every pull request, protected-branch push, or manual dispatch before a release cut. Incorporate the resulting reports into release notes and update scores in this document if thresholds change.

---

## 🚀 Continuous Improvement

- Reassess weights/criteria quarterly.
- Track historical scores in CI for regression detection.
- Treat quality like a **feature**: never optional, always shipped.
- Encourage team-wide ownership, not just QA.

---

📌 **Living document:** Update this `QUALITY.md` whenever requirements, tools, or thresholds evolve.

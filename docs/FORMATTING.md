# Formatting Configuration Guide

This document explains the professional formatting standards and tool coordination for this project.

## 📋 Tool Responsibilities

### 🔧 **EditorConfig (`.editorconfig`)**

-   **Purpose**: Base editor settings across all IDEs/editors
-   **Handles**: Indentation, line endings, charset, trailing whitespace
-   **Coverage**: All file types with sensible defaults

### 🎨 **Prettier (`.prettierrc.json`)**

-   **Purpose**: Code formatting for web technologies
-   **Handles**: JavaScript, TypeScript, JSON, CSS, SCSS, HTML (non-Django), Markdown
-   **Coverage**: Frontend assets and configuration files

### 🐍 **Ruff (`pyproject.toml`)**

-   **Purpose**: Python linting and formatting
-   **Handles**: All Python files (`.py`)
-   **Coverage**: Django backend code

### 🏷️ **djLint (`.djlintrc`)**

-   **Purpose**: Django template formatting and linting
-   **Handles**: Django HTML templates (`.html` in template directories)
-   **Coverage**: Django templates with template tag support

### 🆚 **VS Code (`settings.json`)**

-   **Purpose**: IDE-specific formatter coordination
-   **Handles**: Assigns the right formatter to each file type
-   **Coverage**: Ensures seamless integration in VS Code

## 📏 Professional Standards Applied

### **Line Length: 88 characters**

-   Chosen for optimal readability on modern screens
-   Consistent across all tools (Python PEP 8 suggests 79, but 88 is Black's default)
-   Balances readability with modern screen real estate

### **Indentation Strategy**

```
Python files (.py)           → 4 spaces (PEP 8 standard)
Django templates (.html)     → 2 spaces (Web standard)
JavaScript/TypeScript        → 2 spaces (Web standard)
JSON/YAML/CSS               → 2 spaces (Web standard)
Configuration files         → 2 or 4 spaces (context-dependent)
```

### **Why 2 spaces for HTML templates?**

-   **Web Standard**: HTML/CSS/JS ecosystem uses 2 spaces
-   **Readability**: Less visual noise in nested HTML structures
-   **Industry Practice**: Most major web frameworks use 2 spaces
-   **Consistency**: Matches frontend JavaScript/CSS formatting

## 🔄 File Type Mapping

| File Extension    | Primary Tool | VS Code Formatter        | Indentation |
| ----------------- | ------------ | ------------------------ | ----------- |
| `.py`             | Ruff         | `charliermarsh.ruff`     | 4 spaces    |
| `.html` (Django)  | djLint       | `monosans.djlint`        | 2 spaces    |
| `.html` (regular) | Prettier     | `esbenp.prettier-vscode` | 2 spaces    |
| `.js`, `.ts`      | Prettier     | `esbenp.prettier-vscode` | 2 spaces    |
| `.json`           | Prettier     | `esbenp.prettier-vscode` | 2 spaces    |
| `.css`, `.scss`   | Prettier     | `esbenp.prettier-vscode` | 2 spaces    |
| `.md`             | Prettier     | `esbenp.prettier-vscode` | 2 spaces    |
| `.toml`, `.yaml`  | EditorConfig | N/A                      | 2 spaces    |

## ⚡ Format on Save Configuration

All file types are configured to format automatically on save with these settings:

-   `"editor.formatOnSave": true`
-   `"editor.formatOnSaveMode": "modificationsIfAvailable"` (when supported)

## 🚫 Ignored Patterns

### djLint Ignores:

-   `T003`: Endblock should have name (acceptable for simple templates)
-   `H022`: Use HTTPS for external links (dev environment flexibility)
-   `H030`: Consider adding meta description (not always needed)
-   `H031`: Consider adding meta keywords (SEO practice varies)

### Ruff Ignores:

-   `E203`: Whitespace before ':' (Black compatibility)

## 📁 Excluded Directories

The following directories are excluded from formatting:

```
apps/backend/static/          # Static assets
apps/backend/staticfiles/     # Collected static files
apps/backend/media/           # User uploads
apps/backend/**/migrations/   # Django migrations
apps/frontend/node_modules/   # Node.js dependencies
```

## 🔧 Commands for Manual Formatting

```bash
# Format Python files
ruff format apps/backend/

# Format Django templates
djlint --reformat apps/backend/templates/ apps/backend/apps/

# Format JavaScript/TypeScript
npx prettier --write apps/frontend/src/

# Format all supported files
npx prettier --write "**/*.{js,ts,json,css,scss,md}"
```

## ✅ Best Practices

1. **Let tools do their job**: Don't fight the formatters
2. **Consistent configuration**: All tools use 88-character line length
3. **Appropriate indentation**: Use web standards for web files, Python standards for Python
4. **Format on save**: Automatic formatting prevents inconsistencies
5. **Tool specialization**: Each tool handles what it does best

## 🔍 Troubleshooting

### **Formatter Conflicts**

If you see inconsistent formatting:

1. Check that VS Code is using the correct formatter for each file type
2. Verify that only one tool is configured per file type
3. Restart VS Code after configuration changes

### **Line Length Issues**

All tools are configured for 88 characters. If you see longer lines:

1. Check for very long strings or URLs
2. Some tools may not break certain constructs
3. Manual line breaks are sometimes necessary

### **Indentation Problems**

If indentation is inconsistent:

1. Django templates should use 2 spaces (not 4)
2. Python files should use 4 spaces
3. Clear editor settings that override formatter behavior

# dsutil

Shared utility library for my Python scripts and programs.

## Using in Projects

### Poetry

```toml
[tool.poetry.dependencies]
dsutil = { git = "https://gitlab.dannystewart.com/danny/dsutil.git" }
```

### uv

```toml
[project]
dependencies = ["dsutil"]

[tool.uv.sources]
dsutil = { git = "https://gitlab.dannystewart.com/danny/dsutil.git" }
```

## Maintenance

### Publishing Updates

```bash
# Bump version (patch)
poetry version patch  # 1.0.0 -> 1.0.1 (small changes)
poetry version minor  # 1.0.0 -> 1.1.0 (feature additions)
poetry version major  # 1.0.0 -> 2.0.0 (breaking changes)

# Build and publish
poetry build

# If updating build only
git add pyproject.toml dist/
git commit -m "Bump version to $(poetry version -s)"

# If updating build and code
git add .
git commit -m "Add new feature"

# Tag and push
git tag v$(poetry version -s)
git push && git push --tags
```

### Updating Installations

Update dsutil across environments:

```bash
# Using envscripts
envscripts --update

# Manually updating environment
pip install --upgrade git+https://gitlab.dannystewart.com/danny/dsutil.git

# Updating Poetry projects
poetry update dsutil
```

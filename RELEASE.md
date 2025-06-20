# Release Process for suitable-django-autocomplete

This document describes the release process for publishing new versions to PyPI.

## Automated Release via GitHub Actions

This project uses GitHub Actions to automatically publish to PyPI when a new version tag is pushed. The workflow is defined in `.github/workflows/publish.yml`.

## Release Steps

### 1. Ensure all changes are committed

```bash
git status  # Should show clean working directory
```

### 2. Update version in pyproject.toml

Edit `pyproject.toml` and update the version number following semantic versioning:
- MAJOR version for incompatible API changes
- MINOR version for new functionality in a backward compatible manner
- PATCH version for backward compatible bug fixes

```toml
[project]
version = "X.Y.Z"  # Update this line
```

### 3. Commit the version bump

```bash
git add pyproject.toml
git commit -m "bump version to X.Y.Z

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 4. Create an annotated tag

Create a tag with a descriptive message about the release:

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z

Features:
- List major features here
- Include any breaking changes
- Mention bug fixes

Additional notes about the release..."
```

### 5. Push to GitHub (this triggers the release)

**Note: This step must be run manually by the maintainer:**

```bash
git push origin main --tags
```

This will:
1. Push your commits to the main branch
2. Push the new tag
3. **Automatically trigger** the GitHub Actions workflow

## What Happens Automatically

Once you push the tag, GitHub Actions will:

1. Run tests on Python 3.9 and 3.12 with Django 4.2
2. Build the package using `uv build`
3. Publish to PyPI using trusted publishing (no credentials needed)

## Monitoring the Release

- Check the Actions tab on GitHub to monitor the workflow progress
- Visit https://pypi.org/project/suitable-django-autocomplete/ to confirm publication
- The workflow is defined in `.github/workflows/publish.yml`

## Creating a GitHub Release (Optional)

After the package is published to PyPI, you can create a GitHub Release:

1. Go to the repository's Releases page
2. Click "Create a new release"
3. Select the tag you just created
4. Add a title like "vX.Y.Z - Brief Description"
5. Add detailed release notes
6. Publish the release

## Example Release Commands

Here's a complete example for releasing version 0.3.2:

```bash
# 1. Make sure all changes are committed
git status

# 2. Update version in pyproject.toml (manually edit the file)
# Change version = "0.3.1" to version = "0.3.2"

# 3. Commit version bump
git add pyproject.toml
git commit -m "bump version to 0.3.2

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 4. Create release tag
git tag -a v0.3.2 -m "Release v0.3.2

Features:
- Add event propagation from internal input to host element
- Improve accessibility with aria-describedby

Bug fixes:
- Fix placeholder announcement timing

This release improves integration with external libraries."

# 5. Push and trigger automatic release (run manually)
git push origin main --tags
```

## Notes

- The version in `pyproject.toml` should match the tag name (without the 'v' prefix)
- Always use annotated tags (`git tag -a`) for releases
- The GitHub Actions workflow only triggers on tags matching the pattern `v*`
- PyPI publication uses trusted publishing, so no API tokens are needed in the repository
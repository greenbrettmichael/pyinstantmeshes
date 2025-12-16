# Git Tag: v1.0.0

This file documents the v1.0.0 release tag creation.

- **Tag**: v1.0.0
- **Commit**: 52f00b746fae4a7d3cf48236b24e382dd30e4470
- **Date**: December 16, 2025
- **Description**: Release v1.0.0 - Python bindings for Instant Meshes with TBB manylinux compatibility

The tag points to the "Prepare v1.0.0 release with TBB manylinux compatibility fix (#7)" commit.

## Tag Details

```
tag v1.0.0
Tagger: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>
Date:   Tue Dec 16 18:10:42 2025 +0000

Release v1.0.0 - Python bindings for Instant Meshes with TBB manylinux compatibility
```

## Tag Creation Status

The annotated tag v1.0.0 has been created locally in this branch. However, the repository has protection rules that prevent tag creation via standard push operations. 

Error encountered:
```
remote: error: GH013: Repository rule violations found for refs/tags/v1.0.0
remote: - Cannot create ref due to creations being restricted
```

## Manual Steps Required

To complete the release, a repository administrator or maintainer with appropriate permissions needs to:

### Option 1: Create the tag directly on the target commit
```bash
git fetch origin
git tag -a v1.0.0 52f00b746fae4a7d3cf48236b24e382dd30e4470 -m "Release v1.0.0 - Python bindings for Instant Meshes with TBB manylinux compatibility"
git push origin v1.0.0
```

### Option 2: Create a GitHub Release
1. Navigate to https://github.com/greenbrettmichael/pyinstantmeshes/releases/new
2. Set "Tag version" to: `v1.0.0`
3. Set "Target" to commit: `52f00b7` (Prepare v1.0.0 release)
4. Set "Release title" to: `v1.0.0`
5. Add release notes describing the changes
6. Click "Publish release"

Creating the release via GitHub UI will automatically create the tag and trigger the publish workflow.

## What Happens After Tag Creation

Once the v1.0.0 tag is pushed, it will trigger the `.github/workflows/publish.yml` workflow, which will:
1. Build wheels for Linux, macOS, and Windows
2. Build source distribution
3. Publish to PyPI automatically

The package will then be installable via:
```bash
pip install pyinstantmeshes
```

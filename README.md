# KiCad Snapshot

KiCad project snapshot and visual diff tool (PySide6 GUI).

- Repository: `https://github.com/tanakamasayuki/kicad-snapshot`
- PyPI package name: `kicad-snapshot`
- CLI command: `kicad_snapshot`
- Japanese README: [README.ja.md](README.ja.md)

## Features

- Create manual ZIP snapshots of KiCad projects
- Compare snapshots against current project state
- Compare snapshot-to-snapshot
- Render schematic/PCB visual diffs
- PCB layer-level comparison
- Multi-language UI (English, Japanese, Chinese, French, German)

## Requirements

- Python 3.11+
- `kicad-cli` available on your machine
- KiCad 8+ recommended

## Installation

### From PyPI (recommended)

```bash
pip install kicad-snapshot
```

Or with `pipx`:

```bash
pipx install kicad-snapshot
```

### From source

```bash
git clone https://github.com/tanakamasayuki/kicad-snapshot.git
cd kicad-snapshot
pip install .
```

## Usage

Run from an installed environment:

```bash
kicad_snapshot
```

If running from source with `uv`:

```bash
uv sync --dev
uv run kicad_snapshot
```

## Basic Workflow

1. Start app and confirm `kicad-cli` path.
2. Select a KiCad project (`.kicad_pro`).
3. Open Snapshot screen and choose compare targets.
4. Open Compare screen and review item-by-item diffs.

## Configuration

Settings are stored per user via `platformdirs`.

- Windows: `%APPDATA%/KiCadSnapshot/settings.toml`
- macOS: `~/Library/Application Support/KiCadSnapshot/settings.toml`
- Linux: `~/.config/KiCadSnapshot/settings.toml`

## Development

```bash
uv sync --dev
uv run kicad_snapshot
```

Entry point:

```toml
[project.scripts]
kicad_snapshot = "kicad_snapshot.__main__:main"
```

## Release Automation (GitHub Actions)

Use workflow: `.github/workflows/release.yml`

- Trigger: `workflow_dispatch`
- Inputs:
  - `version` (e.g. `0.0.1`)
  - `publish_pypi` (`true`/`false`)

Automated steps:

1. Update versions in `pyproject.toml` and `src/kicad_snapshot/__init__.py`
2. Update `CHANGELOG.md` by creating a new section after `## Unreleased`
3. Commit + tag (`vX.Y.Z`)
4. Build Windows EXE (`PyInstaller`, onedir)
5. Create ZIP + SHA256 and attach to GitHub Release
6. (Optional) Publish package to PyPI

For PyPI publish, configure PyPI Trusted Publishing for this GitHub repository.

## Documents

- [SPEC.md](SPEC.md) / [SPEC.ja.md](SPEC.ja.md): product specification
- [DEV_SPEC.md](DEV_SPEC.md) / [DEV_SPEC.ja.md](DEV_SPEC.ja.md): development environment specification

## License

MIT (see [LICENSE](LICENSE))

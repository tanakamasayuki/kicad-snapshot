# Development Environment Specification (PySide6 / Cross-Platform GUI OSS)

## 1. Purpose

This project provides a simple admin-style GUI application as OSS
that runs on Windows / macOS / Linux.

- Windows: distribute a Python-bundled binary (exe) as the primary option for non-engineers
- macOS / Linux: distribute as a Python package (pipx recommended)
- pip installation is also available on all OSes

---

## 2. Technology Stack

| Item | Technology |
|------|------------|
| Language | Python 3.11+ |
| GUI Framework | PySide6 (Qt6) |
| Distribution (Windows) | exe (PyInstaller) *primary distribution* |
| Distribution (All OS) | pip / pipx |
| Settings & Data Storage | platformdirs |
| Packaging | pyproject.toml |
| CI/CD | GitHub Actions |

---

## 3. Target Platforms and Distribution Policy

| OS | Primary Distribution | Alternative | Notes |
|----|----------------------|-------------|-------|
| Windows | exe (bundled Python) | pip / pipx | exe recommended for non-engineers |
| macOS | pipx install | pip | no .app packaging |
| Linux | pipx install | pip | avoid distro-specific dependencies |

### Windows Policy

- In principle, recommend the exe version
- Users with Python can also use pip / pipx
- SmartScreen warnings are acceptable for initial releases (signing to be considered later)

---

## 4. Development Environment Requirements

### Required

- Python 3.11 or later
- Git
- venv or pipx

### Recommended

- pipx (for macOS/Linux verification)
- VSCode + Python extension

---

## 5. Project Structure

```
kicad-snapshot/
├── pyproject.toml
├── README.md
├── src/
│   └── kicad_snapshot/
│       ├── __init__.py
│       └── __main__.py
├── SPEC.md
├── SPEC.ja.md
├── DEV_SPEC.md
└── DEV_SPEC.ja.md
```

---

## 6. Startup Method (Unified Design)

### Entry Point Definition

```toml
[project.scripts]
kicad_snapshot = "kicad_snapshot.__main__:main"
```

### How to Start

#### When using pip / pipx

```
kicad_snapshot
```

#### During development (uv)

```
uv run kicad_snapshot
```

#### Windows exe

```
kicad_snapshot.exe
```

All variants should start from the same `main()`.

---

## 7. Distribution

### 7.1 Windows (Primary Distribution)

Publish the following on GitHub Releases:

```
kicad_snapshot-<version>-win-x64.zip
```

Contents:

```
kicad_snapshot.exe
Qt DLLs
resources/
```

#### Alternative (for Python users)

```
pip install kicad_snapshot
```

---

### 7.2 macOS / Linux

```
pipx install kicad_snapshot
kicad_snapshot
```

No .app packaging, signing, or notarization.

---

## 8. Resource Management

Direct file paths are forbidden to support PyInstaller.

```python
import importlib.resources as res

icon_path = res.files("kicad_snapshot.resources").joinpath("icon.png")
```

---

## 9. Configuration Storage Design

```python
from platformdirs import user_config_dir

CONFIG_DIR = user_config_dir("KiCadSnapshot", "KiCadSnapshot")
```

| OS | Example Path |
|----|--------------|
| Windows | %APPDATA%/KiCadSnapshot |
| macOS | ~/Library/Application Support/KiCadSnapshot |
| Linux | ~/.config/KiCadSnapshot |

---

## 10. CI/CD

### Windows

- Build exe via GitHub Actions
- Zip and attach to Release
- Generate SHA256SUM alongside

### macOS / Linux

- Build wheel / sdist
- Publish to PyPI or attach to Release

---

## 11. Future Expansion

- Consider Windows code signing after securing sponsorship
- Consider macOS .app packaging when there is demand
- Keep GUI and logic separated to allow future UI migration

---

End

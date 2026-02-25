## KiCad Snapshot

Repository: `https://github.com/tanakamasayuki/kicad-snapshot`

KiCad project snapshot and visual diff tool (PySide6 GUI).

### Requirements

- Python 3.11+
- `kicad-cli` (KiCad 8+ recommended)

### Setup (uv)

```bash
uv sync --dev
```

### Run

```bash
uv run kicad_snapshot
```

Alternative:

```bash
uv run python -m kicad_snapshot
```

### Package Structure

```text
.
├── pyproject.toml
├── src/
│   └── kicad_snapshot/
│       ├── __init__.py
│       └── __main__.py
├── SPEC.md
├── SPEC.ja.md
├── DEV_SPEC.md
└── DEV_SPEC.ja.md
```

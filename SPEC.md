# KiCad Snapshot --- Specification

## Overview

**KiCad Snapshot** is an open-source tool for backing up and visually
comparing KiCad projects.

It creates ZIP snapshots of KiCad projects using the same rules as
KiCad's built-in archive feature and allows visual diff comparison
between past and current states.

Git is optional. The core workflow is designed for general KiCad users
who may not use Git.

------------------------------------------------------------------------

## Goals

-   Provide visual comparison of KiCad project changes
-   Work without requiring Git knowledge
-   Never create automatic history
-   Only persist data on explicit user action
-   Keep comparisons temporary (no persistent cache)

------------------------------------------------------------------------

## Supported KiCad Versions

-   Windows / macOS / Linux
-   KiCad 8+ minimum
-   Lower versions may be supported when feasible
-   Uses external `kicad-cli`
-   Detection priority:
    -   user-configured path (highest)
    -   likely install locations
    -   PATH
-   When multiple candidates are found, the newest `kicad-cli` is used
    by default
-   Version is checked via `kicad-cli --version`
-   The detected `kicad-cli` path is shown in the UI and can be edited by
    the user
-   User changes are saved
-   No project file saving or upgrading is performed (non-destructive
    design)

------------------------------------------------------------------------

## Core Features

### 1. Snapshot (ZIP Backup)

-   Creates ZIP archive with include + exclude hybrid rules
-   Includes:
    -   `*.kicad_*` (for example `.kicad_pro`, `.kicad_sch`, `.kicad_pcb`, `.kicad_prl`)
    -   `*-lib-table` (for example `fp-lib-table`, `sym-lib-table`, `design-block-lib-table`)
-   Excludes (safety/performance):
    -   `.git/`, `.venv/`, `__pycache__/`, `node_modules/`
    -   `*.zip`, `*.log`, `*.tmp`, `*.bak`, `*.cache`

Reference (KiCad built-in backup):

-   KiCad creates an automatic backup when changes exist and more than
    5 minutes have passed since the last backup
-   Backups older than 25 generations are automatically removed
-   Generation count and auto-backup interval can be changed in KiCad settings

### 2. Diff Comparison

Supported comparisons:

-   ZIP vs Current
-   ZIP vs ZIP
-   (Optional) Git commit vs Current

Internal model:

All comparisons are performed between temporary extracted directories.

    Input A → temp extract
    Input B → temp extract
    ↓
    kicad-cli export
    ↓
    Image diff generation
    ↓
    Temporary cleanup

No persistent cache is stored.

### 3. Visual Diff

#### Schematic

-   Exported as SVG via `kicad-cli sch export svg`
-   Compared per sheet

#### PCB

-   Exported as SVG via `kicad-cli pcb export svg`
-   Top layer view
-   Bottom layer view

UI comparison modes: - A/B toggle - Highlight diff - (Optional) Slider
comparison

Diff generation: pixel-based image diff on rendered outputs.

### 4. Diff Report Output

Generates:

    diff_report/
      diff_sch_<sheet>.png
      diff_pcb_top.png
      diff_pcb_bottom.png
      comment.md

Default output location is the compared project folder. Users can change
the output folder.

User manually shares images and markdown as needed.

No automatic posting.

------------------------------------------------------------------------

## UX Principles

-   Comparison is temporary
-   History is explicit
-   No automatic background snapshots
-   No silent file modifications
-   Non-destructive behavior
-   `kicad-cli` auto-detection is transparent and user-overridable

------------------------------------------------------------------------

## Configuration Storage

There is no project folder requirement. User settings are stored in the
per-user config directory via `platformdirs` (e.g. `user_config_dir`).

------------------------------------------------------------------------

## What We Do

-   Create ZIP snapshots
-   Compare snapshots visually
-   Compare snapshot vs current
-   Generate diff report assets
-   Optional Git integration

------------------------------------------------------------------------

## What We Do NOT Do

-   Auto-backups
-   Persistent caching
-   Modify KiCad project files
-   Perform Git advanced operations (rebase/merge UI)
-   Automatically upload images

------------------------------------------------------------------------

## UI Structure (Minimal)

### Screen 1 -- CLI / Project

-   Show detected `kicad-cli` path
-   If not found or not valid, prompt user to select path
-   If `kicad-cli --version` cannot be confirmed, do not proceed to next
    screen
-   Choose project from recent list or open new

### Screen 2 -- Snapshot List

-   Snapshot list
-   Compare with Current
-   Compare between Snapshots

### Screen 3 -- Diff Viewer

-   Schematic tab
-   PCB tab
-   Generate diff report assets

------------------------------------------------------------------------

## Branding

**Name:** KiCad Snapshot\
**Repository:** kicad-snapshot

Tagline:

> Snapshot for KiCad projects --- Visual backup & diff viewer

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from platformdirs import user_config_dir
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

APP_NAME = "KiCadSnapshot"
APP_AUTHOR = "KiCadSnapshot"
SETTINGS_FILE = "settings.toml"
MAX_RECENT = 20


@dataclass(frozen=True)
class CliCandidate:
    path: Path
    version: tuple[int, ...]
    version_text: str


class SettingsStore:
    def __init__(self) -> None:
        self.config_dir = Path(user_config_dir(APP_NAME, APP_AUTHOR))
        self.config_path = self.config_dir / SETTINGS_FILE

    def load(self) -> dict:
        if not self.config_path.exists():
            return {}
        try:
            import tomllib

            with self.config_path.open("rb") as fp:
                data = tomllib.load(fp)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def save(self, data: dict) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        text = self._to_toml(data)
        self.config_path.write_text(text, encoding="utf-8")

    def _to_toml(self, data: dict) -> str:
        lines: list[str] = []

        manual_cli = data.get("manual_cli_path")
        if isinstance(manual_cli, str):
            lines.append(f'manual_cli_path = {self._quote(manual_cli)}')

        output_dir = data.get("output_dir")
        if isinstance(output_dir, str):
            lines.append(f'output_dir = {self._quote(output_dir)}')

        recent = data.get("recent_projects", [])
        if isinstance(recent, list):
            normalized = [self._quote(str(item)) for item in recent[:MAX_RECENT]]
            lines.append(f"recent_projects = [{', '.join(normalized)}]")

        lines.append("")
        return "\n".join(lines)

    @staticmethod
    def _quote(value: str) -> str:
        escaped = (
            value.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
        )
        return f'"{escaped}"'


def parse_version_text(raw: str) -> tuple[tuple[int, ...] | None, str]:
    match = re.search(r"(\d+(?:\.\d+)+)", raw)
    if not match:
        return None, raw.strip()

    version_text = match.group(1)
    try:
        version_tuple = tuple(int(part) for part in version_text.split("."))
    except ValueError:
        return None, raw.strip()
    return version_tuple, version_text


def probe_kicad_cli(path: Path) -> CliCandidate | None:
    try:
        result = subprocess.run(
            [str(path), "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except Exception:
        return None

    output = (result.stdout or "").strip() or (result.stderr or "").strip()
    version, version_text = parse_version_text(output)
    if result.returncode != 0 or version is None:
        return None

    return CliCandidate(path=path, version=version, version_text=version_text)


def discover_kicad_cli_candidates(manual_path: str | None) -> list[CliCandidate]:
    checked: set[Path] = set()
    candidates: list[CliCandidate] = []

    for candidate_path in iter_candidate_paths(manual_path):
        path = candidate_path.expanduser()
        if not path.exists() or path.is_dir():
            continue

        try:
            resolved = path.resolve()
        except Exception:
            resolved = path

        if resolved in checked:
            continue
        checked.add(resolved)

        candidate = probe_kicad_cli(resolved)
        if candidate:
            candidates.append(candidate)

    return candidates


def iter_candidate_paths(manual_path: str | None) -> Iterable[Path]:
    if manual_path:
        yield Path(manual_path)

    for p in likely_install_paths():
        yield p

    from_path = shutil.which("kicad-cli")
    if from_path:
        yield Path(from_path)


def likely_install_paths() -> list[Path]:
    candidates: list[Path] = []

    if sys.platform.startswith("win"):
        roots = [
            os.environ.get("ProgramFiles"),
            os.environ.get("ProgramFiles(x86)"),
            r"C:\Program Files",
            r"C:\Program Files (x86)",
        ]
        for root in roots:
            if not root:
                continue
            root_path = Path(root)
            if not root_path.exists():
                continue
            candidates.extend(root_path.glob("KiCad/*/bin/kicad-cli.exe"))
            candidates.extend(root_path.glob("KiCad/bin/kicad-cli.exe"))
    else:
        unix_paths = [
            "/usr/bin/kicad-cli",
            "/usr/local/bin/kicad-cli",
            "/snap/bin/kicad-cli",
            "/opt/homebrew/bin/kicad-cli",
            "/opt/local/bin/kicad-cli",
            "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli",
        ]
        candidates.extend(Path(p) for p in unix_paths)

    return candidates


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("KiCad Snapshot")
        self.setMinimumSize(960, 580)

        self.settings_store = SettingsStore()
        self.settings = self.settings_store.load()
        self.cli_candidate: CliCandidate | None = None

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(24, 24, 24, 24)
        root_layout.setSpacing(18)

        title = QLabel("KiCad Snapshot")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)

        subtitle = QLabel("Startup: CLI validation + project selection")
        subtitle.setStyleSheet("color: #666666;")

        root_layout.addWidget(title)
        root_layout.addWidget(subtitle)

        content = QGridLayout()
        content.setHorizontalSpacing(18)
        content.setVerticalSpacing(18)
        root_layout.addLayout(content)

        self.cli_box = QGroupBox("1) Path Check")
        cli_layout = QVBoxLayout(self.cli_box)
        cli_layout.setSpacing(10)

        path_row = QHBoxLayout()
        path_label = QLabel("kicad-cli path")
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Select kicad-cli executable")
        self.path_input.editingFinished.connect(self.on_path_edited)
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.select_cli_path)
        self.detect_btn = QPushButton("Auto Detect")
        self.detect_btn.clicked.connect(self.auto_detect_cli)
        path_row.addWidget(path_label)
        path_row.addWidget(self.path_input, 1)
        path_row.addWidget(self.browse_btn)
        path_row.addWidget(self.detect_btn)

        self.status = QLabel("Status: Checking...")

        git_row = QHBoxLayout()
        git_label = QLabel("git path (optional)")
        self.git_path_input = QLineEdit()
        self.git_path_input.setReadOnly(True)
        git_row.addWidget(git_label)
        git_row.addWidget(self.git_path_input, 1)

        self.git_status = QLabel("Git: Checking...")

        cli_layout.addLayout(path_row)
        cli_layout.addWidget(self.status)
        cli_layout.addLayout(git_row)
        cli_layout.addWidget(self.git_status)

        self.project_box = QGroupBox("2) Project")
        project_layout = QVBoxLayout(self.project_box)
        project_layout.setSpacing(10)

        project_hint = QLabel("Choose from recent projects or open a new one")
        project_hint.setStyleSheet("color: #666666;")

        self.recent_list = QListWidget()
        self.recent_list.itemSelectionChanged.connect(self.update_next_state)
        self.recent_list.itemDoubleClicked.connect(self.on_project_chosen)

        actions = QHBoxLayout()
        self.open_btn = QPushButton("Open Project...")
        self.open_btn.clicked.connect(self.open_project)
        self.remove_btn = QPushButton("Remove from list")
        self.remove_btn.clicked.connect(self.remove_project)
        actions.addWidget(self.open_btn)
        actions.addWidget(self.remove_btn)
        actions.addItem(QSpacerItem(10, 10))
        actions.addStretch(1)

        project_layout.addWidget(project_hint)
        project_layout.addWidget(self.recent_list, 1)
        project_layout.addLayout(actions)

        next_box = QGroupBox("3) Next")
        next_layout = QVBoxLayout(next_box)
        next_layout.setSpacing(10)

        self.next_hint = QLabel(
            "Continue is enabled only when CLI version is confirmed and a project is selected."
        )
        self.next_hint.setWordWrap(True)

        self.proceed_btn = QPushButton("Continue to Snapshot / Compare")
        self.proceed_btn.setEnabled(False)
        self.proceed_btn.clicked.connect(self.on_continue)

        next_layout.addWidget(self.next_hint)
        next_layout.addWidget(self.proceed_btn)

        content.addWidget(self.cli_box, 0, 0)
        content.addWidget(self.project_box, 1, 0)
        content.addWidget(next_box, 0, 1)

        content.setRowStretch(1, 1)
        content.setColumnStretch(0, 3)
        content.setColumnStretch(1, 2)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("color: #dddddd;")
        root_layout.addWidget(divider)

        self.footer = QLabel("Settings are saved as TOML in user config directory.")
        self.footer.setStyleSheet("color: #999999;")
        self.footer.setAlignment(Qt.AlignRight)
        root_layout.addWidget(self.footer)

        self.setCentralWidget(root)

        self.load_recent_projects()
        self.auto_detect_cli(initial=True)
        self.detect_git()

    def load_recent_projects(self) -> None:
        self.recent_list.clear()
        recent = self.settings.get("recent_projects", [])
        if not isinstance(recent, list):
            return

        for item in recent:
            path = str(item)
            self.recent_list.addItem(QListWidgetItem(path))

    def save_settings(self) -> None:
        recent: list[str] = []
        for i in range(self.recent_list.count()):
            recent.append(self.recent_list.item(i).text())

        self.settings["recent_projects"] = recent[:MAX_RECENT]
        self.settings_store.save(self.settings)

    def selected_project(self) -> str | None:
        item = self.recent_list.currentItem()
        return item.text() if item else None

    def update_status(self, ok: bool, message: str) -> None:
        self.status.setText(message)
        self.status.setStyleSheet("color: #2b7a0b;" if ok else "color: #b00020;")

    def update_next_state(self) -> None:
        can_continue = self.cli_candidate is not None and self.selected_project() is not None
        self.proceed_btn.setEnabled(can_continue)

    def select_cli_path(self) -> None:
        default_path = self.path_input.text().strip()
        selected, _ = QFileDialog.getOpenFileName(
            self,
            "Select kicad-cli",
            default_path,
            "Executable (*.exe);;All Files (*)",
        )
        if not selected:
            return

        self.path_input.setText(selected)
        self.validate_manual_cli(selected)

    def on_path_edited(self) -> None:
        path = self.path_input.text().strip()
        if not path:
            self.cli_candidate = None
            self.update_status(False, "Status: kicad-cli path is empty")
            self.settings.pop("manual_cli_path", None)
            self.save_settings()
            self.update_next_state()
            return
        self.validate_manual_cli(path)

    def validate_manual_cli(self, path_text: str) -> None:
        path = Path(path_text)
        candidate = probe_kicad_cli(path)
        if not candidate:
            self.cli_candidate = None
            self.update_status(
                False,
                "Status: invalid CLI path or `kicad-cli --version` failed",
            )
            self.settings["manual_cli_path"] = str(path)
            self.save_settings()
            self.update_next_state()
            return

        self.cli_candidate = candidate
        self.path_input.setText(str(candidate.path))
        self.settings["manual_cli_path"] = str(candidate.path)
        self.save_settings()
        self.update_status(True, f"Status: OK (version {candidate.version_text})")
        self.update_next_state()

    def auto_detect_cli(self, initial: bool = False) -> None:
        manual = self.settings.get("manual_cli_path")
        manual_path = str(manual) if isinstance(manual, str) and manual else None

        candidates = discover_kicad_cli_candidates(manual_path)
        if not candidates:
            self.cli_candidate = None
            self.update_status(False, "Status: kicad-cli not detected. Please set path.")
            if initial and manual_path:
                self.path_input.setText(manual_path)
            self.update_next_state()
            return

        best = max(candidates, key=lambda c: c.version)
        self.cli_candidate = best
        self.path_input.setText(str(best.path))

        if not manual_path:
            self.settings["manual_cli_path"] = str(best.path)
            self.save_settings()

        self.update_status(True, f"Status: OK (version {best.version_text})")
        self.update_next_state()

    def detect_git(self) -> None:
        git_path = shutil.which("git")
        if not git_path:
            self.git_path_input.setText("")
            self.git_status.setText("Git: not detected (optional)")
            self.git_status.setStyleSheet("color: #9a6700;")
            return

        self.git_path_input.setText(git_path)
        try:
            result = subprocess.run(
                [git_path, "--version"],
                check=False,
                capture_output=True,
                text=True,
                timeout=2,
            )
        except Exception:
            self.git_status.setText("Git: path found, but version check failed (optional)")
            self.git_status.setStyleSheet("color: #9a6700;")
            return

        if result.returncode == 0:
            version_text = result.stdout.strip() or result.stderr.strip()
            if version_text:
                self.git_status.setText(f"Git: OK ({version_text})")
            else:
                self.git_status.setText("Git: OK")
            self.git_status.setStyleSheet("color: #2b7a0b;")
            return

        self.git_status.setText("Git: path found, but version check failed (optional)")
        self.git_status.setStyleSheet("color: #9a6700;")

    def open_project(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(
            self,
            "Open KiCad Project",
            "",
            "KiCad Project (*.kicad_pro);;All Files (*)",
        )
        if not selected:
            return

        self.add_recent_project(selected)

    def add_recent_project(self, project_path: str) -> None:
        normalized = str(Path(project_path))

        for i in range(self.recent_list.count()):
            if self.recent_list.item(i).text() == normalized:
                self.recent_list.takeItem(i)
                break

        self.recent_list.insertItem(0, normalized)
        while self.recent_list.count() > MAX_RECENT:
            self.recent_list.takeItem(self.recent_list.count() - 1)

        self.recent_list.setCurrentRow(0)
        self.save_settings()
        self.update_next_state()

    def remove_project(self) -> None:
        row = self.recent_list.currentRow()
        if row < 0:
            return

        self.recent_list.takeItem(row)
        self.save_settings()
        self.update_next_state()

    def on_project_chosen(self) -> None:
        self.update_next_state()

    def on_continue(self) -> None:
        if not self.cli_candidate:
            QMessageBox.warning(
                self,
                "KiCad CLI Required",
                "kicad-cli path is not valid. Please fix CLI settings.",
            )
            return

        project = self.selected_project()
        if not project:
            QMessageBox.warning(
                self,
                "Project Required",
                "Select a project from the list or open a new one.",
            )
            return

        default_output = str(Path(project).resolve().parent / "diff_report")
        self.settings["output_dir"] = default_output
        self.save_settings()

        QMessageBox.information(
            self,
            "Ready",
            (
                "Startup checks passed.\n\n"
                f"CLI: {self.cli_candidate.path}\n"
                f"Project: {project}\n"
                f"Default output: {default_output}"
            ),
        )


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

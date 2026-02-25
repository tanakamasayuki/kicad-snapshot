from __future__ import annotations

import locale
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

from platformdirs import user_config_dir
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QImage, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QListView,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSpacerItem,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

APP_NAME = "KiCadSnapshot"
APP_AUTHOR = "KiCadSnapshot"
SETTINGS_FILE = "settings.toml"
MAX_RECENT = 20
DEFAULT_TIMELINE_LIMIT = 50
BACKUP_DIR_NAME = "snapshot_backups"
SUPPORTED_LANGUAGES = ("en", "ja", "zh", "fr", "de")

LANGUAGE_LABELS = {
    "en": "English",
    "ja": "Japanese",
    "zh": "Chinese",
    "fr": "French",
    "de": "German",
}

TRANSLATIONS = {
    "en": {
        "window_title": "KiCad Snapshot",
        "title": "KiCad Snapshot",
        "subtitle": "Startup: CLI validation + project selection",
        "language": "Language",
        "group_path": "1) Path Check",
        "cli_path": "kicad-cli path",
        "cli_placeholder": "Select kicad-cli executable",
        "browse": "Browse...",
        "auto_detect": "Auto Detect",
        "status_checking": "Status: Checking...",
        "status_empty": "Status: kicad-cli path is empty",
        "status_invalid": "Status: invalid CLI path or `kicad-cli --version` failed",
        "status_not_detected": "Status: kicad-cli not detected. Please set path.",
        "status_ok": "Status: OK (version {version})",
        "git_path": "git path (optional)",
        "git_refresh": "Refresh Git",
        "git_checking": "Git: Checking...",
        "git_not_detected": "Git: not detected (optional)",
        "git_check_failed": "Git: path found, but version check failed (optional)",
        "git_ok": "Git: OK ({version})",
        "git_ok_plain": "Git: OK",
        "group_project": "2) Project",
        "project_hint": "Choose from recent projects or open a new one",
        "open_project": "Open Project...",
        "remove_project": "Remove from list",
        "group_next": "3) Next",
        "next_hint": "Continue is enabled only when CLI version is confirmed and a project is selected.",
        "continue": "Continue to Snapshot / Compare",
        "footer": "Settings file: {path}",
        "dlg_select_cli": "Select kicad-cli",
        "dlg_open_project": "Open KiCad Project",
        "warning_cli_title": "KiCad CLI Required",
        "warning_cli_text": "kicad-cli path is not valid. Please fix CLI settings.",
        "warning_project_title": "Project Required",
        "warning_project_text": "Select a project from the list or open a new one.",
        "ready_title": "Ready",
        "ready_text": "Startup checks passed.\n\nCLI: {cli}\nProject: {project}\nDefault output: {output}",
        "compare_window_title": "Snapshot Compare",
        "compare_filter": "Source",
        "compare_filter_both": "Both",
        "compare_filter_backup": "Backup only",
        "compare_filter_git": "Git only",
        "compare_refresh": "Refresh",
        "compare_limit": "Limit",
        "compare_timeline": "Timeline",
        "compare_create_backup": "Create Backup",
        "compare_backup_memo": "Memo",
        "compare_backup_memo_placeholder": "optional",
        "compare_backup_note": "KiCad built-in backup: auto backup after 5 minutes, auto cleanup after 25 generations (configurable in KiCad settings).",
        "compare_git_group": "Git Operations",
        "compare_git_msg_placeholder": "Commit message",
        "compare_git_commit": "Commit",
        "compare_git_push": "Push",
        "compare_git_pull": "Pull",
        "compare_from": "Compare from (Before)",
        "compare_to": "Compare to (After)",
        "compare_current_project": "[Current] Project files",
        "compare_run": "Compare",
        "compare_git_unavailable": "Git is unavailable for this project.",
        "compare_need_two": "Select both compare targets.",
        "compare_same": "Please choose different items.",
        "compare_started_title": "Compare",
        "compare_backup_title": "Backup",
        "compare_started_text": "Comparison requested.\n\nBefore: {from_item}\nAfter: {to_item}",
        "compare_result_title": "Compare Result",
        "compare_result_summary": "Added: {added}  Removed: {removed}  Changed: {changed}  Unchanged: {unchanged}",
        "compare_result_files": "Changed Files",
        "compare_result_no_diff": "No changed files.",
        "compare_result_error": "Failed to compare: {error}",
        "compare_close": "Close",
        "compare_visual_title": "Visual Diff",
        "compare_visual_file": "File",
        "compare_visual_before": "Before",
        "compare_visual_after": "After",
        "compare_visual_empty": "(empty)",
        "compare_image_title": "Image Diff",
        "compare_image_target": "Target",
        "compare_image_render": "Render",
        "compare_image_status": "Select a sheet/page target and render.",
        "compare_image_no_targets": "No renderable sheet/page target found.",
        "compare_image_missing_side": "This target does not exist on one side. Missing side is shown as empty.",
        "compare_image_pcb_board": "PCB / board",
        "compare_image_before": "Before Image",
        "compare_image_after": "After Image",
        "compare_image_diff": "Diff Image",
        "compare_image_not_available": "Image diff is available for .kicad_sch/.kicad_pcb content.",
        "compare_image_zoom_out": "Zoom Out",
        "compare_image_zoom_in": "Zoom In",
        "compare_image_zoom_fit": "Fit",
        "compare_backup_created": "Backup created: {path}",
        "compare_git_commit_need_msg": "Commit message is required.",
        "compare_git_ok_title": "Git",
        "compare_git_fail_title": "Git Error",
        "compare_git_commit_ok": "Commit completed.",
        "compare_git_push_ok": "Push completed.",
        "compare_git_pull_ok": "Pull completed.",
    },
    "ja": {
        "window_title": "KiCad Snapshot",
        "title": "KiCad Snapshot",
        "subtitle": "起動: CLI確認 + プロジェクト選択",
        "language": "言語",
        "group_path": "1) パス確認",
        "cli_path": "kicad-cli パス",
        "cli_placeholder": "kicad-cli 実行ファイルを選択",
        "browse": "参照...",
        "auto_detect": "自動検出",
        "status_checking": "状態: 確認中...",
        "status_empty": "状態: kicad-cli パスが空です",
        "status_invalid": "状態: CLIパス不正、または `kicad-cli --version` 失敗",
        "status_not_detected": "状態: kicad-cli が未検出です。パスを設定してください。",
        "status_ok": "状態: OK (バージョン {version})",
        "git_path": "git パス（任意）",
        "git_refresh": "Git更新",
        "git_checking": "Git: 確認中...",
        "git_not_detected": "Git: 未検出（任意）",
        "git_check_failed": "Git: パスはあるがバージョン確認失敗（任意）",
        "git_ok": "Git: OK ({version})",
        "git_ok_plain": "Git: OK",
        "group_project": "2) プロジェクト",
        "project_hint": "最近使った一覧から選択、または新規で開く",
        "open_project": "プロジェクトを開く...",
        "remove_project": "一覧から削除",
        "group_next": "3) 次へ",
        "next_hint": "CLIバージョン確認済みかつプロジェクト選択済みの場合のみ続行できます。",
        "continue": "スナップショット / 比較へ進む",
        "footer": "設定ファイル: {path}",
        "dlg_select_cli": "kicad-cli を選択",
        "dlg_open_project": "KiCad プロジェクトを開く",
        "warning_cli_title": "KiCad CLI が必要です",
        "warning_cli_text": "kicad-cli のパスが無効です。CLI設定を修正してください。",
        "warning_project_title": "プロジェクトが必要です",
        "warning_project_text": "一覧からプロジェクトを選択するか新規で開いてください。",
        "ready_title": "準備完了",
        "ready_text": "起動チェックが完了しました。\n\nCLI: {cli}\nProject: {project}\n既定の出力先: {output}",
        "compare_window_title": "スナップショット比較",
        "compare_filter": "ソース",
        "compare_filter_both": "両方",
        "compare_filter_backup": "バックアップのみ",
        "compare_filter_git": "Gitのみ",
        "compare_refresh": "更新",
        "compare_limit": "上限",
        "compare_timeline": "タイムライン",
        "compare_create_backup": "バックアップ作成",
        "compare_backup_memo": "メモ",
        "compare_backup_memo_placeholder": "任意",
        "compare_backup_note": "KiCad標準バックアップ: 最終バックアップから5分経過で自動作成、25世代超は自動削除（KiCad設定で変更可能）。",
        "compare_git_group": "Git操作",
        "compare_git_msg_placeholder": "コミットメッセージ",
        "compare_git_commit": "コミット",
        "compare_git_push": "プッシュ",
        "compare_git_pull": "プル",
        "compare_from": "比較元 (Before)",
        "compare_to": "比較先 (After)",
        "compare_current_project": "[現在] プロジェクトファイル",
        "compare_run": "比較",
        "compare_git_unavailable": "このプロジェクトではGitを利用できません。",
        "compare_need_two": "比較対象を2つ選択してください。",
        "compare_same": "異なる項目を選択してください。",
        "compare_started_title": "比較",
        "compare_backup_title": "バックアップ",
        "compare_started_text": "比較を開始します。\n\nBefore: {from_item}\nAfter: {to_item}",
        "compare_result_title": "比較結果",
        "compare_result_summary": "追加: {added}  削除: {removed}  変更: {changed}  変更なし: {unchanged}",
        "compare_result_files": "差分ファイル",
        "compare_result_no_diff": "差分ファイルはありません。",
        "compare_result_error": "比較に失敗しました: {error}",
        "compare_close": "閉じる",
        "compare_visual_title": "ビジュアル差分",
        "compare_visual_file": "ファイル",
        "compare_visual_before": "Before",
        "compare_visual_after": "After",
        "compare_visual_empty": "(空)",
        "compare_image_title": "画像差分",
        "compare_image_target": "対象",
        "compare_image_render": "描画",
        "compare_image_status": "シート/ページを選択して描画してください。",
        "compare_image_no_targets": "描画可能なシート/ページが見つかりません。",
        "compare_image_missing_side": "片側に存在しないため、無い側は空表示になります。",
        "compare_image_pcb_board": "PCB / 全体",
        "compare_image_before": "Before 画像",
        "compare_image_after": "After 画像",
        "compare_image_diff": "差分画像",
        "compare_image_not_available": ".kicad_sch/.kicad_pcb が無い場合は画像差分を生成できません。",
        "compare_image_zoom_out": "縮小",
        "compare_image_zoom_in": "拡大",
        "compare_image_zoom_fit": "フィット",
        "compare_backup_created": "バックアップを作成しました: {path}",
        "compare_git_commit_need_msg": "コミットメッセージを入力してください。",
        "compare_git_ok_title": "Git",
        "compare_git_fail_title": "Gitエラー",
        "compare_git_commit_ok": "コミット完了。",
        "compare_git_push_ok": "プッシュ完了。",
        "compare_git_pull_ok": "プル完了。",
    },
    "zh": {
        "window_title": "KiCad Snapshot",
        "title": "KiCad Snapshot",
        "subtitle": "启动: CLI 验证 + 项目选择",
        "language": "语言",
        "group_path": "1) 路径检查",
        "cli_path": "kicad-cli 路径",
        "cli_placeholder": "选择 kicad-cli 可执行文件",
        "browse": "浏览...",
        "auto_detect": "自动检测",
        "status_checking": "状态: 检查中...",
        "status_empty": "状态: kicad-cli 路径为空",
        "status_invalid": "状态: CLI 路径无效或 `kicad-cli --version` 失败",
        "status_not_detected": "状态: 未检测到 kicad-cli。请设置路径。",
        "status_ok": "状态: 正常 (版本 {version})",
        "git_path": "git 路径（可选）",
        "git_checking": "Git: 检查中...",
        "git_not_detected": "Git: 未检测到（可选）",
        "git_check_failed": "Git: 已找到路径，但版本检查失败（可选）",
        "git_ok": "Git: 正常 ({version})",
        "git_ok_plain": "Git: 正常",
        "group_project": "2) 项目",
        "project_hint": "从最近项目中选择，或打开新项目",
        "open_project": "打开项目...",
        "remove_project": "从列表移除",
        "group_next": "3) 下一步",
        "next_hint": "仅当 CLI 版本已确认且已选择项目时可继续。",
        "continue": "继续到快照 / 对比",
        "footer": "设置文件: {path}",
        "dlg_select_cli": "选择 kicad-cli",
        "dlg_open_project": "打开 KiCad 项目",
        "warning_cli_title": "需要 KiCad CLI",
        "warning_cli_text": "kicad-cli 路径无效。请修正 CLI 设置。",
        "warning_project_title": "需要项目",
        "warning_project_text": "请从列表中选择项目，或打开新项目。",
        "ready_title": "就绪",
        "ready_text": "启动检查已通过。\n\nCLI: {cli}\nProject: {project}\n默认输出目录: {output}",
    },
    "fr": {
        "window_title": "KiCad Snapshot",
        "title": "KiCad Snapshot",
        "subtitle": "Demarrage: validation CLI + selection du projet",
        "language": "Langue",
        "group_path": "1) Verification des chemins",
        "cli_path": "Chemin kicad-cli",
        "cli_placeholder": "Selectionnez l'executable kicad-cli",
        "browse": "Parcourir...",
        "auto_detect": "Detection auto",
        "status_checking": "Statut: verification...",
        "status_empty": "Statut: chemin kicad-cli vide",
        "status_invalid": "Statut: chemin CLI invalide ou echec de `kicad-cli --version`",
        "status_not_detected": "Statut: kicad-cli introuvable. Configurez le chemin.",
        "status_ok": "Statut: OK (version {version})",
        "git_path": "Chemin git (optionnel)",
        "git_checking": "Git: verification...",
        "git_not_detected": "Git: introuvable (optionnel)",
        "git_check_failed": "Git: chemin trouve, mais verification de version echouee (optionnel)",
        "git_ok": "Git: OK ({version})",
        "git_ok_plain": "Git: OK",
        "group_project": "2) Projet",
        "project_hint": "Choisissez dans les projets recents ou ouvrez un nouveau projet",
        "open_project": "Ouvrir un projet...",
        "remove_project": "Retirer de la liste",
        "group_next": "3) Suivant",
        "next_hint": "Continuer est possible seulement si la version CLI est valide et qu'un projet est selectionne.",
        "continue": "Continuer vers Snapshot / Compare",
        "footer": "Fichier de configuration: {path}",
        "dlg_select_cli": "Selectionner kicad-cli",
        "dlg_open_project": "Ouvrir un projet KiCad",
        "warning_cli_title": "KiCad CLI requis",
        "warning_cli_text": "Le chemin kicad-cli est invalide. Corrigez les parametres CLI.",
        "warning_project_title": "Projet requis",
        "warning_project_text": "Selectionnez un projet dans la liste ou ouvrez-en un nouveau.",
        "ready_title": "Pret",
        "ready_text": "Les verifications de demarrage sont validees.\n\nCLI: {cli}\nProjet: {project}\nSortie par defaut: {output}",
    },
    "de": {
        "window_title": "KiCad Snapshot",
        "title": "KiCad Snapshot",
        "subtitle": "Start: CLI-Prufung + Projektauswahl",
        "language": "Sprache",
        "group_path": "1) Pfadprufung",
        "cli_path": "kicad-cli Pfad",
        "cli_placeholder": "kicad-cli Programm auswahlen",
        "browse": "Durchsuchen...",
        "auto_detect": "Automatisch erkennen",
        "status_checking": "Status: wird gepruft...",
        "status_empty": "Status: kicad-cli Pfad ist leer",
        "status_invalid": "Status: CLI-Pfad ungultig oder `kicad-cli --version` fehlgeschlagen",
        "status_not_detected": "Status: kicad-cli nicht gefunden. Bitte Pfad setzen.",
        "status_ok": "Status: OK (Version {version})",
        "git_path": "git Pfad (optional)",
        "git_checking": "Git: wird gepruft...",
        "git_not_detected": "Git: nicht gefunden (optional)",
        "git_check_failed": "Git: Pfad gefunden, aber Versionsprufung fehlgeschlagen (optional)",
        "git_ok": "Git: OK ({version})",
        "git_ok_plain": "Git: OK",
        "group_project": "2) Projekt",
        "project_hint": "Aus letzter Projektliste auswahlen oder neues Projekt offnen",
        "open_project": "Projekt offnen...",
        "remove_project": "Aus Liste entfernen",
        "group_next": "3) Weiter",
        "next_hint": "Weiter nur moglich, wenn CLI-Version bestatigt und ein Projekt ausgewahlt wurde.",
        "continue": "Weiter zu Snapshot / Compare",
        "footer": "Einstellungsdatei: {path}",
        "dlg_select_cli": "kicad-cli auswahlen",
        "dlg_open_project": "KiCad-Projekt offnen",
        "warning_cli_title": "KiCad CLI erforderlich",
        "warning_cli_text": "kicad-cli Pfad ist ungueltig. Bitte CLI-Einstellungen korrigieren.",
        "warning_project_title": "Projekt erforderlich",
        "warning_project_text": "Projekt aus der Liste auswahlen oder neues Projekt offnen.",
        "ready_title": "Bereit",
        "ready_text": "Startprufungen bestanden.\n\nCLI: {cli}\nProjekt: {project}\nStandardausgabe: {output}",
    },
}


@dataclass(frozen=True)
class CliCandidate:
    path: Path
    version: tuple[int, ...]
    version_text: str


@dataclass(frozen=True)
class SnapshotItem:
    source: str
    identifier: str
    label: str
    timestamp: float


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

        language = data.get("language")
        if isinstance(language, str):
            lines.append(f'language = {self._quote(language)}')

        compare_filter = data.get("compare_filter")
        if isinstance(compare_filter, str):
            lines.append(f'compare_filter = {self._quote(compare_filter)}')

        compare_timeline_limit = data.get("compare_timeline_limit")
        if isinstance(compare_timeline_limit, int):
            lines.append(f"compare_timeline_limit = {compare_timeline_limit}")

        last_project = data.get("last_project")
        if isinstance(last_project, str):
            lines.append(f'last_project = {self._quote(last_project)}')

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


def run_git(project_dir: Path, args: list[str], git_path: str | None) -> subprocess.CompletedProcess[str]:
    executable = git_path or "git"
    return subprocess.run(
        [executable, "-C", str(project_dir), *args],
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )


def run_git_bytes(project_dir: Path, args: list[str], git_path: str | None) -> subprocess.CompletedProcess[bytes]:
    executable = git_path or "git"
    return subprocess.run(
        [executable, "-C", str(project_dir), *args],
        check=False,
        capture_output=True,
        timeout=20,
    )


def detect_git_repo_root(project_dir: Path, git_path: str | None) -> Path | None:
    try:
        result = run_git(project_dir, ["rev-parse", "--show-toplevel"], git_path)
    except Exception:
        return None
    if result.returncode != 0:
        return None
    root = (result.stdout or "").strip()
    if not root:
        return None
    path = Path(root)
    return path if path.exists() else None


def backup_whitelist_paths(project_dir: Path) -> list[Path]:
    file_names = {"fp-lib-table", "sym-lib-table", "design-block-lib-table"}
    suffixes = {
        ".kicad_pro",
        ".kicad_sch",
        ".kicad_pcb",
        ".kicad_sym",
        ".kicad_mod",
        ".kicad_dru",
        ".kicad_wks",
    }

    selected: list[Path] = []
    for path in project_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.name in file_names or path.suffix in suffixes:
            selected.append(path)
    return selected


def is_backup_target_path(rel_path: str) -> bool:
    file_names = {"fp-lib-table", "sym-lib-table", "design-block-lib-table"}
    suffixes = {
        ".kicad_pro",
        ".kicad_sch",
        ".kicad_pcb",
        ".kicad_sym",
        ".kicad_mod",
        ".kicad_dru",
        ".kicad_wks",
    }

    normalized = rel_path.replace("\\", "/").strip("/")
    if not normalized:
        return False
    base_name = Path(normalized).name
    if base_name in file_names:
        return True
    return Path(base_name).suffix in suffixes


def build_current_project_map(project_file: Path) -> dict[str, bytes]:
    project_dir = project_file.resolve().parent
    result: dict[str, bytes] = {}
    for path in backup_whitelist_paths(project_dir):
        rel = path.relative_to(project_dir).as_posix()
        try:
            result[rel] = path.read_bytes()
        except OSError:
            continue
    return result


def build_backup_zip_map(zip_path: Path) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    with zipfile.ZipFile(zip_path, "r") as zf:
        for name in zf.namelist():
            normalized = name.replace("\\", "/").strip("/")
            if not normalized or normalized.endswith("/"):
                continue
            if not is_backup_target_path(normalized):
                continue
            try:
                result[normalized] = zf.read(name)
            except KeyError:
                continue
    return result


def build_git_commit_map(project_file: Path, commit_hash: str, git_path: str | None) -> dict[str, bytes]:
    project_dir = project_file.resolve().parent
    repo_root = detect_git_repo_root(project_dir, git_path)
    if repo_root is None:
        return {}

    try:
        rel_project = project_dir.relative_to(repo_root).as_posix()
    except ValueError:
        rel_project = "."

    args = ["ls-tree", "-r", "--name-only", commit_hash]
    if rel_project != ".":
        args.extend(["--", rel_project])
    list_result = run_git(repo_root, args, git_path)
    if list_result.returncode != 0:
        return {}

    result: dict[str, bytes] = {}
    for line in (list_result.stdout or "").splitlines():
        repo_path = line.strip()
        if not repo_path:
            continue
        if rel_project != ".":
            prefix = rel_project + "/"
            if not repo_path.startswith(prefix):
                continue
            rel_path = repo_path[len(prefix):]
        else:
            rel_path = repo_path
        if not is_backup_target_path(rel_path):
            continue

        show_result = run_git_bytes(repo_root, ["show", f"{commit_hash}:{repo_path}"], git_path)
        if show_result.returncode != 0:
            continue
        result[rel_path] = show_result.stdout
    return result


def compare_file_maps(before: dict[str, bytes], after: dict[str, bytes]) -> tuple[list[str], list[str], list[str], list[str]]:
    before_keys = set(before.keys())
    after_keys = set(after.keys())
    added = sorted(after_keys - before_keys)
    removed = sorted(before_keys - after_keys)
    common = sorted(before_keys & after_keys)
    changed: list[str] = []
    unchanged: list[str] = []
    for key in common:
        if before[key] == after[key]:
            unchanged.append(key)
        else:
            changed.append(key)
    return added, removed, changed, unchanged


def write_file_map(root: Path, file_map: dict[str, bytes]) -> None:
    for rel, data in file_map.items():
        out_path = root / rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(data)


def first_matching_file(root: Path, suffix: str) -> Path | None:
    matches = sorted(root.rglob(f"*{suffix}"))
    if not matches:
        return None
    return matches[0]


def export_svg_bundle_with_kicad_cli(cli_path: Path, source_file: Path, out_dir: Path, kind: str) -> list[Path]:
    if kind == "sch":
        commands = [
            [str(cli_path), "sch", "export", "svg", str(source_file), "-o", str(out_dir)],
        ]
    elif kind == "pcb":
        # Try broad layer sets first to get a board-wide render on varying KiCad versions.
        commands = [
            [
                str(cli_path),
                "pcb",
                "export",
                "svg",
                "--layers",
                "F.Cu,B.Cu,F.SilkS,B.SilkS,Edge.Cuts",
                str(source_file),
                "-o",
                str(out_dir),
            ],
            [
                str(cli_path),
                "pcb",
                "export",
                "svg",
                "--layers",
                "F.Cu,B.Cu",
                str(source_file),
                "-o",
                str(out_dir),
            ],
            [str(cli_path), "pcb", "export", "svg", str(source_file), "-o", str(out_dir)],
        ]
    else:
        raise RuntimeError(f"Unsupported kind: {kind}")

    last_err = ""
    for cmd in commands:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=40)
        if result.returncode == 0:
            svgs = sorted(out_dir.rglob("*.svg"))
            if svgs:
                return svgs
            last_err = "No SVG exported by kicad-cli"
        else:
            last_err = (result.stderr or result.stdout or "").strip() or "kicad-cli export failed"
    raise RuntimeError(last_err or "kicad-cli export failed")


def render_svg_to_image(svg_path: Path) -> QImage:
    renderer = QSvgRenderer(str(svg_path))
    if not renderer.isValid():
        raise RuntimeError(f"Invalid SVG: {svg_path}")

    size = renderer.defaultSize()
    width = max(1, min(size.width() if size.width() > 0 else 1400, 2000))
    height = max(1, min(size.height() if size.height() > 0 else 1000, 2000))

    image = QImage(width, height, QImage.Format_ARGB32)
    image.fill(Qt.white)
    painter = QPainter(image)
    renderer.render(painter)
    painter.end()
    return image


def pad_image(image: QImage, width: int, height: int) -> QImage:
    if image.width() == width and image.height() == height:
        return image
    out = QImage(width, height, QImage.Format_ARGB32)
    out.fill(Qt.white)
    painter = QPainter(out)
    painter.drawImage(0, 0, image)
    painter.end()
    return out


def make_pixel_diff_image(before: QImage, after: QImage) -> QImage:
    width = max(before.width(), after.width())
    height = max(before.height(), after.height())
    b = pad_image(before, width, height)
    a = pad_image(after, width, height)

    diff = QImage(width, height, QImage.Format_ARGB32)
    diff.fill(Qt.white)

    for y in range(height):
        for x in range(width):
            bp = b.pixel(x, y)
            ap = a.pixel(x, y)
            if bp == ap:
                diff.setPixel(x, y, ap)
            else:
                # Highlight changed pixels in red.
                diff.setPixel(x, y, 0xFFFF4040)
    return diff


def normalize_image_sizes(before: QImage, after: QImage) -> tuple[QImage, QImage]:
    width = max(before.width(), after.width())
    height = max(before.height(), after.height())
    return pad_image(before, width, height), pad_image(after, width, height)


def sanitize_memo_for_filename(memo: str) -> str:
    text = memo.strip().replace(" ", "_")
    forbidden = set('/\\:*?"<>|')
    cleaned: list[str] = []
    for ch in text:
        if ch in forbidden:
            continue
        if ord(ch) < 32:
            continue
        if ch.isalnum() or ch in {"_", "-", "."}:
            cleaned.append(ch)
            continue
        # Allow general UTF-8 letters/symbols except risky filesystem characters.
        if ord(ch) >= 128:
            cleaned.append(ch)
    result = "".join(cleaned)
    return result.strip("._-")


def create_project_backup(project_file: Path, memo: str = "") -> Path:
    project_dir = project_file.resolve().parent
    project_name = project_file.stem
    backup_dir = project_dir / f"{project_dir.name}-backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    memo_part = sanitize_memo_for_filename(memo)
    base_name = f"{project_name}-{ts}"
    if memo_part:
        base_name = f"{base_name}-{memo_part}"
    zip_path = backup_dir / f"{base_name}.zip"
    index = 1
    while zip_path.exists():
        zip_path = backup_dir / f"{base_name}_{index}.zip"
        index += 1
    files = backup_whitelist_paths(project_dir)

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in files:
            arcname = file_path.relative_to(project_dir)
            zf.write(file_path, arcname=str(arcname))
    return zip_path


def collect_backup_items(project_file: Path, limit: int) -> list[SnapshotItem]:
    project_dir = project_file.resolve().parent
    local_named_backup_dir = project_dir / f"{project_dir.name}-backups"
    sibling_backup_dir = project_dir.parent / f"{project_dir.name}-backups"
    candidate_dirs = [
        project_dir / BACKUP_DIR_NAME,
        project_dir / "backup",
        project_dir / "backups",
        local_named_backup_dir,
        sibling_backup_dir,
    ]

    seen: set[Path] = set()
    zip_paths: list[Path] = []
    for backup_dir in candidate_dirs:
        if not backup_dir.exists() or not backup_dir.is_dir():
            continue
        for path in backup_dir.iterdir():
            if not path.is_file() or path.suffix.lower() != ".zip":
                continue
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            zip_paths.append(path)

    # Also accept project-root snapshot archives (common manual pattern).
    for path in project_dir.glob("snapshot*.zip"):
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        zip_paths.append(path)

    items: list[SnapshotItem] = []
    for path in zip_paths:
        try:
            stat = path.stat()
        except OSError:
            continue
        dt = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        items.append(
            SnapshotItem(
                source="backup",
                identifier=str(path),
                label=f"{dt}  {path.name}  [Backup]",
                timestamp=stat.st_mtime,
            )
        )
    items.sort(key=lambda x: x.timestamp, reverse=True)
    return items[:limit]


def collect_git_items(project_file: Path, git_path: str | None, limit: int) -> list[SnapshotItem]:
    project_dir = project_file.resolve().parent
    repo_root = detect_git_repo_root(project_dir, git_path)
    if not repo_root:
        return []

    try:
        result = run_git(
            repo_root,
            ["log", f"-n{limit}", "--pretty=format:%H%x1f%cI%x1f%s"],
            git_path,
        )
    except Exception:
        return []
    if result.returncode != 0:
        return []

    items: list[SnapshotItem] = []
    for line in (result.stdout or "").splitlines():
        parts = line.split("\x1f")
        if len(parts) != 3:
            continue
        commit_hash, iso_time, message = parts
        try:
            ts = datetime.fromisoformat(iso_time.replace("Z", "+00:00")).timestamp()
            ts_text = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
        short_hash = commit_hash[:10]
        items.append(
            SnapshotItem(
                source="git",
                identifier=commit_hash,
                label=f"{ts_text}  {short_hash}  {message}  [Git]",
                timestamp=ts,
            )
        )
    items.sort(key=lambda x: x.timestamp, reverse=True)
    return items[:limit]


def normalize_language(code: str | None) -> str:
    if not code:
        return "en"
    lowered = code.lower().replace("-", "_")
    base = lowered.split("_", 1)[0]
    if base in SUPPORTED_LANGUAGES:
        return base
    return "en"


def detect_environment_language() -> str:
    candidates = [
        os.environ.get("LC_ALL"),
        os.environ.get("LC_MESSAGES"),
        os.environ.get("LANG"),
        locale.getlocale()[0],
        locale.getdefaultlocale()[0] if hasattr(locale, "getdefaultlocale") else None,
    ]
    for item in candidates:
        lang = normalize_language(item)
        if lang != "en":
            return lang
    return "en"


class SnapshotCompareDialog(QDialog):
    def __init__(
        self,
        project_file: Path,
        cli_path: Path,
        git_path: str | None,
        language: str,
        translate,
        settings: dict,
        save_settings_cb,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.project_file = project_file.resolve()
        self.project_dir = self.project_file.parent
        self.cli_path = cli_path
        self.git_path = git_path
        self.language = language
        self.t = translate
        self.settings = settings
        self.save_settings_cb = save_settings_cb
        self.timeline_limit = self.resolve_timeline_limit()
        self.settings["compare_timeline_limit"] = self.timeline_limit
        self.save_settings_cb()
        self.timeline_limit_options = [20, 50, 100, 200, 500]

        self.all_items: list[SnapshotItem] = []
        self.backup_items: list[SnapshotItem] = []
        self.git_items: list[SnapshotItem] = []
        self.filtered_items: list[SnapshotItem] = []

        self.setMinimumSize(1000, 620)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        header = QHBoxLayout()
        self.filter_label = QLabel("")
        self.filter_group = QButtonGroup(self)
        self.filter_both_radio = QRadioButton("")
        self.filter_backup_radio = QRadioButton("")
        self.filter_git_radio = QRadioButton("")
        self.filter_group.addButton(self.filter_both_radio)
        self.filter_group.addButton(self.filter_backup_radio)
        self.filter_group.addButton(self.filter_git_radio)
        self.refresh_btn = QPushButton("")
        self.refresh_btn.clicked.connect(self.refresh_data)
        self.limit_label = QLabel("")
        self.limit_combo = QComboBox()
        self.backup_memo_label = QLabel("")
        self.backup_memo_input = QLineEdit()
        self.create_backup_btn = QPushButton("")
        self.create_backup_btn.clicked.connect(self.create_backup)
        header.addWidget(self.filter_label)
        header.addWidget(self.filter_both_radio)
        header.addWidget(self.filter_backup_radio)
        header.addWidget(self.filter_git_radio)
        header.addWidget(self.refresh_btn)
        header.addWidget(self.limit_label)
        header.addWidget(self.limit_combo)
        header.addStretch(1)
        header.addWidget(self.backup_memo_label)
        header.addWidget(self.backup_memo_input)
        header.addWidget(self.create_backup_btn)
        root.addLayout(header)

        self.backup_note_label = QLabel("")
        self.backup_note_label.setWordWrap(True)
        self.backup_note_label.setStyleSheet("color: #666666;")
        root.addWidget(self.backup_note_label)

        self.timeline_group = QGroupBox("")
        timeline_layout = QVBoxLayout(self.timeline_group)
        self.timeline_list = QListWidget()
        self.timeline_list.currentRowChanged.connect(self.on_timeline_row_changed)
        timeline_layout.addWidget(self.timeline_list)
        root.addWidget(self.timeline_group, 1)

        compare_group = QGroupBox("")
        compare_layout = QGridLayout(compare_group)
        self.compare_from_label = QLabel("")
        self.compare_to_label = QLabel("")
        self.compare_from_combo = QComboBox()
        self.compare_to_combo = QComboBox()
        from_view = QListView(self.compare_from_combo)
        to_view = QListView(self.compare_to_combo)
        from_view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        to_view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.compare_from_combo.setView(from_view)
        self.compare_to_combo.setView(to_view)
        self.compare_from_combo.setMaxVisibleItems(10)
        self.compare_to_combo.setMaxVisibleItems(10)
        self.compare_btn = QPushButton("")
        self.compare_btn.clicked.connect(self.run_compare)
        compare_layout.addWidget(self.compare_from_label, 0, 0)
        compare_layout.addWidget(self.compare_from_combo, 0, 1)
        compare_layout.addWidget(self.compare_to_label, 1, 0)
        compare_layout.addWidget(self.compare_to_combo, 1, 1)
        compare_layout.addWidget(self.compare_btn, 0, 2, 2, 1)
        root.addWidget(compare_group)

        self.git_group = QGroupBox("")
        git_layout = QHBoxLayout(self.git_group)
        self.git_message = QLineEdit()
        self.git_commit_btn = QPushButton("")
        self.git_push_btn = QPushButton("")
        self.git_pull_btn = QPushButton("")
        self.git_commit_btn.clicked.connect(self.git_commit)
        self.git_push_btn.clicked.connect(self.git_push)
        self.git_pull_btn.clicked.connect(self.git_pull)
        git_layout.addWidget(self.git_message, 1)
        git_layout.addWidget(self.git_commit_btn)
        git_layout.addWidget(self.git_push_btn)
        git_layout.addWidget(self.git_pull_btn)
        root.addWidget(self.git_group)

        # Connect after dependent widgets are created to avoid init-time callbacks.
        self.filter_both_radio.toggled.connect(self.on_filter_changed)
        self.filter_backup_radio.toggled.connect(self.on_filter_changed)
        self.filter_git_radio.toggled.connect(self.on_filter_changed)

        self.apply_translations()
        self.setup_timeline_limit_combo()
        initial_filter = self.settings.get("compare_filter")
        if initial_filter == "backup":
            self.filter_backup_radio.setChecked(True)
        elif initial_filter == "git":
            self.filter_git_radio.setChecked(True)
        else:
            self.filter_both_radio.setChecked(True)
        self.refresh_data()

    def apply_translations(self) -> None:
        self.setWindowTitle(self.t("compare_window_title"))
        self.filter_label.setText(self.t("compare_filter"))
        self.filter_both_radio.setText(self.t("compare_filter_both"))
        self.filter_backup_radio.setText(self.t("compare_filter_backup"))
        self.filter_git_radio.setText(self.t("compare_filter_git"))
        self.refresh_btn.setText(self.t("compare_refresh"))
        self.limit_label.setText(self.t("compare_limit"))
        self.backup_memo_label.setText(self.t("compare_backup_memo"))
        self.backup_memo_input.setPlaceholderText(self.t("compare_backup_memo_placeholder"))
        self.create_backup_btn.setText(self.t("compare_create_backup"))
        self.backup_note_label.setText(self.t("compare_backup_note"))
        self.timeline_group.setTitle(self.t("compare_timeline"))
        self.compare_from_label.setText(self.t("compare_from"))
        self.compare_to_label.setText(self.t("compare_to"))
        self.compare_btn.setText(self.t("compare_run"))
        self.git_group.setTitle(self.t("compare_git_group"))
        self.git_message.setPlaceholderText(self.t("compare_git_msg_placeholder"))
        self.git_commit_btn.setText(self.t("compare_git_commit"))
        self.git_push_btn.setText(self.t("compare_git_push"))
        self.git_pull_btn.setText(self.t("compare_git_pull"))

    def refresh_data(self) -> None:
        self.backup_items = collect_backup_items(self.project_file, self.timeline_limit)
        self.git_items = (
            collect_git_items(self.project_file, self.git_path, self.timeline_limit)
            if self.git_path
            else []
        )
        self.all_items = sorted(
            [*self.backup_items, *self.git_items],
            key=lambda x: x.timestamp,
            reverse=True,
        )[: self.timeline_limit]
        self.refresh_view()
        git_ok = bool(detect_git_repo_root(self.project_dir, self.git_path)) if self.git_path else False
        self.git_group.setEnabled(git_ok)

    def refresh_view(self) -> None:
        mode = self.current_filter_mode()
        if mode == "backup":
            self.filtered_items = self.backup_items[: self.timeline_limit]
        elif mode == "git":
            self.filtered_items = self.git_items[: self.timeline_limit]
        else:
            self.filtered_items = list(self.all_items)

        self.timeline_list.clear()
        for item in self.filtered_items:
            self.timeline_list.addItem(item.label)

        self.compare_from_combo.clear()
        self.compare_to_combo.clear()

        # Keep current project at the top of "After" targets.
        self.compare_to_combo.addItem(
            self.t("compare_current_project"),
            "__current_project__",
        )
        for item in self.filtered_items:
            self.compare_from_combo.addItem(item.label, item.identifier)
            self.compare_to_combo.addItem(item.label, item.identifier)
        self.compare_to_combo.setCurrentIndex(0)

    def current_filter_mode(self) -> str:
        if self.filter_backup_radio.isChecked():
            return "backup"
        if self.filter_git_radio.isChecked():
            return "git"
        return "both"

    def on_timeline_row_changed(self, row: int) -> None:
        if row < 0:
            return
        if row >= self.compare_from_combo.count():
            return
        self.compare_from_combo.setCurrentIndex(row)

    def resolve_timeline_limit(self) -> int:
        raw = self.settings.get("compare_timeline_limit")
        if isinstance(raw, int):
            value = raw
        else:
            value = DEFAULT_TIMELINE_LIMIT
        if value < 1:
            return DEFAULT_TIMELINE_LIMIT
        if value > 500:
            return 500
        return value

    def on_filter_changed(self) -> None:
        mode = self.current_filter_mode()
        self.settings["compare_filter"] = mode
        self.save_settings_cb()
        self.refresh_view()

    def setup_timeline_limit_combo(self) -> None:
        self.limit_combo.blockSignals(True)
        self.limit_combo.clear()

        options = list(self.timeline_limit_options)
        if self.timeline_limit not in options:
            options.append(self.timeline_limit)
            options.sort()

        for value in options:
            self.limit_combo.addItem(str(value), value)

        idx = self.limit_combo.findData(self.timeline_limit)
        if idx >= 0:
            self.limit_combo.setCurrentIndex(idx)
        self.limit_combo.blockSignals(False)
        self.limit_combo.currentIndexChanged.connect(self.on_timeline_limit_changed)

    def on_timeline_limit_changed(self) -> None:
        value = self.limit_combo.currentData()
        if not isinstance(value, int):
            return
        if value == self.timeline_limit:
            return
        self.timeline_limit = value
        self.settings["compare_timeline_limit"] = value
        self.save_settings_cb()
        self.refresh_data()

    def create_backup(self) -> None:
        try:
            zip_path = create_project_backup(
                self.project_file,
                memo=self.backup_memo_input.text(),
            )
        except Exception as exc:
            QMessageBox.warning(self, self.t("compare_git_fail_title"), str(exc))
            return
        QMessageBox.information(
            self,
            self.t("compare_backup_title"),
            self.t("compare_backup_created", path=str(zip_path)),
        )
        self.backup_memo_input.clear()
        self.refresh_data()

    def run_compare(self) -> None:
        if self.compare_from_combo.count() < 1 or self.compare_to_combo.count() < 1:
            QMessageBox.warning(self, self.t("compare_started_title"), self.t("compare_need_two"))
            return

        from_idx = self.compare_from_combo.currentIndex()
        to_idx = self.compare_to_combo.currentIndex()
        if from_idx < 0 or to_idx < 0:
            QMessageBox.warning(self, self.t("compare_started_title"), self.t("compare_need_two"))
            return
        from_id = self.compare_from_combo.currentData()
        to_id = self.compare_to_combo.currentData()
        if isinstance(from_id, str) and isinstance(to_id, str) and from_id == to_id:
            QMessageBox.warning(self, self.t("compare_started_title"), self.t("compare_same"))
            return

        if not isinstance(from_id, str) or not isinstance(to_id, str):
            QMessageBox.warning(self, self.t("compare_started_title"), self.t("compare_need_two"))
            return

        try:
            before_map = self._load_source_map(from_id)
            after_map = self._load_source_map(to_id)
        except Exception as exc:
            QMessageBox.warning(
                self,
                self.t("compare_result_title"),
                self.t("compare_result_error", error=str(exc)),
            )
            return

        added, removed, changed, unchanged = compare_file_maps(before_map, after_map)
        dialog = CompareResultDialog(
            title=self.t("compare_result_title"),
            summary=self.t(
                "compare_result_summary",
                added=str(len(added)),
                removed=str(len(removed)),
                changed=str(len(changed)),
                unchanged=str(len(unchanged)),
            ),
            files_title=self.t("compare_result_files"),
            no_diff_text=self.t("compare_result_no_diff"),
            close_text=self.t("compare_close"),
            visual_title=self.t("compare_visual_title"),
            visual_file_label=self.t("compare_visual_file"),
            visual_before_label=self.t("compare_visual_before"),
            visual_after_label=self.t("compare_visual_after"),
            visual_empty_text=self.t("compare_visual_empty"),
            image_title=self.t("compare_image_title"),
            image_target_text=self.t("compare_image_target"),
            image_render_text=self.t("compare_image_render"),
            image_status_text=self.t("compare_image_status"),
            image_no_targets_text=self.t("compare_image_no_targets"),
            image_missing_side_text=self.t("compare_image_missing_side"),
            image_before_text=self.t("compare_image_before"),
            image_after_text=self.t("compare_image_after"),
            image_diff_text=self.t("compare_image_diff"),
            image_not_available_text=self.t("compare_image_not_available"),
            image_zoom_out_text=self.t("compare_image_zoom_out"),
            image_zoom_in_text=self.t("compare_image_zoom_in"),
            image_zoom_fit_text=self.t("compare_image_zoom_fit"),
            added=added,
            removed=removed,
            changed=changed,
            before_map=before_map,
            after_map=after_map,
            cli_path=self.cli_path,
            parent=self,
        )
        dialog.exec()

    def _load_source_map(self, source_id: str) -> dict[str, bytes]:
        if source_id == "__current_project__":
            return build_current_project_map(self.project_file)

        item = next((it for it in self.filtered_items if it.identifier == source_id), None)
        if item is None:
            raise RuntimeError(f"Unknown source id: {source_id}")

        if item.source == "backup":
            return build_backup_zip_map(Path(item.identifier))
        if item.source == "git":
            return build_git_commit_map(self.project_file, item.identifier, self.git_path)
        raise RuntimeError(f"Unsupported source type: {item.source}")

    def git_commit(self) -> None:
        message = self.git_message.text().strip()
        if not message:
            QMessageBox.warning(self, self.t("compare_git_fail_title"), self.t("compare_git_commit_need_msg"))
            return
        if not self.git_path:
            QMessageBox.warning(self, self.t("compare_git_fail_title"), self.t("compare_git_unavailable"))
            return

        add_result = run_git(self.project_dir, ["add", "-A"], self.git_path)
        if add_result.returncode != 0:
            QMessageBox.warning(self, self.t("compare_git_fail_title"), add_result.stderr.strip() or add_result.stdout.strip())
            return
        commit_result = run_git(self.project_dir, ["commit", "-m", message], self.git_path)
        if commit_result.returncode != 0:
            QMessageBox.warning(self, self.t("compare_git_fail_title"), commit_result.stderr.strip() or commit_result.stdout.strip())
            return
        QMessageBox.information(self, self.t("compare_git_ok_title"), self.t("compare_git_commit_ok"))
        self.refresh_data()

    def git_push(self) -> None:
        if not self.git_path:
            QMessageBox.warning(self, self.t("compare_git_fail_title"), self.t("compare_git_unavailable"))
            return
        result = run_git(self.project_dir, ["push"], self.git_path)
        if result.returncode != 0:
            QMessageBox.warning(self, self.t("compare_git_fail_title"), result.stderr.strip() or result.stdout.strip())
            return
        QMessageBox.information(self, self.t("compare_git_ok_title"), self.t("compare_git_push_ok"))
        self.refresh_data()

    def git_pull(self) -> None:
        if not self.git_path:
            QMessageBox.warning(self, self.t("compare_git_fail_title"), self.t("compare_git_unavailable"))
            return
        result = run_git(self.project_dir, ["pull"], self.git_path)
        if result.returncode != 0:
            QMessageBox.warning(self, self.t("compare_git_fail_title"), result.stderr.strip() or result.stdout.strip())
            return
        QMessageBox.information(self, self.t("compare_git_ok_title"), self.t("compare_git_pull_ok"))
        self.refresh_data()


class CompareResultDialog(QDialog):
    def __init__(
        self,
        title: str,
        summary: str,
        files_title: str,
        no_diff_text: str,
        close_text: str,
        visual_title: str,
        visual_file_label: str,
        visual_before_label: str,
        visual_after_label: str,
        visual_empty_text: str,
        image_title: str,
        image_target_text: str,
        image_render_text: str,
        image_status_text: str,
        image_no_targets_text: str,
        image_missing_side_text: str,
        image_before_text: str,
        image_after_text: str,
        image_diff_text: str,
        image_not_available_text: str,
        image_zoom_out_text: str,
        image_zoom_in_text: str,
        image_zoom_fit_text: str,
        added: list[str],
        removed: list[str],
        changed: list[str],
        before_map: dict[str, bytes],
        after_map: dict[str, bytes],
        cli_path: Path,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(760, 520)
        self.before_map = before_map
        self.after_map = after_map
        self.visual_empty_text = visual_empty_text
        self.cli_path = cli_path
        self.image_not_available_text = image_not_available_text
        self.image_no_targets_text = image_no_targets_text
        self.image_missing_side_text = image_missing_side_text
        self.image_status_default_text = image_status_text
        self.image_zoom_mode = "fit"
        self.image_zoom_scale = 1.0
        self.before_image_raw: QImage | None = None
        self.after_image_raw: QImage | None = None
        self.diff_image_raw: QImage | None = None
        self.image_scrolls: dict[str, QScrollArea] = {}
        self._syncing_scroll = False
        self.image_targets: list[tuple[str, str]] = []
        self.before_svg_map: dict[str, Path] = {}
        self.after_svg_map: dict[str, Path] = {}
        self._tmp_before_dir_obj: tempfile.TemporaryDirectory[str] | None = None
        self._tmp_after_dir_obj: tempfile.TemporaryDirectory[str] | None = None
        self._tmp_svg_before_obj: tempfile.TemporaryDirectory[str] | None = None
        self._tmp_svg_after_obj: tempfile.TemporaryDirectory[str] | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        tabs = QTabWidget()
        root.addWidget(tabs, 1)

        summary_tab = QWidget()
        summary_layout = QVBoxLayout(summary_tab)
        summary_layout.setContentsMargins(8, 8, 8, 8)
        summary_layout.setSpacing(10)

        summary_label = QLabel(summary)
        summary_label.setWordWrap(True)
        summary_label.setStyleSheet("font-weight: 600;")
        summary_layout.addWidget(summary_label)

        files_title_label = QLabel(files_title)
        files_title_label.setStyleSheet("color: #444444;")
        summary_layout.addWidget(files_title_label)

        self.list_widget = QListWidget()
        summary_layout.addWidget(self.list_widget, 1)

        for path in changed:
            self.list_widget.addItem(f"~ {path}")
        for path in added:
            self.list_widget.addItem(f"+ {path}")
        for path in removed:
            self.list_widget.addItem(f"- {path}")

        if self.list_widget.count() == 0:
            self.list_widget.addItem(no_diff_text)

        tabs.addTab(summary_tab, files_title)

        visual_tab = QWidget()
        visual_layout = QVBoxLayout(visual_tab)
        visual_layout.setContentsMargins(8, 8, 8, 8)
        visual_layout.setSpacing(8)

        visual_header = QHBoxLayout()
        visual_file_label_widget = QLabel(visual_file_label)
        self.visual_file_combo = QComboBox()
        visual_header.addWidget(visual_file_label_widget)
        visual_header.addWidget(self.visual_file_combo, 1)
        visual_layout.addLayout(visual_header)

        split = QSplitter()
        before_wrap = QWidget()
        before_layout = QVBoxLayout(before_wrap)
        before_layout.setContentsMargins(0, 0, 0, 0)
        before_layout.setSpacing(4)
        before_title = QLabel(visual_before_label)
        self.before_text = QPlainTextEdit()
        self.before_text.setReadOnly(True)
        before_layout.addWidget(before_title)
        before_layout.addWidget(self.before_text, 1)

        after_wrap = QWidget()
        after_layout = QVBoxLayout(after_wrap)
        after_layout.setContentsMargins(0, 0, 0, 0)
        after_layout.setSpacing(4)
        after_title = QLabel(visual_after_label)
        self.after_text = QPlainTextEdit()
        self.after_text.setReadOnly(True)
        after_layout.addWidget(after_title)
        after_layout.addWidget(self.after_text, 1)

        split.addWidget(before_wrap)
        split.addWidget(after_wrap)
        visual_layout.addWidget(split, 1)
        tabs.addTab(visual_tab, visual_title)

        image_tab = QWidget()
        image_layout = QVBoxLayout(image_tab)
        image_layout.setContentsMargins(8, 8, 8, 8)
        image_layout.setSpacing(8)
        image_button_row = QHBoxLayout()
        self.image_target_label = QLabel(image_target_text)
        self.image_target_combo = QComboBox()
        self.image_render_btn = QPushButton(image_render_text)
        self.image_zoom_out_btn = QPushButton(image_zoom_out_text)
        self.image_zoom_in_btn = QPushButton(image_zoom_in_text)
        self.image_zoom_fit_btn = QPushButton(image_zoom_fit_text)
        self.image_render_btn.clicked.connect(self.generate_image_diff_for_selected_target)
        self.image_zoom_out_btn.clicked.connect(self.zoom_out_images)
        self.image_zoom_in_btn.clicked.connect(self.zoom_in_images)
        self.image_zoom_fit_btn.clicked.connect(self.zoom_fit_images)
        image_button_row.addWidget(self.image_target_label)
        image_button_row.addWidget(self.image_target_combo, 1)
        image_button_row.addWidget(self.image_render_btn)
        image_button_row.addWidget(self.image_zoom_out_btn)
        image_button_row.addWidget(self.image_zoom_in_btn)
        image_button_row.addWidget(self.image_zoom_fit_btn)
        image_button_row.addStretch(1)
        image_layout.addLayout(image_button_row)

        self.image_status = QLabel(image_status_text)
        self.image_status.setWordWrap(True)
        self.image_status.setStyleSheet("color: #666666;")
        image_layout.addWidget(self.image_status)

        self.before_image_label = QLabel()
        self.after_image_label = QLabel()
        self.diff_image_label = QLabel()
        self.before_image_label.setAlignment(Qt.AlignCenter)
        self.after_image_label.setAlignment(Qt.AlignCenter)
        self.diff_image_label.setAlignment(Qt.AlignCenter)
        self.before_image_label.setText(image_before_text)
        self.after_image_label.setText(image_after_text)
        self.diff_image_label.setText(image_diff_text)
        self.image_tabs = QTabWidget()
        self.image_tabs.addTab(
            self._wrap_image_label("diff", image_diff_text, self.diff_image_label),
            image_diff_text,
        )
        self.image_tabs.addTab(
            self._wrap_image_label("before", image_before_text, self.before_image_label),
            image_before_text,
        )
        self.image_tabs.addTab(
            self._wrap_image_label("after", image_after_text, self.after_image_label),
            image_after_text,
        )
        image_layout.addWidget(self.image_tabs, 1)
        tabs.addTab(image_tab, image_title)
        self._connect_image_scroll_sync()

        diff_paths = [*changed, *added, *removed]
        for path in diff_paths:
            self.visual_file_combo.addItem(path, path)
        self.visual_file_combo.currentIndexChanged.connect(self.on_visual_file_changed)
        if self.visual_file_combo.count() > 0:
            self.visual_file_combo.setCurrentIndex(0)
            self.on_visual_file_changed(0)
        else:
            self.before_text.setPlainText(self.visual_empty_text)
            self.after_text.setPlainText(self.visual_empty_text)
        self.prepare_image_targets()

        actions = QHBoxLayout()
        actions.addStretch(1)
        close_btn = QPushButton(close_text)
        close_btn.clicked.connect(self.accept)
        actions.addWidget(close_btn)
        root.addLayout(actions)

    def _wrap_image_label(self, key: str, title: str, label: QLabel) -> QWidget:
        wrap = QWidget()
        layout = QVBoxLayout(wrap)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        title_label = QLabel(title)
        scroll = QScrollArea()
        scroll.setWidgetResizable(False)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setWidget(label)
        self.image_scrolls[key] = scroll
        layout.addWidget(title_label)
        layout.addWidget(scroll, 1)
        return wrap

    def _connect_image_scroll_sync(self) -> None:
        for scroll in self.image_scrolls.values():
            scroll.horizontalScrollBar().valueChanged.connect(self.on_image_scroll_changed)
            scroll.verticalScrollBar().valueChanged.connect(self.on_image_scroll_changed)

    def on_image_scroll_changed(self, _: int) -> None:
        if self._syncing_scroll:
            return

        source_bar = self.sender()
        if source_bar is None:
            return

        bars = []
        for scroll in self.image_scrolls.values():
            bars.append(scroll.horizontalScrollBar())
            bars.append(scroll.verticalScrollBar())
        if source_bar not in bars:
            return

        self._syncing_scroll = True
        try:
            source_max = source_bar.maximum()
            source_value = source_bar.value()
            ratio = 0.0 if source_max <= 0 else source_value / source_max
            source_is_vertical = source_bar.orientation() == Qt.Vertical

            for scroll in self.image_scrolls.values():
                target_bar = scroll.verticalScrollBar() if source_is_vertical else scroll.horizontalScrollBar()
                if target_bar is source_bar:
                    continue
                target_max = target_bar.maximum()
                target_value = int(round(ratio * target_max)) if target_max > 0 else 0
                target_bar.setValue(target_value)
        finally:
            self._syncing_scroll = False

    def on_visual_file_changed(self, _: int) -> None:
        path = self.visual_file_combo.currentData()
        if not isinstance(path, str):
            self.before_text.setPlainText(self.visual_empty_text)
            self.after_text.setPlainText(self.visual_empty_text)
            return
        before_raw = self.before_map.get(path)
        after_raw = self.after_map.get(path)
        self.before_text.setPlainText(self._decode_bytes(before_raw))
        self.after_text.setPlainText(self._decode_bytes(after_raw))

    def _decode_bytes(self, data: bytes | None) -> str:
        if data is None:
            return self.visual_empty_text
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data.decode("utf-8", errors="replace")

    def prepare_image_targets(self) -> None:
        self.image_target_combo.clear()
        self.image_targets.clear()
        self.before_svg_map.clear()
        self.after_svg_map.clear()
        self._cleanup_temp_dirs()

        try:
            self._tmp_before_dir_obj = tempfile.TemporaryDirectory(prefix="ksnap_before_")
            self._tmp_after_dir_obj = tempfile.TemporaryDirectory(prefix="ksnap_after_")
            self._tmp_svg_before_obj = tempfile.TemporaryDirectory(prefix="ksnap_svg_before_")
            self._tmp_svg_after_obj = tempfile.TemporaryDirectory(prefix="ksnap_svg_after_")

            before_root = Path(self._tmp_before_dir_obj.name)
            after_root = Path(self._tmp_after_dir_obj.name)
            out_before = Path(self._tmp_svg_before_obj.name)
            out_after = Path(self._tmp_svg_after_obj.name)

            write_file_map(before_root, self.before_map)
            write_file_map(after_root, self.after_map)

            self.before_svg_map.update(self._export_side_svgs(before_root, out_before))
            self.after_svg_map.update(self._export_side_svgs(after_root, out_after))

            all_keys = sorted(set(self.before_svg_map.keys()) | set(self.after_svg_map.keys()))
            for key in all_keys:
                kind, rel = key.split("|", 1)
                if kind == "pcb" and rel == "__board__":
                    label = self.t("compare_image_pcb_board")
                else:
                    prefix = "SCH" if kind == "sch" else "PCB"
                    label = f"{prefix} / {rel}"
                self.image_targets.append((key, label))
                self.image_target_combo.addItem(label, key)

            if self.image_target_combo.count() == 0:
                self.image_status.setText(self.image_no_targets_text)
                self.image_status.setStyleSheet("color: #9a6700;")
            else:
                self.image_status.setText(self.image_status_default_text)
                self.image_status.setStyleSheet("color: #666666;")
        except Exception as exc:
            self.image_status.setText(str(exc))
            self.image_status.setStyleSheet("color: #b00020;")

    def _export_side_svgs(self, source_root: Path, out_root: Path) -> dict[str, Path]:
        result: dict[str, Path] = {}
        sch_src = first_matching_file(source_root, ".kicad_sch")
        if sch_src is not None:
            sch_out = out_root / "sch"
            sch_out.mkdir(parents=True, exist_ok=True)
            try:
                for svg in export_svg_bundle_with_kicad_cli(self.cli_path, sch_src, sch_out, "sch"):
                    rel = svg.relative_to(sch_out).as_posix()
                    result[f"sch|{rel}"] = svg
            except Exception:
                # Keep other targets available even if schematic export fails.
                pass

        pcb_src = first_matching_file(source_root, ".kicad_pcb")
        if pcb_src is not None:
            pcb_out = out_root / "pcb"
            pcb_out.mkdir(parents=True, exist_ok=True)
            try:
                pcb_svgs = export_svg_bundle_with_kicad_cli(self.cli_path, pcb_src, pcb_out, "pcb")
                for svg in pcb_svgs:
                    rel = svg.relative_to(pcb_out).as_posix()
                    result[f"pcb|{rel}"] = svg
                # Also expose a stable board-level target (first exported SVG as primary).
                if pcb_svgs:
                    result["pcb|__board__"] = pcb_svgs[0]
            except Exception:
                # Keep other targets available even if PCB export fails.
                pass
        return result

    def generate_image_diff_for_selected_target(self) -> None:
        key = self.image_target_combo.currentData()
        if not isinstance(key, str):
            self.image_status.setText(self.image_no_targets_text)
            self.image_status.setStyleSheet("color: #9a6700;")
            return
        try:
            before_img, after_img, diff_img = self._build_image_diff_for_target(key)
        except Exception as exc:
            self.image_status.setText(str(exc))
            self.image_status.setStyleSheet("color: #b00020;")
            return

        self.image_status.setText("OK")
        self.image_status.setStyleSheet("color: #2b7a0b;")
        self.before_image_raw = before_img
        self.after_image_raw = after_img
        self.diff_image_raw = diff_img
        self.image_zoom_scale = 1.0
        self.zoom_fit_images()

    def _build_image_diff_for_target(self, target_key: str) -> tuple[QImage, QImage, QImage]:
        before_svg = self.before_svg_map.get(target_key)
        after_svg = self.after_svg_map.get(target_key)
        if before_svg is None and after_svg is None:
            raise RuntimeError(self.image_not_available_text)

        before_img = render_svg_to_image(before_svg) if before_svg is not None else None
        after_img = render_svg_to_image(after_svg) if after_svg is not None else None

        if before_img is None and after_img is None:
            raise RuntimeError(self.image_not_available_text)
        if before_img is None:
            before_img = QImage(after_img.width(), after_img.height(), QImage.Format_ARGB32)  # type: ignore[union-attr]
            before_img.fill(Qt.white)
            self.image_status.setText(self.image_missing_side_text)
            self.image_status.setStyleSheet("color: #9a6700;")
        if after_img is None:
            after_img = QImage(before_img.width(), before_img.height(), QImage.Format_ARGB32)  # type: ignore[union-attr]
            after_img.fill(Qt.white)
            self.image_status.setText(self.image_missing_side_text)
            self.image_status.setStyleSheet("color: #9a6700;")

        before_img, after_img = normalize_image_sizes(before_img, after_img)
        diff_img = make_pixel_diff_image(before_img, after_img)
        return before_img, after_img, diff_img

    def zoom_fit_images(self) -> None:
        self.image_zoom_mode = "fit"
        self._render_image_labels()

    def zoom_in_images(self) -> None:
        self.image_zoom_mode = "manual"
        self.image_zoom_scale = min(self.image_zoom_scale * 1.25, 8.0)
        self._render_image_labels()

    def zoom_out_images(self) -> None:
        self.image_zoom_mode = "manual"
        self.image_zoom_scale = max(self.image_zoom_scale / 1.25, 0.1)
        self._render_image_labels()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self.image_zoom_mode == "fit":
            self._render_image_labels()

    def _render_image_labels(self) -> None:
        common_fit_scale = None
        if self.image_zoom_mode == "fit":
            common_fit_scale = self._compute_common_fit_scale()
        self._set_image_for_key("before", self.before_image_label, self.before_image_raw, common_fit_scale)
        self._set_image_for_key("after", self.after_image_label, self.after_image_raw, common_fit_scale)
        self._set_image_for_key("diff", self.diff_image_label, self.diff_image_raw, common_fit_scale)

    def _compute_common_fit_scale(self) -> float:
        images = [img for img in [self.before_image_raw, self.after_image_raw, self.diff_image_raw] if img is not None]
        if not images:
            return 1.0
        max_w = max(img.width() for img in images)
        max_h = max(img.height() for img in images)
        if max_w <= 0 or max_h <= 0:
            return 1.0

        scroll = self.image_scrolls.get("diff") or next(iter(self.image_scrolls.values()), None)
        if scroll is None:
            return 1.0
        vp = scroll.viewport().size()
        avail_w = max(1, vp.width())
        avail_h = max(1, vp.height())
        scale = min(avail_w / max_w, avail_h / max_h)
        return max(0.05, min(scale, 8.0))

    def _set_image_for_key(
        self,
        key: str,
        label: QLabel,
        image: QImage | None,
        common_fit_scale: float | None = None,
    ) -> None:
        if image is None:
            return
        pixmap = QPixmap.fromImage(image)
        if self.image_zoom_mode == "fit":
            scale = common_fit_scale if common_fit_scale is not None else 1.0
            width = max(1, int(pixmap.width() * scale))
            height = max(1, int(pixmap.height() * scale))
            pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            width = max(1, int(pixmap.width() * self.image_zoom_scale))
            height = max(1, int(pixmap.height() * self.image_zoom_scale))
            pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(pixmap)
        label.resize(pixmap.size())

    def _cleanup_temp_dirs(self) -> None:
        for obj in [
            self._tmp_before_dir_obj,
            self._tmp_after_dir_obj,
            self._tmp_svg_before_obj,
            self._tmp_svg_after_obj,
        ]:
            if obj is not None:
                obj.cleanup()
        self._tmp_before_dir_obj = None
        self._tmp_after_dir_obj = None
        self._tmp_svg_before_obj = None
        self._tmp_svg_after_obj = None

    def closeEvent(self, event) -> None:
        self._cleanup_temp_dirs()
        super().closeEvent(event)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.settings_store = SettingsStore()
        self.settings = self.settings_store.load()
        self.language = self.resolve_initial_language()

        self.cli_candidate: CliCandidate | None = None
        self.git_path: str | None = None
        self.cli_status_key = "status_checking"
        self.cli_status_args: dict[str, str] = {}
        self.cli_status_ok = False

        self.git_status_key = "git_checking"
        self.git_status_args: dict[str, str] = {}
        self.git_status_level = "warn"

        self.setMinimumSize(960, 580)

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(24, 24, 24, 24)
        root_layout.setSpacing(18)

        header_row = QHBoxLayout()
        self.title = QLabel("")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        self.title.setFont(title_font)

        header_row.addWidget(self.title)
        header_row.addStretch(1)

        self.language_label = QLabel("")
        self.language_combo = QComboBox()
        for code in SUPPORTED_LANGUAGES:
            self.language_combo.addItem(LANGUAGE_LABELS[code], code)
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)

        header_row.addWidget(self.language_label)
        header_row.addWidget(self.language_combo)

        self.subtitle = QLabel("")
        self.subtitle.setStyleSheet("color: #666666;")

        root_layout.addLayout(header_row)
        root_layout.addWidget(self.subtitle)

        content = QGridLayout()
        content.setHorizontalSpacing(18)
        content.setVerticalSpacing(18)
        root_layout.addLayout(content)

        self.cli_box = QGroupBox("")
        cli_layout = QVBoxLayout(self.cli_box)
        cli_layout.setSpacing(10)

        path_row = QHBoxLayout()
        self.path_label = QLabel("")
        self.path_input = QLineEdit()
        self.path_input.editingFinished.connect(self.on_path_edited)
        self.browse_btn = QPushButton("")
        self.browse_btn.clicked.connect(self.select_cli_path)
        self.detect_btn = QPushButton("")
        self.detect_btn.clicked.connect(self.auto_detect_cli)
        path_row.addWidget(self.path_label)
        path_row.addWidget(self.path_input, 1)
        path_row.addWidget(self.browse_btn)
        path_row.addWidget(self.detect_btn)

        self.status = QLabel("")

        git_row = QHBoxLayout()
        self.git_label = QLabel("")
        self.git_path_input = QLineEdit()
        self.git_path_input.setReadOnly(True)
        self.git_refresh_btn = QPushButton("")
        self.git_refresh_btn.clicked.connect(self.detect_git)
        git_row.addWidget(self.git_label)
        git_row.addWidget(self.git_path_input, 1)
        git_row.addWidget(self.git_refresh_btn)

        self.git_status = QLabel("")

        cli_layout.addLayout(path_row)
        cli_layout.addWidget(self.status)
        cli_layout.addLayout(git_row)
        cli_layout.addWidget(self.git_status)

        self.project_box = QGroupBox("")
        project_layout = QVBoxLayout(self.project_box)
        project_layout.setSpacing(10)

        self.project_hint = QLabel("")
        self.project_hint.setStyleSheet("color: #666666;")

        self.recent_list = QListWidget()
        self.recent_list.itemSelectionChanged.connect(self.update_next_state)
        self.recent_list.itemDoubleClicked.connect(self.on_project_chosen)

        actions = QHBoxLayout()
        self.open_btn = QPushButton("")
        self.open_btn.clicked.connect(self.open_project)
        self.remove_btn = QPushButton("")
        self.remove_btn.clicked.connect(self.remove_project)
        actions.addWidget(self.open_btn)
        actions.addWidget(self.remove_btn)
        actions.addItem(QSpacerItem(10, 10))
        actions.addStretch(1)

        project_layout.addWidget(self.project_hint)
        project_layout.addWidget(self.recent_list, 1)
        project_layout.addLayout(actions)

        self.next_box = QGroupBox("")
        next_layout = QVBoxLayout(self.next_box)
        next_layout.setSpacing(10)

        self.next_hint = QLabel("")
        self.next_hint.setWordWrap(True)

        self.proceed_btn = QPushButton("")
        self.proceed_btn.setEnabled(False)
        self.proceed_btn.clicked.connect(self.on_continue)

        next_layout.addWidget(self.next_hint)
        next_layout.addWidget(self.proceed_btn)

        content.addWidget(self.cli_box, 0, 0)
        content.addWidget(self.project_box, 1, 0)
        content.addWidget(self.next_box, 0, 1)

        content.setRowStretch(1, 1)
        content.setColumnStretch(0, 3)
        content.setColumnStretch(1, 2)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("color: #dddddd;")
        root_layout.addWidget(divider)

        self.footer = QLabel("")
        self.footer.setStyleSheet("color: #999999;")
        self.footer.setAlignment(Qt.AlignRight)
        root_layout.addWidget(self.footer)

        self.setCentralWidget(root)

        self.load_recent_projects()
        self.apply_translations()

        idx = self.language_combo.findData(self.language)
        if idx >= 0:
            self.language_combo.setCurrentIndex(idx)

        self.auto_detect_cli(initial=True)
        self.detect_git()

    def t(self, key: str, **kwargs: str) -> str:
        table = TRANSLATIONS.get(self.language, TRANSLATIONS["en"])
        text = table.get(key, TRANSLATIONS["en"].get(key, key))
        return text.format(**kwargs) if kwargs else text

    def resolve_initial_language(self) -> str:
        configured = self.settings.get("language")
        if isinstance(configured, str):
            lang = normalize_language(configured)
            if lang in SUPPORTED_LANGUAGES:
                return lang
        return detect_environment_language()

    def apply_translations(self) -> None:
        self.setWindowTitle(self.t("window_title"))
        self.title.setText(self.t("title"))
        self.subtitle.setText(self.t("subtitle"))
        self.language_label.setText(self.t("language"))
        self.cli_box.setTitle(self.t("group_path"))
        self.path_label.setText(self.t("cli_path"))
        self.path_input.setPlaceholderText(self.t("cli_placeholder"))
        self.browse_btn.setText(self.t("browse"))
        self.detect_btn.setText(self.t("auto_detect"))
        self.git_label.setText(self.t("git_path"))
        self.git_refresh_btn.setText(self.t("git_refresh"))
        self.project_box.setTitle(self.t("group_project"))
        self.project_hint.setText(self.t("project_hint"))
        self.open_btn.setText(self.t("open_project"))
        self.remove_btn.setText(self.t("remove_project"))
        self.next_box.setTitle(self.t("group_next"))
        self.next_hint.setText(self.t("next_hint"))
        self.proceed_btn.setText(self.t("continue"))
        self.footer.setText(self.t("footer", path=str(self.settings_store.config_path)))
        self.render_cli_status()
        self.render_git_status()

    def on_language_changed(self) -> None:
        code = self.language_combo.currentData()
        if not isinstance(code, str):
            return
        if code not in SUPPORTED_LANGUAGES:
            return
        self.language = code
        self.settings["language"] = code
        self.save_settings()
        self.apply_translations()

    def load_recent_projects(self) -> None:
        self.recent_list.clear()
        recent = self.settings.get("recent_projects", [])
        if not isinstance(recent, list):
            return

        selected_row = -1
        last_project = self.settings.get("last_project")
        for item in recent:
            path = str(item)
            self.recent_list.addItem(QListWidgetItem(path))
            if isinstance(last_project, str) and path == last_project:
                selected_row = self.recent_list.count() - 1

        if selected_row >= 0:
            self.recent_list.setCurrentRow(selected_row)
        elif self.recent_list.count() > 0:
            self.recent_list.setCurrentRow(0)

    def save_settings(self) -> None:
        recent: list[str] = []
        for i in range(self.recent_list.count()):
            recent.append(self.recent_list.item(i).text())

        self.settings["recent_projects"] = recent[:MAX_RECENT]
        selected = self.selected_project()
        if selected:
            self.settings["last_project"] = selected
        self.settings_store.save(self.settings)

    def selected_project(self) -> str | None:
        item = self.recent_list.currentItem()
        return item.text() if item else None

    def set_cli_status(self, key: str, ok: bool, **kwargs: str) -> None:
        self.cli_status_key = key
        self.cli_status_args = kwargs
        self.cli_status_ok = ok
        self.render_cli_status()

    def render_cli_status(self) -> None:
        self.status.setText(self.t(self.cli_status_key, **self.cli_status_args))
        self.status.setStyleSheet("color: #2b7a0b;" if self.cli_status_ok else "color: #b00020;")

    def set_git_status(self, key: str, level: str, **kwargs: str) -> None:
        self.git_status_key = key
        self.git_status_args = kwargs
        self.git_status_level = level
        self.render_git_status()

    def render_git_status(self) -> None:
        self.git_status.setText(self.t(self.git_status_key, **self.git_status_args))
        if self.git_status_level == "ok":
            self.git_status.setStyleSheet("color: #2b7a0b;")
        else:
            self.git_status.setStyleSheet("color: #9a6700;")

    def update_next_state(self) -> None:
        can_continue = self.cli_candidate is not None and self.selected_project() is not None
        self.proceed_btn.setEnabled(can_continue)

    def select_cli_path(self) -> None:
        default_path = self.path_input.text().strip()
        selected, _ = QFileDialog.getOpenFileName(
            self,
            self.t("dlg_select_cli"),
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
            self.set_cli_status("status_empty", False)
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
            self.set_cli_status("status_invalid", False)
            self.settings["manual_cli_path"] = str(path)
            self.save_settings()
            self.update_next_state()
            return

        self.cli_candidate = candidate
        self.path_input.setText(str(candidate.path))
        self.settings["manual_cli_path"] = str(candidate.path)
        self.save_settings()
        self.set_cli_status("status_ok", True, version=candidate.version_text)
        self.update_next_state()

    def auto_detect_cli(self, initial: bool = False) -> None:
        manual = self.settings.get("manual_cli_path")
        manual_path = str(manual) if isinstance(manual, str) and manual else None

        candidates = discover_kicad_cli_candidates(manual_path)
        if not candidates:
            self.cli_candidate = None
            self.set_cli_status("status_not_detected", False)
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

        self.set_cli_status("status_ok", True, version=best.version_text)
        self.update_next_state()

    def detect_git(self) -> None:
        git_path = shutil.which("git")
        if not git_path:
            self.git_path = None
            self.git_path_input.setText("")
            self.set_git_status("git_not_detected", "warn")
            return

        self.git_path = git_path
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
            self.set_git_status("git_check_failed", "warn")
            return

        if result.returncode == 0:
            version_text = result.stdout.strip() or result.stderr.strip()
            if version_text:
                self.set_git_status("git_ok", "ok", version=version_text)
            else:
                self.set_git_status("git_ok_plain", "ok")
            return

        self.set_git_status("git_check_failed", "warn")

    def open_project(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(
            self,
            self.t("dlg_open_project"),
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
                self.t("warning_cli_title"),
                self.t("warning_cli_text"),
            )
            return

        project = self.selected_project()
        if not project:
            QMessageBox.warning(
                self,
                self.t("warning_project_title"),
                self.t("warning_project_text"),
            )
            return

        default_output = str(Path(project).resolve().parent / "diff_report")
        self.settings["output_dir"] = default_output
        self.save_settings()

        dialog = SnapshotCompareDialog(
            project_file=Path(project),
            cli_path=self.cli_candidate.path,
            git_path=self.git_path,
            language=self.language,
            translate=self.t,
            settings=self.settings,
            save_settings_cb=self.save_settings,
            parent=self,
        )
        dialog.exec()


def main() -> None:
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

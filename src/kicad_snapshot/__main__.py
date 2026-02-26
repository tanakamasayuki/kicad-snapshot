from __future__ import annotations

import hashlib
import json
import locale
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import urllib.request
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterable

from platformdirs import user_config_dir
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices, QFont, QGuiApplication, QImage, QPainter, QPixmap
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
    QSizePolicy,
    QScrollArea,
    QSpacerItem,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from . import __version__

APP_NAME = "KiCadSnapshot"
APP_AUTHOR = "KiCadSnapshot"
SETTINGS_FILE = "settings.toml"
MAX_RECENT = 20
DEFAULT_TIMELINE_LIMIT = 50
BACKUP_DIR_NAME = "snapshot_backups"
GITHUB_LATEST_RELEASE_API = "https://api.github.com/repos/tanakamasayuki/kicad-snapshot/releases/latest"
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
        "git_refresh": "Auto Detect Git",
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
        "version_current": "Version: {current}",
        "version_check_latest": "Check Latest",
        "version_checking": "Checking latest version...",
        "version_latest_up_to_date": "Latest: {latest} (up to date)",
        "version_latest_available": "Latest: {latest} (update available)",
        "version_latest_ahead": "Latest: {latest} (current is newer)",
        "version_latest_unknown": "Latest: {latest}",
        "version_check_failed": "Latest version check failed",
        "version_open_repo": "Open Web Page",
        "snapshot_window_title": "Snapshots",
        "snapshot_selected_project": "Project: {project}",
        "snapshot_open_compare": "Open Compare Screen",
        "snapshot_back": "Back",
        "compare_preview_title": "Preview",
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
        "compare_back": "Back",
        "compare_visual_title": "Visual Diff",
        "compare_visual_file": "File",
        "compare_visual_before": "Before",
        "compare_visual_after": "After",
        "compare_visual_empty": "(empty)",
        "compare_image_title": "Image Diff",
        "compare_loading": "Loading compare data...",
        "compare_image_target": "Target",
        "compare_image_rendering": "Rendering...",
        "compare_image_status_ready": "Ready.",
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
        "compare_item_status_pending": "Pending",
        "compare_item_status_rendering": "Rendering",
        "compare_item_status_diff": "Diff",
        "compare_item_status_same": "Same",
        "compare_item_status_error": "Error",
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
        "git_refresh": "Git自動検出",
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
        "version_current": "バージョン: {current}",
        "version_check_latest": "最新を確認",
        "version_checking": "最新バージョン確認中...",
        "version_latest_up_to_date": "最新: {latest}（最新です）",
        "version_latest_available": "最新: {latest}（更新あり）",
        "version_latest_ahead": "最新: {latest}（現在の方が新しい）",
        "version_latest_unknown": "最新: {latest}",
        "version_check_failed": "最新バージョンの確認に失敗",
        "version_open_repo": "Webページを開く",
        "snapshot_window_title": "スナップショット",
        "snapshot_selected_project": "プロジェクト: {project}",
        "snapshot_open_compare": "比較画面を開く",
        "snapshot_back": "戻る",
        "compare_preview_title": "プレビュー",
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
        "compare_back": "戻る",
        "compare_visual_title": "ビジュアル差分",
        "compare_visual_file": "ファイル",
        "compare_visual_before": "Before",
        "compare_visual_after": "After",
        "compare_visual_empty": "(空)",
        "compare_image_title": "画像差分",
        "compare_loading": "比較データを読み込み中...",
        "compare_image_target": "対象",
        "compare_image_rendering": "レンダリング中...",
        "compare_image_status_ready": "準備完了。",
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
        "compare_item_status_pending": "未完了",
        "compare_item_status_rendering": "レンダリング中",
        "compare_item_status_diff": "差分あり",
        "compare_item_status_same": "差分なし",
        "compare_item_status_error": "エラー",
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
        "version_current": "版本: {current}",
        "version_check_latest": "检查最新版本",
        "version_checking": "正在检查最新版本...",
        "version_latest_up_to_date": "最新: {latest}（已是最新）",
        "version_latest_available": "最新: {latest}（有可用更新）",
        "version_latest_ahead": "最新: {latest}（当前版本更新）",
        "version_latest_unknown": "最新: {latest}",
        "version_check_failed": "最新版本检查失败",
        "version_open_repo": "打开网页",
        "snapshot_window_title": "快照",
        "snapshot_selected_project": "项目: {project}",
        "snapshot_open_compare": "打开对比界面",
        "snapshot_back": "返回",
        "compare_preview_title": "预览",
        "footer": "设置文件: {path}",
        "dlg_select_cli": "选择 kicad-cli",
        "dlg_open_project": "打开 KiCad 项目",
        "warning_cli_title": "需要 KiCad CLI",
        "warning_cli_text": "kicad-cli 路径无效。请修正 CLI 设置。",
        "warning_project_title": "需要项目",
        "warning_project_text": "请从列表中选择项目，或打开新项目。",
        "ready_title": "就绪",
        "ready_text": "启动检查已通过。\n\nCLI: {cli}\nProject: {project}\n默认输出目录: {output}",
        "compare_window_title": "快照比较",
        "compare_filter": "来源",
        "compare_filter_both": "全部",
        "compare_filter_backup": "仅备份",
        "compare_filter_git": "仅 Git",
        "compare_refresh": "刷新",
        "compare_limit": "上限",
        "compare_timeline": "时间线",
        "compare_create_backup": "创建备份",
        "compare_backup_memo": "备注",
        "compare_backup_memo_placeholder": "可选",
        "compare_backup_note": "KiCad 内置备份：5 分钟后自动备份，超过 25 代自动清理（可在 KiCad 设置中修改）。",
        "compare_git_group": "Git 操作",
        "compare_git_msg_placeholder": "提交信息",
        "compare_git_commit": "提交",
        "compare_git_push": "推送",
        "compare_git_pull": "拉取",
        "compare_from": "比较来源 (Before)",
        "compare_to": "比较目标 (After)",
        "compare_current_project": "[当前] 项目文件",
        "compare_run": "比较",
        "compare_git_unavailable": "此项目不可用 Git。",
        "compare_need_two": "请选择两个比较目标。",
        "compare_same": "请选择不同项目。",
        "compare_started_title": "比较",
        "compare_backup_title": "备份",
        "compare_started_text": "开始比较。\n\nBefore: {from_item}\nAfter: {to_item}",
        "compare_result_title": "比较结果",
        "compare_result_summary": "新增: {added}  删除: {removed}  变更: {changed}  无变更: {unchanged}",
        "compare_result_files": "变更文件",
        "compare_result_no_diff": "没有差异文件。",
        "compare_result_error": "比较失败: {error}",
        "compare_close": "关闭",
        "compare_back": "返回",
        "compare_visual_title": "可视化差异",
        "compare_visual_file": "文件",
        "compare_visual_before": "Before",
        "compare_visual_after": "After",
        "compare_visual_empty": "(空)",
        "compare_image_title": "图像差异",
        "compare_loading": "正在加载比较数据...",
        "compare_image_target": "目标",
        "compare_image_rendering": "渲染中...",
        "compare_image_status_ready": "就绪。",
        "compare_image_render": "渲染",
        "compare_image_status": "请选择图纸/页面目标并渲染。",
        "compare_image_no_targets": "未找到可渲染的图纸/页面目标。",
        "compare_image_missing_side": "此目标在一侧不存在。缺失侧将显示为空白。",
        "compare_image_pcb_board": "PCB / 全体",
        "compare_image_before": "Before 图像",
        "compare_image_after": "After 图像",
        "compare_image_diff": "差分图像",
        "compare_image_not_available": "仅对 .kicad_sch/.kicad_pcb 内容提供图像差分。",
        "compare_image_zoom_out": "缩小",
        "compare_image_zoom_in": "放大",
        "compare_image_zoom_fit": "适应",
        "compare_item_status_pending": "未完成",
        "compare_item_status_rendering": "渲染中",
        "compare_item_status_diff": "有差异",
        "compare_item_status_same": "无差异",
        "compare_item_status_error": "错误",
        "compare_backup_created": "已创建备份: {path}",
        "compare_git_commit_need_msg": "请输入提交信息。",
        "compare_git_ok_title": "Git",
        "compare_git_fail_title": "Git 错误",
        "compare_git_commit_ok": "提交完成。",
        "compare_git_push_ok": "推送完成。",
        "compare_git_pull_ok": "拉取完成。",
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
        "version_current": "Version: {current}",
        "version_check_latest": "Verifier la derniere version",
        "version_checking": "Verification de la derniere version...",
        "version_latest_up_to_date": "Derniere: {latest} (a jour)",
        "version_latest_available": "Derniere: {latest} (mise a jour disponible)",
        "version_latest_ahead": "Derniere: {latest} (version courante plus recente)",
        "version_latest_unknown": "Derniere: {latest}",
        "version_check_failed": "Echec de verification de la derniere version",
        "version_open_repo": "Ouvrir la page web",
        "snapshot_window_title": "Snapshots",
        "snapshot_selected_project": "Projet: {project}",
        "snapshot_open_compare": "Ouvrir l'ecran de comparaison",
        "snapshot_back": "Retour",
        "compare_preview_title": "Apercu",
        "footer": "Fichier de configuration: {path}",
        "dlg_select_cli": "Selectionner kicad-cli",
        "dlg_open_project": "Ouvrir un projet KiCad",
        "warning_cli_title": "KiCad CLI requis",
        "warning_cli_text": "Le chemin kicad-cli est invalide. Corrigez les parametres CLI.",
        "warning_project_title": "Projet requis",
        "warning_project_text": "Selectionnez un projet dans la liste ou ouvrez-en un nouveau.",
        "ready_title": "Pret",
        "ready_text": "Les verifications de demarrage sont validees.\n\nCLI: {cli}\nProjet: {project}\nSortie par defaut: {output}",
        "compare_window_title": "Comparaison de snapshots",
        "compare_filter": "Source",
        "compare_filter_both": "Les deux",
        "compare_filter_backup": "Sauvegarde seulement",
        "compare_filter_git": "Git seulement",
        "compare_refresh": "Rafraichir",
        "compare_limit": "Limite",
        "compare_timeline": "Chronologie",
        "compare_create_backup": "Creer une sauvegarde",
        "compare_backup_memo": "Memo",
        "compare_backup_memo_placeholder": "optionnel",
        "compare_backup_note": "Sauvegarde KiCad: sauvegarde auto apres 5 minutes, suppression auto apres 25 generations (configurable).",
        "compare_git_group": "Operations Git",
        "compare_git_msg_placeholder": "Message de commit",
        "compare_git_commit": "Commit",
        "compare_git_push": "Push",
        "compare_git_pull": "Pull",
        "compare_from": "Comparer depuis (Before)",
        "compare_to": "Comparer vers (After)",
        "compare_current_project": "[Actuel] Fichiers du projet",
        "compare_run": "Comparer",
        "compare_git_unavailable": "Git est indisponible pour ce projet.",
        "compare_need_two": "Selectionnez deux cibles de comparaison.",
        "compare_same": "Veuillez choisir des elements differents.",
        "compare_started_title": "Comparaison",
        "compare_backup_title": "Sauvegarde",
        "compare_started_text": "Comparaison demandee.\n\nBefore: {from_item}\nAfter: {to_item}",
        "compare_result_title": "Resultat de comparaison",
        "compare_result_summary": "Ajoutes: {added}  Supprimes: {removed}  Modifies: {changed}  Inchanges: {unchanged}",
        "compare_result_files": "Fichiers modifies",
        "compare_result_no_diff": "Aucun fichier modifie.",
        "compare_result_error": "Echec de comparaison: {error}",
        "compare_close": "Fermer",
        "compare_back": "Retour",
        "compare_visual_title": "Diff visuel",
        "compare_visual_file": "Fichier",
        "compare_visual_before": "Before",
        "compare_visual_after": "After",
        "compare_visual_empty": "(vide)",
        "compare_image_title": "Diff d'image",
        "compare_loading": "Chargement des donnees de comparaison...",
        "compare_image_target": "Cible",
        "compare_image_rendering": "Rendu en cours...",
        "compare_image_status_ready": "Pret.",
        "compare_image_render": "Rendu",
        "compare_image_status": "Selectionnez une cible feuille/page et lancez le rendu.",
        "compare_image_no_targets": "Aucune cible de feuille/page trouvée.",
        "compare_image_missing_side": "Cette cible n'existe que d'un cote. Le cote manquant est vide.",
        "compare_image_pcb_board": "PCB / carte",
        "compare_image_before": "Image Before",
        "compare_image_after": "Image After",
        "compare_image_diff": "Image Diff",
        "compare_image_not_available": "Le diff d'image est disponible pour .kicad_sch/.kicad_pcb.",
        "compare_image_zoom_out": "Zoom -",
        "compare_image_zoom_in": "Zoom +",
        "compare_image_zoom_fit": "Ajuster",
        "compare_item_status_pending": "En attente",
        "compare_item_status_rendering": "Rendu",
        "compare_item_status_diff": "Diff",
        "compare_item_status_same": "Identique",
        "compare_item_status_error": "Erreur",
        "compare_backup_created": "Sauvegarde creee: {path}",
        "compare_git_commit_need_msg": "Le message de commit est requis.",
        "compare_git_ok_title": "Git",
        "compare_git_fail_title": "Erreur Git",
        "compare_git_commit_ok": "Commit termine.",
        "compare_git_push_ok": "Push termine.",
        "compare_git_pull_ok": "Pull termine.",
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
        "version_current": "Version: {current}",
        "version_check_latest": "Neueste Version prufen",
        "version_checking": "Neueste Version wird gepruft...",
        "version_latest_up_to_date": "Neueste: {latest} (aktuell)",
        "version_latest_available": "Neueste: {latest} (Update verfugbar)",
        "version_latest_ahead": "Neueste: {latest} (aktuelle Version ist neuer)",
        "version_latest_unknown": "Neueste: {latest}",
        "version_check_failed": "Prufung der neuesten Version fehlgeschlagen",
        "version_open_repo": "Webseite offnen",
        "snapshot_window_title": "Snapshots",
        "snapshot_selected_project": "Projekt: {project}",
        "snapshot_open_compare": "Vergleichsansicht offnen",
        "snapshot_back": "Zuruck",
        "compare_preview_title": "Vorschau",
        "footer": "Einstellungsdatei: {path}",
        "dlg_select_cli": "kicad-cli auswahlen",
        "dlg_open_project": "KiCad-Projekt offnen",
        "warning_cli_title": "KiCad CLI erforderlich",
        "warning_cli_text": "kicad-cli Pfad ist ungueltig. Bitte CLI-Einstellungen korrigieren.",
        "warning_project_title": "Projekt erforderlich",
        "warning_project_text": "Projekt aus der Liste auswahlen oder neues Projekt offnen.",
        "ready_title": "Bereit",
        "ready_text": "Startprufungen bestanden.\n\nCLI: {cli}\nProjekt: {project}\nStandardausgabe: {output}",
        "compare_window_title": "Snapshot Vergleich",
        "compare_filter": "Quelle",
        "compare_filter_both": "Beide",
        "compare_filter_backup": "Nur Backup",
        "compare_filter_git": "Nur Git",
        "compare_refresh": "Aktualisieren",
        "compare_limit": "Limit",
        "compare_timeline": "Zeitachse",
        "compare_create_backup": "Backup erstellen",
        "compare_backup_memo": "Memo",
        "compare_backup_memo_placeholder": "optional",
        "compare_backup_note": "KiCad Standard-Backup: auto nach 5 Minuten, auto-bereinigt nach 25 Generationen (konfigurierbar).",
        "compare_git_group": "Git Operationen",
        "compare_git_msg_placeholder": "Commit Nachricht",
        "compare_git_commit": "Commit",
        "compare_git_push": "Push",
        "compare_git_pull": "Pull",
        "compare_from": "Vergleichen von (Before)",
        "compare_to": "Vergleichen mit (After)",
        "compare_current_project": "[Aktuell] Projektdateien",
        "compare_run": "Vergleichen",
        "compare_git_unavailable": "Git ist fur dieses Projekt nicht verfugbar.",
        "compare_need_two": "Bitte zwei Vergleichsziele auswahlen.",
        "compare_same": "Bitte unterschiedliche Elemente auswahlen.",
        "compare_started_title": "Vergleich",
        "compare_backup_title": "Backup",
        "compare_started_text": "Vergleich angefordert.\n\nBefore: {from_item}\nAfter: {to_item}",
        "compare_result_title": "Vergleichsergebnis",
        "compare_result_summary": "Hinzugefugt: {added}  Entfernt: {removed}  Geandert: {changed}  Unverandert: {unchanged}",
        "compare_result_files": "Geanderte Dateien",
        "compare_result_no_diff": "Keine geanderten Dateien.",
        "compare_result_error": "Vergleich fehlgeschlagen: {error}",
        "compare_close": "Schliessen",
        "compare_back": "Zuruck",
        "compare_visual_title": "Visueller Diff",
        "compare_visual_file": "Datei",
        "compare_visual_before": "Before",
        "compare_visual_after": "After",
        "compare_visual_empty": "(leer)",
        "compare_image_title": "Bildvergleich",
        "compare_loading": "Vergleichsdaten werden geladen...",
        "compare_image_target": "Ziel",
        "compare_image_rendering": "Rendering...",
        "compare_image_status_ready": "Bereit.",
        "compare_image_render": "Rendern",
        "compare_image_status": "Bitte Zielblatt/-seite auswahlen und rendern.",
        "compare_image_no_targets": "Kein renderbares Blatt/Seitenziel gefunden.",
        "compare_image_missing_side": "Dieses Ziel existiert nur auf einer Seite. Fehlende Seite wird leer angezeigt.",
        "compare_image_pcb_board": "PCB / Platine",
        "compare_image_before": "Before Bild",
        "compare_image_after": "After Bild",
        "compare_image_diff": "Diff Bild",
        "compare_image_not_available": "Bilddiff ist fur .kicad_sch/.kicad_pcb Inhalte verfugbar.",
        "compare_image_zoom_out": "Verkleinern",
        "compare_image_zoom_in": "Vergrossern",
        "compare_image_zoom_fit": "Anpassen",
        "compare_item_status_pending": "Ausstehend",
        "compare_item_status_rendering": "Rendering",
        "compare_item_status_diff": "Diff",
        "compare_item_status_same": "Gleich",
        "compare_item_status_error": "Fehler",
        "compare_backup_created": "Backup erstellt: {path}",
        "compare_git_commit_need_msg": "Commit Nachricht ist erforderlich.",
        "compare_git_ok_title": "Git",
        "compare_git_fail_title": "Git Fehler",
        "compare_git_commit_ok": "Commit abgeschlossen.",
        "compare_git_push_ok": "Push abgeschlossen.",
        "compare_git_pull_ok": "Pull abgeschlossen.",
    },
}

# Fill missing localized keys with English fallback values so every locale
# has a complete key set.
_en_table = TRANSLATIONS["en"]
for _lang, _table in TRANSLATIONS.items():
    if _lang == "en":
        continue
    for _key, _value in _en_table.items():
        _table.setdefault(_key, _value)


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

        window_width = data.get("window_width")
        if isinstance(window_width, int):
            lines.append(f"window_width = {window_width}")

        window_height = data.get("window_height")
        if isinstance(window_height, int):
            lines.append(f"window_height = {window_height}")

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


def run_subprocess(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    if sys.platform.startswith("win"):
        flags = int(kwargs.pop("creationflags", 0))
        kwargs["creationflags"] = flags | int(getattr(subprocess, "CREATE_NO_WINDOW", 0))
        startupinfo = kwargs.pop("startupinfo", None)
        if startupinfo is None:
            startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0  # SW_HIDE
        kwargs["startupinfo"] = startupinfo
    return subprocess.run(cmd, **kwargs)


def probe_kicad_cli(path: Path) -> CliCandidate | None:
    result: subprocess.CompletedProcess[str] | None = None
    for timeout_sec in (5, 10):
        try:
            result = run_subprocess(
                [str(path), "--version"],
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
            )
            break
        except Exception:
            continue
    if result is None:
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


def probe_git(path: Path) -> CliCandidate | None:
    result: subprocess.CompletedProcess[str] | None = None
    for timeout_sec in (5, 10):
        try:
            result = run_subprocess(
                [str(path), "--version"],
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
            )
            break
        except Exception:
            continue
    if result is None:
        return None

    output = (result.stdout or "").strip() or (result.stderr or "").strip()
    version, version_text = parse_version_text(output)
    if result.returncode != 0 or version is None:
        return None
    return CliCandidate(path=path, version=version, version_text=version_text)


def discover_git_candidates() -> list[CliCandidate]:
    checked: set[Path] = set()
    candidates: list[CliCandidate] = []
    for p in iter_git_candidate_paths():
        path = p.expanduser()
        if not path.exists() or path.is_dir():
            continue
        try:
            resolved = path.resolve()
        except Exception:
            resolved = path
        if resolved in checked:
            continue
        checked.add(resolved)
        cand = probe_git(resolved)
        if cand:
            candidates.append(cand)
    return candidates


def iter_git_candidate_paths() -> Iterable[Path]:
    for p in likely_git_paths():
        yield p
    from_path = shutil.which("git")
    if from_path:
        yield Path(from_path)


def likely_git_paths() -> list[Path]:
    candidates: list[Path] = []
    if sys.platform.startswith("win"):
        roots = [
            os.environ.get("ProgramFiles"),
            os.environ.get("ProgramFiles(x86)"),
            os.environ.get("LOCALAPPDATA"),
            str(Path.home() / "AppData" / "Local"),
            r"C:\Program Files",
            r"C:\Program Files (x86)",
        ]
        for root in roots:
            if not root:
                continue
            root_path = Path(root)
            if not root_path.exists():
                continue
            candidates.extend(root_path.glob("Git/cmd/git.exe"))
            candidates.extend(root_path.glob("Git/bin/git.exe"))
            candidates.extend(root_path.glob("Programs/Git/cmd/git.exe"))
            candidates.extend(root_path.glob("Programs/Git/bin/git.exe"))
    else:
        for p in ["/usr/bin/git", "/usr/local/bin/git", "/opt/homebrew/bin/git", "/opt/local/bin/git"]:
            candidates.append(Path(p))
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
            # Per-user installer location (e.g. %LOCALAPPDATA%\\Programs\\KiCad\\9.0\\bin)
            os.environ.get("LOCALAPPDATA"),
            str(Path.home() / "AppData" / "Local"),
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
            candidates.extend(root_path.glob("Programs/KiCad/*/bin/kicad-cli.exe"))
            candidates.extend(root_path.glob("Programs/KiCad/bin/kicad-cli.exe"))
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
    return run_subprocess(
        [executable, "-C", str(project_dir), *args],
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )


def run_git_bytes(project_dir: Path, args: list[str], git_path: str | None) -> subprocess.CompletedProcess[bytes]:
    executable = git_path or "git"
    return run_subprocess(
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


def export_svg_bundle_with_kicad_cli(
    cli_path: Path,
    source_file: Path,
    out_dir: Path,
    kind: str,
    pcb_layers: str | None = None,
) -> list[Path]:
    if kind == "sch":
        commands = [
            [str(cli_path), "sch", "export", "svg", str(source_file), "-o", str(out_dir)],
        ]
    elif kind == "pcb":
        # Try broad layer sets first to get a board-wide render on varying KiCad versions.
        if pcb_layers:
            # Some KiCad versions expect file output when --layers is specified.
            out_file = out_dir / "layer.svg"
            commands = [[
                str(cli_path),
                "pcb",
                "export",
                "svg",
                "--layers",
                pcb_layers,
                str(source_file),
                "-o",
                str(out_file),
            ]]
        else:
            layer_sets = [
                "F.Cu,B.Cu,F.SilkS,B.SilkS,Edge.Cuts",
                "F.Cu,B.Cu",
                "F.Cu",
            ]
            commands = [
                (
                    [
                        str(cli_path),
                        "pcb",
                        "export",
                        "svg",
                        "--layers",
                        layers,
                        str(source_file),
                        "-o",
                        str(out_dir / "board.svg"),
                    ]
                )
                for layers in layer_sets
            ]
    else:
        raise RuntimeError(f"Unsupported kind: {kind}")

    last_err = ""
    for cmd in commands:
        result = run_subprocess(cmd, check=False, capture_output=True, text=True, timeout=40)
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


def images_different(before: QImage, after: QImage) -> bool:
    width = max(before.width(), after.width())
    height = max(before.height(), after.height())
    b = pad_image(before, width, height)
    a = pad_image(after, width, height)
    for y in range(height):
        for x in range(width):
            if b.pixel(x, y) != a.pixel(x, y):
                return True
    return False


def normalize_image_sizes(before: QImage, after: QImage) -> tuple[QImage, QImage]:
    width = max(before.width(), after.width())
    height = max(before.height(), after.height())
    return pad_image(before, width, height), pad_image(after, width, height)


def parse_pcb_layers_from_file(pcb_path: Path) -> list[str]:
    try:
        text = pcb_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    # KiCad PCB format contains lines like: (0 "F.Cu" signal)
    names = re.findall(r'\(\s*\d+\s+"([^"]+)"\s+', text)
    unique: list[str] = []
    seen = set()
    for name in names:
        if name in seen:
            continue
        seen.add(name)
        unique.append(name)
    return unique


def detect_pcb_layers(cli_path: Path, pcb_path: Path) -> list[str]:
    candidates = [
        [str(cli_path), "pcb", "layers", "list", str(pcb_path)],
        [str(cli_path), "pcb", "list-layers", str(pcb_path)],
    ]
    for cmd in candidates:
        try:
            result = run_subprocess(cmd, check=False, capture_output=True, text=True, timeout=10)
        except Exception:
            continue
        if result.returncode != 0:
            continue
        layers: list[str] = []
        for line in (result.stdout or "").splitlines():
            token = line.strip().split()[0] if line.strip() else ""
            if token and "." in token:
                layers.append(token)
        if layers:
            return list(dict.fromkeys(layers))
    return parse_pcb_layers_from_file(pcb_path)


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
        if hasattr(self, "compare_back_btn"):
            self.compare_back_btn.setText(self.t("compare_back"))
        if hasattr(self, "compare_close_btn"):
            self.compare_close_btn.setText(self.t("compare_close"))

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
            create_project_backup(
                self.project_file,
                memo=self.backup_memo_input.text(),
            )
        except Exception as exc:
            QMessageBox.warning(self, self.t("compare_git_fail_title"), str(exc))
            return
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

        dialog = EmptyCompareDialog(
            title=self.t("compare_result_title"),
            close_text=self.t("compare_close"),
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


class EmptyCompareDialog(QDialog):
    def __init__(self, title: str, close_text: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setModal(True)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle(title)
        self.setMinimumSize(900, 560)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        placeholder = QWidget()
        placeholder.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        root.addWidget(placeholder, 1)

        actions = QHBoxLayout()
        actions.addStretch(1)
        close_btn = QPushButton(close_text)
        close_btn.clicked.connect(self.accept)
        actions.addWidget(close_btn)
        root.addLayout(actions)


class ItemDiffDialog(QDialog):
    def __init__(
        self,
        title: str,
        cli_path: Path,
        before_map: dict[str, bytes],
        after_map: dict[str, bytes],
        t_func: Callable[[str], str],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setWindowModality(Qt.ApplicationModal)
        self.setMinimumSize(1100, 680)

        self.cli_path = cli_path
        self.before_map = before_map
        self.after_map = after_map
        self.t = t_func
        self.targets: list[dict[str, str | None]] = []
        self._tmp_before_dir_obj: tempfile.TemporaryDirectory[str] | None = None
        self._tmp_after_dir_obj: tempfile.TemporaryDirectory[str] | None = None
        self._tmp_render_dir_obj: tempfile.TemporaryDirectory[str] | None = None
        self.before_root: Path | None = None
        self.after_root: Path | None = None
        self.render_root: Path | None = None
        self.render_cache: dict[str, tuple[QImage, QImage, QImage]] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        self.status = QLabel(self.t("compare_image_rendering"))
        self.status.setStyleSheet("color: #666666;")
        root.addWidget(self.status)

        split = QSplitter(Qt.Horizontal)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)
        left_layout.addWidget(QLabel(self.t("compare_image_target")))
        self.target_list = QListWidget()
        self.target_list.currentRowChanged.connect(self.on_target_selected)
        left_layout.addWidget(self.target_list, 1)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)

        self.image_tabs = QTabWidget()
        self.diff_label = QLabel()
        self.before_label = QLabel()
        self.after_label = QLabel()
        for label in [self.diff_label, self.before_label, self.after_label]:
            label.setAlignment(Qt.AlignCenter)
            label.setText(self.t("compare_image_not_available"))
        self.image_tabs.addTab(self._wrap_image_label(self.diff_label), self.t("compare_image_diff"))
        self.image_tabs.addTab(self._wrap_image_label(self.before_label), self.t("compare_image_before"))
        self.image_tabs.addTab(self._wrap_image_label(self.after_label), self.t("compare_image_after"))
        right_layout.addWidget(self.image_tabs, 1)

        split.addWidget(left)
        split.addWidget(right)
        split.setStretchFactor(0, 2)
        split.setStretchFactor(1, 5)
        root.addWidget(split, 1)

        actions = QHBoxLayout()
        actions.addStretch(1)
        close_btn = QPushButton(self.t("compare_close"))
        close_btn.clicked.connect(self.accept)
        actions.addWidget(close_btn)
        root.addLayout(actions)

        QTimer.singleShot(0, self.load_targets)

    def _wrap_image_label(self, label: QLabel) -> QWidget:
        wrap = QWidget()
        layout = QVBoxLayout(wrap)
        layout.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(False)
        scroll.setWidget(label)
        layout.addWidget(scroll, 1)
        return wrap

    def _target_key(self, target: dict[str, str | None]) -> str:
        kind = target.get("kind") or ""
        rel_path = target.get("path") or ""
        layer = target.get("layer") or ""
        return f"{kind}|{rel_path}|{layer}"

    def load_targets(self) -> None:
        self.target_list.clear()
        self.targets.clear()
        self.render_cache.clear()

        self._cleanup_temp_dirs()
        self._tmp_before_dir_obj = tempfile.TemporaryDirectory(prefix="ksnap_list_before_")
        self._tmp_after_dir_obj = tempfile.TemporaryDirectory(prefix="ksnap_list_after_")
        self._tmp_render_dir_obj = tempfile.TemporaryDirectory(prefix="ksnap_list_render_")
        self.before_root = Path(self._tmp_before_dir_obj.name)
        self.after_root = Path(self._tmp_after_dir_obj.name)
        self.render_root = Path(self._tmp_render_dir_obj.name)
        write_file_map(self.before_root, self.before_map)
        write_file_map(self.after_root, self.after_map)

        sch_paths = sorted(
            {
                p.relative_to(self.before_root).as_posix()
                for p in self.before_root.rglob("*.kicad_sch")
            }
            | {
                p.relative_to(self.after_root).as_posix()
                for p in self.after_root.rglob("*.kicad_sch")
            }
        )
        for rel_path in sch_paths:
            self.targets.append({"kind": "sch", "path": rel_path, "layer": None})
            self.target_list.addItem(f"SCH / {rel_path}")

        pcb_paths = sorted(
            {
                p.relative_to(self.before_root).as_posix()
                for p in self.before_root.rglob("*.kicad_pcb")
            }
            | {
                p.relative_to(self.after_root).as_posix()
                for p in self.after_root.rglob("*.kicad_pcb")
            }
        )
        for rel_path in pcb_paths:
            self.targets.append({"kind": "pcb", "path": rel_path, "layer": None})
            self.target_list.addItem(f"PCB / {rel_path} / board")

            layers: list[str] = []
            before_pcb = self.before_root / rel_path
            after_pcb = self.after_root / rel_path
            if before_pcb.exists():
                layers.extend(detect_pcb_layers(self.cli_path, before_pcb))
            if after_pcb.exists():
                layers.extend(detect_pcb_layers(self.cli_path, after_pcb))
            unique_layers = list(dict.fromkeys(layers))
            for layer in unique_layers:
                self.targets.append({"kind": "pcb", "path": rel_path, "layer": layer})
                self.target_list.addItem(f"PCB / {rel_path} / {layer}")

        if self.target_list.count() == 0:
            self.status.setText(self.t("compare_image_no_targets"))
            self.status.setStyleSheet("color: #9a6700;")
            return

        self.status.setText(self.t("compare_image_status_ready"))
        self.status.setStyleSheet("color: #2b7a0b;")
        self.target_list.setCurrentRow(0)

    def on_target_selected(self, row: int) -> None:
        if row < 0 or row >= len(self.targets):
            return
        target = self.targets[row]
        key = self._target_key(target)
        if key in self.render_cache:
            before_img, after_img, diff_img = self.render_cache[key]
            self._set_images(before_img, after_img, diff_img)
            return

        try:
            before_img, after_img, diff_img = self._render_target(target)
        except Exception as exc:
            self.status.setText(str(exc))
            self.status.setStyleSheet("color: #b00020;")
            return
        self.render_cache[key] = (before_img, after_img, diff_img)
        self._set_images(before_img, after_img, diff_img)
        self.status.setText(self.t("compare_image_status_ready"))
        self.status.setStyleSheet("color: #2b7a0b;")

    def _render_target(self, target: dict[str, str | None]) -> tuple[QImage, QImage, QImage]:
        if self.before_root is None or self.after_root is None or self.render_root is None:
            raise RuntimeError(self.t("compare_image_not_available"))

        kind = target.get("kind")
        rel_path = target.get("path")
        layer = target.get("layer")
        if not isinstance(kind, str) or not isinstance(rel_path, str):
            raise RuntimeError(self.t("compare_image_not_available"))

        before_source = self.before_root / rel_path
        after_source = self.after_root / rel_path
        base = self._safe_name(self._target_key(target))

        before_svg = self._export_side_svg(
            source=before_source if before_source.exists() else None,
            out_dir=self.render_root / "before" / base,
            kind=kind,
            layer=layer,
        )
        after_svg = self._export_side_svg(
            source=after_source if after_source.exists() else None,
            out_dir=self.render_root / "after" / base,
            kind=kind,
            layer=layer,
        )

        if before_svg is None and after_svg is None:
            raise RuntimeError(self.t("compare_image_not_available"))

        before_img = render_svg_to_image(before_svg) if before_svg is not None else None
        after_img = render_svg_to_image(after_svg) if after_svg is not None else None
        if before_img is None and after_img is None:
            raise RuntimeError(self.t("compare_image_not_available"))
        if before_img is None:
            before_img = QImage(after_img.width(), after_img.height(), QImage.Format_ARGB32)  # type: ignore[union-attr]
            before_img.fill(Qt.white)
        if after_img is None:
            after_img = QImage(before_img.width(), before_img.height(), QImage.Format_ARGB32)  # type: ignore[union-attr]
            after_img.fill(Qt.white)

        before_img, after_img = normalize_image_sizes(before_img, after_img)
        diff_img = make_pixel_diff_image(before_img, after_img)
        return before_img, after_img, diff_img

    def _export_side_svg(
        self,
        source: Path | None,
        out_dir: Path,
        kind: str,
        layer: str | None,
    ) -> Path | None:
        if source is None:
            return None
        out_dir.mkdir(parents=True, exist_ok=True)
        if kind == "sch":
            svgs = export_svg_bundle_with_kicad_cli(self.cli_path, source, out_dir, "sch")
        elif kind == "pcb":
            svgs = export_svg_bundle_with_kicad_cli(self.cli_path, source, out_dir, "pcb", pcb_layers=layer)
        else:
            return None
        return svgs[0] if svgs else None

    @staticmethod
    def _safe_name(value: str) -> str:
        return re.sub(r"[^A-Za-z0-9._-]+", "_", value)

    def _set_images(self, before_img: QImage, after_img: QImage, diff_img: QImage) -> None:
        self._set_image(self.diff_label, diff_img)
        self._set_image(self.before_label, before_img)
        self._set_image(self.after_label, after_img)
        self.image_tabs.setCurrentIndex(0)

    def _set_image(self, label: QLabel, image: QImage) -> None:
        pixmap = QPixmap.fromImage(image)
        label.setPixmap(pixmap)
        label.resize(pixmap.size())

    def _cleanup_temp_dirs(self) -> None:
        for obj in [self._tmp_before_dir_obj, self._tmp_after_dir_obj, self._tmp_render_dir_obj]:
            if obj is not None:
                obj.cleanup()
        self._tmp_before_dir_obj = None
        self._tmp_after_dir_obj = None
        self._tmp_render_dir_obj = None

    def closeEvent(self, event) -> None:
        self._cleanup_temp_dirs()
        super().closeEvent(event)


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
        self.before_root: Path | None = None
        self.after_root: Path | None = None

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
        self.image_zoom_out_btn = QPushButton(image_zoom_out_text)
        self.image_zoom_in_btn = QPushButton(image_zoom_in_text)
        self.image_zoom_fit_btn = QPushButton(image_zoom_fit_text)
        self.image_zoom_out_btn.clicked.connect(self.zoom_out_images)
        self.image_zoom_in_btn.clicked.connect(self.zoom_in_images)
        self.image_zoom_fit_btn.clicked.connect(self.zoom_fit_images)
        image_button_row.addWidget(self.image_target_label)
        image_button_row.addWidget(self.image_zoom_out_btn)
        image_button_row.addWidget(self.image_zoom_in_btn)
        image_button_row.addWidget(self.image_zoom_fit_btn)
        image_button_row.addStretch(1)
        image_layout.addLayout(image_button_row)

        self.image_status = QLabel(image_status_text)
        self.image_status.setWordWrap(True)
        self.image_status.setStyleSheet("color: #666666;")
        image_layout.addWidget(self.image_status)

        self.image_target_list = QListWidget()
        self.image_target_list.currentRowChanged.connect(self.on_image_target_selected)
        image_layout.addWidget(self.image_target_list, 1)

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
        self.image_status.setText(image_status_text)
        self.image_status.setStyleSheet("color: #666666;")
        QTimer.singleShot(0, self.prepare_image_targets)

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
        self.image_target_list.clear()
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
            self.before_root = before_root
            self.after_root = after_root

            write_file_map(before_root, self.before_map)
            write_file_map(after_root, self.after_map)

            self.before_svg_map.update(self._export_side_svgs(before_root, out_before, []))
            self.after_svg_map.update(self._export_side_svgs(after_root, out_after, []))

            before_pcb = first_matching_file(before_root, ".kicad_pcb")
            after_pcb = first_matching_file(after_root, ".kicad_pcb")
            layers: list[str] = []
            if before_pcb is not None:
                layers.extend(detect_pcb_layers(self.cli_path, before_pcb))
            if after_pcb is not None:
                layers.extend(detect_pcb_layers(self.cli_path, after_pcb))
            layers = list(dict.fromkeys(layers))
            self.before_svg_map.update(self._export_side_svgs(before_root, out_before, layers))
            self.after_svg_map.update(self._export_side_svgs(after_root, out_after, layers))

            all_keys = sorted(set(self.before_svg_map.keys()) | set(self.after_svg_map.keys()))
            for key in all_keys:
                kind, rel = key.split("|", 1)
                if kind == "pcb" and rel == "__board__":
                    label = self.t("compare_image_pcb_board")
                else:
                    prefix = "SCH" if kind == "sch" else "PCB"
                    label = f"{prefix} / {rel}"
                self.image_targets.append((key, label))
                status = "Diff" if self._target_has_diff(key) else "Same"
                self.image_target_list.addItem(f"{label}  [{status}]")

            if self.image_target_list.count() == 0:
                self.image_status.setText(self.image_no_targets_text)
                self.image_status.setStyleSheet("color: #9a6700;")
            else:
                self.image_status.setText(self.image_status_default_text)
                self.image_status.setStyleSheet("color: #666666;")
                self.image_target_list.setCurrentRow(0)
        except Exception as exc:
            self.image_status.setText(str(exc))
            self.image_status.setStyleSheet("color: #b00020;")

    def _export_side_svgs(self, source_root: Path, out_root: Path, layers: list[str]) -> dict[str, Path]:
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

            # Layer-specific exports
            for layer in layers:
                layer_dir = pcb_out / f"layer_{layer.replace('.', '_')}"
                layer_dir.mkdir(parents=True, exist_ok=True)
                try:
                    layer_svgs = export_svg_bundle_with_kicad_cli(
                        self.cli_path,
                        pcb_src,
                        layer_dir,
                        "pcb",
                        pcb_layers=layer,
                    )
                    if layer_svgs:
                        result[f"pcb|layer:{layer}"] = layer_svgs[0]
                except Exception:
                    continue
        return result

    def on_image_target_selected(self, row: int) -> None:
        if row < 0 or row >= len(self.image_targets):
            return
        key = self.image_targets[row][0]
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

    def _target_has_diff(self, key: str) -> bool:
        before_svg = self.before_svg_map.get(key)
        after_svg = self.after_svg_map.get(key)
        if before_svg is None or after_svg is None:
            return True
        try:
            return before_svg.read_bytes() != after_svg.read_bytes()
        except OSError:
            return True

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
        self.latest_version: str | None = None
        self.latest_version_state = "idle"

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

        version_row = QHBoxLayout()
        self.version_current_label = QLabel("")
        self.version_check_btn = QPushButton("")
        self.version_check_btn.clicked.connect(self.on_check_latest_version)
        self.version_repo_btn = QPushButton("")
        self.version_repo_btn.clicked.connect(self.open_repository)
        self.version_latest_label = QLabel("")
        self.version_latest_label.setStyleSheet("color: #666666;")
        version_row.addWidget(self.version_current_label)
        version_row.addWidget(self.version_check_btn)
        version_row.addWidget(self.version_repo_btn)
        version_row.addWidget(self.version_latest_label)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("color: #dddddd;")
        root_layout.addWidget(divider)

        self.footer = QLabel("")
        self.footer.setStyleSheet("color: #999999;")
        version_row.addStretch(1)
        version_row.addWidget(self.footer)
        root_layout.addLayout(version_row)

        self.startup_page = root
        self.snapshot_page = self._build_snapshot_page()
        self.compare_page = self._build_compare_page()
        self.page_stack = QStackedWidget()
        self.page_stack.addWidget(self.startup_page)
        self.page_stack.addWidget(self.snapshot_page)
        self.page_stack.addWidget(self.compare_page)
        self.page_stack.setCurrentWidget(self.startup_page)
        self.setCentralWidget(self.page_stack)
        self.restore_window_size()

        self.load_recent_projects()
        self.apply_translations()

        idx = self.language_combo.findData(self.language)
        if idx >= 0:
            self.language_combo.setCurrentIndex(idx)

        self.auto_detect_cli(initial=True)
        self.detect_git()

    def restore_window_size(self) -> None:
        width = self.settings.get("window_width")
        height = self.settings.get("window_height")
        if not isinstance(width, int) or not isinstance(height, int):
            return
        if width < 1 or height < 1:
            return
        screen = self.screen() or QGuiApplication.primaryScreen()
        if screen is not None:
            geom = screen.availableGeometry()
            width = min(width, geom.width())
            height = min(height, geom.height())
        self.resize(width, height)

    def closeEvent(self, event) -> None:
        self._cleanup_compare_temp_dirs()
        self.settings["window_width"] = self.width()
        self.settings["window_height"] = self.height()
        self.save_settings()
        super().closeEvent(event)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if hasattr(self, "compare_zoom_mode") and self.compare_zoom_mode == "fit":
            self._render_compare_image_labels()

    def _build_snapshot_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        self.snapshot_title = QLabel(self.t("snapshot_window_title"))
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.snapshot_title.setFont(font)
        layout.addWidget(self.snapshot_title)

        self.snapshot_project_label = QLabel("")
        self.snapshot_project_label.setStyleSheet("color: #666666;")
        layout.addWidget(self.snapshot_project_label)

        tools = QHBoxLayout()
        self.snapshot_filter_label = QLabel(self.t("compare_filter"))
        self.snapshot_filter_group = QButtonGroup(self)
        self.snapshot_filter_both = QRadioButton(self.t("compare_filter_both"))
        self.snapshot_filter_backup = QRadioButton(self.t("compare_filter_backup"))
        self.snapshot_filter_git = QRadioButton(self.t("compare_filter_git"))
        self.snapshot_filter_group.addButton(self.snapshot_filter_both)
        self.snapshot_filter_group.addButton(self.snapshot_filter_backup)
        self.snapshot_filter_group.addButton(self.snapshot_filter_git)
        self.snapshot_filter_both.toggled.connect(self.on_snapshot_filter_changed)
        self.snapshot_filter_backup.toggled.connect(self.on_snapshot_filter_changed)
        self.snapshot_filter_git.toggled.connect(self.on_snapshot_filter_changed)

        self.snapshot_limit_label = QLabel(self.t("compare_limit"))
        self.snapshot_limit_combo = QComboBox()
        for v in [20, 50, 100, 200, 500]:
            self.snapshot_limit_combo.addItem(str(v), v)
        limit = self.resolve_timeline_limit()
        idx = self.snapshot_limit_combo.findData(limit)
        if idx >= 0:
            self.snapshot_limit_combo.setCurrentIndex(idx)
        self.snapshot_limit_combo.currentIndexChanged.connect(self.on_snapshot_limit_changed)

        self.snapshot_refresh_btn = QPushButton(self.t("compare_refresh"))
        self.snapshot_refresh_btn.clicked.connect(self.refresh_snapshot_timeline)

        self.snapshot_backup_memo_label = QLabel(self.t("compare_backup_memo"))
        self.snapshot_backup_memo_input = QLineEdit()
        self.snapshot_backup_memo_input.setPlaceholderText(self.t("compare_backup_memo_placeholder"))
        self.snapshot_create_backup_btn = QPushButton(self.t("compare_create_backup"))
        self.snapshot_create_backup_btn.clicked.connect(self.on_snapshot_create_backup)

        tools.addWidget(self.snapshot_filter_label)
        tools.addWidget(self.snapshot_filter_both)
        tools.addWidget(self.snapshot_filter_backup)
        tools.addWidget(self.snapshot_filter_git)
        tools.addWidget(self.snapshot_limit_label)
        tools.addWidget(self.snapshot_limit_combo)
        tools.addWidget(self.snapshot_refresh_btn)
        tools.addStretch(1)
        tools.addWidget(self.snapshot_backup_memo_label)
        tools.addWidget(self.snapshot_backup_memo_input)
        tools.addWidget(self.snapshot_create_backup_btn)
        layout.addLayout(tools)

        self.snapshot_timeline_list = QListWidget()
        self.snapshot_timeline_list.currentRowChanged.connect(self.on_snapshot_timeline_row_changed)
        self.snapshot_timeline_list.itemDoubleClicked.connect(self.on_snapshot_timeline_double_clicked)
        layout.addWidget(self.snapshot_timeline_list, 1)

        compare_col = QVBoxLayout()
        from_row = QHBoxLayout()
        self.snapshot_from_label = QLabel(self.t("compare_from"))
        self.snapshot_from_combo = QComboBox()
        from_row.addWidget(self.snapshot_from_label)
        from_row.addWidget(self.snapshot_from_combo, 1)

        to_row = QHBoxLayout()
        self.snapshot_to_label = QLabel(self.t("compare_to"))
        self.snapshot_to_combo = QComboBox()
        self.snapshot_to_combo.addItem(self.t("compare_current_project"), "__current_project__")
        to_row.addWidget(self.snapshot_to_label)
        to_row.addWidget(self.snapshot_to_combo, 1)

        run_row = QHBoxLayout()
        self.snapshot_compare_btn = QPushButton("")
        self.snapshot_compare_btn.clicked.connect(self.open_compare_from_snapshot)
        run_row.addStretch(1)
        run_row.addWidget(self.snapshot_compare_btn)

        compare_col.addLayout(from_row)
        compare_col.addLayout(to_row)
        compare_col.addLayout(run_row)
        layout.addLayout(compare_col)

        actions = QHBoxLayout()
        self.snapshot_back_btn = QPushButton("")
        self.snapshot_back_btn.clicked.connect(self.show_startup_page)
        actions.addWidget(self.snapshot_back_btn)
        actions.addStretch(1)
        layout.addLayout(actions)

        self.snapshot_active_project: Path | None = None
        self.snapshot_items_all: list[SnapshotItem] = []
        self.snapshot_items_filtered: list[SnapshotItem] = []
        self.snapshot_filter_group.blockSignals(True)
        self.snapshot_filter_both.setChecked(True)
        self.snapshot_filter_group.blockSignals(False)
        return page

    def _build_compare_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)

        self.compare_title = QLabel(self.t("compare_window_title"))
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.compare_title.setFont(font)
        layout.addWidget(self.compare_title)

        content_split = QSplitter(Qt.Horizontal)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)
        self.compare_items_label = QLabel(self.t("compare_image_target"))
        left_layout.addWidget(self.compare_items_label)
        self.compare_item_list = QListWidget()
        self.compare_item_list.currentRowChanged.connect(self.on_compare_item_selected)
        left_layout.addWidget(self.compare_item_list, 1)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)
        self.compare_preview_title = QLabel(self.t("compare_image_title"))
        right_layout.addWidget(self.compare_preview_title)
        self.compare_image_scrolls: dict[str, QScrollArea] = {}
        zoom_row = QHBoxLayout()
        self.compare_zoom_out_btn = QPushButton(self.t("compare_image_zoom_out"))
        self.compare_zoom_in_btn = QPushButton(self.t("compare_image_zoom_in"))
        self.compare_zoom_fit_btn = QPushButton(self.t("compare_image_zoom_fit"))
        self.compare_zoom_out_btn.clicked.connect(self.on_compare_zoom_out)
        self.compare_zoom_in_btn.clicked.connect(self.on_compare_zoom_in)
        self.compare_zoom_fit_btn.clicked.connect(self.on_compare_zoom_fit)
        zoom_row.addWidget(self.compare_zoom_out_btn)
        zoom_row.addWidget(self.compare_zoom_in_btn)
        zoom_row.addWidget(self.compare_zoom_fit_btn)
        zoom_row.addStretch(1)
        right_layout.addLayout(zoom_row)
        self.compare_image_tabs = QTabWidget()
        self.compare_image_tabs.currentChanged.connect(self.on_compare_image_tab_changed)
        self.compare_diff_image_label = QLabel()
        self.compare_before_image_label = QLabel()
        self.compare_after_image_label = QLabel()
        for label in [self.compare_diff_image_label, self.compare_before_image_label, self.compare_after_image_label]:
            label.setAlignment(Qt.AlignCenter)
            label.setText(self.t("compare_image_not_available"))
        self.compare_image_tabs.addTab(self._wrap_compare_image_label("diff", self.compare_diff_image_label), self.t("compare_image_diff"))
        self.compare_image_tabs.addTab(self._wrap_compare_image_label("before", self.compare_before_image_label), self.t("compare_image_before"))
        self.compare_image_tabs.addTab(self._wrap_compare_image_label("after", self.compare_after_image_label), self.t("compare_image_after"))
        right_layout.addWidget(self.compare_image_tabs, 1)

        content_split.addWidget(left_panel)
        content_split.addWidget(right_panel)
        content_split.setStretchFactor(0, 1)
        content_split.setStretchFactor(1, 5)
        content_split.setSizes([260, 980])
        layout.addWidget(content_split, 1)
        self.compare_status_label = QLabel(self.t("compare_image_rendering"))
        self.compare_status_label.setStyleSheet("color: #666666;")
        layout.addWidget(self.compare_status_label)

        self.compare_active_project: Path | None = None
        self.compare_from_id: str | None = None
        self.compare_to_id: str | None = None
        self._compare_pending_from_id: str | None = None
        self._compare_pending_to_id: str | None = None
        self.compare_before_map: dict[str, bytes] = {}
        self.compare_after_map: dict[str, bytes] = {}
        self.compare_targets: list[dict[str, str | None]] = []
        self.compare_target_labels: list[str] = []
        self.compare_target_status: dict[str, str] = {}
        self.compare_render_cache: dict[str, tuple[QImage, QImage, QImage]] = {}
        self.compare_before_image_raw: QImage | None = None
        self.compare_after_image_raw: QImage | None = None
        self.compare_diff_image_raw: QImage | None = None
        self.compare_zoom_mode = "fit"
        self.compare_zoom_scale = 1.0
        self._compare_syncing_scroll = False
        self._compare_scroll_ratio_x = 0.0
        self._compare_scroll_ratio_y = 0.0
        self.compare_before_root: Path | None = None
        self.compare_after_root: Path | None = None
        self.compare_render_root: Path | None = None
        self._compare_tmp_before_obj: tempfile.TemporaryDirectory[str] | None = None
        self._compare_tmp_after_obj: tempfile.TemporaryDirectory[str] | None = None
        self._compare_tmp_render_obj: tempfile.TemporaryDirectory[str] | None = None
        self._compare_precache_thread: threading.Thread | None = None
        self._compare_precache_stop = threading.Event()
        self._compare_render_lock = threading.Lock()
        self._compare_status_lock = threading.Lock()
        self.compare_precache_active = False
        self.compare_status_refresh_timer = QTimer(self)
        self.compare_status_refresh_timer.setInterval(300)
        self.compare_status_refresh_timer.timeout.connect(self._refresh_compare_item_list_labels)

        actions = QHBoxLayout()
        actions.addStretch(1)
        self.compare_back_btn = QPushButton("")
        self.compare_back_btn.clicked.connect(self.show_snapshot_page_from_state)
        actions.addWidget(self.compare_back_btn)
        layout.addLayout(actions)
        self._connect_compare_image_scroll_sync()

        return page

    def show_startup_page(self) -> None:
        self.page_stack.setCurrentWidget(self.startup_page)

    def _wrap_compare_image_label(self, key: str, label: QLabel) -> QWidget:
        wrap = QWidget()
        layout = QVBoxLayout(wrap)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(False)
        scroll.setWidget(label)
        self.compare_image_scrolls[key] = scroll
        layout.addWidget(scroll, 1)
        return wrap

    def show_snapshot_page(self, project: str, output_dir: str) -> None:
        del output_dir
        self.snapshot_active_project = Path(project)
        self.snapshot_project_label.setText(self.t("snapshot_selected_project", project=project))
        mode = self.settings.get("compare_filter")
        self.snapshot_filter_group.blockSignals(True)
        if mode == "backup":
            self.snapshot_filter_backup.setChecked(True)
        elif mode == "git":
            self.snapshot_filter_git.setChecked(True)
        else:
            self.snapshot_filter_both.setChecked(True)
        self.snapshot_filter_group.blockSignals(False)
        self.refresh_snapshot_timeline()
        self.page_stack.setCurrentWidget(self.snapshot_page)

    def show_snapshot_page_from_state(self) -> None:
        if self.snapshot_active_project is None:
            self.show_startup_page()
            return
        self.snapshot_project_label.setText(self.t("snapshot_selected_project", project=str(self.snapshot_active_project)))
        self.refresh_snapshot_timeline()
        self.page_stack.setCurrentWidget(self.snapshot_page)

    def open_compare_from_snapshot(self) -> None:
        if self.snapshot_active_project is None:
            QMessageBox.warning(self, self.t("warning_project_title"), self.t("warning_project_text"))
            return
        if self.cli_candidate is None:
            QMessageBox.warning(self, self.t("warning_cli_title"), self.t("warning_cli_text"))
            return
        if self.snapshot_from_combo.count() < 1 or self.snapshot_to_combo.count() < 1:
            QMessageBox.warning(self, self.t("compare_started_title"), self.t("compare_need_two"))
            return
        from_id = self.snapshot_from_combo.currentData()
        to_id = self.snapshot_to_combo.currentData()
        if isinstance(from_id, str) and isinstance(to_id, str) and from_id == to_id:
            QMessageBox.warning(self, self.t("compare_started_title"), self.t("compare_same"))
            return
        if not isinstance(from_id, str) or not isinstance(to_id, str):
            QMessageBox.warning(self, self.t("compare_started_title"), self.t("compare_need_two"))
            return
        self._compare_pending_from_id = from_id
        self._compare_pending_to_id = to_id
        # Show compare page immediately, then run heavy preparation.
        self.show_compare_page(project=str(self.snapshot_active_project), output_dir="")
        QTimer.singleShot(0, self._prepare_compare_after_show)

    def _load_snapshot_source_map(self, source_id: str) -> dict[str, bytes]:
        if self.snapshot_active_project is None:
            raise RuntimeError(self.t("warning_project_text"))
        if source_id == "__current_project__":
            return build_current_project_map(self.snapshot_active_project)
        item = next((it for it in self.snapshot_items_filtered if it.identifier == source_id), None)
        if item is None:
            raise RuntimeError(f"Unknown source id: {source_id}")
        if item.source == "backup":
            return build_backup_zip_map(Path(item.identifier))
        if item.source == "git":
            return build_git_commit_map(self.snapshot_active_project, item.identifier, self.git_path)
        raise RuntimeError(f"Unsupported source type: {item.source}")

    def refresh_snapshot_timeline(self) -> None:
        self.snapshot_timeline_list.clear()
        self.snapshot_from_combo.clear()
        self.snapshot_to_combo.clear()
        self.snapshot_to_combo.addItem(self.t("compare_current_project"), "__current_project__")
        if self.snapshot_active_project is None:
            return
        limit = self.resolve_timeline_limit()
        backups = collect_backup_items(self.snapshot_active_project, limit)
        commits = collect_git_items(self.snapshot_active_project, self.git_path, limit) if self.git_path else []
        self.snapshot_items_all = sorted([*backups, *commits], key=lambda x: x.timestamp, reverse=True)[:limit]
        self.apply_snapshot_filter()

    def apply_snapshot_filter(self) -> None:
        mode = "both"
        if self.snapshot_filter_backup.isChecked():
            mode = "backup"
        elif self.snapshot_filter_git.isChecked():
            mode = "git"
        if mode == "backup":
            self.snapshot_items_filtered = [x for x in self.snapshot_items_all if x.source == "backup"]
        elif mode == "git":
            self.snapshot_items_filtered = [x for x in self.snapshot_items_all if x.source == "git"]
        else:
            self.snapshot_items_filtered = list(self.snapshot_items_all)

        self.snapshot_timeline_list.clear()
        self.snapshot_from_combo.clear()
        self.snapshot_to_combo.clear()
        self.snapshot_to_combo.addItem(self.t("compare_current_project"), "__current_project__")
        for item in self.snapshot_items_filtered:
            self.snapshot_timeline_list.addItem(item.label)
            self.snapshot_from_combo.addItem(item.label, item.identifier)
            self.snapshot_to_combo.addItem(item.label, item.identifier)
        self.snapshot_to_combo.setCurrentIndex(0)

    def on_snapshot_filter_changed(self) -> None:
        if self.snapshot_filter_backup.isChecked():
            self.settings["compare_filter"] = "backup"
        elif self.snapshot_filter_git.isChecked():
            self.settings["compare_filter"] = "git"
        else:
            self.settings["compare_filter"] = "both"
        self.save_settings()
        self.apply_snapshot_filter()

    def on_snapshot_limit_changed(self) -> None:
        value = self.snapshot_limit_combo.currentData()
        if not isinstance(value, int):
            return
        self.settings["compare_timeline_limit"] = value
        self.save_settings()
        self.refresh_snapshot_timeline()

    def on_snapshot_timeline_row_changed(self, row: int) -> None:
        if row < 0:
            return
        if row >= self.snapshot_from_combo.count():
            return
        self.snapshot_from_combo.setCurrentIndex(row)

    def on_snapshot_timeline_double_clicked(self, _item: QListWidgetItem) -> None:
        self.open_compare_from_snapshot()

    def on_snapshot_create_backup(self) -> None:
        if self.snapshot_active_project is None:
            QMessageBox.warning(self, self.t("compare_backup_title"), self.t("warning_project_text"))
            return
        try:
            create_project_backup(self.snapshot_active_project, memo=self.snapshot_backup_memo_input.text())
        except Exception as exc:
            QMessageBox.warning(self, self.t("compare_backup_title"), str(exc))
            return
        self.snapshot_backup_memo_input.clear()
        self.refresh_snapshot_timeline()

    def show_compare_page(
        self,
        project: str,
        output_dir: str,
        from_id: str | None = None,
        to_id: str | None = None,
        before_map: dict[str, bytes] | None = None,
        after_map: dict[str, bytes] | None = None,
    ) -> None:
        del output_dir
        self.compare_active_project = Path(project)
        self.compare_from_id = from_id
        self.compare_to_id = to_id
        self.compare_before_map = before_map or {}
        self.compare_after_map = after_map or {}
        self.compare_item_list.clear()
        self._reset_compare_preview()
        self.compare_status_label.setText(self.t("compare_loading"))
        self.compare_status_label.setStyleSheet("color: #666666;")
        self.page_stack.setCurrentWidget(self.compare_page)

    def _prepare_compare_after_show(self) -> None:
        if self.compare_active_project is None:
            return
        if self._compare_pending_from_id is None or self._compare_pending_to_id is None:
            return
        from_id = self._compare_pending_from_id
        to_id = self._compare_pending_to_id
        try:
            before_map = self._load_snapshot_source_map(from_id)
            after_map = self._load_snapshot_source_map(to_id)
            self.compare_from_id = from_id
            self.compare_to_id = to_id
            self.compare_before_map = before_map
            self.compare_after_map = after_map
            self._prepare_compare_temp_dirs()
            self.populate_compare_item_list()
            if self.compare_item_list.count() > 0:
                self.compare_item_list.setCurrentRow(0)
                self._start_compare_precache()
        except Exception as exc:
            self.compare_status_label.setText(str(exc))
            self.compare_status_label.setStyleSheet("color: #b00020;")
        finally:
            self._compare_pending_from_id = None
            self._compare_pending_to_id = None

    def _prepare_compare_temp_dirs(self) -> None:
        self._cleanup_compare_temp_dirs()
        self.compare_render_cache.clear()
        self.compare_targets.clear()
        if not self.compare_before_map and not self.compare_after_map:
            return
        self._compare_tmp_before_obj = tempfile.TemporaryDirectory(prefix="ksnap_cmp_before_")
        self._compare_tmp_after_obj = tempfile.TemporaryDirectory(prefix="ksnap_cmp_after_")
        self._compare_tmp_render_obj = tempfile.TemporaryDirectory(prefix="ksnap_cmp_render_")
        self.compare_before_root = Path(self._compare_tmp_before_obj.name)
        self.compare_after_root = Path(self._compare_tmp_after_obj.name)
        self.compare_render_root = Path(self._compare_tmp_render_obj.name)
        write_file_map(self.compare_before_root, self.compare_before_map)
        write_file_map(self.compare_after_root, self.compare_after_map)

    def _cleanup_compare_temp_dirs(self) -> None:
        if hasattr(self, "compare_status_refresh_timer"):
            self.compare_status_refresh_timer.stop()
        self.compare_precache_active = False
        self._compare_precache_stop.set()
        if self._compare_precache_thread is not None and self._compare_precache_thread.is_alive():
            self._compare_precache_thread.join(timeout=0.2)
        self._compare_precache_thread = None
        for obj in [self._compare_tmp_before_obj, self._compare_tmp_after_obj, self._compare_tmp_render_obj]:
            if obj is not None:
                obj.cleanup()
        self._compare_tmp_before_obj = None
        self._compare_tmp_after_obj = None
        self._compare_tmp_render_obj = None
        self.compare_before_root = None
        self.compare_after_root = None
        self.compare_render_root = None

    def populate_compare_item_list(self) -> None:
        self.compare_item_list.clear()
        self.compare_targets.clear()
        self.compare_target_labels.clear()
        with self._compare_status_lock:
            self.compare_target_status.clear()
        self._reset_compare_preview()
        if self.compare_active_project is None:
            return
        if self.compare_before_root is None or self.compare_after_root is None:
            return

        sch_paths = sorted(
            {p.relative_to(self.compare_before_root).as_posix() for p in self.compare_before_root.rglob("*.kicad_sch")}
            | {p.relative_to(self.compare_after_root).as_posix() for p in self.compare_after_root.rglob("*.kicad_sch")}
        )
        for rel_path in sch_paths:
            target = {"kind": "sch", "path": rel_path, "layer": None}
            self.compare_targets.append(target)
            label = f"SCH / {rel_path}"
            self.compare_target_labels.append(label)
            with self._compare_status_lock:
                self.compare_target_status[self._compare_target_key(target)] = "pending"

        pcb_paths = sorted(
            {p.relative_to(self.compare_before_root).as_posix() for p in self.compare_before_root.rglob("*.kicad_pcb")}
            | {p.relative_to(self.compare_after_root).as_posix() for p in self.compare_after_root.rglob("*.kicad_pcb")}
        )
        for rel_path in pcb_paths:
            target = {"kind": "pcb", "path": rel_path, "layer": None}
            self.compare_targets.append(target)
            label = f"PCB / {rel_path} / board"
            self.compare_target_labels.append(label)
            with self._compare_status_lock:
                self.compare_target_status[self._compare_target_key(target)] = "pending"

            layers: list[str] = []
            before_pcb = self.compare_before_root / rel_path
            after_pcb = self.compare_after_root / rel_path
            if before_pcb.exists() and self.cli_candidate is not None:
                layers.extend(detect_pcb_layers(self.cli_candidate.path, before_pcb))
            elif before_pcb.exists():
                layers.extend(parse_pcb_layers_from_file(before_pcb))
            if after_pcb.exists() and self.cli_candidate is not None:
                layers.extend(detect_pcb_layers(self.cli_candidate.path, after_pcb))
            elif after_pcb.exists():
                layers.extend(parse_pcb_layers_from_file(after_pcb))
            for layer in list(dict.fromkeys(layers)):
                target = {"kind": "pcb", "path": rel_path, "layer": layer}
                self.compare_targets.append(target)
                label = f"PCB / {rel_path} / {layer}"
                self.compare_target_labels.append(label)
                with self._compare_status_lock:
                    self.compare_target_status[self._compare_target_key(target)] = "pending"

        self._refresh_compare_item_list_labels()

        if self.compare_item_list.count() == 0:
            self.compare_status_label.setText(self.t("compare_image_no_targets"))
            self.compare_status_label.setStyleSheet("color: #9a6700;")
            if self.compare_status_refresh_timer.isActive():
                self.compare_status_refresh_timer.stop()
        else:
            self.compare_status_label.setText(self.t("compare_image_status_ready"))
            self.compare_status_label.setStyleSheet("color: #2b7a0b;")
            if not self.compare_status_refresh_timer.isActive():
                self.compare_status_refresh_timer.start()

    def on_compare_item_selected(self, row: int) -> None:
        if row < 0 or row >= len(self.compare_targets):
            self._reset_compare_preview()
            return
        target = self.compare_targets[row]
        key = self._compare_target_key(target)
        cached = self.compare_render_cache.get(key)
        if cached is not None:
            self._set_compare_images(*cached)
            self.compare_status_label.setText(self.t("compare_image_status_ready"))
            self.compare_status_label.setStyleSheet("color: #2b7a0b;")
            return

        with self._compare_status_lock:
            self.compare_target_status[key] = "rendering"
        self._refresh_compare_item_list_labels()
        self.compare_status_label.setText(self.t("compare_image_rendering"))
        self.compare_status_label.setStyleSheet("color: #666666;")
        self._set_compare_rendering_text()
        QApplication.processEvents()
        try:
            before_img, after_img, diff_img = self._render_compare_target(target)
        except Exception as exc:
            with self._compare_status_lock:
                self.compare_target_status[key] = "error"
            self.compare_status_label.setText(str(exc))
            self.compare_status_label.setStyleSheet("color: #b00020;")
            self._reset_compare_preview()
            self._refresh_compare_item_list_labels()
            return
        self.compare_render_cache[key] = (before_img, after_img, diff_img)
        self._set_compare_images(before_img, after_img, diff_img)
        self.compare_status_label.setText(self.t("compare_image_status_ready"))
        self.compare_status_label.setStyleSheet("color: #2b7a0b;")

    def _compare_target_key(self, target: dict[str, str | None]) -> str:
        return f"{target.get('kind') or ''}|{target.get('path') or ''}|{target.get('layer') or ''}"

    def _render_compare_target(self, target: dict[str, str | None]) -> tuple[QImage, QImage, QImage]:
        before_png, after_png, diff_png = self._ensure_compare_target_cache(target)
        before_img = QImage(str(before_png))
        after_img = QImage(str(after_png))
        diff_img = QImage(str(diff_png))
        if before_img.isNull() or after_img.isNull() or diff_img.isNull():
            raise RuntimeError(self.t("compare_image_not_available"))
        return before_img, after_img, diff_img

    def _cache_paths_for_target(self, target: dict[str, str | None]) -> tuple[Path, Path, Path]:
        if self.compare_render_root is None:
            raise RuntimeError(self.t("compare_image_not_available"))
        cache_key = hashlib.sha1(self._compare_target_key(target).encode("utf-8")).hexdigest()
        cache_dir = self.compare_render_root / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return (
            cache_dir / f"{cache_key}_before.png",
            cache_dir / f"{cache_key}_after.png",
            cache_dir / f"{cache_key}_diff.png",
        )

    def _ensure_compare_target_cache(self, target: dict[str, str | None]) -> tuple[Path, Path, Path]:
        if self.compare_before_root is None or self.compare_after_root is None or self.compare_render_root is None:
            raise RuntimeError(self.t("compare_image_not_available"))
        if self.cli_candidate is None:
            raise RuntimeError(self.t("warning_cli_text"))

        kind = target.get("kind")
        rel_path = target.get("path")
        layer = target.get("layer")
        if not isinstance(kind, str) or not isinstance(rel_path, str):
            raise RuntimeError(self.t("compare_image_not_available"))

        before_png, after_png, diff_png = self._cache_paths_for_target(target)
        if before_png.exists() and after_png.exists() and diff_png.exists():
            try:
                b = QImage(str(before_png))
                a = QImage(str(after_png))
                status = "diff" if (not b.isNull() and not a.isNull() and images_different(b, a)) else "same"
            except Exception:
                status = "error"
            with self._compare_status_lock:
                self.compare_target_status[self._compare_target_key(target)] = status
            return before_png, after_png, diff_png

        with self._compare_render_lock:
            if before_png.exists() and after_png.exists() and diff_png.exists():
                try:
                    b = QImage(str(before_png))
                    a = QImage(str(after_png))
                    status = "diff" if (not b.isNull() and not a.isNull() and images_different(b, a)) else "same"
                except Exception:
                    status = "error"
                with self._compare_status_lock:
                    self.compare_target_status[self._compare_target_key(target)] = status
                return before_png, after_png, diff_png

            before_src = self.compare_before_root / rel_path
            after_src = self.compare_after_root / rel_path
            key = re.sub(r"[^A-Za-z0-9._-]+", "_", self._compare_target_key(target))
            before_svg = self._export_compare_svg(
                before_src if before_src.exists() else None,
                kind,
                layer,
                self.compare_render_root / "before" / key,
            )
            after_svg = self._export_compare_svg(
                after_src if after_src.exists() else None,
                kind,
                layer,
                self.compare_render_root / "after" / key,
            )

            if before_svg is None and after_svg is None:
                raise RuntimeError(self.t("compare_image_not_available"))
            before_img = render_svg_to_image(before_svg) if before_svg is not None else None
            after_img = render_svg_to_image(after_svg) if after_svg is not None else None
            if before_img is None and after_img is None:
                raise RuntimeError(self.t("compare_image_not_available"))
            if before_img is None:
                before_img = QImage(after_img.width(), after_img.height(), QImage.Format_ARGB32)  # type: ignore[union-attr]
                before_img.fill(Qt.white)
            if after_img is None:
                after_img = QImage(before_img.width(), before_img.height(), QImage.Format_ARGB32)  # type: ignore[union-attr]
                after_img.fill(Qt.white)
            before_img, after_img = normalize_image_sizes(before_img, after_img)
            has_diff = images_different(before_img, after_img)
            diff_img = make_pixel_diff_image(before_img, after_img)
            before_img.save(str(before_png), "PNG")
            after_img.save(str(after_png), "PNG")
            diff_img.save(str(diff_png), "PNG")
            with self._compare_status_lock:
                self.compare_target_status[self._compare_target_key(target)] = "diff" if has_diff else "same"
        return before_png, after_png, diff_png

    def _export_compare_svg(self, source: Path | None, kind: str, layer: str | None, out_dir: Path) -> Path | None:
        if source is None:
            return None
        out_dir.mkdir(parents=True, exist_ok=True)
        if kind == "sch":
            svgs = export_svg_bundle_with_kicad_cli(self.cli_candidate.path, source, out_dir, "sch")  # type: ignore[union-attr]
        elif kind == "pcb":
            svgs = export_svg_bundle_with_kicad_cli(self.cli_candidate.path, source, out_dir, "pcb", pcb_layers=layer)  # type: ignore[union-attr]
        else:
            return None
        return svgs[0] if svgs else None

    def _set_compare_images(self, before_img: QImage, after_img: QImage, diff_img: QImage) -> None:
        self.compare_before_image_raw = before_img
        self.compare_after_image_raw = after_img
        self.compare_diff_image_raw = diff_img
        self.compare_zoom_mode = "fit"
        self.compare_zoom_scale = 1.0
        self._render_compare_image_labels()
        self.compare_image_tabs.setCurrentIndex(0)

    def _reset_compare_preview(self) -> None:
        self.compare_before_image_raw = None
        self.compare_after_image_raw = None
        self.compare_diff_image_raw = None
        for label in [self.compare_diff_image_label, self.compare_before_image_label, self.compare_after_image_label]:
            label.clear()
            label.setText(self.t("compare_image_not_available"))

    def _set_compare_rendering_text(self) -> None:
        self.compare_before_image_raw = None
        self.compare_after_image_raw = None
        self.compare_diff_image_raw = None
        for label in [self.compare_diff_image_label, self.compare_before_image_label, self.compare_after_image_label]:
            label.clear()
            label.setText(self.t("compare_image_rendering"))

    def _format_compare_list_label(self, base_label: str, status: str) -> str:
        # Keep status markers language-independent for quick visual scanning.
        if status == "diff":
            suffix = " [*]"
        elif status == "rendering":
            suffix = " [...]"
        elif status == "pending":
            suffix = " [?]"
        elif status == "same":
            suffix = ""
        else:
            suffix = " [!]"
        return f"{base_label}{suffix}"

    def _refresh_compare_item_list_labels(self) -> None:
        if not hasattr(self, "compare_item_list"):
            return
        current = self.compare_item_list.currentRow()
        self.compare_item_list.blockSignals(True)
        self.compare_item_list.clear()
        with self._compare_status_lock:
            for i, base in enumerate(self.compare_target_labels):
                status = "pending"
                if i < len(self.compare_targets):
                    key = self._compare_target_key(self.compare_targets[i])
                    status = self.compare_target_status.get(key, "pending")
                self.compare_item_list.addItem(self._format_compare_list_label(base, status))
        if 0 <= current < self.compare_item_list.count():
            self.compare_item_list.setCurrentRow(current)
        self.compare_item_list.blockSignals(False)

    def _start_compare_precache(self) -> None:
        if self.compare_precache_active:
            return
        self._compare_precache_stop.clear()
        self.compare_precache_active = True
        targets = list(self.compare_targets)
        self._compare_precache_thread = threading.Thread(
            target=self._run_compare_precache_worker,
            args=(targets,),
            daemon=True,
        )
        self._compare_precache_thread.start()

    def _run_compare_precache_worker(self, targets: list[dict[str, str | None]]) -> None:
        try:
            for target in targets:
                if self._compare_precache_stop.is_set():
                    break
                key = self._compare_target_key(target)
                with self._compare_status_lock:
                    current = self.compare_target_status.get(key, "pending")
                    if current == "pending":
                        self.compare_target_status[key] = "rendering"
                try:
                    self._ensure_compare_target_cache(target)
                except Exception:
                    with self._compare_status_lock:
                        self.compare_target_status[key] = "error"
                    continue
        finally:
            self.compare_precache_active = False

    def _connect_compare_image_scroll_sync(self) -> None:
        for scroll in self.compare_image_scrolls.values():
            scroll.horizontalScrollBar().valueChanged.connect(self.on_compare_image_scroll_changed)
            scroll.verticalScrollBar().valueChanged.connect(self.on_compare_image_scroll_changed)

    def on_compare_image_scroll_changed(self, _: int) -> None:
        if self._compare_syncing_scroll:
            return
        source_bar = self.sender()
        if source_bar is None:
            return
        source_max = source_bar.maximum()
        ratio = 0.0 if source_max <= 0 else source_bar.value() / source_max
        source_is_vertical = source_bar.orientation() == Qt.Vertical
        if source_is_vertical:
            self._compare_scroll_ratio_y = ratio
        else:
            self._compare_scroll_ratio_x = ratio
        self._compare_syncing_scroll = True
        try:
            for scroll in self.compare_image_scrolls.values():
                target_bar = scroll.verticalScrollBar() if source_is_vertical else scroll.horizontalScrollBar()
                if target_bar is source_bar:
                    continue
                tmax = target_bar.maximum()
                target_bar.setValue(int(round(ratio * tmax)) if tmax > 0 else 0)
        finally:
            self._compare_syncing_scroll = False

    def on_compare_image_tab_changed(self, _: int) -> None:
        # Hidden tab scroll ranges may be finalized after tab switch.
        QTimer.singleShot(0, self._apply_compare_scroll_ratios)

    def on_compare_zoom_fit(self) -> None:
        self.compare_zoom_mode = "fit"
        self._render_compare_image_labels()

    def on_compare_zoom_in(self) -> None:
        self.compare_zoom_mode = "manual"
        self.compare_zoom_scale = min(self.compare_zoom_scale * 1.25, 8.0)
        self._render_compare_image_labels()

    def on_compare_zoom_out(self) -> None:
        self.compare_zoom_mode = "manual"
        self.compare_zoom_scale = max(self.compare_zoom_scale / 1.25, 0.1)
        self._render_compare_image_labels()

    def _render_compare_image_labels(self) -> None:
        fit_scale = self._compute_compare_fit_scale() if self.compare_zoom_mode == "fit" else None
        self._set_compare_image_for_key(self.compare_before_image_label, self.compare_before_image_raw, fit_scale)
        self._set_compare_image_for_key(self.compare_after_image_label, self.compare_after_image_raw, fit_scale)
        self._set_compare_image_for_key(self.compare_diff_image_label, self.compare_diff_image_raw, fit_scale)
        QTimer.singleShot(0, self._apply_compare_scroll_ratios)

    def _apply_compare_scroll_ratios(self) -> None:
        if self._compare_syncing_scroll:
            return
        self._compare_syncing_scroll = True
        try:
            for scroll in self.compare_image_scrolls.values():
                hbar = scroll.horizontalScrollBar()
                vbar = scroll.verticalScrollBar()
                hmax = hbar.maximum()
                vmax = vbar.maximum()
                hbar.setValue(int(round(self._compare_scroll_ratio_x * hmax)) if hmax > 0 else 0)
                vbar.setValue(int(round(self._compare_scroll_ratio_y * vmax)) if vmax > 0 else 0)
        finally:
            self._compare_syncing_scroll = False

    def _compute_compare_fit_scale(self) -> float:
        images = [img for img in [self.compare_before_image_raw, self.compare_after_image_raw, self.compare_diff_image_raw] if img is not None]
        if not images:
            return 1.0
        max_w = max(img.width() for img in images)
        max_h = max(img.height() for img in images)
        if max_w <= 0 or max_h <= 0:
            return 1.0
        scroll = self.compare_image_scrolls.get("diff") or next(iter(self.compare_image_scrolls.values()), None)
        if scroll is None:
            return 1.0
        vp = scroll.viewport().size()
        scale = min(max(1, vp.width()) / max_w, max(1, vp.height()) / max_h)
        return max(0.05, min(scale, 8.0))

    def _set_compare_image_for_key(self, label: QLabel, image: QImage | None, fit_scale: float | None) -> None:
        if image is None:
            return
        pixmap = QPixmap.fromImage(image)
        if self.compare_zoom_mode == "fit":
            scale = fit_scale if fit_scale is not None else 1.0
        else:
            scale = self.compare_zoom_scale
        w = max(1, int(pixmap.width() * scale))
        h = max(1, int(pixmap.height() * scale))
        scaled = pixmap.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(scaled)
        label.resize(scaled.size())

    def refresh_compare_timeline(self) -> None:
        if self.compare_active_project is None:
            self.compare_timeline_list.clear()
            return
        backups = collect_backup_items(self.compare_active_project, self.resolve_timeline_limit())
        commits = collect_git_items(self.compare_active_project, self.git_path, self.resolve_timeline_limit()) if self.git_path else []
        self.compare_items_all = sorted([*backups, *commits], key=lambda x: x.timestamp, reverse=True)[: self.resolve_timeline_limit()]
        self.apply_compare_filter()

    def apply_compare_filter(self) -> None:
        if not hasattr(self, "compare_items_all"):
            return
        if not hasattr(self, "compare_timeline_list"):
            return
        if self.compare_timeline_list is None:
            return
        if not hasattr(self, "compare_from_combo2") or self.compare_from_combo2 is None:
            return
        if not hasattr(self, "compare_to_combo2") or self.compare_to_combo2 is None:
            return
        if self.compare_source_backup.isChecked():
            mode = "backup"
        elif self.compare_source_git.isChecked():
            mode = "git"
        else:
            mode = "both"
        if mode == "backup":
            self.compare_items_filtered = [x for x in self.compare_items_all if x.source == "backup"]
        elif mode == "git":
            self.compare_items_filtered = [x for x in self.compare_items_all if x.source == "git"]
        else:
            self.compare_items_filtered = list(self.compare_items_all)

        self.compare_timeline_list.clear()
        self.compare_from_combo2.clear()
        self.compare_to_combo2.clear()
        self.compare_to_combo2.addItem(self.t("compare_current_project"), "__current_project__")
        for item in self.compare_items_filtered:
            self.compare_timeline_list.addItem(item.label)
            self.compare_from_combo2.addItem(item.label, item.identifier)
            self.compare_to_combo2.addItem(item.label, item.identifier)
        self.compare_to_combo2.setCurrentIndex(0)

    def on_compare_filter_changed(self) -> None:
        self.apply_compare_filter()

    def on_compare_limit_changed(self) -> None:
        value = self.compare_limit_combo.currentData()
        if not isinstance(value, int):
            return
        self.settings["compare_timeline_limit"] = value
        self.save_settings()
        self.refresh_compare_timeline()

    def on_compare_timeline_row_changed(self, row: int) -> None:
        if row < 0:
            return
        if row >= self.compare_from_combo2.count():
            return
        self.compare_from_combo2.setCurrentIndex(row)

    def on_compare_create_backup(self) -> None:
        if self.compare_active_project is None:
            QMessageBox.warning(self, self.t("compare_backup_title"), self.t("warning_project_text"))
            return
        try:
            create_project_backup(
                self.compare_active_project,
                memo=self.compare_backup_memo_input.text(),
            )
        except Exception as exc:
            QMessageBox.warning(self, self.t("compare_backup_title"), str(exc))
            return
        self.compare_backup_memo_input.clear()
        self.refresh_compare_timeline()

    def _load_compare_source_map(self, source_id: str) -> dict[str, bytes]:
        if self.compare_active_project is None:
            raise RuntimeError(self.t("warning_project_text"))
        if source_id == "__current_project__":
            return build_current_project_map(self.compare_active_project)
        item = next((it for it in self.compare_items_filtered if it.identifier == source_id), None)
        if item is None:
            raise RuntimeError(f"Unknown source id: {source_id}")
        if item.source == "backup":
            return build_backup_zip_map(Path(item.identifier))
        if item.source == "git":
            return build_git_commit_map(self.compare_active_project, item.identifier, self.git_path)
        raise RuntimeError(f"Unsupported source type: {item.source}")

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
        self.render_version_info()
        self.footer.setText(self.t("footer", path=str(self.settings_store.config_path)))
        if hasattr(self, "snapshot_title"):
            self.snapshot_title.setText(self.t("snapshot_window_title"))
        if hasattr(self, "snapshot_project_label") and self.snapshot_active_project is not None:
            self.snapshot_project_label.setText(
                self.t("snapshot_selected_project", project=str(self.snapshot_active_project))
            )
        if hasattr(self, "snapshot_compare_btn"):
            self.snapshot_compare_btn.setText(self.t("snapshot_open_compare"))
        if hasattr(self, "snapshot_back_btn"):
            self.snapshot_back_btn.setText(self.t("snapshot_back"))
        if hasattr(self, "snapshot_filter_label"):
            self.snapshot_filter_label.setText(self.t("compare_filter"))
        if hasattr(self, "snapshot_filter_both"):
            self.snapshot_filter_both.setText(self.t("compare_filter_both"))
        if hasattr(self, "snapshot_filter_backup"):
            self.snapshot_filter_backup.setText(self.t("compare_filter_backup"))
        if hasattr(self, "snapshot_filter_git"):
            self.snapshot_filter_git.setText(self.t("compare_filter_git"))
        if hasattr(self, "snapshot_limit_label"):
            self.snapshot_limit_label.setText(self.t("compare_limit"))
        if hasattr(self, "snapshot_refresh_btn"):
            self.snapshot_refresh_btn.setText(self.t("compare_refresh"))
        if hasattr(self, "snapshot_backup_memo_label"):
            self.snapshot_backup_memo_label.setText(self.t("compare_backup_memo"))
        if hasattr(self, "snapshot_backup_memo_input"):
            self.snapshot_backup_memo_input.setPlaceholderText(self.t("compare_backup_memo_placeholder"))
        if hasattr(self, "snapshot_create_backup_btn"):
            self.snapshot_create_backup_btn.setText(self.t("compare_create_backup"))
        if hasattr(self, "snapshot_from_label"):
            self.snapshot_from_label.setText(self.t("compare_from"))
        if hasattr(self, "snapshot_to_label"):
            self.snapshot_to_label.setText(self.t("compare_to"))
        if hasattr(self, "compare_title"):
            self.compare_title.setText(self.t("compare_window_title"))
        if hasattr(self, "compare_source_label"):
            self.compare_source_label.setText(self.t("compare_filter"))
        if hasattr(self, "compare_source_both"):
            self.compare_source_both.setText(self.t("compare_filter_both"))
        if hasattr(self, "compare_source_backup"):
            self.compare_source_backup.setText(self.t("compare_filter_backup"))
        if hasattr(self, "compare_source_git"):
            self.compare_source_git.setText(self.t("compare_filter_git"))
        if hasattr(self, "compare_limit_label"):
            self.compare_limit_label.setText(self.t("compare_limit"))
        if hasattr(self, "compare_refresh_btn"):
            self.compare_refresh_btn.setText(self.t("compare_refresh"))
        if hasattr(self, "compare_backup_memo_label"):
            self.compare_backup_memo_label.setText(self.t("compare_backup_memo"))
        if hasattr(self, "compare_backup_memo_input"):
            self.compare_backup_memo_input.setPlaceholderText(self.t("compare_backup_memo_placeholder"))
        if hasattr(self, "compare_create_backup_btn"):
            self.compare_create_backup_btn.setText(self.t("compare_create_backup"))
        if hasattr(self, "compare_from_label2"):
            self.compare_from_label2.setText(self.t("compare_from"))
        if hasattr(self, "compare_to_label2"):
            self.compare_to_label2.setText(self.t("compare_to"))
        if hasattr(self, "compare_run_btn2"):
            self.compare_run_btn2.setText(self.t("compare_run"))
        if hasattr(self, "compare_back_btn"):
            self.compare_back_btn.setText(self.t("compare_back"))
        if hasattr(self, "compare_items_label"):
            self.compare_items_label.setText(self.t("compare_image_target"))
        if hasattr(self, "compare_preview_title"):
            self.compare_preview_title.setText(self.t("compare_image_title"))
        if hasattr(self, "compare_zoom_out_btn"):
            self.compare_zoom_out_btn.setText(self.t("compare_image_zoom_out"))
        if hasattr(self, "compare_zoom_in_btn"):
            self.compare_zoom_in_btn.setText(self.t("compare_image_zoom_in"))
        if hasattr(self, "compare_zoom_fit_btn"):
            self.compare_zoom_fit_btn.setText(self.t("compare_image_zoom_fit"))
        if hasattr(self, "compare_image_tabs"):
            self.compare_image_tabs.setTabText(0, self.t("compare_image_diff"))
            self.compare_image_tabs.setTabText(1, self.t("compare_image_before"))
            self.compare_image_tabs.setTabText(2, self.t("compare_image_after"))
        if hasattr(self, "compare_item_list") and hasattr(self, "compare_target_labels"):
            self._refresh_compare_item_list_labels()
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

        if recent:
            self.settings["recent_projects"] = recent[:MAX_RECENT]
        else:
            # Avoid accidentally wiping history when UI state is temporarily empty.
            existing = self.settings.get("recent_projects", [])
            if not isinstance(existing, list):
                self.settings["recent_projects"] = []
            else:
                self.settings["recent_projects"] = [str(x) for x in existing[:MAX_RECENT]]
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
        candidates = discover_git_candidates()
        if not candidates:
            self.git_path = None
            self.git_path_input.setText("")
            self.set_git_status("git_not_detected", "warn")
            return

        best = max(candidates, key=lambda c: c.version)
        self.git_path = str(best.path)
        self.git_path_input.setText(self.git_path)
        if best.version_text:
            self.set_git_status("git_ok", "ok", version=best.version_text)
        else:
            self.set_git_status("git_ok_plain", "ok")

    def fetch_latest_release_version(self) -> str:
        req = urllib.request.Request(
            GITHUB_LATEST_RELEASE_API,
            headers={"Accept": "application/vnd.github+json", "User-Agent": "kicad-snapshot"},
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            payload = json.loads(resp.read().decode("utf-8", errors="replace"))
        tag = str(payload.get("tag_name", "")).strip()
        if not tag:
            raise RuntimeError("tag_name not found")
        return tag[1:] if tag.startswith("v") else tag

    def on_check_latest_version(self) -> None:
        self.latest_version_state = "checking"
        self.render_version_info()
        self.version_check_btn.setEnabled(False)
        QApplication.processEvents()
        try:
            latest = self.fetch_latest_release_version()
            self.latest_version = latest
            current_tuple, _ = parse_version_text(__version__)
            latest_tuple, _ = parse_version_text(latest)
            if current_tuple is not None and latest_tuple is not None:
                if current_tuple == latest_tuple:
                    self.latest_version_state = "up_to_date"
                elif current_tuple < latest_tuple:
                    self.latest_version_state = "available"
                else:
                    self.latest_version_state = "ahead"
            else:
                self.latest_version_state = "unknown"
        except Exception:
            self.latest_version = None
            self.latest_version_state = "failed"
        finally:
            self.version_check_btn.setEnabled(True)
            self.render_version_info()

    def open_repository(self) -> None:
        QDesktopServices.openUrl(QUrl("https://github.com/tanakamasayuki/kicad-snapshot"))

    def render_version_info(self) -> None:
        self.version_current_label.setText(self.t("version_current", current=__version__))
        self.version_check_btn.setText(self.t("version_check_latest"))
        self.version_repo_btn.setText(self.t("version_open_repo"))
        if self.latest_version_state == "checking":
            self.version_latest_label.setText(self.t("version_checking"))
            self.version_latest_label.setStyleSheet("color: #666666;")
            return
        if self.latest_version_state == "failed":
            self.version_latest_label.setText(self.t("version_check_failed"))
            self.version_latest_label.setStyleSheet("color: #b00020;")
            return
        if not self.latest_version:
            self.version_latest_label.setText("")
            self.version_latest_label.setStyleSheet("color: #666666;")
            return
        if self.latest_version_state == "up_to_date":
            self.version_latest_label.setText(self.t("version_latest_up_to_date", latest=self.latest_version))
            self.version_latest_label.setStyleSheet("color: #2b7a0b;")
        elif self.latest_version_state == "available":
            self.version_latest_label.setText(self.t("version_latest_available", latest=self.latest_version))
            self.version_latest_label.setStyleSheet("color: #9a6700;")
        elif self.latest_version_state == "ahead":
            self.version_latest_label.setText(self.t("version_latest_ahead", latest=self.latest_version))
            self.version_latest_label.setStyleSheet("color: #2b7a0b;")
        else:
            self.version_latest_label.setText(self.t("version_latest_unknown", latest=self.latest_version))
            self.version_latest_label.setStyleSheet("color: #666666;")

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

    def run_compare(self) -> None:
        if self.compare_from_combo2.count() < 1 or self.compare_to_combo2.count() < 1:
            QMessageBox.warning(self, self.t("compare_started_title"), self.t("compare_need_two"))
            return
        if self.cli_candidate is None:
            QMessageBox.warning(self, self.t("warning_cli_title"), self.t("warning_cli_text"))
            return
        from_id = self.compare_from_combo2.currentData()
        to_id = self.compare_to_combo2.currentData()
        if isinstance(from_id, str) and isinstance(to_id, str) and from_id == to_id:
            QMessageBox.warning(self, self.t("compare_started_title"), self.t("compare_same"))
            return
        if not isinstance(from_id, str) or not isinstance(to_id, str):
            QMessageBox.warning(self, self.t("compare_started_title"), self.t("compare_need_two"))
            return
        try:
            before_map = self._load_compare_source_map(from_id)
            after_map = self._load_compare_source_map(to_id)
        except Exception as exc:
            QMessageBox.warning(self, self.t("compare_started_title"), str(exc))
            return

        dialog = ItemDiffDialog(
            title=self.t("compare_started_title"),
            cli_path=self.cli_candidate.path,
            before_map=before_map,
            after_map=after_map,
            t_func=lambda key: self.t(key),
            parent=self,
        )
        dialog.exec()

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

        self.show_snapshot_page(project=project, output_dir=default_output)


def main() -> None:
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

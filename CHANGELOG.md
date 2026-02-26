# Changelog / 変更履歴

## Unreleased

## 1.0.6
- (EN) Fixed temp-directory race when leaving Compare view: stop/wait background precache rendering before cleanup to prevent reopen errors.
- (JA) 比較画面を離れる際の一時フォルダ競合を修正: バックグラウンドのプリキャッシュ描画を停止・完了待ちしてから削除するようにし、再オープン時エラーを防止。

## 1.0.5
- (EN) Updated snapshot backup target rules to hybrid include/exclude: include `*.kicad_*` and `*-lib-table` (including `.kicad_prl`), while excluding common dev/temp artifacts.
- (JA) スナップショットのバックアップ対象ルールを include/exclude のハイブリッド方式に更新: `*.kicad_*` と `*-lib-table`（`.kicad_prl` 含む）を対象にし、開発・一時ファイルを除外。

## 1.0.4
- (EN) Added a render scale dropdown in Compare preview (`1x`, `1.5x`, `2x`, `3x`, `4x`, `5x`) and persisted the selected scale in settings.
- (JA) 比較プレビューにレンダリング倍率プルダウン（`1x`、`1.5x`、`2x`、`3x`、`4x`、`5x`）を追加し、選択値を設定へ保存するように変更。
- (EN) Optimized diff processing with NumPy for `images_different` and pixel diff image generation (with safe fallback path).
- (JA) `images_different` とピクセル差分画像生成をNumPyで高速化（安全なフォールバック経路あり）。
- (EN) Added an Auto tab for compare preview that cycles Diff/Before/After, and set it as the default (leftmost) tab.
- (JA) 比較プレビューに Diff/Before/After を自動切替する Auto タブを追加し、左端のデフォルトタブに変更。
- (EN) Improved compare Fit behavior to use the active tab image size and rerender on tab switch.
- (JA) 比較プレビューの Fit 表示を改善し、アクティブタブ基準の拡大率計算とタブ切替時の再描画に対応。
- (EN) Fixed compare preview initialization timing issues (auto-cycle start and missing-attribute guards during startup).
- (JA) 比較プレビュー初期化時のタイミング問題を修正（自動切替の開始漏れと起動時属性未初期化ガード）。

## 1.0.3
- (EN) Added alternate CLI script name `kicad-snapshot` in addition to `kicad_snapshot`.
- (JA) CLIスクリプト名として既存の `kicad_snapshot` に加え、`kicad-snapshot` の別名を追加。

## 1.0.2
- (EN) Improved app version resolution for Windows EXE startup to avoid showing `0.0.0` (added absolute-import and metadata name fallbacks).
- (JA) Windows EXE起動時のバージョン取得を改善し、`0.0.0` 表示を回避（絶対importとmetadata名のフォールバックを追加）。

## 1.0.1
- (EN) Fixed Windows EXE startup import error in `__main__.py` by adding safe `__version__` fallback resolution.
- (JA) `__main__.py` の `__version__` 取得にフォールバック処理を追加し、Windows EXE起動時のimportエラーを修正。

## 1.0.0
- (EN) Added startup version utilities: check latest release from GitHub and open the project web page.
- (JA) 起動画面にバージョン関連機能を追加: GitHubから最新リリース確認とWebページを開くボタン。
- (EN) Expanded translation dictionaries for Chinese/French/German with explicit UI strings (reduced fallback-to-English usage).
- (JA) 中国語・フランス語・ドイツ語の翻訳辞書を拡充し、UI文言の英語フォールバック依存を削減。
- (EN) Updated compare preview interactions: wheel zoom, `Shift+Wheel` vertical scroll, `Ctrl+Wheel` horizontal scroll, and cursor-centered zooming.
- (JA) 比較プレビューの操作を更新: ホイールで拡大縮小、`Shift+ホイール`で縦スクロール、`Ctrl+ホイール`で横スクロール、カーソル位置中心のズームに対応。
- (EN) Improved SVG preview rendering: preserve aspect ratio on fallback sizing and increase default rasterization size (upscaled from SVG default size, currently 2x).
- (JA) SVGプレビュー描画を改善: フォールバック時も縦横比を維持し、ラスタライズ時の既定サイズを拡大（SVG既定サイズからの拡大、現在は2倍）。
- (EN) Updated project list interaction: double-click now proceeds to Snapshot/Compare when the Continue button is enabled.
- (JA) プロジェクト一覧の操作を更新: 「続行」ボタンが有効な場合、ダブルクリックでスナップショット/比較画面へ進むように変更。
- (EN) Removed unused `output_dir` setting and related dead parameters from the code/config serialization.
- (JA) 未使用だった `output_dir` 設定項目と関連する不要な引数・シリアライズ処理を削除。

## 0.2.0
- (EN) Initial release
- (JA) 初期リリース

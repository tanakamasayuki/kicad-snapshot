# Changelog / 変更履歴

## Unreleased
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

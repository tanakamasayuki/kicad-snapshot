# KiCad Snapshot

KiCadプロジェクト向けのスナップショット作成・視覚差分確認ツール（PySide6 GUI）です。

- Repository: `https://github.com/tanakamasayuki/kicad-snapshot`
- PyPIパッケージ名: `kicad-snapshot`
- CLIコマンド名: `kicad_snapshot`
- English README: [README.md](README.md)

## 主な機能

- KiCadプロジェクトの手動ZIPスナップショット作成
- スナップショット対象ルール: `*.kicad_*` / `*-lib-table` を含め、テンポラリ・開発系ファイルを除外
- スナップショットと現在プロジェクトの比較
- スナップショット同士の比較
- 回路図/PCBの視覚差分レンダリング
- PCBレイヤー単位の比較
- 多言語UI（英語/日本語/中国語/フランス語/ドイツ語）

## 動作要件

- Python 3.11以上
- `kicad-cli` が利用可能であること
- KiCad 8以上を推奨

## インストール

### PyPIから（推奨）

```bash
pip install kicad-snapshot
```

`pipx` を使う場合:

```bash
pipx install kicad-snapshot
```

### ソースから

```bash
git clone https://github.com/tanakamasayuki/kicad-snapshot.git
cd kicad-snapshot
pip install .
```

## 起動方法

インストール済み環境から:

```bash
kicad_snapshot
```

`uv` で開発実行する場合:

```bash
uv sync --dev
uv run kicad_snapshot
```

## バージョンアップ

### インストール済みパッケージを更新

`pip` の場合:

```bash
pip install -U kicad-snapshot
```

`pipx` の場合:

```bash
pipx upgrade kicad-snapshot
```

### ZIP版（Windows EXE）を更新

ZIP版は上書きアップデート機能がないため、最新版のZIPをGitHub Releasesから再ダウンロードして展開し直してください。

### プロジェクトのバージョン更新（メンテナー向け）

GitHub Actions の `.github/workflows/release.yml` を実行し、次を指定します。

- `version`: 次のバージョン（例: `1.0.2`）
- `publish_pypi`: PyPI公開するなら `true`、しないなら `false`

このワークフローで、バージョンファイル更新・`CHANGELOG.md` 更新・`vX.Y.Z` タグ作成・Windows向けZIP生成・（任意で）PyPI公開まで自動化されます。

## 基本フロー

1. 起動して `kicad-cli` パスを確認
2. KiCadプロジェクト（`.kicad_pro`）を選択
3. スナップショット画面で比較元/比較先を選択
4. 比較画面で項目ごとの差分を確認

## 設定ファイル

設定は `platformdirs` でユーザーごとに保存されます。

- Windows: `%APPDATA%/KiCadSnapshot/settings.toml`
- macOS: `~/Library/Application Support/KiCadSnapshot/settings.toml`
- Linux: `~/.config/KiCadSnapshot/settings.toml`

## 開発

```bash
uv sync --dev
uv run kicad_snapshot
```

Windows EXEを手動ビルドする場合（PyInstaller, onedir）:

```bash
uv sync --dev
uv run pyinstaller --noconfirm --clean --windowed --onedir --name kicad_snapshot --paths src src/kicad_snapshot/__main__.py
```

エントリポイント:

```toml
[project.scripts]
kicad_snapshot = "kicad_snapshot.__main__:main"
```

## リリース自動化（GitHub Actions）

ワークフロー: `.github/workflows/release.yml`

- 起動方法: `workflow_dispatch`
- 入力:
  - `version`（例: `0.0.1`）
  - `publish_pypi`（`true`/`false`）

自動化される処理:

1. `pyproject.toml` と `src/kicad_snapshot/__init__.py` のバージョン更新
2. `CHANGELOG.md` で `## Unreleased` の直下に新バージョン見出しを追加
3. コミット + タグ作成（`vX.Y.Z`）
4. Windows EXE のビルド（PyInstaller, onedir）
5. 配布用ZIP + SHA256生成とGitHub Release添付
6. （任意）PyPI公開

PyPI公開を使う場合は、このリポジトリに対して PyPI Trusted Publishing の設定が必要です。

## ドキュメント

- [SPEC.md](SPEC.md) / [SPEC.ja.md](SPEC.ja.md): プロダクト仕様
- [DEV_SPEC.md](DEV_SPEC.md) / [DEV_SPEC.ja.md](DEV_SPEC.ja.md): 開発環境仕様

## ライセンス

MIT（[LICENSE](LICENSE) 参照）

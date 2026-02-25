# KiCad Snapshot

KiCadプロジェクト向けのスナップショット作成・視覚差分確認ツール（PySide6 GUI）です。

- Repository: `https://github.com/tanakamasayuki/kicad-snapshot`
- PyPIパッケージ名: `kicad-snapshot`
- CLIコマンド名: `kicad_snapshot`
- English README: [README.md](README.md)

## 主な機能

- KiCadプロジェクトの手動ZIPスナップショット作成
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

エントリポイント:

```toml
[project.scripts]
kicad_snapshot = "kicad_snapshot.__main__:main"
```

## ドキュメント

- [SPEC.md](SPEC.md) / [SPEC.ja.md](SPEC.ja.md): プロダクト仕様
- [DEV_SPEC.md](DEV_SPEC.md) / [DEV_SPEC.ja.md](DEV_SPEC.ja.md): 開発環境仕様

## ライセンス

MIT（[LICENSE](LICENSE) 参照）

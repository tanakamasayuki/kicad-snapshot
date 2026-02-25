# 開発環境仕様書（PySide6 / クロスプラットフォームGUI OSS）

## 1. 目的

本プロジェクトは、Windows / macOS / Linux 上で動作する  
シンプルな管理画面型GUIアプリケーションを OSS として提供する。

- Windows：非エンジニア向けに Python 同梱のバイナリ（exe）を基本配布とする  
- macOS / Linux：Pythonパッケージとして配布（pipx推奨）  
- すべてのOSで pip によるインストールも可能とする  

---

## 2. 採用技術

| 項目 | 技術 |
|------|------|
| 言語 | Python 3.11+ |
| GUIフレームワーク | PySide6（Qt6） |
| 配布（Windows） | exe（PyInstaller）※基本配布 |
| 配布（全OS） | pip / pipx |
| 設定・データ保存 | platformdirs |
| パッケージ管理 | pyproject.toml |
| CI/CD | GitHub Actions |

---

## 3. 対象プラットフォームと配布方針

| OS | 基本配布 | 代替手段 | 備考 |
|----|----------|----------|------|
| Windows | exe（Python同梱） | pip / pipx | 非エンジニア向けはexeを推奨 |
| macOS | pipx install | pip | .app化は行わない |
| Linux | pipx install | pip | ディストリ依存を避ける |

### Windows方針

- 原則として exe 版を利用することを推奨  
- Python環境があるユーザーは pip / pipx による利用も可能  
- SmartScreen警告は初期リリースでは許容する（署名は将来検討）  

---

## 4. 開発環境要件

### 必須

- Python 3.11 以上  
- Git  
- venv または pipx  

### 推奨

- pipx（macOS/Linux動作確認用）  
- VSCode + Python拡張  

---

## 5. プロジェクト構成

```
kicad_snapshot/
├── pyproject.toml
├── README.md
├── src/
│   └── kicad_snapshot/
│       ├── __init__.py
│       ├── __main__.py
│       ├── gui.py
│       ├── core/
│       ├── resources/
│       └── config.py
└── .github/
    └── workflows/
        └── build.yml
```

---

## 6. 起動方式（統一設計）

### エントリポイント定義

```toml
[project.scripts]
kicad_snapshot = "kicad_snapshot.__main__:main"
```

### 起動方法

#### pip / pipx 利用時

```
kicad_snapshot
```

#### Windows exe 版

```
kicad_snapshot.exe
```

すべて同一の `main()` から起動する設計とする。

---

## 7. 配布方法

### 7.1 Windows（基本配布）

GitHub Releases に以下を公開する：

```
kicad_snapshot-<version>-win-x64.zip
```

内容：

```
kicad_snapshot.exe
Qt関連DLL
resources/
```

#### 代替（Python利用者向け）

```
pip install kicad_snapshot
```

---

### 7.2 macOS / Linux

```
pipx install kicad_snapshot
kicad_snapshot
```

.app化・署名・Notarizationは行わない。

---

## 8. リソース管理

PyInstaller対応のため、ファイルパス直指定は禁止する。

```python
import importlib.resources as res

icon_path = res.files("kicad_snapshot.resources").joinpath("icon.png")
```

---

## 9. 設定保存設計

```python
from platformdirs import user_config_dir

CONFIG_DIR = user_config_dir("KiCadSnapshot", "KiCadSnapshot")
```

| OS | 保存先例 |
|----|----------|
| Windows | %APPDATA%/KiCadSnapshot |
| macOS | ~/Library/Application Support/KiCadSnapshot |
| Linux | ~/.config/KiCadSnapshot |

---

## 10. CI/CD

### Windows

- GitHub Actions により exe を自動生成  
- zip化して Release 添付  
- SHA256SUM を同時生成  

### macOS / Linux

- wheel / sdist をビルド  
- PyPI公開またはRelease添付  

---

## 11. 今後の拡張方針

- Windowsコード署名はスポンサー獲得後に検討  
- macOS .app化は需要発生時に検討  
- GUIとロジック分離により将来的な他UI移行も可能  

---

以上

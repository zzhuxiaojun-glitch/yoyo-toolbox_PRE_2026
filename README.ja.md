# YOYO's Toolbox 2026

[简体中文](README.md) | **日本語** | [English](README.en.md)

YOYO のツールボックス：2026 年に作ったアプリとツールの厳選集です。

- **Web アプリ**：リンクを開けばすぐ使えます
- **デスクトップツール**：[Releases](../../releases/latest) からダウンロード
- **Claude Code スキル / スクリプト**：このリポジトリの [`skills/`](skills) と [`scripts/`](scripts)

---

## 🌐 Web アプリ

| アプリ | 概要 | URL |
|---|---|---|
| **JLPTsimu** | JLPT（日本語能力試験）の模擬試験＋学習進捗トラッキング＋知識ベース | https://jlptsimu.manga-re.com |
| **FEsimu** | 基本情報／応用情報技術者試験の問題集と模擬演習 | https://fe-siken.manga-re.com |

## 🧰 デスクトップツール（Windows）

[Releases](../../releases/latest) からダウンロードできます。

| ツール | 概要 | ファイル |
|---|---|---|
| **MangaTL** | 日本語漫画の半自動翻訳＋中国語写植：吹き出し検出（YOLO）、manga-ocr による文字認識、用語集つきの一文ずつの翻訳、写植エディタ。中国語版 EPUB／LabelPlus／校正用原稿を出力 | `MangaTL-Setup-0.1.0.exe` |
| **BatchRename** | ファイル名・拡張子を一括変更する GUI ツール。zip に変更した場合はそのまま一括解凍も可能 | `BatchRenameGUI.exe` |
| **TranEPUB** | 画像フォルダや ZIP をまとめて EPUB に変換。Web 画面とコマンドラインの両方に対応（[ソース](https://github.com/zzhuxiaojun-glitch/TranEPUB_DeskTopAPP)） | `TranEPUB_DeskTopAPP_v1.0.zip` |

<details>
<summary>インストール方法</summary>

- **MangaTL**：ダブルクリックでインストール。初回起動時にモデルとフォントを自動でダウンロードします。
- **BatchRename**：インストール不要。ダブルクリックで起動します。
- **TranEPUB**：解凍して `TranEPUB.bat` をダブルクリック。Python 3.10 以上が必要です。入っていない場合は先に `setup_python.bat` を実行してください。

> コード署名をしていないため、初回起動時に Windows SmartScreen の警告が出ることがあります。「詳細情報 → 実行」で起動できます。

</details>

## 📦 その他のプロジェクト

| プロジェクト | 概要 | リポジトリ |
|---|---|---|
| **Nihongo Kaiwa** | 日本語会話練習 Web アプリ：AI との会話、音声認識、音声合成（Vue 3 + Go） | ソース非公開 |
| **jmdict-cn** | 日本語辞書 JMdict の中国語版。日中対訳の例文を追加 | [jmdict-cn](https://github.com/zzhuxiaojun-glitch/jmdict-cn) |

## 🤖 Claude Code スキルとスクリプト

`skills/<名前>/` フォルダごと `~/.claude/skills/` にコピーすれば使えます。

| 名前 | 用途 |
|---|---|
| [manga-img-to-epub](skills/manga-img-to-epub) | 画像フォルダを標準的な EPUB3 に変換。一括変換に対応し、デフォルトは日本の漫画と同じ右→左のページ送り |
| [playwright-mcp-uitest](skills/playwright-mcp-uitest) | Playwright MCP で実際のブラウザを操作して UI の流れを確認し、フロントエンドの変更を検証 |
| [dispatch-board](skills/dispatch-board) | 大量の同種タスクを複数の作業票に分け、複数の Claude Code セッションが並行で引き受けて進められるようにし、進捗ダッシュボードを自動集計 |
| [project-db-query-audit](skills/project-db-query-audit) | DB クエリ最適化の一連の流れ：静的監査（N+1 など）→ EXPLAIN ANALYZE でベースライン計測 → 1 件ずつ修正 → 正誤の再確認 |
| [themed-mascot-designer](skills/themed-mascot-designer) | プロジェクト用のテーマ別マスコット一式をデザイン：性格設定 → はっきり見分けられる造形 → 画像生成用プロンプト文書 |
| [yoyo_dev](skills/yoyo_dev) | プロジェクト共通の自分の開発ルール：TDD、PR の書き方、複数セッションでの git 衝突防止、一括タスクの中断・再開など |
| [statusline.py](scripts/statusline.py) | Claude Code 用の 3 段ステータスライン：端末の幅に合わせて 1～3 行に切り替わり、モデル・ブランチ・コンテキスト使用量などを表示。導入方法はファイル冒頭のコメント参照 |

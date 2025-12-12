# Shell-Gotchi 🎮

Linuxターミナルでの作業（コマンド入力）を「ゲーム」に変える常駐型CLIアプリケーション。
コマンドを実行することで「エサ」を獲得し、ペットを育成し、ガチャを回してコレクションを増やそう！

**コンセプト:** "Work to Earn" （作業して稼ぐ）

## 機能

- 🍖 **エサドロップ**: コマンド実行で確率的にエサを獲得
- 🐱 **ペット育成**: エサをあげて満腹度を維持し、経験値を稼いでレベルアップ
- 🎰 **ガチャシステム**: チケットでガチャを回してスキンや称号を獲得
- 📅 **ログインボーナス**: 毎日のログインで報酬をゲット
- 🎨 **スキン変更**: ガチャで獲得したスキンに着せ替え
- 🏪 **ショップ**: コインでアイテムを購入
- 📋 **デイリーミッション**: 毎日の目標を達成して報酬獲得
- 🏆 **実績システム**: 様々な条件を達成して報酬をゲット

## インストール

### 1. 依存ライブラリのインストール

```bash
cd shell-gotchi
pip install -r requirements.txt
```

### 2. シェルフックの設定

#### Bash の場合
```bash
echo 'source /path/to/shell-gotchi/hooks/shell_hook.sh' >> ~/.bashrc
source ~/.bashrc
```

#### Zsh の場合
```bash
echo 'source /path/to/shell-gotchi/hooks/shell_hook.sh' >> ~/.zshrc
source ~/.zshrc
```

## コマンド一覧

### 基本コマンド
| コマンド | 説明 |
|---------|------|
| `sg status` | ペットのステータスを表示 |
| `sg feed` | ペットにエサをあげる |
| `sg gacha` | ガチャを回す（チケット1枚消費） |
| `sg collection` | コレクション一覧を表示 |
| `sg rename <名前>` | ペットの名前を変更 |
| `sg reset` | ゲームデータをリセット |

### 新機能コマンド
| コマンド | 説明 |
|---------|------|
| `sg skin` | 所持スキン一覧を表示 |
| `sg skin <ID>` | スキンを変更 |
| `sg stats` | 詳細な統計情報を表示 |
| `sg shop list` | ショップの商品一覧 |
| `sg shop buy <ID>` | 商品を購入 |
| `sg daily list` | デイリーミッション一覧 |
| `sg daily claim <ID>` | ミッション報酬を受け取る |
| `sg achievement` | 実績一覧を表示 |

## ゲームシステム

### エサドロップ
- コマンド実行ごとに **5%** の確率でエサがドロップ
- **30回** コマンドを実行すると確定でエサがドロップ
- 空のコマンド（Enterのみ）はカウントされません

### 満腹度
- コマンド実行ごとに **-0.5%** 減少
- 0%になると経験値が入らなくなります
- エサをあげると **+20%** 回復

### レベルアップ
- エサをあげると経験値 **+10**
- 一定の経験値でレベルアップ
- Lv.5, 10, 15, 20 でボーナスチケット獲得

### ガチャ確率
| レアリティ | 確率 | 排出物 |
|-----------|------|--------|
| SSR | 1% | 特殊スキン、レア称号 |
| SR | 9% | 色違いスキン |
| R | 90% | 豆知識、ハズレの石 |

### ログインボーナス
- 毎日ログインで「チケットの破片」×1
- 7個集めるとガチャチケット×1に変換
- 7日連続ログインでガチャチケット×1

## データ保存場所

`~/.local/share/shell-gotchi/data.json`

## 開発

### ディレクトリ構造

```
shell-gotchi/
├── src/
│   ├── __init__.py      # パッケージ初期化
│   ├── main.py          # CLIエントリーポイント
│   ├── config.py        # 設定・定数管理
│   ├── storage.py       # JSONデータの読み書き
│   ├── game_logic.py    # ゲームロジック
│   ├── ui.py            # Rich表示処理
│   └── assets.py        # ASCIIアート定義
├── hooks/
│   └── shell_hook.sh    # シェルフック
├── data/                # (実行時に生成)
├── requirements.txt     # 依存ライブラリ
└── README.md
```

### 直接実行

```bash
cd shell-gotchi
python -m src.main status
python -m src.main feed
python -m src.main gacha
```

## ライセンス

MIT License

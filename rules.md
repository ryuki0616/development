# Shell-Gotchi プロジェクト コーディング規約

## プロジェクト概要
Linuxターミナルでの作業（コマンド入力）を「ゲーム」に変える常駐型CLIアプリケーションです。コマンドを実行することで「エサ」を獲得し、ペットを育成し、ガチャを回してコレクションを増やします。

## 技術スタック
- Python 3.10+
- Rich (TUI表示ライブラリ)
- Click (CLIフレームワーク)
- JSON (データ保存)

## コーディング規約

### 設定値の管理
- すべての設定値は`config.py`に集約
- 定数は大文字のスネークケース（`DROP_CHANCE`など）
- 設定値の変更は`config.py`のみを編集

```python
# config.py
DROP_CHANCE = 0.05  # 5%の確率でエサドロップ
GUARANTEED_DROP_COMMANDS = 30  # N回コマンドでエサ確定ドロップ
```

### データ保存
- JSON形式でデータを保存
- 保存先: `~/.local/share/shell-gotchi/data.json`
- パス操作は`pathlib.Path`を使用

```python
from pathlib import Path

DATA_DIR = Path.home() / ".local" / "share" / "shell-gotchi"
DATA_FILE = DATA_DIR / "data.json"
```

### UI表示
- RichライブラリでTUI表示
- 色やスタイルを適切に使用
- テーブル、プログレスバーなどRichの機能を活用

### コマンドライン
- ClickライブラリでCLIコマンドを定義
- コマンドは`sg`プレフィックスで実行（例: `sg status`）

### インデント
- 4スペースを使用

### 命名規則
- 変数・関数: `snake_case`
- 定数: `UPPER_SNAKE_CASE`
- クラス: `PascalCase`

## コメントの書き方

### 設定定数のコメント
各定数の意味と単位をコメントで説明します。

```python
# ===== ゲームパラメータ =====

# ドロップ関連
DROP_CHANCE = 0.05  # 5%の確率でエサドロップ
GUARANTEED_DROP_COMMANDS = 30  # N回コマンドでエサ確定ドロップ

# 満腹度関連
HUNGER_DECREASE_PER_COMMAND = 0.5  # コマンド実行ごとの満腹度減少（%）
MAX_HUNGER = 100  # 満腹度の最大値
MIN_HUNGER = 0    # 満腹度の最小値

# エサやり効果
FEED_HUNGER_GAIN = 20  # 満腹度回復量（%）
FEED_EXP_GAIN = 10     # 経験値獲得量

# ログインボーナス
TICKET_FRAGMENTS_FOR_TICKET = 7  # チケット1枚に必要な破片数
LOGIN_STREAK_FOR_TICKET = 7      # 連続ログイン日数でチケット獲得
```

### ゲームロジックのコメント
確率計算や状態遷移をコメントで説明します。

```python
def calculate_drop(commands_since_drop: int) -> bool:
    """
    エサドロップ判定

    Args:
        commands_since_drop: 前回ドロップからのコマンド数

    Returns:
        ドロップした場合True

    判定ロジック:
    1. 確率的ドロップ: DROP_CHANCE（5%）の確率でドロップ
    2. 確定ドロップ: GUARANTEED_DROP_COMMANDS（30回）コマンドで確定ドロップ
    """
    # 確定ドロップの判定（30回コマンドで確定）
    if commands_since_drop >= GUARANTEED_DROP_COMMANDS:
        return True

    # 確率的ドロップの判定（5%の確率）
    return random.random() < DROP_CHANCE
```

### レベル計算のコメント
レベルアップの計算ロジックをコメントで説明します。

```python
def calculate_level(exp: int) -> int:
    """
    経験値からレベルを計算

    Args:
        exp: 現在の経験値

    Returns:
        現在のレベル

    計算方法:
    - LEVEL_THRESHOLDS辞書を使用してレベルを判定
    - 例: exp=50 → level=2, exp=120 → level=3
    """
    level = 1
    for lv, threshold in LEVEL_THRESHOLDS.items():
        if exp >= threshold:
            level = lv
        else:
            break
    return level
```

### CLIコマンドのコメント
コマンドの機能と使用例をdocstringで説明します。

```python
import click

@click.group()
def cli():
    """Shell-Gotchi: ターミナル作業をゲーム化するCLIアプリ"""
    pass

@cli.command()
def status():
    """
    ペットのステータスを表示

    表示内容:
    - ペットの名前、レベル、経験値
    - 満腹度、所持エサ数
    - 所持チケット、コイン
    - ログインストリーク

    使用例:
        sg status
    """
    # ステータス表示の処理
    pass

@cli.command()
@click.argument('name')
def rename(name: str):
    """
    ペットの名前を変更

    Args:
        name: 新しいペットの名前

    使用例:
        sg rename "マイペット"
    """
    # 名前変更の処理
    pass
```

### UI表示のコメント
Richの表示ロジックをコメントで説明します。

```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

def display_status(data: Dict[str, Any]):
    """
    ペットのステータスをRichで表示

    Args:
        data: ゲームデータ（pet, stats, userを含む）

    表示内容:
    - ペット情報パネル（名前、レベル、経験値）
    - ステータステーブル（満腹度、エサ数など）
    - プログレスバー（満腹度、経験値）
    """
    console = Console()
    pet = data["pet"]

    # ペット情報パネルを作成
    pet_info = Panel(
        f"[bold]{pet['name']}[/bold]\n"
        f"レベル: {pet['level']}\n"
        f"経験値: {pet['exp']}",
        title="ペット情報",
        border_style="green"
    )
    console.print(pet_info)

    # 満腹度をプログレスバーで表示
    hunger_bar = ProgressBar(
        completed=pet["hunger"],
        total=100,
        description="満腹度"
    )
    console.print(hunger_bar)
```

### データ保存・読み込みのコメント
JSONファイルの操作をコメントで説明します。

```python
def load_data() -> Dict[str, Any]:
    """
    ゲームデータをJSONファイルから読み込む

    Returns:
        ゲームデータの辞書

    データ構造:
    {
        "pet": {"name": str, "level": int, "exp": int, ...},
        "user": {"food": int, "tickets": int, ...},
        "stats": {"total_commands": int, ...}
    }

    Raises:
        FileNotFoundError: データファイルが存在しない場合（初回起動時）
    """
    if not DATA_FILE.exists():
        # 初回起動時はデフォルトデータを返す
        return get_default_data()

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data: Dict[str, Any]) -> None:
    """
    ゲームデータをJSONファイルに保存

    Args:
        data: 保存するゲームデータ

    処理内容:
    1. データディレクトリが存在しない場合は作成
    2. JSONファイルにデータを書き込み
    3. エラー時は適切にハンドリング
    """
    # データディレクトリが存在しない場合は作成
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

### ガチャシステムのコメント
ガチャの抽選ロジックをコメントで説明します。

```python
def draw_gacha() -> Dict[str, Any]:
    """
    ガチャを引く

    Returns:
        獲得アイテムの情報（レアリティ、名前など）

    抽選ロジック:
    1. 乱数を生成（0.0～1.0）
    2. レアリティを判定:
       - 0.00～0.01: SSR (1%)
       - 0.01～0.10: SR (9%)
       - 0.10～1.00: R (90%)
    3. レアリティに応じたアイテムプールから抽選

    使用例:
        item = draw_gacha()
        print(f"獲得: {item['name']} ({item['rarity']})")
    """
    rand = random.random()

    # レアリティ判定（累積確率で判定）
    if rand < 0.01:
        rarity = "SSR"  # 1%の確率
    elif rand < 0.10:
        rarity = "SR"   # 9%の確率
    else:
        rarity = "R"    # 90%の確率

    # レアリティに応じたアイテムプールから抽選
    items = [item for item in GACHA_ITEMS if item["rarity"] == rarity]
    return random.choice(items)
```

## ファイル構造

### ディレクトリ構成
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

## その他の注意事項

### シェルフック
- `.bashrc`または`.zshrc`にフックスクリプトを追加
- コマンド実行時に自動的にゲームロジックを実行

### エラーハンドリング
- ファイル読み書きエラーを適切に処理
- データ構造の不整合をチェック
- エラーメッセージは日本語でわかりやすく記述

### パフォーマンス
- データファイルの読み書きは必要最小限に
- 大量のデータ処理は適切に最適化


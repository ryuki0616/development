"""
Shell-Gotchi 設定・定数管理
"""
import os
from pathlib import Path

# ===== データ保存パス =====
DATA_DIR = Path.home() / ".local" / "share" / "shell-gotchi"
DATA_FILE = DATA_DIR / "data.json"

# ===== ゲームパラメータ =====
# ドロップ関連
DROP_CHANCE = 0.05  # 5%の確率でエサドロップ
GUARANTEED_DROP_COMMANDS = 30  # N回コマンドでエサ確定ドロップ

# 満腹度関連
HUNGER_DECREASE_PER_COMMAND = 0.5  # コマンド実行ごとの満腹度減少
MAX_HUNGER = 100
MIN_HUNGER = 0

# エサやり効果
FEED_HUNGER_GAIN = 20  # 満腹度回復量
FEED_EXP_GAIN = 10  # 経験値獲得量

# ログインボーナス
TICKET_FRAGMENTS_FOR_TICKET = 7  # チケット1枚に必要な破片数
LOGIN_STREAK_FOR_TICKET = 7  # 連続ログイン日数でチケット獲得

# ===== レベルアップ閾値 =====
# レベルごとの累積経験値閾値
LEVEL_THRESHOLDS = {
    1: 0,
    2: 50,
    3: 120,
    4: 200,
    5: 300,
    6: 420,
    7: 560,
    8: 720,
    9: 900,
    10: 1100,
    11: 1350,
    12: 1650,
    13: 2000,
    14: 2400,
    15: 2850,
    16: 3350,
    17: 3900,
    18: 4500,
    19: 5150,
    20: 5850,
}

# レベルアップ時のチケット報酬（特定レベルで付与）
LEVEL_UP_TICKET_REWARDS = {
    5: 1,
    10: 2,
    15: 2,
    20: 3,
}

# ===== ガチャ確率 =====
GACHA_RATES = {
    "SSR": 0.01,  # 1%
    "SR": 0.09,   # 9%
    "R": 0.90,    # 90%
}

# ガチャアイテムプール
GACHA_ITEMS = {
    "SSR": [
        {"id": "skin_golden_dragon", "name": "黄金龍スキン", "type": "skin"},
        {"id": "skin_cyber_cat", "name": "サイバーキャットスキン", "type": "skin"},
        {"id": "title_legendary", "name": "伝説のコマンダー", "type": "title"},
    ],
    "SR": [
        {"id": "skin_blue_cat", "name": "青色キャットスキン", "type": "skin"},
        {"id": "skin_red_cat", "name": "赤色キャットスキン", "type": "skin"},
        {"id": "skin_green_cat", "name": "緑色キャットスキン", "type": "skin"},
        {"id": "skin_purple_cat", "name": "紫色キャットスキン", "type": "skin"},
    ],
    "R": [
        {"id": "tip_git", "name": "豆知識: git stash は一時退避に便利", "type": "tip"},
        {"id": "tip_vim", "name": "豆知識: :wq で保存して終了", "type": "tip"},
        {"id": "tip_grep", "name": "豆知識: grep -r で再帰検索", "type": "tip"},
        {"id": "tip_find", "name": "豆知識: find . -name で検索", "type": "tip"},
        {"id": "stone", "name": "ハズレの石", "type": "junk"},
    ],
}

# ===== 初期データスキーマ =====
DEFAULT_DATA = {
    "user": {
        "last_login": None,
        "login_streak": 0,
        "food": 5,  # 初期エサ5個
        "ticket_fragments": 0,
        "tickets": 1,  # 初回チケット1枚
    },
    "stats": {
        "total_commands": 0,
        "commands_since_drop": 0,
    },
    "pet": {
        "name": "Termi",
        "skin_id": "default_cat",
        "level": 1,
        "exp": 0,
        "hunger": 100,
    },
    "collection": ["default_cat"],
}

# ===== 表示設定 =====
APP_NAME = "Shell-Gotchi"
VERSION = "1.0.0"

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

# ===== ショップアイテム =====
SHOP_ITEMS = {
    "food_pack_small": {
        "name": "エサパック（小）",
        "description": "エサ x5",
        "price": 50,  # コイン
        "reward": {"food": 5},
    },
    "food_pack_large": {
        "name": "エサパック（大）",
        "description": "エサ x20",
        "price": 180,
        "reward": {"food": 20},
    },
    "ticket_single": {
        "name": "ガチャチケット",
        "description": "チケット x1",
        "price": 100,
        "reward": {"tickets": 1},
    },
    "exp_boost": {
        "name": "経験値ブースト",
        "description": "次の10回のエサやりで経験値2倍",
        "price": 150,
        "reward": {"exp_boost": 10},
    },
}

# ===== デイリーミッション =====
DAILY_MISSIONS = {
    "commands_10": {
        "name": "コマンド実行 10回",
        "description": "コマンドを10回実行する",
        "target": 10,
        "type": "commands",
        "reward": {"coins": 20},
    },
    "commands_50": {
        "name": "コマンド実行 50回",
        "description": "コマンドを50回実行する",
        "target": 50,
        "type": "commands",
        "reward": {"coins": 50},
    },
    "feed_3": {
        "name": "エサやり 3回",
        "description": "ペットにエサを3回あげる",
        "target": 3,
        "type": "feed",
        "reward": {"coins": 30},
    },
    "gacha_1": {
        "name": "ガチャを回す",
        "description": "ガチャを1回回す",
        "target": 1,
        "type": "gacha",
        "reward": {"ticket_fragments": 2},
    },
}

# ===== 実績 =====
ACHIEVEMENTS = {
    # コマンド系
    "first_command": {
        "name": "はじめの一歩",
        "description": "初めてコマンドを実行",
        "condition": {"type": "total_commands", "target": 1},
        "reward": {"coins": 10},
    },
    "commands_100": {
        "name": "見習いコマンダー",
        "description": "コマンドを100回実行",
        "condition": {"type": "total_commands", "target": 100},
        "reward": {"coins": 50},
    },
    "commands_500": {
        "name": "熟練コマンダー",
        "description": "コマンドを500回実行",
        "condition": {"type": "total_commands", "target": 500},
        "reward": {"coins": 100, "tickets": 1},
    },
    "commands_1000": {
        "name": "マスターコマンダー",
        "description": "コマンドを1000回実行",
        "condition": {"type": "total_commands", "target": 1000},
        "reward": {"coins": 200, "tickets": 2},
    },
    "commands_5000": {
        "name": "伝説のコマンダー",
        "description": "コマンドを5000回実行",
        "condition": {"type": "total_commands", "target": 5000},
        "reward": {"coins": 500, "tickets": 5},
    },
    # レベル系
    "level_5": {
        "name": "成長中",
        "description": "ペットがレベル5に到達",
        "condition": {"type": "level", "target": 5},
        "reward": {"coins": 30},
    },
    "level_10": {
        "name": "一人前",
        "description": "ペットがレベル10に到達",
        "condition": {"type": "level", "target": 10},
        "reward": {"coins": 100, "tickets": 1},
    },
    "level_20": {
        "name": "達人",
        "description": "ペットがレベル20に到達",
        "condition": {"type": "level", "target": 20},
        "reward": {"coins": 300, "tickets": 3},
    },
    # ガチャ系
    "first_gacha": {
        "name": "運試し",
        "description": "初めてガチャを回す",
        "condition": {"type": "total_gacha", "target": 1},
        "reward": {"coins": 20},
    },
    "gacha_10": {
        "name": "ガチャ愛好家",
        "description": "ガチャを10回回す",
        "condition": {"type": "total_gacha", "target": 10},
        "reward": {"coins": 50},
    },
    "first_ssr": {
        "name": "超激レア！",
        "description": "SSRを引く",
        "condition": {"type": "ssr_count", "target": 1},
        "reward": {"coins": 100},
    },
    # ログイン系
    "login_7": {
        "name": "週間プレイヤー",
        "description": "7日連続ログイン",
        "condition": {"type": "login_streak", "target": 7},
        "reward": {"coins": 50, "tickets": 1},
    },
    "login_30": {
        "name": "月間プレイヤー",
        "description": "30日連続ログイン",
        "condition": {"type": "login_streak", "target": 30},
        "reward": {"coins": 200, "tickets": 3},
    },
    # コレクション系
    "collection_5": {
        "name": "コレクター",
        "description": "5種類のアイテムを集める",
        "condition": {"type": "collection_count", "target": 5},
        "reward": {"coins": 50},
    },
    "collection_10": {
        "name": "熱心なコレクター",
        "description": "10種類のアイテムを集める",
        "condition": {"type": "collection_count", "target": 10},
        "reward": {"coins": 150, "tickets": 2},
    },
}

# ===== 初期データスキーマ =====
DEFAULT_DATA = {
    "user": {
        "last_login": None,
        "login_streak": 0,
        "food": 5,  # 初期エサ5個
        "ticket_fragments": 0,
        "tickets": 1,  # 初回チケット1枚
        "coins": 0,  # ショップ用コイン
        "exp_boost": 0,  # 経験値ブースト残り回数
    },
    "stats": {
        "total_commands": 0,
        "commands_since_drop": 0,
        "total_feed": 0,  # 累計エサやり回数
        "total_gacha": 0,  # 累計ガチャ回数
        "ssr_count": 0,  # SSR獲得回数
        "max_login_streak": 0,  # 最大連続ログイン
    },
    "pet": {
        "name": "Termi",
        "skin_id": "default_cat",
        "level": 1,
        "exp": 0,
        "hunger": 100,
    },
    "collection": ["default_cat"],
    "achievements": [],  # 達成済み実績ID
    "daily": {
        "date": None,  # ミッションの日付
        "progress": {},  # ミッションごとの進捗
        "completed": [],  # 完了済みミッションID
    },
}

# ===== 表示設定 =====
APP_NAME = "Shell-Gotchi"
VERSION = "2.0.0"

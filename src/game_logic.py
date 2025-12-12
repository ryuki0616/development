"""
Shell-Gotchi ゲームロジック
ドロップ判定、レベル計算、ガチャ抽選など
"""
import random
from datetime import datetime, date
from typing import Any, Dict, List, Optional

from .config import (
    DROP_CHANCE, GUARANTEED_DROP_COMMANDS,
    HUNGER_DECREASE_PER_COMMAND, MAX_HUNGER, MIN_HUNGER,
    FEED_HUNGER_GAIN, FEED_EXP_GAIN,
    LEVEL_THRESHOLDS, LEVEL_UP_TICKET_REWARDS,
    GACHA_RATES, GACHA_ITEMS,
    TICKET_FRAGMENTS_FOR_TICKET, LOGIN_STREAK_FOR_TICKET
)


# ===== Step 2: コマンド処理・ドロップロジック =====

def process_command(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    コマンド実行時の処理
    - カウンター増加
    - 満腹度減少
    - ドロップ判定
    
    Returns:
        Dict with keys: dropped (bool), drop_count (int)
    """
    stats = data["stats"]
    pet = data["pet"]
    user = data["user"]
    
    # 総コマンド数増加
    stats["total_commands"] += 1
    stats["commands_since_drop"] += 1
    
    # 満腹度減少
    pet["hunger"] = max(MIN_HUNGER, pet["hunger"] - HUNGER_DECREASE_PER_COMMAND)
    
    # ドロップ判定
    dropped = calculate_drop(stats["commands_since_drop"])
    
    if dropped:
        user["food"] += 1
        stats["commands_since_drop"] = 0
    
    return {
        "dropped": dropped,
        "food_count": user["food"]
    }


def calculate_drop(commands_since_drop: int) -> bool:
    """
    ドロップ判定ロジック
    - N回ごとに確定ドロップ
    - または確率でドロップ
    """
    # 確定ドロップ
    if commands_since_drop >= GUARANTEED_DROP_COMMANDS:
        return True
    
    # 確率ドロップ
    return random.random() < DROP_CHANCE


# ===== Step 3: 育成ロジック =====

def feed_pet(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    ペットにエサをあげる
    - エサ消費
    - 満腹度回復
    - 経験値獲得
    - レベルアップ判定
    
    Returns:
        Dict with keys: exp_gained, level_up, tickets_earned
    """
    pet = data["pet"]
    user = data["user"]
    
    # エサ消費
    user["food"] -= 1
    
    # 満腹度回復（上限100%）
    pet["hunger"] = min(MAX_HUNGER, pet["hunger"] + FEED_HUNGER_GAIN)
    
    # 経験値獲得（満腹度が0でなければ）
    exp_gained = FEED_EXP_GAIN
    if pet["hunger"] > 0:
        pet["exp"] += exp_gained
    
    # レベルアップ判定
    old_level = pet["level"]
    level_up, new_level = check_level_up(pet)
    
    # レベルアップ報酬
    tickets_earned = 0
    if level_up:
        pet["level"] = new_level
        tickets_earned = calculate_level_up_reward(old_level, new_level)
        user["tickets"] += tickets_earned
    
    return {
        "exp_gained": exp_gained,
        "level_up": level_up,
        "new_level": new_level,
        "tickets_earned": tickets_earned
    }


def check_level_up(pet: Dict[str, Any]) -> tuple:
    """
    レベルアップ判定
    
    Returns:
        (level_up: bool, new_level: int)
    """
    current_level = pet["level"]
    current_exp = pet["exp"]
    
    # 次のレベルの閾値をチェック
    next_level = current_level + 1
    if next_level in LEVEL_THRESHOLDS:
        if current_exp >= LEVEL_THRESHOLDS[next_level]:
            return True, next_level
    
    return False, current_level


def calculate_level_up_reward(old_level: int, new_level: int) -> int:
    """
    レベルアップ報酬（チケット）を計算
    特定レベルでボーナスチケット付与
    """
    tickets = 0
    for level in range(old_level + 1, new_level + 1):
        if level in LEVEL_UP_TICKET_REWARDS:
            tickets += LEVEL_UP_TICKET_REWARDS[level]
    return tickets


def calculate_exp_for_level(level: int) -> int:
    """次のレベルまでに必要な経験値を計算"""
    current_threshold = LEVEL_THRESHOLDS.get(level, 0)
    next_threshold = LEVEL_THRESHOLDS.get(level + 1, current_threshold + 500)
    return next_threshold - current_threshold


# ===== Step 4: ガチャロジック =====

def pull_gacha(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    ガチャを引く
    - チケット消費
    - 確率に基づいて抽選
    - コレクションに追加
    
    Returns:
        Dict with keys: rarity, item
    """
    user = data["user"]
    collection = data["collection"]
    
    # チケット消費
    user["tickets"] -= 1
    
    # レアリティ抽選
    rarity = determine_rarity()
    
    # アイテム抽選
    item = select_item(rarity)
    
    # コレクションに追加（重複しない場合のみ）
    if item["id"] not in collection:
        collection.append(item["id"])
    
    return {
        "rarity": rarity,
        "item": item
    }


def determine_rarity() -> str:
    """
    ガチャのレアリティを決定
    """
    roll = random.random()
    
    cumulative = 0
    for rarity, rate in GACHA_RATES.items():
        cumulative += rate
        if roll < cumulative:
            return rarity
    
    return "R"  # フォールバック


def select_item(rarity: str) -> Dict[str, Any]:
    """
    指定されたレアリティからアイテムを選択
    """
    items = GACHA_ITEMS.get(rarity, GACHA_ITEMS["R"])
    return random.choice(items)


# ===== ログインボーナス =====

def check_login_bonus(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    ログインボーナスをチェック
    
    Returns:
        Dict with keys: is_new_day, reward_type, streak
    """
    user = data["user"]
    today = date.today().isoformat()
    last_login = user.get("last_login")
    
    # 同じ日ならボーナスなし
    if last_login == today:
        return {
            "is_new_day": False,
            "reward_type": None,
            "streak": user["login_streak"]
        }
    
    # 連続ログイン判定
    if last_login:
        try:
            last_date = date.fromisoformat(last_login)
            today_date = date.today()
            diff = (today_date - last_date).days
            
            if diff == 1:
                # 連続ログイン
                user["login_streak"] += 1
            elif diff > 1:
                # 連続ログインが途切れた
                user["login_streak"] = 1
        except ValueError:
            user["login_streak"] = 1
    else:
        # 初回ログイン
        user["login_streak"] = 1
    
    # 最終ログイン日を更新
    user["last_login"] = today
    
    # 報酬付与
    reward_type = "fragment"
    
    if user["login_streak"] >= LOGIN_STREAK_FOR_TICKET and user["login_streak"] % LOGIN_STREAK_FOR_TICKET == 0:
        # 7日連続でチケット
        user["tickets"] += 1
        reward_type = "ticket"
    else:
        # 通常は破片
        user["ticket_fragments"] += 1
        
        # 破片が7個溜まったらチケットに変換
        if user["ticket_fragments"] >= TICKET_FRAGMENTS_FOR_TICKET:
            user["ticket_fragments"] -= TICKET_FRAGMENTS_FOR_TICKET
            user["tickets"] += 1
    
    return {
        "is_new_day": True,
        "reward_type": reward_type,
        "streak": user["login_streak"]
    }

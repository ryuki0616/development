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
    TICKET_FRAGMENTS_FOR_TICKET, LOGIN_STREAK_FOR_TICKET,
    SHOP_ITEMS, DAILY_MISSIONS, ACHIEVEMENTS
)


# ===== Step 2: コマンド処理・ドロップロジック =====

def process_command(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    コマンド実行時の処理
    - カウンター増加
    - 満腹度減少
    - ドロップ判定
    - デイリーミッション進捗
    - コイン獲得（10コマンドごとに1コイン）
    
    Returns:
        Dict with keys: dropped (bool), drop_count (int), coins_earned (int)
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
    
    # コイン獲得（10コマンドごとに1コイン）
    coins_earned = 0
    if stats["total_commands"] % 10 == 0:
        coins_earned = 1
        user["coins"] = user.get("coins", 0) + coins_earned
    
    # デイリーミッション進捗更新
    update_daily_progress(data, "commands", 1)
    
    return {
        "dropped": dropped,
        "food_count": user["food"],
        "coins_earned": coins_earned
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
    - 経験値獲得（ブースト対応）
    - レベルアップ判定
    - デイリーミッション進捗
    
    Returns:
        Dict with keys: exp_gained, level_up, tickets_earned
    """
    pet = data["pet"]
    user = data["user"]
    stats = data["stats"]
    
    # エサ消費
    user["food"] -= 1
    
    # 満腹度回復（上限100%）
    pet["hunger"] = min(MAX_HUNGER, pet["hunger"] + FEED_HUNGER_GAIN)
    
    # 経験値獲得（満腹度が0でなければ）
    exp_gained = FEED_EXP_GAIN
    
    # 経験値ブーストチェック
    exp_boost = user.get("exp_boost", 0)
    if exp_boost > 0:
        exp_gained *= 2
        user["exp_boost"] = exp_boost - 1
    
    if pet["hunger"] > 0:
        pet["exp"] += exp_gained
    
    # 統計更新
    stats["total_feed"] = stats.get("total_feed", 0) + 1
    
    # レベルアップ判定
    old_level = pet["level"]
    level_up, new_level = check_level_up(pet)
    
    # レベルアップ報酬
    tickets_earned = 0
    if level_up:
        pet["level"] = new_level
        tickets_earned = calculate_level_up_reward(old_level, new_level)
        user["tickets"] += tickets_earned
    
    # デイリーミッション進捗更新
    update_daily_progress(data, "feed", 1)
    
    return {
        "exp_gained": exp_gained,
        "level_up": level_up,
        "new_level": new_level,
        "tickets_earned": tickets_earned,
        "boosted": exp_boost > 0
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
    - 統計・デイリーミッション更新
    
    Returns:
        Dict with keys: rarity, item, is_new
    """
    user = data["user"]
    stats = data["stats"]
    collection = data["collection"]
    
    # チケット消費
    user["tickets"] -= 1
    
    # 統計更新
    stats["total_gacha"] = stats.get("total_gacha", 0) + 1
    
    # レアリティ抽選
    rarity = determine_rarity()
    
    # SSRカウント
    if rarity == "SSR":
        stats["ssr_count"] = stats.get("ssr_count", 0) + 1
    
    # アイテム抽選
    item = select_item(rarity)
    
    # コレクションに追加（重複しない場合のみ）
    is_new = item["id"] not in collection
    if is_new:
        collection.append(item["id"])
    
    # デイリーミッション進捗更新
    update_daily_progress(data, "gacha", 1)
    
    return {
        "rarity": rarity,
        "item": item,
        "is_new": is_new
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
    stats = data["stats"]
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
    
    # 最大ログインストリーク更新
    stats["max_login_streak"] = max(
        stats.get("max_login_streak", 0),
        user["login_streak"]
    )
    
    # 最終ログイン日を更新
    user["last_login"] = today
    
    # デイリーミッションリセット
    reset_daily_missions(data)
    
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


# ===== スキン変更 =====

def change_skin(data: Dict[str, Any], skin_id: str) -> Dict[str, Any]:
    """
    ペットのスキンを変更する
    
    Returns:
        Dict with keys: success, message
    """
    collection = data["collection"]
    pet = data["pet"]
    
    # スキンを所持しているかチェック
    if skin_id not in collection:
        return {
            "success": False,
            "message": "このスキンは所持していません"
        }
    
    old_skin = pet["skin_id"]
    pet["skin_id"] = skin_id
    
    return {
        "success": True,
        "message": f"スキンを変更しました",
        "old_skin": old_skin,
        "new_skin": skin_id
    }


# ===== ショップ =====

def buy_item(data: Dict[str, Any], item_id: str) -> Dict[str, Any]:
    """
    ショップでアイテムを購入
    
    Returns:
        Dict with keys: success, message, item
    """
    user = data["user"]
    
    if item_id not in SHOP_ITEMS:
        return {
            "success": False,
            "message": "アイテムが見つかりません"
        }
    
    item = SHOP_ITEMS[item_id]
    price = item["price"]
    coins = user.get("coins", 0)
    
    if coins < price:
        return {
            "success": False,
            "message": f"コインが足りません（必要: {price}、所持: {coins}）"
        }
    
    # 購入処理
    user["coins"] = coins - price
    
    # 報酬付与
    reward = item["reward"]
    for key, value in reward.items():
        user[key] = user.get(key, 0) + value
    
    return {
        "success": True,
        "message": f"{item['name']}を購入しました！",
        "item": item
    }


# ===== デイリーミッション =====

def reset_daily_missions(data: Dict[str, Any]) -> None:
    """デイリーミッションをリセット"""
    today = date.today().isoformat()
    
    if "daily" not in data:
        data["daily"] = {}
    
    daily = data["daily"]
    
    # 日付が変わっていたらリセット
    if daily.get("date") != today:
        daily["date"] = today
        daily["progress"] = {mission_id: 0 for mission_id in DAILY_MISSIONS}
        daily["completed"] = []


def update_daily_progress(data: Dict[str, Any], mission_type: str, amount: int) -> List[str]:
    """
    デイリーミッションの進捗を更新
    
    Returns:
        新しく完了したミッションIDのリスト
    """
    if "daily" not in data:
        reset_daily_missions(data)
    
    daily = data["daily"]
    today = date.today().isoformat()
    
    # 日付チェック
    if daily.get("date") != today:
        reset_daily_missions(data)
        daily = data["daily"]
    
    newly_completed = []
    
    for mission_id, mission in DAILY_MISSIONS.items():
        if mission["type"] == mission_type:
            # 進捗更新
            current = daily["progress"].get(mission_id, 0)
            daily["progress"][mission_id] = current + amount
            
            # 完了チェック
            if (mission_id not in daily["completed"] and 
                daily["progress"][mission_id] >= mission["target"]):
                daily["completed"].append(mission_id)
                newly_completed.append(mission_id)
    
    return newly_completed


def claim_daily_reward(data: Dict[str, Any], mission_id: str) -> Dict[str, Any]:
    """
    デイリーミッションの報酬を受け取る
    
    Returns:
        Dict with keys: success, message, reward
    """
    if "daily" not in data:
        reset_daily_missions(data)
    
    daily = data["daily"]
    user = data["user"]
    
    if mission_id not in DAILY_MISSIONS:
        return {
            "success": False,
            "message": "ミッションが見つかりません"
        }
    
    if mission_id not in daily["completed"]:
        return {
            "success": False,
            "message": "ミッションがまだ完了していません"
        }
    
    mission = DAILY_MISSIONS[mission_id]
    
    # 報酬がすでに受け取り済みかチェック（completedリストから削除で管理）
    if f"claimed_{mission_id}" in daily.get("claimed", []):
        return {
            "success": False,
            "message": "すでに報酬を受け取っています"
        }
    
    # 報酬付与
    reward = mission["reward"]
    for key, value in reward.items():
        user[key] = user.get(key, 0) + value
    
    # 受け取り済みマーク
    if "claimed" not in daily:
        daily["claimed"] = []
    daily["claimed"].append(f"claimed_{mission_id}")
    
    return {
        "success": True,
        "message": f"報酬を受け取りました！",
        "reward": reward
    }


def get_daily_status(data: Dict[str, Any]) -> Dict[str, Any]:
    """デイリーミッションの状態を取得"""
    if "daily" not in data:
        reset_daily_missions(data)
    
    daily = data["daily"]
    today = date.today().isoformat()
    
    if daily.get("date") != today:
        reset_daily_missions(data)
        daily = data["daily"]
    
    missions = []
    for mission_id, mission in DAILY_MISSIONS.items():
        progress = daily["progress"].get(mission_id, 0)
        is_completed = mission_id in daily["completed"]
        is_claimed = f"claimed_{mission_id}" in daily.get("claimed", [])
        
        missions.append({
            "id": mission_id,
            "name": mission["name"],
            "description": mission["description"],
            "progress": progress,
            "target": mission["target"],
            "completed": is_completed,
            "claimed": is_claimed,
            "reward": mission["reward"]
        })
    
    return {
        "date": daily.get("date"),
        "missions": missions
    }


# ===== 実績システム =====

def check_achievements(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    実績の達成状況をチェックし、新規達成した実績を返す
    
    Returns:
        新規達成した実績のリスト
    """
    if "achievements" not in data:
        data["achievements"] = []
    
    achieved = data["achievements"]
    stats = data["stats"]
    pet = data["pet"]
    user = data["user"]
    collection = data["collection"]
    
    newly_achieved = []
    
    for ach_id, ach in ACHIEVEMENTS.items():
        if ach_id in achieved:
            continue
        
        condition = ach["condition"]
        target = condition["target"]
        achieved_flag = False
        
        if condition["type"] == "total_commands":
            achieved_flag = stats.get("total_commands", 0) >= target
        elif condition["type"] == "level":
            achieved_flag = pet.get("level", 1) >= target
        elif condition["type"] == "total_gacha":
            achieved_flag = stats.get("total_gacha", 0) >= target
        elif condition["type"] == "ssr_count":
            achieved_flag = stats.get("ssr_count", 0) >= target
        elif condition["type"] == "login_streak":
            achieved_flag = stats.get("max_login_streak", 0) >= target
        elif condition["type"] == "collection_count":
            achieved_flag = len(collection) >= target
        
        if achieved_flag:
            achieved.append(ach_id)
            
            # 報酬付与
            for key, value in ach["reward"].items():
                user[key] = user.get(key, 0) + value
            
            newly_achieved.append({
                "id": ach_id,
                "name": ach["name"],
                "description": ach["description"],
                "reward": ach["reward"]
            })
    
    return newly_achieved


def get_achievements_status(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """全実績の状態を取得"""
    if "achievements" not in data:
        data["achievements"] = []
    
    achieved = data["achievements"]
    stats = data["stats"]
    pet = data["pet"]
    collection = data["collection"]
    
    result = []
    
    for ach_id, ach in ACHIEVEMENTS.items():
        condition = ach["condition"]
        target = condition["target"]
        
        # 現在の進捗を取得
        current = 0
        if condition["type"] == "total_commands":
            current = stats.get("total_commands", 0)
        elif condition["type"] == "level":
            current = pet.get("level", 1)
        elif condition["type"] == "total_gacha":
            current = stats.get("total_gacha", 0)
        elif condition["type"] == "ssr_count":
            current = stats.get("ssr_count", 0)
        elif condition["type"] == "login_streak":
            current = stats.get("max_login_streak", 0)
        elif condition["type"] == "collection_count":
            current = len(collection)
        
        result.append({
            "id": ach_id,
            "name": ach["name"],
            "description": ach["description"],
            "progress": min(current, target),
            "target": target,
            "completed": ach_id in achieved,
            "reward": ach["reward"]
        })
    
    return result

"""
Shell-Gotchi JSONデータの読み書き
"""
import json
import copy
from pathlib import Path
from typing import Any, Dict

from .config import DATA_DIR, DATA_FILE, DEFAULT_DATA


def ensure_data_dir() -> None:
    """データディレクトリが存在しない場合は作成する"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_data() -> Dict[str, Any]:
    """
    JSONデータを読み込む
    ファイルが存在しない場合は初期データを生成して返す
    """
    ensure_data_dir()
    
    if not DATA_FILE.exists():
        # 初期データを作成
        data = copy.deepcopy(DEFAULT_DATA)
        save_data(data)
        return data
    
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # データの整合性チェック・マイグレーション
        data = migrate_data(data)
        return data
    except (json.JSONDecodeError, IOError) as e:
        # 読み込みエラー時は初期データで上書き
        print(f"[SG] Warning: Failed to load data, resetting... ({e})")
        data = copy.deepcopy(DEFAULT_DATA)
        save_data(data)
        return data


def save_data(data: Dict[str, Any]) -> None:
    """JSONデータを保存する"""
    ensure_data_dir()
    
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def migrate_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    古いバージョンのデータを最新形式にマイグレーションする
    """
    default = copy.deepcopy(DEFAULT_DATA)
    
    # 各セクションが存在しない場合はデフォルト値で補完
    for section in ["user", "stats", "pet"]:
        if section not in data:
            data[section] = default[section]
        else:
            # 各セクション内のキーを補完
            for key, value in default[section].items():
                if key not in data[section]:
                    data[section][key] = value
    
    # collectionが存在しない場合
    if "collection" not in data:
        data["collection"] = default["collection"]
    
    # statsにcommands_since_dropがない場合（旧バージョン対応）
    if "commands_since_drop" not in data["stats"]:
        data["stats"]["commands_since_drop"] = 0
    
    return data


def reset_data() -> Dict[str, Any]:
    """データを初期状態にリセットする"""
    data = copy.deepcopy(DEFAULT_DATA)
    save_data(data)
    return data


def get_pet_info(data: Dict[str, Any]) -> Dict[str, Any]:
    """ペット情報を取得する"""
    return data.get("pet", DEFAULT_DATA["pet"])


def get_user_info(data: Dict[str, Any]) -> Dict[str, Any]:
    """ユーザー情報を取得する"""
    return data.get("user", DEFAULT_DATA["user"])


def get_stats(data: Dict[str, Any]) -> Dict[str, Any]:
    """統計情報を取得する"""
    return data.get("stats", DEFAULT_DATA["stats"])


def get_collection(data: Dict[str, Any]) -> list:
    """コレクション一覧を取得する"""
    return data.get("collection", DEFAULT_DATA["collection"])

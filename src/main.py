"""
Shell-Gotchi CLIエントリーポイント
"""
import click
from typing import Optional

from .storage import load_data, save_data, reset_data
from .ui import (
    display_status, display_drop_message, display_login_bonus,
    display_feed_result, display_no_food, display_hunger_full,
    display_gacha_animation, display_gacha_result, display_no_tickets,
    display_collection, display_ticket_reward, display_name_changed,
    display_skin_changed, display_skin_list, display_skin_not_owned,
    display_stats, display_shop, display_shop_purchase, display_shop_error,
    display_daily_missions, display_daily_reward_claimed,
    display_achievements, display_achievement_unlocked,
    console
)
from .game_logic import (
    process_command, feed_pet, pull_gacha, check_login_bonus,
    change_skin, buy_item, get_daily_status, claim_daily_reward,
    check_achievements, get_achievements_status
)
from .config import APP_NAME, VERSION
from .assets import PET_SKINS


@click.group()
@click.version_option(version=VERSION, prog_name=APP_NAME)
def cli():
    """
    Shell-Gotchi - ターミナルでペットを育成しよう！
    
    コマンドを実行してエサを集め、ペットを育て、ガチャを回そう！
    """
    pass


@cli.command()
def status():
    """ペットのステータスを表示する"""
    data = load_data()
    display_status(data)


@cli.command()
def feed():
    """ペットにエサをあげる"""
    data = load_data()
    
    # エサチェック
    if data["user"]["food"] <= 0:
        display_no_food()
        return
    
    # 満腹度チェック
    if data["pet"]["hunger"] >= 100:
        display_hunger_full()
        return
    
    # エサやり実行
    result = feed_pet(data)
    save_data(data)
    
    display_feed_result(
        pet_name=data["pet"]["name"],
        hunger=data["pet"]["hunger"],
        exp_gained=result["exp_gained"],
        level_up=result["level_up"],
        new_level=data["pet"]["level"]
    )
    
    # レベルアップ報酬
    if result["tickets_earned"] > 0:
        display_ticket_reward(result["tickets_earned"])
    
    # 実績チェック
    new_achievements = check_achievements(data)
    if new_achievements:
        save_data(data)
        for ach in new_achievements:
            display_achievement_unlocked(ach)


@cli.command()
def gacha():
    """ガチャを回す"""
    data = load_data()
    
    # チケットチェック
    if data["user"]["tickets"] <= 0:
        display_no_tickets()
        return
    
    # ガチャ演出
    display_gacha_animation()
    
    # ガチャ実行
    result = pull_gacha(data)
    save_data(data)
    
    # 結果表示
    display_gacha_result(result["rarity"], result["item"])
    
    # 実績チェック
    new_achievements = check_achievements(data)
    if new_achievements:
        save_data(data)
        for ach in new_achievements:
            display_achievement_unlocked(ach)


@cli.command()
def collection():
    """コレクション一覧を表示する"""
    data = load_data()
    display_collection(data["collection"])


@cli.command()
@click.option("--trigger", is_flag=True, help="シェルフックからのトリガー")
@click.option("--command", "cmd", default="", help="実行されたコマンド（スパム検出用）")
def hook(trigger: bool, cmd: str):
    """シェルフック用コマンド（通常は直接使用しない）"""
    if not trigger:
        console.print("[yellow][SG][/yellow] このコマンドはシェルフックから自動的に呼び出されます。")
        return
    
    # 空コマンドはスキップ
    if not cmd or cmd.strip() == "":
        return
    
    data = load_data()
    
    # ログインボーナスチェック
    login_result = check_login_bonus(data)
    if login_result["is_new_day"]:
        save_data(data)
        display_login_bonus(login_result["reward_type"], data["user"]["login_streak"])
    
    # コマンド処理
    result = process_command(data)
    save_data(data)
    
    # ドロップした場合のみ表示
    if result["dropped"]:
        display_drop_message(data["user"]["food"])


@cli.command()
@click.argument("new_name")
def rename(new_name: str):
    """ペットの名前を変更する"""
    if not new_name or len(new_name) > 20:
        console.print("[red][SG][/red] 名前は1〜20文字で指定してください。")
        return
    
    data = load_data()
    old_name = data["pet"]["name"]
    data["pet"]["name"] = new_name
    save_data(data)
    
    display_name_changed(old_name, new_name)


@cli.command()
@click.confirmation_option(prompt="本当にデータをリセットしますか？")
def reset():
    """ゲームデータをリセットする"""
    reset_data()
    console.print("[green][SG][/green] データをリセットしました。")


@cli.command()
@click.argument("skin_id", required=False)
def skin(skin_id: Optional[str]):
    """スキンを変更する / 所持スキン一覧を表示"""
    data = load_data()
    
    if not skin_id:
        # スキン一覧表示
        display_skin_list(data["collection"], data["pet"]["skin_id"])
        return
    
    # スキン変更
    result = change_skin(data, skin_id)
    
    if result["success"]:
        save_data(data)
        display_skin_changed(result["old_skin"], result["new_skin"])
    else:
        display_skin_not_owned()


@cli.command()
def stats():
    """詳細な統計情報を表示する"""
    data = load_data()
    display_stats(data)


@cli.group()
def shop():
    """ショップでアイテムを購入する"""
    pass


@shop.command("list")
def shop_list():
    """ショップの商品一覧を表示する"""
    data = load_data()
    display_shop(data["user"].get("coins", 0))


@shop.command("buy")
@click.argument("item_id")
def shop_buy(item_id: str):
    """商品を購入する"""
    data = load_data()
    result = buy_item(data, item_id)
    
    if result["success"]:
        save_data(data)
        display_shop_purchase(result["item"]["name"], data["user"]["coins"])
        
        # 実績チェック
        new_achievements = check_achievements(data)
        if new_achievements:
            save_data(data)
            for ach in new_achievements:
                display_achievement_unlocked(ach)
    else:
        display_shop_error(result["message"])


@cli.group()
def daily():
    """デイリーミッションを確認・報酬を受け取る"""
    pass


@daily.command("list")
def daily_list():
    """デイリーミッション一覧を表示する"""
    data = load_data()
    daily_status = get_daily_status(data)
    display_daily_missions(daily_status)


@daily.command("claim")
@click.argument("mission_id")
def daily_claim(mission_id: str):
    """ミッション報酬を受け取る"""
    data = load_data()
    result = claim_daily_reward(data, mission_id)
    
    if result["success"]:
        save_data(data)
        display_daily_reward_claimed(result["reward"])
        
        # 実績チェック
        new_achievements = check_achievements(data)
        if new_achievements:
            save_data(data)
            for ach in new_achievements:
                display_achievement_unlocked(ach)
    else:
        console.print(f"[red][SG][/red] {result['message']}")


@cli.command()
def achievement():
    """実績一覧を表示する"""
    data = load_data()
    
    # 実績チェック（新規達成があれば表示）
    new_achievements = check_achievements(data)
    if new_achievements:
        save_data(data)
        for ach in new_achievements:
            display_achievement_unlocked(ach)
    
    # 全実績表示
    achievements = get_achievements_status(data)
    display_achievements(achievements)


def main():
    """エントリーポイント"""
    cli()


if __name__ == "__main__":
    main()

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
    console
)
from .game_logic import (
    process_command, feed_pet, pull_gacha, check_login_bonus
)
from .config import APP_NAME, VERSION


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


def main():
    """エントリーポイント"""
    cli()


if __name__ == "__main__":
    main()

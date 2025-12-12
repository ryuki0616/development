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
from rich.table import Table
from rich.panel import Panel
from rich import box


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


@cli.command("help")
@click.argument("command_name", required=False)
def help_command(command_name: Optional[str]):
    """コマンドの説明を表示する"""
    
    commands = {
        "status": {
            "usage": "sg status",
            "description": "ペットの現在のステータスを表示します",
            "details": [
                "ペットのASCIIアート、名前、レベル、経験値、満腹度を表示",
                "所持品（エサ、チケット、破片、コイン）を確認",
                "統計情報（総コマンド数、連続ログイン）を表示"
            ]
        },
        "feed": {
            "usage": "sg feed",
            "description": "ペットにエサをあげます",
            "details": [
                "エサを1個消費",
                "満腹度 +20%（最大100%）",
                "経験値 +10（ブースト中は +20）",
                "レベルアップ時にチケット獲得の可能性あり"
            ]
        },
        "gacha": {
            "usage": "sg gacha",
            "description": "ガチャを回してアイテムを獲得します",
            "details": [
                "チケットを1枚消費",
                "SSR (1%): 特殊スキン、レア称号",
                "SR (9%): 色違いスキン",
                "R (90%): 豆知識、ハズレの石"
            ]
        },
        "collection": {
            "usage": "sg collection",
            "description": "コレクション一覧を表示します",
            "details": [
                "所持しているスキンの一覧",
                "獲得した称号・アイテムの一覧",
                "コレクション達成率を表示"
            ]
        },
        "skin": {
            "usage": "sg skin [スキンID]",
            "description": "スキンを変更または一覧表示します",
            "details": [
                "引数なし: 所持スキン一覧を表示",
                "スキンID指定: そのスキンに変更",
                "例: sg skin skin_blue_cat"
            ]
        },
        "stats": {
            "usage": "sg stats",
            "description": "詳細な統計情報を表示します",
            "details": [
                "コマンド統計（総数、次のドロップまで）",
                "ペット統計（レベル、経験値、エサやり回数）",
                "ガチャ統計（回数、SSR獲得数）",
                "ログイン統計（連続日数、最大記録）"
            ]
        },
        "shop": {
            "usage": "sg shop list / sg shop buy <商品ID>",
            "description": "ショップでアイテムを購入します",
            "details": [
                "sg shop list: 商品一覧を表示",
                "sg shop buy <ID>: コインで商品を購入",
                "商品: エサパック、チケット、経験値ブースト"
            ]
        },
        "daily": {
            "usage": "sg daily list / sg daily claim <ミッションID>",
            "description": "デイリーミッションを確認・報酬受取",
            "details": [
                "sg daily list: ミッション一覧と進捗を表示",
                "sg daily claim <ID>: 完了したミッションの報酬を受取",
                "毎日0時にリセット"
            ]
        },
        "achievement": {
            "usage": "sg achievement",
            "description": "実績一覧を表示します",
            "details": [
                "達成済み・未達成の実績を一覧表示",
                "各実績の進捗状況を確認",
                "達成時に自動で報酬を獲得"
            ]
        },
        "rename": {
            "usage": "sg rename <新しい名前>",
            "description": "ペットの名前を変更します",
            "details": [
                "1〜20文字で指定",
                "例: sg rename ニャンコ"
            ]
        },
        "reset": {
            "usage": "sg reset",
            "description": "ゲームデータをリセットします",
            "details": [
                "すべてのデータが初期化されます",
                "確認プロンプトが表示されます"
            ]
        },
        "help": {
            "usage": "sg help [コマンド名]",
            "description": "コマンドの説明を表示します",
            "details": [
                "引数なし: 全コマンド一覧を表示",
                "コマンド名指定: そのコマンドの詳細を表示"
            ]
        }
    }
    
    if command_name:
        # 特定のコマンドの詳細表示
        if command_name in commands:
            cmd = commands[command_name]
            console.print()
            console.print(Panel(
                f"[bold cyan]{cmd['usage']}[/bold cyan]",
                title=f"📖 {command_name}",
                border_style="cyan"
            ))
            console.print(f"\n[bold]説明:[/bold] {cmd['description']}\n")
            console.print("[bold]詳細:[/bold]")
            for detail in cmd["details"]:
                console.print(f"  • {detail}")
            console.print()
        else:
            console.print(f"[red][SG][/red] コマンド '{command_name}' が見つかりません。")
            console.print("     'sg help' で全コマンド一覧を確認してください。")
    else:
        # 全コマンド一覧表示
        console.print()
        console.print(Panel(
            "[bold]Shell-Gotchi コマンドヘルプ[/bold]\n"
            "[dim]ターミナルでペットを育成しよう！[/dim]",
            border_style="blue"
        ))
        
        # 基本コマンド
        console.print("\n[bold yellow]🎮 基本コマンド[/bold yellow]")
        table1 = Table(box=box.SIMPLE)
        table1.add_column("コマンド", style="cyan")
        table1.add_column("説明")
        table1.add_row("sg status", "ペットのステータスを表示")
        table1.add_row("sg feed", "ペットにエサをあげる")
        table1.add_row("sg gacha", "ガチャを回す")
        table1.add_row("sg collection", "コレクション一覧")
        console.print(table1)
        
        # カスタマイズ
        console.print("\n[bold yellow]🎨 カスタマイズ[/bold yellow]")
        table2 = Table(box=box.SIMPLE)
        table2.add_column("コマンド", style="cyan")
        table2.add_column("説明")
        table2.add_row("sg skin [ID]", "スキン変更・一覧表示")
        table2.add_row("sg rename <名前>", "ペットの名前を変更")
        console.print(table2)
        
        # 情報・統計
        console.print("\n[bold yellow]📊 情報・統計[/bold yellow]")
        table3 = Table(box=box.SIMPLE)
        table3.add_column("コマンド", style="cyan")
        table3.add_column("説明")
        table3.add_row("sg stats", "詳細な統計情報")
        table3.add_row("sg achievement", "実績一覧")
        console.print(table3)
        
        # ショップ・ミッション
        console.print("\n[bold yellow]🏪 ショップ・ミッション[/bold yellow]")
        table4 = Table(box=box.SIMPLE)
        table4.add_column("コマンド", style="cyan")
        table4.add_column("説明")
        table4.add_row("sg shop list", "ショップ商品一覧")
        table4.add_row("sg shop buy <ID>", "商品を購入")
        table4.add_row("sg daily list", "デイリーミッション一覧")
        table4.add_row("sg daily claim <ID>", "報酬を受け取る")
        console.print(table4)
        
        # その他
        console.print("\n[bold yellow]⚙️ その他[/bold yellow]")
        table5 = Table(box=box.SIMPLE)
        table5.add_column("コマンド", style="cyan")
        table5.add_column("説明")
        table5.add_row("sg help [コマンド]", "ヘルプを表示")
        table5.add_row("sg reset", "データをリセット")
        table5.add_row("sg --version", "バージョン表示")
        console.print(table5)
        
        console.print("\n[dim]詳細を見るには: sg help <コマンド名>[/dim]")
        console.print()


def main():
    """エントリーポイント"""
    cli()


if __name__ == "__main__":
    main()

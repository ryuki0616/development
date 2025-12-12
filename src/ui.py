"""
Shell-Gotchi Richを使った表示処理
"""
import time
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn
from rich.align import Align
from rich import box

from .config import (
    APP_NAME, VERSION, MAX_HUNGER, LEVEL_THRESHOLDS,
    GACHA_ITEMS
)
from .assets import (
    LOGO, WELCOME_BANNER, get_pet_art, get_skin_name, get_skin_color,
    PET_SKINS, GACHA_ANIMATION_FRAMES, GACHA_RESULT_FRAMES,
    FOOD_ICON, TICKET_ICON, FRAGMENT_ICON, LEVEL_UP_ICON,
    HUNGER_FULL, HUNGER_LOW, HUNGER_EMPTY
)

console = Console()


def display_status(data: Dict[str, Any]) -> None:
    """ペットのステータスを表示する"""
    pet = data["pet"]
    user = data["user"]
    stats = data["stats"]
    
    # ペットのASCIIアート
    pet_art = get_pet_art(pet["skin_id"], pet["hunger"])
    skin_color = get_skin_color(pet["skin_id"])
    
    # 満腹度バー
    hunger_bar = create_hunger_bar(pet["hunger"])
    
    # 経験値バー
    exp_bar = create_exp_bar(pet["level"], pet["exp"])
    
    # ペット情報テーブル
    pet_table = Table(show_header=False, box=None, padding=(0, 1))
    pet_table.add_column("Key", style="cyan")
    pet_table.add_column("Value")
    
    pet_table.add_row("名前", f"[bold]{pet['name']}[/bold]")
    pet_table.add_row("スキン", get_skin_name(pet["skin_id"]))
    pet_table.add_row("レベル", f"[yellow]Lv.{pet['level']}[/yellow]")
    pet_table.add_row("経験値", exp_bar)
    pet_table.add_row("満腹度", hunger_bar)
    
    # 所持品テーブル
    items_table = Table(show_header=False, box=None, padding=(0, 1))
    items_table.add_column("Key", style="cyan")
    items_table.add_column("Value")
    
    items_table.add_row(f"{FOOD_ICON} エサ", f"[green]{user['food']}[/green] 個")
    items_table.add_row(f"{TICKET_ICON} チケット", f"[magenta]{user['tickets']}[/magenta] 枚")
    items_table.add_row(f"{FRAGMENT_ICON} 破片", f"[blue]{user['ticket_fragments']}/7[/blue]")
    
    # 統計テーブル
    stats_table = Table(show_header=False, box=None, padding=(0, 1))
    stats_table.add_column("Key", style="dim")
    stats_table.add_column("Value", style="dim")
    
    stats_table.add_row("総コマンド数", f"{stats['total_commands']:,}")
    stats_table.add_row("連続ログイン", f"{user['login_streak']} 日")
    
    # ASCIIアートパネル
    art_panel = Panel(
        Align.center(Text(pet_art, style=skin_color)),
        title=f"[bold]{pet['name']}[/bold]",
        border_style="green" if pet["hunger"] > 50 else "yellow" if pet["hunger"] > 20 else "red"
    )
    
    # メインパネル
    main_content = Table.grid(padding=1)
    main_content.add_column()
    main_content.add_column()
    
    # 左側：ペット情報
    left_content = Table.grid()
    left_content.add_row(art_panel)
    left_content.add_row(pet_table)
    
    # 右側：所持品と統計
    right_content = Table.grid()
    right_content.add_row(Panel(items_table, title="所持品", border_style="cyan"))
    right_content.add_row(Panel(stats_table, title="統計", border_style="dim"))
    
    main_content.add_row(left_content, right_content)
    
    console.print()
    console.print(Panel(
        main_content,
        title=f"[bold blue]{APP_NAME}[/bold blue] v{VERSION}",
        border_style="blue",
        box=box.DOUBLE
    ))
    console.print()


def create_hunger_bar(hunger: float) -> str:
    """満腹度バーを作成する"""
    bar_length = 20
    filled = int(hunger / MAX_HUNGER * bar_length)
    empty = bar_length - filled
    
    if hunger > 50:
        color = "green"
    elif hunger > 20:
        color = "yellow"
    else:
        color = "red"
    
    bar = f"[{color}]{HUNGER_FULL * filled}[/{color}][dim]{HUNGER_EMPTY * empty}[/dim]"
    return f"{bar} {hunger:.0f}%"


def create_exp_bar(level: int, exp: int) -> str:
    """経験値バーを作成する"""
    current_threshold = LEVEL_THRESHOLDS.get(level, 0)
    next_threshold = LEVEL_THRESHOLDS.get(level + 1, current_threshold + 500)
    
    exp_in_level = exp - current_threshold
    exp_needed = next_threshold - current_threshold
    
    bar_length = 20
    if exp_needed > 0:
        filled = int(exp_in_level / exp_needed * bar_length)
    else:
        filled = bar_length
    empty = bar_length - filled
    
    bar = f"[cyan]{'█' * filled}[/cyan][dim]{'·' * empty}[/dim]"
    return f"{bar} {exp}/{next_threshold}"


def display_drop_message(food_count: int) -> None:
    """エサドロップ時のメッセージを表示する"""
    console.print(f"[green][SG][/green] {FOOD_ICON} You found a Bit-Food! (Total: {food_count})")


def display_login_bonus(reward_type: str, streak: int) -> None:
    """ログインボーナスを表示する"""
    console.print()
    console.print(Panel(
        Text(LOGO, style="bold cyan"),
        border_style="yellow"
    ))
    console.print(WELCOME_BANNER)
    
    if reward_type == "ticket":
        console.print(f"  ║  {TICKET_ICON} [bold yellow]7日連続ログインボーナス！[/bold yellow]     ║")
        console.print(f"  ║  🎉 ガチャチケット x1 を獲得！        ║")
    else:
        console.print(f"  ║  {FRAGMENT_ICON} [cyan]ログインボーナス！[/cyan]               ║")
        console.print(f"  ║  💫 チケットの破片 x1 を獲得！        ║")
    
    console.print(f"  ║  📅 連続ログイン: {streak} 日                 ║")
    console.print("  ╚══════════════════════════════════════════════════════════╝")
    console.print()


def display_feed_result(pet_name: str, hunger: float, exp_gained: int, level_up: bool = False, new_level: int = 0) -> None:
    """エサやり結果を表示する"""
    console.print()
    console.print(f"[green][SG][/green] {FOOD_ICON} {pet_name}にエサをあげました！")
    console.print(f"     満腹度: [green]+20%[/green] → {hunger:.0f}%")
    console.print(f"     経験値: [cyan]+{exp_gained}[/cyan]")
    
    if level_up:
        console.print()
        console.print(Panel(
            f"{LEVEL_UP_ICON} [bold yellow]レベルアップ！[/bold yellow]\n"
            f"   {pet_name} は Lv.{new_level} になりました！",
            border_style="yellow"
        ))
    console.print()


def display_no_food() -> None:
    """エサがない場合のメッセージを表示する"""
    console.print("[red][SG][/red] エサがありません！コマンドを実行してエサを集めましょう。")


def display_hunger_full() -> None:
    """満腹度がすでに最大の場合のメッセージを表示する"""
    console.print("[yellow][SG][/yellow] ペットはもうお腹いっぱいです！")


def display_gacha_animation() -> None:
    """ガチャ演出を表示する"""
    console.clear()
    
    # アニメーションフレーム
    for frame in GACHA_ANIMATION_FRAMES:
        console.clear()
        console.print(Align.center(Text(frame, style="bold cyan")))
        time.sleep(0.3)
    
    # ドラムロール風の演出
    for _ in range(5):
        console.clear()
        console.print(Align.center(Text("🎰 ガチャを回しています... 🎰", style="bold yellow")))
        time.sleep(0.1)
        console.clear()
        console.print(Align.center(Text("🎰 ガチャを回しています... 🎰", style="bold magenta")))
        time.sleep(0.1)


def display_gacha_result(rarity: str, item: Dict[str, Any]) -> None:
    """ガチャ結果を表示する"""
    result_frame = GACHA_RESULT_FRAMES.get(rarity, GACHA_RESULT_FRAMES["R"])
    
    # レアリティに応じた色
    colors = {"SSR": "bold yellow", "SR": "bold magenta", "R": "cyan"}
    color = colors.get(rarity, "white")
    
    console.print()
    console.print(Text(result_frame, style=color))
    console.print(f"║  獲得: [bold]{item['name']}[/bold]")
    console.print(f"║  タイプ: {item['type']}")
    console.print("╚══════════════════════════════════════╝")
    
    # SSRの場合は特別な演出
    if rarity == "SSR":
        console.print()
        console.print(Align.center(Text("🎊 おめでとうございます！ 🎊", style="bold yellow")))
    
    console.print()


def display_no_tickets() -> None:
    """チケットがない場合のメッセージを表示する"""
    console.print("[red][SG][/red] ガチャチケットがありません！")
    console.print("     レベルアップやログインボーナスでチケットを獲得しましょう。")


def display_collection(collection: List[str], all_items: Dict[str, Any] = None) -> None:
    """コレクション一覧を表示する"""
    console.print()
    
    # スキンテーブル
    skin_table = Table(title="🎨 スキンコレクション", box=box.ROUNDED)
    skin_table.add_column("ID", style="dim")
    skin_table.add_column("名前")
    skin_table.add_column("レアリティ")
    skin_table.add_column("状態")
    
    for skin_id, skin_data in PET_SKINS.items():
        owned = "✅ 所持" if skin_id in collection else "❌ 未所持"
        rarity = skin_data.get("rarity", "N")
        rarity_style = {"SSR": "bold yellow", "SR": "magenta", "N": "white"}.get(rarity, "white")
        
        skin_table.add_row(
            skin_id,
            skin_data["name"],
            f"[{rarity_style}]{rarity}[/{rarity_style}]",
            owned if skin_id in collection else f"[dim]{owned}[/dim]"
        )
    
    console.print(skin_table)
    
    # アイテム/称号テーブル
    item_table = Table(title="📦 アイテム・称号", box=box.ROUNDED)
    item_table.add_column("名前")
    item_table.add_column("タイプ")
    item_table.add_column("状態")
    
    # 全ガチャアイテムをチェック
    for rarity, items in GACHA_ITEMS.items():
        for item in items:
            if item["type"] in ["tip", "junk"]:
                continue  # 豆知識とハズレは表示しない
            owned = "✅ 所持" if item["id"] in collection else "❌ 未所持"
            item_table.add_row(
                item["name"],
                item["type"],
                owned if item["id"] in collection else f"[dim]{owned}[/dim]"
            )
    
    console.print()
    console.print(item_table)
    console.print()
    
    # コレクション達成率
    total_collectibles = len(PET_SKINS) + sum(
        1 for items in GACHA_ITEMS.values() 
        for item in items 
        if item["type"] not in ["tip", "junk"]
    )
    owned_count = len([c for c in collection if c in PET_SKINS or any(
        item["id"] == c for items in GACHA_ITEMS.values() for item in items if item["type"] not in ["tip", "junk"]
    )])
    
    console.print(f"コレクション達成率: [cyan]{owned_count}/{total_collectibles}[/cyan]")
    console.print()


def display_ticket_reward(tickets: int) -> None:
    """チケット獲得を表示する"""
    console.print(f"     {TICKET_ICON} ガチャチケット x{tickets} を獲得！")


def display_name_changed(old_name: str, new_name: str) -> None:
    """名前変更を表示する"""
    console.print(f"[green][SG][/green] ペットの名前を [bold]{old_name}[/bold] から [bold]{new_name}[/bold] に変更しました！")

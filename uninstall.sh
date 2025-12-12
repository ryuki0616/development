#!/bin/bash
# Shell-Gotchi アンインストールスクリプト
# このスクリプトはShell-Gotchiのデータとフック設定を削除します

set -e

echo "=========================================="
echo "  Shell-Gotchi アンインストーラー"
echo "=========================================="
echo ""

# データディレクトリのパス
DATA_DIR="$HOME/.local/share/shell-gotchi"

# 確認プロンプト
read -p "本当にShell-Gotchiをアンインストールしますか？ (y/N): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "キャンセルしました。"
    exit 0
fi

echo ""
echo "🗑️  アンインストール中..."

# 1. セーブデータの削除
if [ -d "$DATA_DIR" ]; then
    echo "  - セーブデータを削除: $DATA_DIR"
    rm -rf "$DATA_DIR"
    echo "    ✅ 完了"
else
    echo "  - セーブデータなし（スキップ）"
fi

# 2. .bashrc からフックを削除
BASHRC="$HOME/.bashrc"
if [ -f "$BASHRC" ] && grep -q "shell_hook.sh" "$BASHRC"; then
    echo "  - .bashrc からフックを削除"
    # shell_hook.sh を含む行を削除
    sed -i '/shell-gotchi.*shell_hook\.sh/d' "$BASHRC"
    sed -i '/shell_hook\.sh/d' "$BASHRC"
    echo "    ✅ 完了"
else
    echo "  - .bashrc にフックなし（スキップ）"
fi

# 3. .zshrc からフックを削除
ZSHRC="$HOME/.zshrc"
if [ -f "$ZSHRC" ] && grep -q "shell_hook.sh" "$ZSHRC"; then
    echo "  - .zshrc からフックを削除"
    sed -i '/shell-gotchi.*shell_hook\.sh/d' "$ZSHRC"
    sed -i '/shell_hook\.sh/d' "$ZSHRC"
    echo "    ✅ 完了"
else
    echo "  - .zshrc にフックなし（スキップ）"
fi

echo ""
echo "=========================================="
echo "  アンインストール完了！"
echo "=========================================="
echo ""
echo "以下が削除されました："
echo "  • セーブデータ (~/.local/share/shell-gotchi/)"
echo "  • シェルフック設定 (.bashrc / .zshrc)"
echo ""
echo "アプリ本体を削除するには、このフォルダを手動で削除してください。"
echo "シェルを再起動するか、'source ~/.bashrc' を実行してください。"
echo ""

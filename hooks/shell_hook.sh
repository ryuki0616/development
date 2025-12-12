#!/bin/bash
# Shell-Gotchi シェルフック
# このスクリプトを .bashrc または .zshrc に source して使用する
#
# 使い方:
#   echo 'source /path/to/shell-gotchi/hooks/shell_hook.sh' >> ~/.bashrc
#   echo 'source /path/to/shell-gotchi/hooks/shell_hook.sh' >> ~/.zshrc

# Shell-Gotchi のパス（このスクリプトからの相対パス）
SHELL_GOTCHI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)"

# Python実行パス（必要に応じて変更）
PYTHON_CMD="${PYTHON_CMD:-python3}"

# 最後に実行したコマンドを保存する変数
_SG_LAST_COMMAND=""

# スパム防止: 連続した空コマンドをカウント
_SG_EMPTY_COUNT=0
_SG_MAX_EMPTY=3

# Shell-Gotchi フック関数
_shell_gotchi_hook() {
    local last_cmd="$1"
    
    # 空コマンドチェック
    if [[ -z "${last_cmd// }" ]]; then
        ((_SG_EMPTY_COUNT++))
        if [[ $_SG_EMPTY_COUNT -ge $_SG_MAX_EMPTY ]]; then
            return 0
        fi
        return 0
    fi
    
    # 空コマンドカウントをリセット
    _SG_EMPTY_COUNT=0
    
    # 同じコマンドの連続実行を検出（スパム防止）
    if [[ "$last_cmd" == "$_SG_LAST_COMMAND" ]]; then
        # 同じコマンドでもカウントはする（連続は許可）
        :
    fi
    _SG_LAST_COMMAND="$last_cmd"
    
    # Shell-Gotchi の sg コマンド自体は除外
    if [[ "$last_cmd" == sg* ]] || [[ "$last_cmd" == "python"*"main.py"* ]]; then
        return 0
    fi
    
    # Shell-Gotchi フック呼び出し
    # バックグラウンドで実行して遅延を最小化
    (
        cd "$SHELL_GOTCHI_DIR" && \
        $PYTHON_CMD -m src.main hook --trigger --command "$last_cmd" 2>/dev/null
    )
}

# Bash用フック
if [[ -n "$BASH_VERSION" ]]; then
    # 既存の PROMPT_COMMAND を保存
    _SG_OLD_PROMPT_COMMAND="${PROMPT_COMMAND:-}"
    
    # 最後のコマンドを取得するための DEBUG トラップ
    _sg_save_command() {
        _SG_CURRENT_COMMAND="$(HISTTIMEFORMAT= history 1 | sed 's/^[ ]*[0-9]*[ ]*//')"
    }
    trap '_sg_save_command' DEBUG
    
    # PROMPT_COMMAND にフックを追加
    _sg_prompt_command() {
        local exit_code=$?
        
        # 前のコマンドをフックに渡す
        _shell_gotchi_hook "$_SG_CURRENT_COMMAND"
        
        # 既存の PROMPT_COMMAND を実行
        if [[ -n "$_SG_OLD_PROMPT_COMMAND" ]]; then
            eval "$_SG_OLD_PROMPT_COMMAND"
        fi
        
        return $exit_code
    }
    
    PROMPT_COMMAND="_sg_prompt_command"
fi

# Zsh用フック
if [[ -n "$ZSH_VERSION" ]]; then
    # precmd フックを追加
    _sg_precmd() {
        local last_cmd="$(fc -ln -1 2>/dev/null | sed 's/^[ ]*//')"
        _shell_gotchi_hook "$last_cmd"
    }
    
    # precmd_functions 配列にフックを追加
    if [[ -z "${precmd_functions[(r)_sg_precmd]}" ]]; then
        precmd_functions+=(_sg_precmd)
    fi
fi

# sg コマンドのエイリアス
sg() {
    cd "$SHELL_GOTCHI_DIR" && $PYTHON_CMD -m src.main "$@"
}

# 初期化メッセージ（オプション）
if [[ "${SG_QUIET:-}" != "1" ]]; then
    echo "[Shell-Gotchi] 🎮 Ready! Type 'sg status' to check your pet."
fi

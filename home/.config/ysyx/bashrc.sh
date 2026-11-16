# Source this from the end of the NEW machine's existing ~/.bashrc.
# Keep Red Hat's original ~/.bashrc and /etc/bashrc initialization.
export NEMU_HOME="$HOME/ysyx/ysyx-workbench/nemu"
export AM_HOME="$HOME/ysyx/ysyx-workbench/abstract-machine"
export NPC_HOME="$HOME/ysyx/ysyx-workbench/npc"
export NVBOARD_HOME="$HOME/ysyx/ysyx-workbench/nvboard"
if [ -d "$HOME/.local/bin" ]; then
    case ":$PATH:" in
        *":$HOME/.local/bin:"*) ;;
        *) export PATH="$HOME/.local/bin:$PATH" ;;
    esac
fi
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
# Tool executable paths must be checked on Red Hat 8 before adding more aliases.

# MONODESK OS — Default Shell Environment Profile
# Clean dot-matrix prompt, sensible aliases, high legibility

# Don't do anything for non-interactive shells
[[ $- != *i* ]] && return

# Shell history configuration
HISTCONTROL=ignoreboth
HISTSIZE=5000
HISTFILESIZE=10000
shopt -s histappend
shopt -s checkwinsize

# High-contrast monochrome dot-matrix style prompt
# Shows: [user@host directory] $
PS1='\[\033[38;5;244m\][\[\033[38;5;255m\]\u@monodesk\[\033[38;5;244m\]:\[\033[38;5;196m\]\w\[\033[38;5;244m\]]\[\033[00m\]\$ '

# Aliases
alias ls='ls --color=auto'
alias ll='ls -alF --color=auto'
alias la='ls -A --color=auto'
alias grep='grep --color=auto'
alias update='sudo apt-get update && sudo apt-get upgrade'
alias hwinfo='monodesk-hardware-report'
alias profile='monodesk-profile-ctl'

# Fast command completion
if [ -f /etc/bash_completion ] && ! shopt -oq posix; then
    . /etc/bash_completion
fi

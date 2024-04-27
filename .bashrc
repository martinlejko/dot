#PS1='\[\e[33m\][\u@\h \W]\$\[\e[0m\] '
export CLICOLOR=1

#Prompt
parse_git_branch() {
	git branch 2>/dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/ (\1)/'
}

PS1='\[\e[1;32m\]\u@\h\[\e[0m\]:\[\e[1;34m\]\w\[\e[1;31m\]$(parse_git_branch)\[\e[0m\] \$ '

#Bash completions@2
export BASH_COMPLETION_COMPAT_DIR="/usr/local/etc/bash_completion.d"
[[ -r "/usr/local/etc/profile.d/bash_completion.sh" ]] && . "/usr/local/etc/profile.d/bash_completion.sh"

# Set to superior editing mode
set -o vi

#the fuck
eval "$(thefuck --alias)"

# env variables
export VISUAL=nvim
export EDITOR=nvim

# fzf aliases
# use fp to do a fzf search and preview the files
alias fp="fzf --preview 'bat --style=numbers --color=always --line-range :500 {}'"
# search for a file with fzf and open it in vim
alias vf='v $(fp)'

export BROWSER="firefox"

alias v=nvim

# ls
alias ls='ls --color=auto'
alias ll='ls -la'
alias la='ls -lathr'

# cd
alias ..='cd ../'
alias ...='cd ../../'
alias github='cd ~/Desktop/github/'
alias nastroje='cd ~/Desktop/github/LS2024/NSWI154-Nastroje-pro-vyvoj/'
alias paralelne='cd ~/Desktop/github/LS2024/para/NPRG042-Parallel-Prog/'
alias csharp='cd ~/Desktop/github/LS2024/NPRG038-Adv-CSharp/'


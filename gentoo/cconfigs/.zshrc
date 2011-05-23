#!/bin/zsh

zhome=~/.cconf/zsh
#source some files
source $zhome/opts
source $zhome/gitprompt
source $zhome/batt
source $zhome/functions
source $zhome/alias
source $zhome/completion
source $zhome/git
#opts

# Enable ls colors
autoload colors; colors;
export LSCOLORS="Gxfxcxdxbxegedabagacad"
# Find the option for using colors in ls, depending on the version: Linux or BSD
ls --color -d . &>/dev/null 2>&1 && alias ls='ls --color=tty' || alias ls='ls -G'
# prompt
autoload -U promptinit
promptinit
prompt_char() {
    if [[ -d .git ]]; then
	echo "%F{magenta}±%f" || return
    else
	echo "%F{magenta}ø%f" || return
    fi

}
custom_prompt_info() {
    if [[ -d .git ]]; then
	echo  "$(git_prompt_info)%F{magenta}← →%f[$(git_prompt_status)]" 
    fi
   
}
command_succes() {
if [ $? = 0 ]
then 
	echo "%F{yellow}^_^%f"
else 
	echo "%F{red}O_O%f"
fi
}

PROMPT='┌[%F{grey}%3c%f] $(custom_prompt_info) 
└[ %F{green}%#%f $(prompt_char) ]>> '
RPROMPT='$(command_succes) $(batt_prompt_perc)$(bat_prompt_acstt) '


ZSH_THEME_GIT_PROMPT_PREFIX="[%F{yellow}"
ZSH_THEME_GIT_PROMPT_SUFFIX="%f]"
ZSH_THEME_GIT_PROMPT_DIRTY=" %F{red}*%f"
ZSH_THEME_GIT_PROMPT_CLEAN=" %F{green}°%f"

ZSH_THEME_GIT_PROMPT_ADDED="%F{green}+%f"
ZSH_THEME_GIT_PROMPT_MODIFIED="%F{blue}*%f"
ZSH_THEME_GIT_PROMPT_DELETED="%F{red}x%f"
ZSH_THEME_GIT_PROMPT_RENAMED="%F{magenta}->%f"
ZSH_THEME_GIT_PROMPT_UNMERGED="%F{yellow}═%f"
ZSH_THEME_GIT_PROMPT_UNTRACKED="%F{cyan}?%f"

ZSH_THEME_ACBAT_PROMPT_CHARGED="%F{green}°%"
ZSH_THEME_ACBAT_PROMPT_CHARGING="%F{cyan}+%"
ZSH_THEME_ACBAT_PROMPT_DISCHARGING="%F{yellow}-%"

ZSH_THEME_BATPERC_PROMPT_PREFIX="%F{yellow}⚡% :"
#ZSH_THEME_BATPERC_PROMPT_SUFFIX=""
ZSH_THEME_BATPERC_PROMPT_CLRLESS25PRC="red"
ZSH_THEME_BATPERC_PROMPT_CLRMORE80PRC="cyan"
ZSH_THEME_BATPERC_PROMPT_CLR40TO80PRC="green"
ZSH_THEME_BATPERC_PROMPT_CLR25TO40PRC="yellow"

#exports
##pager
export PAGER=less
export LC_CTYPE=en_US.UTF-8
export GREP_OPTIONS='--color=auto'
export GREP_COLOR='1;32'
export vblank_mode=0
## Command history configuration
HISTFILE=$HOME/.zsh_history
HISTSIZE=10000
SAVEHIST=10000


eval "$(/opt/homebrew/bin/brew shellenv)"
if [ -r ~/.bashrc ]; then
	source ~/.bashrc
fi
export BASH_SILENCE_DEPRECATION_WARNING=1

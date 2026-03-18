_iterm_autoconfig_script="${0:h}/apply_iterm_config.py"

_iterm_start_daemon() {
  [[ -S "$HOME/.iterm-autoconfig.sock" ]] || \
    python3 "$_iterm_autoconfig_script" --daemon &!
}

_iterm_apply_config() {
  local config_file=".iterm.json"
  local dir="$PWD"
  local config_dir=""

  while [[ "$dir" != "/" ]]; do
    if [[ -f "$dir/$config_file" ]]; then
      config_dir="$dir"
      break
    fi
    dir="${dir:h}"
  done

  if [[ -S "$HOME/.iterm-autoconfig.sock" ]]; then
    printf "%s\n" "$config_dir" | nc -U "$HOME/.iterm-autoconfig.sock" 2>/dev/null || {
      _iterm_start_daemon
      python3 "$_iterm_autoconfig_script" "$config_dir"
    }
  else
    python3 "$_iterm_autoconfig_script" "$config_dir"
  fi
}

_iterm_init() {
  _iterm_start_daemon
  add-zsh-hook -d precmd _iterm_init
}

autoload -U add-zsh-hook
add-zsh-hook precmd _iterm_init
add-zsh-hook chpwd _iterm_apply_config

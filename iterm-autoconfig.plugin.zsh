_iterm_autoconfig_script="${0:h}/apply_iterm_config.py"

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

  python3 "$_iterm_autoconfig_script" "$config_dir" &!
}

autoload -U add-zsh-hook
add-zsh-hook chpwd _iterm_apply_config

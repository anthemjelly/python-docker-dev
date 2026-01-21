
alias ruff_check="ruff check --no-cache"
alias ruff_format="ruff format --no-cache"
ruff() {
  if [ "$1" = "check" ] || [ "$1" = "format" ]; then
    command ruff "$@" --no-cache
  else
    command ruff "$@"
  fi
}

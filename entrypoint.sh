#!/bin/ash

# No arguments passed
if [ $# -eq 0 ]; then
  # Run in interactive mode, start ash
  if [ -t 0 ]; then
    exec ash
  # Not run in interactive mode, run cron
  else
    crond -f
  fi
# Arguments passed, run in single-execution mode
else
  /usr/local/bin/python /app/main.py "$@"
fi
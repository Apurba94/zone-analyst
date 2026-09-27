#!/usr/bin/env sh
# Serve the website at http://localhost:8000 (macOS / Linux). Ctrl+C stops it.
cd "$(dirname "$0")/website" || exit 1
echo "Zone Analyst: http://localhost:8000  (Ctrl+C to stop)"
( sleep 1
  if command -v open >/dev/null 2>&1; then open http://localhost:8000/index.html
  elif command -v xdg-open >/dev/null 2>&1; then xdg-open http://localhost:8000/index.html
  fi ) >/dev/null 2>&1 &
exec python3 -m http.server 8000 --bind 127.0.0.1

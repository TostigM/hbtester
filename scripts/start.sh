#!/usr/bin/env bash
set -e

echo "=== START DIAGNOSTICS ==="
echo "--- Working directory ---"
pwd
echo "--- Directory contents ---"
ls -la
echo "--- .venv exists? ---"
ls -la .venv/bin/ 2>/dev/null || echo ".venv/bin/ NOT FOUND"
echo "--- gunicorn binary ---"
ls -la .venv/bin/gunicorn 2>/dev/null || echo ".venv/bin/gunicorn NOT FOUND"
echo "--- gunicorn shebang ---"
head -1 .venv/bin/gunicorn 2>/dev/null || echo "cannot read .venv/bin/gunicorn"
echo "--- Python in shebang resolves to ---"
SHEBANG=$(head -1 .venv/bin/gunicorn 2>/dev/null | sed 's/#!//')
echo "Shebang: $SHEBANG"
ls -la "$SHEBANG" 2>/dev/null || echo "Shebang interpreter NOT FOUND at $SHEBANG"
echo "--- Env vars ---"
echo "PORT=$PORT"
echo "PYTHONPATH=$PYTHONPATH"
echo "CONTENT_DIR=$CONTENT_DIR"
echo "BASELINES_DIR=$BASELINES_DIR"

echo ""
echo "=== STARTING GUNICORN ==="
exec .venv/bin/gunicorn api.app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120

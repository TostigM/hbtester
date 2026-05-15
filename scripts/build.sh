#!/usr/bin/env bash
set -e

echo "=== BUILD DIAGNOSTICS ==="
echo "--- System info ---"
uname -a
echo "--- PATH ---"
echo "$PATH"
echo "--- Python binaries ---"
which python  2>/dev/null && python  --version || echo "python:  not found"
which python3 2>/dev/null && python3 --version || echo "python3: not found"
ls /usr/bin/python* 2>/dev/null || echo "no /usr/bin/python*"
ls /usr/local/bin/python* 2>/dev/null || echo "no /usr/local/bin/python*"
echo "--- pip binaries ---"
which pip  2>/dev/null && pip  --version || echo "pip:  not found"
which pip3 2>/dev/null && pip3 --version || echo "pip3: not found"
ls /usr/bin/pip* 2>/dev/null || echo "no /usr/bin/pip*"
echo "--- Render Python install ---"
ls /opt/render/project/ 2>/dev/null || echo "/opt/render/project/ not found"
find /opt/render -name "python3" -type f 2>/dev/null | head -10 || echo "no python3 found under /opt/render"
find /opt/render -name "pip" -type f 2>/dev/null | head -10 || echo "no pip found under /opt/render"
echo "--- Poetry ---"
ls /opt/render/project/poetry/bin/ 2>/dev/null || echo "poetry bin not at /opt/render/project/poetry/bin/"
which poetry 2>/dev/null && poetry --version || echo "poetry: not in PATH"

echo ""
echo "=== CREATING VENV ==="
/usr/bin/python3 -m venv .venv
echo "Venv created. Contents of .venv/bin:"
ls -la .venv/bin/

echo ""
echo "=== INSTALLING REQUIREMENTS ==="
.venv/bin/pip install -r requirements.txt

echo ""
echo "=== POST-INSTALL CHECK ==="
echo "--- gunicorn location ---"
.venv/bin/pip show gunicorn
echo "--- gunicorn binary ---"
ls -la .venv/bin/gunicorn
echo "--- gunicorn shebang ---"
head -1 .venv/bin/gunicorn
echo "--- python symlink in venv ---"
ls -la .venv/bin/python*
echo "=== BUILD COMPLETE ==="

#!/usr/bin/env bash
set -u

failed=0

check_cmd() {
  local name="$1"
  local required="$2"
  shift 2

  if ! command -v "$name" >/dev/null 2>&1; then
    if [ "$required" = "required" ]; then
      echo "[FAIL] $name: not found"
      failed=$((failed + 1))
    else
      echo "[OPTIONAL] $name: not found"
    fi
    return
  fi

  local output
  output=$("$name" "$@" 2>&1 | head -n 1)
  echo "[OK] $name: $output"
}

echo "=== Agent Environment Preflight ==="
echo "PATH=$PATH"
echo

check_cmd git required --version

if command -v python3 >/dev/null 2>&1; then
  echo "[OK] python3: $(python3 --version 2>&1 | head -n 1)"
  if python3 -m pip --version >/dev/null 2>&1; then
    echo "[OK] pip: $(python3 -m pip --version 2>&1 | head -n 1)"
  else
    echo "[FAIL] pip: python3 -m pip unavailable"
    failed=$((failed + 1))
  fi
elif command -v python >/dev/null 2>&1; then
  echo "[OK] python: $(python --version 2>&1 | head -n 1)"
  if python -m pip --version >/dev/null 2>&1; then
    echo "[OK] pip: $(python -m pip --version 2>&1 | head -n 1)"
  else
    echo "[FAIL] pip: python -m pip unavailable"
    failed=$((failed + 1))
  fi
else
  echo "[FAIL] python: not found"
  failed=$((failed + 1))
fi

check_cmd node required --version
check_cmd npm required --version
check_cmd curl required --version
check_cmd ssh required -V
check_cmd docker optional --version

echo
echo "=== Git Identity ==="
echo "user.name : $(git config --get user.name 2>/dev/null || true)"
echo "user.email: $(git config --get user.email 2>/dev/null || true)"

echo
echo "=== Package Sources ==="
if command -v npm >/dev/null 2>&1; then
  echo "npm registry: $(npm config get registry 2>/dev/null || true)"
fi
if command -v python3 >/dev/null 2>&1; then
  python3 -m pip config list 2>/dev/null || true
elif command -v python >/dev/null 2>&1; then
  python -m pip config list 2>/dev/null || true
fi

echo
if [ "$failed" -gt 0 ]; then
  echo "Preflight FAILED: $failed required capability/capabilities missing."
  exit 1
fi

echo "Preflight PASSED."
exit 0

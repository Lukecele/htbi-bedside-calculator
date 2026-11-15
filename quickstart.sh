#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

echo ""
echo "=========================================================================="
echo -e "\033[1;33m ⭐ Support Open Science: Please Star the Repository on GitHub!\033[0m"
echo -e "\033[4;34m 👉 https://github.com/Lukecele/htbi-bedside-calculator\033[0m"
echo "=========================================================================="
echo ""
echo "🔬 Launching HTBI Bedside Calculator CLI..."
echo ""

python3 "$DIR/cli.py" "$@"

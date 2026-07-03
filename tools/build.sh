#!/usr/bin/env bash
# Rebuild course.html from the three source parts, then validate it.
set -e
cd "$(dirname "$0")/.."
cat src/part1_shell.html src/content.txt src/part3_engine.html > course.html
node tools/validate.js
echo "Built course.html ($(wc -c < course.html) bytes)"

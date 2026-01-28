#!/bin/bash
# 代码格式化脚本 - 使用 Black 和 Ruff

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "======================================"
echo "格式化代码"
echo "======================================"

echo ""
echo "1. 运行 Black 格式化..."
uv run black backend/ --line-length 100

echo ""
echo "2. 运行 Ruff 修复问题..."
uv run ruff check backend/ --fix

echo ""
echo "3. 运行 Ruff 排序导入..."
uv run ruff check backend/ --select I --fix

echo ""
echo "======================================"
echo "代码格式化完成！"
echo "======================================"

#!/bin/bash
# 代码质量检查脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "======================================"
echo "运行代码质量检查"
echo "======================================"

echo ""
echo "1. 运行 Ruff 进行代码检查..."
uv run ruff check backend/ --fix

echo ""
echo "2. 运行 Black 进行代码格式化..."
uv run black backend/ --line-length 100

echo ""
echo "3. 运行 MyPy 进行类型检查..."
uv run mypy backend/ --ignore-missing-imports

echo ""
echo "======================================"
echo "代码质量检查完成！"
echo "======================================"

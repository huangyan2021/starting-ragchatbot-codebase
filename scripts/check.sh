#!/bin/bash
# 代码检查脚本（不修改文件）

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "======================================"
echo "检查代码质量（只读模式）"
echo "======================================"

echo ""
echo "1. 检查代码风格 (Ruff)..."
uv run ruff check backend/

echo ""
echo "2. 检查代码格式 (Black)..."
uv run black backend/ --check --line-length 100

echo ""
echo "3. 检查类型注解 (MyPy)..."
uv run mypy backend/ --ignore-missing-imports

echo ""
echo "======================================"
echo "代码检查完成！"
echo "======================================"

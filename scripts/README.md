# 代码质量工具使用指南

本项目使用以下工具来保持代码质量和一致性：

## 工具说明

- **Black**: Python 代码自动格式化工具，确保代码风格一致
- **Ruff**: 快速的 Python 代码检查工具，替代 flake8、isort 等多个工具
- **MyPy**: Python 静态类型检查工具

## 配置说明

代码格式化配置位于 `pyproject.toml`：

```toml
[tool.black]
line-length = 100    # 最大行长度为 100 字符
target-version = ["py313"]
```

## 使用方法

### 格式化代码

修改代码后，运行以下命令来自动格式化：

**Linux/macOS:**
```bash
./scripts/format.sh
```

**Windows:**
```cmd
scripts\format.bat
```

### 检查代码（不修改）

在提交代码前，运行检查命令确保代码符合规范：

**Linux/macOS:**
```bash
./scripts/check.sh
```

**Windows:**
```cmd
scripts\check.bat
```

### 完整质量检查

运行所有代码质量工具（格式化 + 检查）：

**Linux/macOS:**
```bash
./scripts/quality.sh
```

**Windows:**
```cmd
scripts\quality.bat
```

## 单独使用各工具

### Black 格式化
```bash
# 格式化代码
uv run black backend/ --line-length 100

# 只检查格式（不修改）
uv run black backend/ --check --line-length 100
```

### Ruff 检查
```bash
# 检查代码问题
uv run ruff check backend/

# 自动修复可修复的问题
uv run ruff check backend/ --fix
```

### MyPy 类型检查
```bash
uv run mypy backend/ --ignore-missing-imports
```

## 开发工作流建议

1. **编写代码**: 正常编写功能代码
2. **格式化**: 提交前运行 `./scripts/format.sh`
3. **检查**: 运行 `./scripts/check.sh` 确保没有问题
4. **提交**: 提交代码

## 预提交钩子（可选）

为了自动在提交前运行代码质量检查，可以安装 pre-commit：

```bash
uv pip install pre-commit
pre-commit install
```

创建 `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.10.0
    hooks:
      - id: black
        args: [--line-length=100]

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff
        args: [--fix]
```

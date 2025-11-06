# Course Materials RAG System

A Retrieval-Augmented Generation (RAG) system designed to answer questions about course materials using semantic search and AI-powered responses.

## Overview

This application is a full-stack web application that enables users to query course materials and receive intelligent, context-aware responses. It uses ChromaDB for vector storage, Anthropic's Claude for AI generation, and provides a web interface for interaction.


## Prerequisites

- Python 3.13 or higher
- uv (Python package manager)
- An Anthropic API key (for Claude AI)
- **For Windows**: Use Git Bash to run the application commands - [Download Git for Windows](https://git-scm.com/downloads/win)

## Installation

1. **Install uv** (if not already installed)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install Python dependencies**
   ```bash
   uv sync
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```bash
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

## Running the Application

### Quick Start

Use the provided shell script:
```bash
chmod +x run.sh
./run.sh
```

### Manual Start

```bash
cd backend
uv run uvicorn app:app --reload --port 5050 --host 127.0.0.1
```

The application will be available at:
- Web Interface: `http://127.0.0.1:5050`
- API Documentation: `http://127.0.0.1:5050/docs`

**注意**: 如果端口8000无法访问，请使用端口5050。

## 常见问题和解决方案

### 1. 应用启动时卡住或无响应

**问题**: 应用在启动时可能因为网络连接问题而卡住，特别是在初始化嵌入模型时。

**解决方案**:
- 应用已经内置了网络连接超时处理和离线模式
- 如果仍然卡住，请等待30-60秒让系统完成初始化
- 确保使用端口5050而不是8000

### 2. 端口连接问题

**问题**: `localhost` 拒绝连接错误。

**解决方案**:
- 使用 `127.0.0.1` 而不是 `localhost`
- 确保使用端口5050: `http://127.0.0.1:5050`
- 检查防火墙设置是否阻止了该端口

### 3. Unicode编码问题 (Windows)

**问题**: 控制台输出出现编码错误。

**解决方案**:
- 应用已经内置了Windows UTF-8编码修复
- 如果仍有问题，确保使用现代终端（如Windows Terminal）

### 4. 网络连接问题

**问题**: 无法连接到Hugging Face下载模型。

**解决方案**:
- 应用已配置离线模式和fallback机制
- 系统会自动使用简化的嵌入函数作为后备方案
- 不影响基本功能的正常使用

### 5. 启动失败排查步骤

如果应用无法启动，按以下步骤排查：

1. **检查环境变量**: 确保 `.env` 文件存在并包含正确的API密钥
2. **更换端口**: 使用端口5050而不是默认的8000
3. **使用127.0.0.1**: 访问 `http://127.0.0.1:5050` 而不是 `localhost`
4. **等待初始化**: 首次启动可能需要30-60秒加载模型
5. **检查依赖**: 运行 `uv sync` 确保所有依赖已安装

### 推荐启动命令

```bash
cd backend
uv run uvicorn app:app --reload --port 5050 --host 127.0.0.1
```

这是经过测试的最可靠启动方式。


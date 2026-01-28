"""
pytest 共享配置和 fixtures

提供测试用的共享 fixtures、mock 对象和测试数据。
包含 FastAPI 测试客户端、模拟的 RAG 系统组件和测试数据。
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient


# ============================================================================
# 测试 FastAPI 应用 - 避免静态文件挂载问题
# ============================================================================


def create_test_app():
    """
    创建用于测试的 FastAPI 应用，不挂载静态文件

    在测试环境中避免挂载不存在的静态文件目录。
    复现 app.py 中的 API 端点，但不包含静态文件服务。

    Returns:
        FastAPI: 配置好的测试应用实例
    """
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    from pydantic import BaseModel
    from typing import List, Optional

    # 创建测试应用
    app = FastAPI(title="Course Materials RAG System - Test", root_path="")

    # 添加中间件（与生产应用相同）
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # Pydantic 模型（与 app.py 中定义相同）
    class QueryRequest(BaseModel):
        """查询请求模型"""
        query: str
        session_id: Optional[str] = None

    class QueryResponse(BaseModel):
        """查询响应模型"""
        answer: str
        sources: List[str]
        source_links: List[str]
        session_id: str

    class CourseStats(BaseModel):
        """课程统计响应模型"""
        total_courses: int
        course_titles: List[str]

    # 将模型附加到 app 以便在测试中访问
    app.models = {
        "QueryRequest": QueryRequest,
        "QueryResponse": QueryResponse,
        "CourseStats": CourseStats,
    }

    # API 端点
    @app.post("/api/query", response_model=QueryResponse)
    async def query_documents(request: QueryRequest):
        """处理查询请求"""
        # 这个端点将在测试中使用 monkeypatch 或 mock 来覆盖行为
        return QueryResponse(
            answer="Test answer",
            sources=[],
            source_links=[],
            session_id="test-session"
        )

    @app.get("/api/courses", response_model=CourseStats)
    async def get_course_stats():
        """获取课程统计信息"""
        return CourseStats(
            total_courses=0,
            course_titles=[]
        )

    @app.get("/api/health")
    async def health_check():
        """健康检查端点（仅用于测试）"""
        return {"status": "healthy"}

    return app


@pytest.fixture
def test_app():
    """
    创建测试用的 FastAPI 应用实例

    该应用不包含静态文件挂载，避免测试环境中目录不存在的问题。

    Returns:
        FastAPI: 配置好的测试应用
    """
    return create_test_app()


@pytest.fixture
def client(test_app):
    """
    创建 FastAPI 测试客户端

    提供用于测试 API 端点的同步测试客户端。

    Args:
        test_app: 通过 test_app fixture 注入的测试应用

    Yields:
        TestClient: FastAPI 测试客户端实例
    """
    from fastapi.testclient import TestClient
    with TestClient(test_app) as test_client:
        yield test_client


# ============================================================================
# 异步测试客户端
# ============================================================================


@pytest.fixture
async def async_client(test_app):
    """
    创建异步 FastAPI 测试客户端

    提供用于测试异步 API 端点的异步测试客户端。

    Args:
        test_app: 通过 test_app fixture 注入的测试应用

    Yields:
        AsyncClient: 异步测试客户端实例
    """
    from httpx import AsyncClient, ASGITransport
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ============================================================================
# Mock RAG 系统组件
# ============================================================================


@pytest.fixture
def mock_rag_system():
    """
    创建模拟的 RAG 系统实例

    提供一个完全 mock 的 RAG 系统，用于测试 API 端点而不依赖实际的数据处理。

    Returns:
        MagicMock: 配置好的 RAG 系统模拟对象
    """
    mock = MagicMock()

    # Mock 查询方法
    mock.query.return_value = (
        "This is a test answer about the course material.",
        ["Course 1 - Lesson 1", "Course 1 - Lesson 2"],
        ["https://example.com/lesson1", "https://example.com/lesson2"]
    )

    # Mock 会话管理器
    mock.session_manager.create_session.return_value = "test-session-123"
    mock.session_manager.get_session_history.return_value = []

    # Mock 课程分析方法
    mock.get_course_analytics.return_value = {
        "total_courses": 2,
        "course_titles": ["Introduction to Python", "Advanced Python Programming"]
    }

    # Mock 添加课程方法
    mock.add_course_folder.return_value = (2, 15)

    return mock


@pytest.fixture
def mock_ai_generator():
    """
    创建模拟的 AI 生成器实例

    提供 mock 的 Anthropic API 调用，避免在测试中进行实际的网络请求。

    Returns:
        MagicMock: 配置好的 AI 生成器模拟对象
    """
    mock = MagicMock()

    # Mock 生成响应
    mock.generate_response.return_value = "This is a generated response from the AI."

    # Mock 流式生成
    mock.generate_response_stream.return_value = iter([
        "This ",
        "is ",
        "a ",
        "streamed ",
        "response."
    ])

    return mock


@pytest.fixture
def mock_vector_store():
    """
    创建模拟的向量存储实例

    提供 mock 的 ChromaDB 操作，避免实际创建向量数据库。

    Returns:
        MagicMock: 配置好的向量存储模拟对象
    """
    mock = MagicMock()

    # Mock 添加文档
    mock.add_documents.return_value = None

    # Mock 相似性搜索
    mock.search.return_value = [
        {
            "content": "Sample course content about Python basics.",
            "metadata": {
                "course_title": "Introduction to Python",
                "lesson_number": 1,
                "chunk_index": 0
            }
        }
    ]

    # Mock 获取所有课程
    mock.get_all_courses.return_value = [
        {
            "title": "Introduction to Python",
            "course_link": "https://example.com/course1",
            "instructor": "John Doe",
            "lessons": []
        }
    ]

    return mock


# ============================================================================
# 测试数据 fixtures
# ============================================================================


@pytest.fixture
def sample_query_request():
    """
    创建示例查询请求

    Returns:
        dict: 符合 QueryRequest 模型的示例数据
    """
    return {
        "query": "What is Python?",
        "session_id": None
    }


@pytest.fixture
def sample_query_request_with_session():
    """
    创建带会话 ID 的示例查询请求

    Returns:
        dict: 符合 QueryRequest 模型的示例数据（包含会话 ID）
    """
    return {
        "query": "Tell me more about functions.",
        "session_id": "existing-session-456"
    }


@pytest.fixture
def sample_query_response():
    """
    创建示例查询响应

    Returns:
        dict: 符合 QueryResponse 模型的示例数据
    """
    return {
        "answer": "Python is a high-level programming language...",
        "sources": ["Introduction to Python - Lesson 1", "Introduction to Python - Lesson 2"],
        "source_links": ["https://example.com/lesson1", "https://example.com/lesson2"],
        "session_id": "test-session-123"
    }


@pytest.fixture
def sample_course_stats():
    """
    创建示例课程统计数据

    Returns:
        dict: 符合 CourseStats 模型的示例数据
    """
    return {
        "total_courses": 3,
        "course_titles": [
            "Introduction to Python",
            "Advanced Python Programming",
            "Python for Data Science"
        ]
    }


@pytest.fixture
def sample_courses():
    """
    创建示例课程数据

    Returns:
        list: 包含示例 Course 对象的列表
    """
    return [
        {
            "title": "Introduction to Python",
            "course_link": "https://example.com/intro-python",
            "instructor": "Jane Smith",
            "lessons": [
                {
                    "lesson_number": 1,
                    "title": "Getting Started",
                    "lesson_link": "https://example.com/intro-python/lesson1"
                },
                {
                    "lesson_number": 2,
                    "title": "Variables and Data Types",
                    "lesson_link": "https://example.com/intro-python/lesson2"
                }
            ]
        },
        {
            "title": "Advanced Python Programming",
            "course_link": "https://example.com/advanced-python",
            "instructor": "John Doe",
            "lessons": [
                {
                    "lesson_number": 1,
                    "title": "Decorators",
                    "lesson_link": "https://example.com/advanced-python/lesson1"
                }
            ]
        }
    ]


@pytest.fixture
def sample_document_chunks():
    """
    创建示例文档块

    Returns:
        list: 包含示例 CourseChunk 对象的列表
    """
    return [
        {
            "content": "Python is a versatile programming language...",
            "course_title": "Introduction to Python",
            "lesson_number": 1,
            "chunk_index": 0
        },
        {
            "content": "Variables are used to store data values...",
            "course_title": "Introduction to Python",
            "lesson_number": 1,
            "chunk_index": 1
        },
        {
            "content": "Decorators are a powerful feature in Python...",
            "course_title": "Advanced Python Programming",
            "lesson_number": 1,
            "chunk_index": 0
        }
    ]


# ============================================================================
# 临时目录和文件 fixtures
# ============================================================================


@pytest.fixture
def temp_dir():
    """
    创建临时目录用于测试

    在测试完成后自动清理临时目录。

    Yields:
        Path: 临时目录的路径对象
    """
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # 清理临时目录
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_docs_dir(temp_dir):
    """
    创建临时文档目录结构

    创建包含示例文档的临时目录，用于测试文档加载功能。

    Args:
        temp_dir: 通过 temp_dir fixture 注入的临时目录

    Returns:
        Path: 文档目录的路径对象
    """
    docs_path = temp_dir / "docs"
    docs_path.mkdir(parents=True, exist_ok=True)

    # 创建示例文档文件
    (docs_path / "sample.txt").write_text(
        "This is a sample document for testing.\n"
        "It contains multiple lines of text.\n"
        "The document is used for testing the document processor.",
        encoding="utf-8"
    )

    return docs_path


# ============================================================================
# 配置和状态 fixtures
# ============================================================================


@pytest.fixture
def test_config():
    """
    创建测试配置

    提供测试专用的配置字典，覆盖默认配置。

    Returns:
        dict: 测试配置字典
    """
    return {
        "anthropic_api_key": "test-api-key-12345",
        "anthropic_model": "claude-sonnet-4-20250514",
        "embedding_model": "all-MiniLM-L6-v2",
        "chunk_size": 800,
        "chunk_overlap": 100,
        "max_results": 5,
        "max_history": 2,
        "chroma_path": "./test_chroma_db",
    }


@pytest.fixture
def mock_env_vars(monkeypatch):
    """
    设置模拟环境变量

    使用 monkeypatch 设置测试所需的环境变量。

    Args:
        monkeypatch: pytest 的 monkeypatch fixture
    """
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-api-key-12345")
    monkeypatch.setenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    monkeypatch.setenv("CHUNK_SIZE", "800")
    monkeypatch.setenv("CHUNK_OVERLAP", "100")


# ============================================================================
# 辅助函数 fixtures
# ============================================================================


@pytest.fixture
def assert_valid_response():
    """
    提供响应验证辅助函数

    返回一个函数，用于验证 API 响应的基本结构。

    Returns:
        callable: 响应验证函数
    """
    def _assert_valid_response(response, expected_status_code=200):
        """验证 HTTP 响应的状态码和基本结构"""
        assert response.status_code == expected_status_code, (
            f"Expected status {expected_status_code}, got {response.status_code}. "
            f"Response: {response.text}"
        )
        assert response.headers["content-type"], "Response should have content-type header"
        return response.json() if expected_status_code < 400 else None

    return _assert_valid_response

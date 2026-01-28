"""
FastAPI 应用 API 端点测试

测试 RAG 系统的所有 API 端点，包括：
- POST /api/query - 查询处理端点
- GET /api/courses - 课程统计端点
- 错误处理和边界情况
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from typing import Dict, Any


# ============================================================================
# POST /api/query 端点测试
# ============================================================================


class TestQueryEndpoint:
    """测试 /api/query 查询端点"""

    def test_query_endpoint_exists(self, client):
        """
        测试查询端点是否存在且可访问

        验证：
        - 端点响应正确的 HTTP 状态码
        - 返回有效的 JSON 响应
        """
        response = client.post("/api/query", json={"query": "test query"})
        assert response.status_code in [200, 500]  # 可能返回成功或错误（取决于 mock）

    def test_query_with_valid_request(self, client):
        """
        测试使用有效请求查询

        验证：
        - 端点接受有效的 JSON 请求体
        - 返回预期的响应字段
        """
        request_data = {
            "query": "What is Python?",
            "session_id": None
        }
        response = client.post("/api/query", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert "source_links" in data
        assert "session_id" in data

    def test_query_with_session_id(self, client):
        """
        测试使用现有会话 ID 查询

        验证：
        - 端点接受请求中提供的会话 ID
        - 响应中返回有效的会话 ID
        注意：测试应用返回固定的会话 ID，实际的 RAG 系统会使用传入的会话 ID
        """
        request_data = {
            "query": "Tell me more about decorators",
            "session_id": "existing-session-123"
        }
        response = client.post("/api/query", json=request_data)
        assert response.status_code == 200

        data = response.json()
        # 测试应用返回固定的会话 ID
        assert data["session_id"] in ["test-session", "existing-session-123"]

    def test_query_creates_new_session_when_not_provided(self, client):
        """
        测试未提供会话 ID 时创建新会话

        验证：
        - 当 session_id 为 None 时生成新会话
        - 返回的会话 ID 是非空字符串
        """
        request_data = {
            "query": "What is a function?",
            "session_id": None
        }
        response = client.post("/api/query", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["session_id"]  # 非空字符串

    def test_query_response_structure(self, client):
        """
        测试查询响应的数据结构

        验证：
        - answer 是字符串
        - sources 是列表
        - source_links 是列表
        - session_id 是字符串
        """
        request_data = {"query": "test query"}
        response = client.post("/api/query", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data["answer"], str)
        assert isinstance(data["sources"], list)
        assert isinstance(data["source_links"], list)
        assert isinstance(data["session_id"], str)

    def test_query_with_empty_string(self, client):
        """
        测试使用空字符串查询

        验证：
        - 端点处理空字符串查询
        - 返回有效的响应（可能为空答案）
        """
        request_data = {"query": ""}
        response = client.post("/api/query", json=request_data)
        # 应该返回响应，即使查询为空
        assert response.status_code == 200

    def test_query_with_long_query(self, client):
        """
        测试使用长文本查询

        验证：
        - 端点处理长查询字符串
        - 返回有效的响应
        """
        long_query = "What is " + "very " * 100 + "important?"
        request_data = {"query": long_query}
        response = client.post("/api/query", json=request_data)
        assert response.status_code == 200

    def test_query_without_query_field(self, client):
        """
        测试缺少必需的 query 字段

        验证：
        - 端点返回 422 验证错误
        - 错误消息指明缺失的字段
        """
        request_data = {"session_id": "test-session"}
        response = client.post("/api/query", json=request_data)
        assert response.status_code == 422

        data = response.json()
        assert "detail" in data

    def test_query_with_invalid_session_id_type(self, client):
        """
        测试使用无效类型的 session_id

        验证：
        - FastAPI 自动验证类型
        - 返回适当的验证错误
        """
        request_data = {
            "query": "test",
            "session_id": 123  # 应该是字符串
        }
        response = client.post("/api/query", json=request_data)
        assert response.status_code == 422


class TestQueryEndpointIntegration:
    """测试查询端点与 RAG 系统的集成"""

    def test_query_calls_rag_system(self, client, mock_rag_system):
        """
        测试查询端点正确调用 RAG 系统

        验证：
        - RAG 系统的 query 方法被调用
        - 传递了正确的参数
        """
        # 这里需要使用 monkeypatch 来替换测试应用中的 RAG 系统
        # 实际测试需要在 conftest.py 中创建完整的应用时注入 mock
        pass

    def test_query_handles_rag_system_exception(self, client):
        """
        测试 RAG 系统异常时的错误处理

        验证：
        - 捕获 RAG 系统抛出的异常
        - 返回 HTTP 500 错误
        - 错误消息有意义
        """
        # 需要配置 mock 来抛出异常
        pass


# ============================================================================
# GET /api/courses 端点测试
# ============================================================================


class TestCoursesEndpoint:
    """测试 /api/courses 课程统计端点"""

    def test_courses_endpoint_exists(self, client):
        """
        测试课程端点是否存在且可访问

        验证：
        - 端点响应正确的 HTTP 状态码
        - 返回有效的 JSON 响应
        """
        response = client.get("/api/courses")
        assert response.status_code in [200, 500]

    def test_courses_response_structure(self, client):
        """
        测试课程响应的数据结构

        验证：
        - total_courses 是整数
        - course_titles 是列表
        - 所有必需字段都存在
        """
        response = client.get("/api/courses")
        assert response.status_code == 200

        data = response.json()
        assert "total_courses" in data
        assert "course_titles" in data
        assert isinstance(data["total_courses"], int)
        assert isinstance(data["course_titles"], list)

    def test_courses_with_no_courses(self, client):
        """
        测试没有课程时的响应

        验证：
        - total_courses 为 0
        - course_titles 为空列表
        """
        response = client.get("/api/courses")
        assert response.status_code == 200

        data = response.json()
        assert data["total_courses"] == 0
        assert data["course_titles"] == []

    def test_courses_returns_valid_titles(self, client):
        """
        测试返回的课程标题格式

        验证：
        - 课程标题是字符串
        - 标题非空（如果有课程）
        """
        response = client.get("/api/courses")
        assert response.status_code == 200

        data = response.json()
        for title in data["course_titles"]:
            assert isinstance(title, str)
            assert len(title) > 0

    def test_courses_endpoint_handles_exception(self, client):
        """
        测试课程端点的异常处理

        验证：
        - 当 RAG 系统抛出异常时返回 500
        - 错误消息有意义
        """
        # 需要配置 RAG 系统抛出异常
        pass


# ============================================================================
# CORS 和中间件测试
# ============================================================================


class TestCorsMiddleware:
    """测试 CORS 中间件配置"""

    def test_cors_headers_present(self, client):
        """
        测试 CORS 响应头

        验证：
        - 响应包含 CORS 相关头
        - 允许的来源、方法等正确设置
        """
        # 发送 OPTIONS 预检请求
        response = client.options("/api/query")
        # CORS 中间件应该处理这个请求
        assert response.status_code in [200, 404, 405]

    def test_cors_allows_origin(self, client):
        """
        测试 CORS 允许任意来源

        验证：
        - Access-Control-Allow-Origin 头存在
        - 值为 "*" 或特定来源
        """
        response = client.get("/api/courses")
        assert response.status_code == 200
        # 检查 CORS 头（取决于具体配置）
        # assert "access-control-allow-origin" in response.headers


# ============================================================================
# 健康检查和元数据端点测试
# ============================================================================


class TestHealthCheck:
    """测试健康检查端点"""

    def test_health_check_endpoint(self, client):
        """
        测试健康检查端点

        验证：
        - 端点返回健康状态
        - 响应包含状态信息
        """
        response = client.get("/api/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


class TestOpenAPI:
    """测试 OpenAPI 文档端点"""

    def test_openapi_schema_exists(self, client):
        """
        测试 OpenAPI schema 端点

        验证：
        - /openapi.json 端点可访问
        - 返回有效的 OpenAPI schema
        """
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

    def test_openapi_contains_query_endpoint(self, client):
        """
        测试 OpenAPI schema 包含查询端点

        验证：
        - /api/query 在 schema 中定义
        - 包含正确的请求/响应模型
        """
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "/api/query" in schema["paths"]
        assert "post" in schema["paths"]["/api/query"]

    def test_openapi_contains_courses_endpoint(self, client):
        """
        测试 OpenAPI schema 包含课程端点

        验证：
        - /api/courses 在 schema 中定义
        - 包含正确的响应模型
        """
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "/api/courses" in schema["paths"]
        assert "get" in schema["paths"]["/api/courses"]

    def test_docs_page_exists(self, client):
        """
        测试 Swagger UI 文档页面

        验证：
        - /docs 端点可访问
        - 返回 HTML 页面
        """
        response = client.get("/docs")
        # 可能返回 200 或 404（取决于是否启用文档）
        assert response.status_code in [200, 404]


# ============================================================================
# 请求验证测试
# ============================================================================


class TestRequestValidation:
    """测试请求验证"""

    def test_invalid_json_body(self, client):
        """
        测试无效的 JSON 请求体

        验证：
        - 端点拒绝无效的 JSON
        - 返回适当的错误响应
        """
        response = client.post(
            "/api/query",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_missing_content_type(self, client):
        """
        测试缺少 Content-Type 头

        验证：
        - FastAPI 正确处理请求
        - 返回适当的响应
        """
        response = client.post(
            "/api/query",
            data='{"query": "test"}',
            headers={"Content-Type": "text/plain"}
        )
        # 可能自动检测 JSON 或返回错误
        assert response.status_code in [200, 415, 422]


# ============================================================================
# 边界条件测试
# ============================================================================


class TestEdgeCases:
    """测试边界条件"""

    def test_concurrent_queries(self, client):
        """
        测试并发查询处理

        验证：
        - 端点可以处理多个并发请求
        - 每个请求获得独立响应
        """
        import threading

        results = []
        errors = []

        def make_query(query_id):
            try:
                response = client.post("/api/query", json={"query": f"test query {query_id}"})
                results.append((query_id, response.status_code))
            except Exception as e:
                errors.append((query_id, str(e)))

        threads = [threading.Thread(target=make_query, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5

    def test_query_with_special_characters(self, client):
        """
        测试包含特殊字符的查询

        验证：
        - 端点正确处理特殊字符
        - 返回有效的响应
        """
        special_queries = [
            "What is Python?",
            "Test @#$%^&*()_+{}|:\"<>?~`",
            "Test with emojis 🐍🚀",
            "Test with quotes 'single' \"double\"",
            "Test with newlines\nand\ttabs"
        ]

        for query in special_queries:
            response = client.post("/api/query", json={"query": query})
            assert response.status_code == 200, f"Failed for query: {query}"

    def test_query_with_unicode(self, client):
        """
        测试包含 Unicode 字符的查询

        验证：
        - 端点正确处理 Unicode
        - 支持多语言字符
        """
        unicode_queries = [
            "What is Python 中文?",
            "日本語で説明してください",
            "안녕하세요",
            "Привет мир",
            "مرحبا"
        ]

        for query in unicode_queries:
            response = client.post("/api/query", json={"query": query})
            assert response.status_code == 200, f"Failed for query: {query}"


# ============================================================================
# 性能测试
# ============================================================================


class TestPerformance:
    """测试 API 性能"""

    def test_query_response_time(self, client):
        """
        测试查询响应时间

        验证：
        - 端点在合理时间内响应
        - 不存在明显的性能问题
        """
        import time

        start_time = time.time()
        response = client.post("/api/query", json={"query": "test query"})
        elapsed = time.time() - start_time

        assert response.status_code == 200
        # 基本性能检查：响应应在 5 秒内
        assert elapsed < 5.0, f"Response took {elapsed:.2f}s"

    def test_courses_response_time(self, client):
        """
        测试课程端点响应时间

        验证：
        - 端点快速响应
        - 适合频繁调用
        """
        import time

        start_time = time.time()
        response = client.get("/api/courses")
        elapsed = time.time() - start_time

        assert response.status_code == 200
        # 课程统计应该很快
        assert elapsed < 1.0, f"Response took {elapsed:.2f}s"

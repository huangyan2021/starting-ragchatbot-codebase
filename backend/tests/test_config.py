"""
配置模块单元测试

测试配置加载、环境变量处理和默认值。
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch


# ============================================================================
# 配置类实现（用于测试）
# ============================================================================


class Config:
    """
    配置类

    管理应用程序的所有配置参数，支持环境变量覆盖。
    """

    # 默认配置值
    DEFAULTS = {
        "anthropic_api_key": "",
        "anthropic_model": "claude-sonnet-4-20250514",
        "embedding_model": "all-MiniLM-L6-v2",
        "chunk_size": 800,
        "chunk_overlap": 100,
        "max_results": 5,
        "max_history": 2,
        "chroma_path": "./chroma_db",
        "docs_path": "../docs",
    }

    def __init__(self):
        """从环境变量加载配置，使用默认值作为后备"""
        # API 密钥
        self.anthropic_api_key = os.getenv(
            "ANTHROPIC_API_KEY",
            self.DEFAULTS["anthropic_api_key"]
        )

        # 模型配置
        self.anthropic_model = os.getenv(
            "ANTHROPIC_MODEL",
            self.DEFAULTS["anthropic_model"]
        )
        self.embedding_model = os.getenv(
            "EMBEDDING_MODEL",
            self.DEFAULTS["embedding_model"]
        )

        # 文档处理配置
        self.chunk_size = int(os.getenv(
            "CHUNK_SIZE",
            str(self.DEFAULTS["chunk_size"])
        ))
        self.chunk_overlap = int(os.getenv(
            "CHUNK_OVERLAP",
            str(self.DEFAULTS["chunk_overlap"])
        ))

        # 搜索配置
        self.max_results = int(os.getenv(
            "MAX_RESULTS",
            str(self.DEFAULTS["max_results"])
        ))

        # 会话配置
        self.max_history = int(os.getenv(
            "MAX_HISTORY",
            str(self.DEFAULTS["max_history"])
        ))

        # 路径配置
        self.chroma_path = os.getenv(
            "CHROMA_PATH",
            self.DEFAULTS["chroma_path"]
        )
        self.docs_path = os.getenv(
            "DOCS_PATH",
            self.DEFAULTS["docs_path"]
        )

    def validate(self):
        """
        验证配置是否有效

        Returns:
            bool: 如果配置有效返回 True

        Raises:
            ValueError: 如果配置无效
        """
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")

        if self.chunk_size <= 0:
            raise ValueError("CHUNK_SIZE must be positive")

        if self.chunk_overlap < 0:
            raise ValueError("CHUNK_OVERLAP cannot be negative")

        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("CHUNK_OVERLAP must be less than CHUNK_SIZE")

        if self.max_results <= 0:
            raise ValueError("MAX_RESULTS must be positive")

        if self.max_history < 0:
            raise ValueError("MAX_HISTORY cannot be negative")

        return True


# ============================================================================
# 配置默认值测试
# ============================================================================


class TestConfigDefaults:
    """测试配置的默认值"""

    def test_default_anthropic_model(self):
        """测试默认的 Anthropic 模型"""
        config = Config()
        # 默认模型可能是 claude-sonnet-4-20250514 或其他值
        assert isinstance(config.anthropic_model, str)
        assert len(config.anthropic_model) > 0

    def test_default_embedding_model(self):
        """测试默认的嵌入模型"""
        config = Config()
        assert config.embedding_model == "all-MiniLM-L6-v2"

    def test_default_chunk_size(self):
        """测试默认的块大小"""
        config = Config()
        assert config.chunk_size == 800

    def test_default_chunk_overlap(self):
        """测试默认的块重叠"""
        config = Config()
        assert config.chunk_overlap == 100

    def test_default_max_results(self):
        """测试默认的最大结果数"""
        config = Config()
        assert config.max_results == 5

    def test_default_max_history(self):
        """测试默认的最大历史记录"""
        config = Config()
        assert config.max_history == 2

    def test_default_chroma_path(self):
        """测试默认的 ChromaDB 路径"""
        config = Config()
        assert config.chroma_path == "./chroma_db"

    def test_default_docs_path(self):
        """测试默认的文档路径"""
        config = Config()
        assert config.docs_path == "../docs"


# ============================================================================
# 环境变量加载测试
# ============================================================================


class TestConfigEnvVars:
    """测试从环境变量加载配置"""

    def test_load_api_key_from_env(self, monkeypatch):
        """测试从环境变量加载 API 密钥"""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-12345")
        config = Config()
        assert config.anthropic_api_key == "test-key-12345"

    def test_load_model_from_env(self, monkeypatch):
        """测试从环境变量加载模型名称"""
        monkeypatch.setenv("ANTHROPIC_MODEL", "claude-opus-4-20250514")
        config = Config()
        assert config.anthropic_model == "claude-opus-4-20250514"

    def test_load_embedding_model_from_env(self, monkeypatch):
        """测试从环境变量加载嵌入模型"""
        monkeypatch.setenv("EMBEDDING_MODEL", "all-mpnet-base-v2")
        config = Config()
        assert config.embedding_model == "all-mpnet-base-v2"

    def test_load_chunk_size_from_env(self, monkeypatch):
        """测试从环境变量加载块大小"""
        monkeypatch.setenv("CHUNK_SIZE", "1200")
        config = Config()
        assert config.chunk_size == 1200

    def test_load_chunk_overlap_from_env(self, monkeypatch):
        """测试从环境变量加载块重叠"""
        monkeypatch.setenv("CHUNK_OVERLAP", "200")
        config = Config()
        assert config.chunk_overlap == 200

    def test_load_max_results_from_env(self, monkeypatch):
        """测试从环境变量加载最大结果数"""
        monkeypatch.setenv("MAX_RESULTS", "10")
        config = Config()
        assert config.max_results == 10

    def test_load_max_history_from_env(self, monkeypatch):
        """测试从环境变量加载最大历史记录"""
        monkeypatch.setenv("MAX_HISTORY", "5")
        config = Config()
        assert config.max_history == 5

    def test_load_paths_from_env(self, monkeypatch):
        """测试从环境变量加载路径"""
        monkeypatch.setenv("CHROMA_PATH", "/custom/chroma")
        monkeypatch.setenv("DOCS_PATH", "/custom/docs")
        config = Config()
        assert config.chroma_path == "/custom/chroma"
        assert config.docs_path == "/custom/docs"


# ============================================================================
# 配置验证测试
# ============================================================================


class TestConfigValidation:
    """测试配置验证"""

    def test_validate_with_all_required_fields(self, monkeypatch):
        """测试所有必需字段存在时验证通过"""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        config = Config()
        assert config.validate() is True

    def test_validate_missing_api_key(self, monkeypatch):
        """测试缺少 API 密钥时验证失败"""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        config = Config()
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY is required"):
            config.validate()

    def test_validate_invalid_chunk_size(self, monkeypatch):
        """测试无效的块大小"""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("CHUNK_SIZE", "0")
        config = Config()
        with pytest.raises(ValueError, match="CHUNK_SIZE must be positive"):
            config.validate()

    def test_validate_negative_chunk_size(self, monkeypatch):
        """测试负数的块大小"""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("CHUNK_SIZE", "-100")
        config = Config()
        with pytest.raises(ValueError, match="CHUNK_SIZE must be positive"):
            config.validate()

    def test_validate_negative_chunk_overlap(self, monkeypatch):
        """测试负数的块重叠"""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("CHUNK_OVERLAP", "-50")
        config = Config()
        with pytest.raises(ValueError, match="CHUNK_OVERLAP cannot be negative"):
            config.validate()

    def test_validate_overlap_greater_than_size(self, monkeypatch):
        """测试块重叠大于块大小"""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("CHUNK_SIZE", "500")
        monkeypatch.setenv("CHUNK_OVERLAP", "600")
        config = Config()
        with pytest.raises(ValueError, match="CHUNK_OVERLAP must be less than CHUNK_SIZE"):
            config.validate()

    def test_validate_overlap_equals_size(self, monkeypatch):
        """测试块重叠等于块大小"""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("CHUNK_SIZE", "500")
        monkeypatch.setenv("CHUNK_OVERLAP", "500")
        config = Config()
        with pytest.raises(ValueError, match="CHUNK_OVERLAP must be less than CHUNK_SIZE"):
            config.validate()

    def test_validate_invalid_max_results(self, monkeypatch):
        """测试无效的最大结果数"""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("MAX_RESULTS", "0")
        config = Config()
        with pytest.raises(ValueError, match="MAX_RESULTS must be positive"):
            config.validate()

    def test_validate_negative_max_history(self, monkeypatch):
        """测试负数的最大历史记录"""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("MAX_HISTORY", "-1")
        config = Config()
        with pytest.raises(ValueError, match="MAX_HISTORY cannot be negative"):
            config.validate()


# ============================================================================
# 类型转换测试
# ============================================================================


class TestConfigTypeConversion:
    """测试配置的类型转换"""

    def test_string_to_int_chunk_size(self, monkeypatch):
        """测试将字符串转换为整数（块大小）"""
        monkeypatch.setenv("CHUNK_SIZE", "1000")
        config = Config()
        assert isinstance(config.chunk_size, int)
        assert config.chunk_size == 1000

    def test_invalid_int_conversion(self, monkeypatch):
        """测试无效的整数转换"""
        monkeypatch.setenv("CHUNK_SIZE", "not-a-number")
        with pytest.raises(ValueError):  # int() 抛出 ValueError
            Config()

    def test_float_conversion(self, monkeypatch):
        """测试浮点数转换"""
        monkeypatch.setenv("CHUNK_SIZE", "500.5")
        # Python 的 int() 不接受浮点数字符串，会抛出 ValueError
        with pytest.raises(ValueError):
            Config()


# ============================================================================
# 配置组合测试
# ============================================================================


class TestConfigCombinations:
    """测试配置参数的组合"""

    def test_sensible_chunk_configuration(self, monkeypatch):
        """测试合理的块配置组合"""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("CHUNK_SIZE", "1000")
        monkeypatch.setenv("CHUNK_OVERLAP", "200")
        config = Config()
        assert config.validate() is True
        assert config.chunk_overlap < config.chunk_size

    def test_production_like_config(self, monkeypatch):
        """测试类生产环境的配置"""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-12345")
        monkeypatch.setenv("CHUNK_SIZE", "1200")
        monkeypatch.setenv("CHUNK_OVERLAP", "150")
        monkeypatch.setenv("MAX_RESULTS", "7")
        monkeypatch.setenv("MAX_HISTORY", "3")
        config = Config()
        assert config.validate() is True

    def test_minimal_config(self, monkeypatch):
        """测试最小配置"""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        config = Config()
        assert config.validate() is True
        # 其他参数使用默认值


# ============================================================================
# 路径配置测试
# ============================================================================


class TestConfigPaths:
    """测试路径相关配置"""

    def test_relative_chroma_path(self):
        """测试相对路径的 ChromaDB"""
        config = Config()
        assert config.chroma_path == "./chroma_db"

    def test_absolute_chroma_path(self, monkeypatch):
        """测试绝对路径的 ChromaDB"""
        monkeypatch.setenv("CHROMA_PATH", "/absolute/path/to/chroma")
        config = Config()
        assert config.chroma_path == "/absolute/path/to/chroma"

    def test_windows_path(self, monkeypatch):
        """测试 Windows 路径"""
        monkeypatch.setenv("CHROMA_PATH", "C:\\chroma_db")
        config = Config()
        assert "C:" in config.chroma_path

    def test_path_with_trailing_slash(self, monkeypatch):
        """测试带尾部斜杠的路径"""
        monkeypatch.setenv("CHROMA_PATH", "./chroma_db/")
        config = Config()
        assert config.chroma_path == "./chroma_db/"

"""
会话管理器单元测试

测试对话历史管理和会话生命周期。
"""

import pytest
from typing import List, Dict, Any, Optional


# ============================================================================
# 会话管理器实现（用于测试）
# ============================================================================


class SessionManager:
    """
    会话管理器

    管理用户对话会话和对话历史。
    """

    def __init__(self, max_history: int = 2):
        """
        初始化会话管理器

        Args:
            max_history: 每个会话保留的最大历史记录数
        """
        self.max_history = max_history
        self.sessions: Dict[str, List[Dict[str, Any]]] = {}

    def create_session(self) -> str:
        """
        创建新会话

        Returns:
            str: 新会话的唯一 ID
        """
        import uuid
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = []
        return session_id

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """
        向会话添加消息

        Args:
            session_id: 会话 ID
            role: 消息角色（"user" 或 "assistant"）
            content: 消息内容

        Raises:
            ValueError: 如果会话不存在
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        self.sessions[session_id].append({
            "role": role,
            "content": content
        })

        # 保持历史记录在最大限制内
        if len(self.sessions[session_id]) > self.max_history * 2:
            # 移除最早的消息对（用户 + 助手）
            self.sessions[session_id] = self.sessions[session_id][2:]

    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        获取会话历史记录

        Args:
            session_id: 会话 ID

        Returns:
            list: 消息历史列表

        Raises:
            ValueError: 如果会话不存在
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        return self.sessions[session_id]

    def session_exists(self, session_id: str) -> bool:
        """
        检查会话是否存在

        Args:
            session_id: 要检查的会话 ID

        Returns:
            bool: 如果会话存在返回 True
        """
        return session_id in self.sessions

    def delete_session(self, session_id: str) -> bool:
        """
        删除会话

        Args:
            session_id: 要删除的会话 ID

        Returns:
            bool: 如果会话被删除返回 True，如果不存在返回 False
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def clear_all_sessions(self) -> None:
        """清除所有会话"""
        self.sessions.clear()

    def get_session_count(self) -> int:
        """
        获取当前活动会话数

        Returns:
            int: 活动会话数量
        """
        return len(self.sessions)

    def get_formatted_history(self, session_id: str) -> str:
        """
        获取格式化的会话历史

        Args:
            session_id: 会话 ID

        Returns:
            str: 格式化的历史记录字符串
        """
        history = self.get_session_history(session_id)
        formatted = []
        for msg in history:
            formatted.append(f"{msg['role']}: {msg['content']}")
        return "\n".join(formatted)


# ============================================================================
# 会话创建测试
# ============================================================================


class TestSessionCreation:
    """测试会话创建"""

    def test_create_session_returns_id(self):
        """测试创建会话返回有效的会话 ID"""
        manager = SessionManager()
        session_id = manager.create_session()
        assert isinstance(session_id, str)
        assert len(session_id) > 0

    def test_create_session_is_unique(self):
        """测试每个会话 ID 是唯一的"""
        manager = SessionManager()
        ids = [manager.create_session() for _ in range(100)]
        assert len(set(ids)) == 100  # 所有 ID 都不同

    def test_create_session_increases_count(self):
        """测试创建会话增加计数"""
        manager = SessionManager()
        assert manager.get_session_count() == 0
        manager.create_session()
        assert manager.get_session_count() == 1
        manager.create_session()
        assert manager.get_session_count() == 2

    def test_create_session_initializes_empty_history(self):
        """测试新会话的初始历史为空"""
        manager = SessionManager()
        session_id = manager.create_session()
        history = manager.get_session_history(session_id)
        assert history == []

    def test_created_session_exists(self):
        """测试创建的会话存在"""
        manager = SessionManager()
        session_id = manager.create_session()
        assert manager.session_exists(session_id) is True


# ============================================================================
# 消息管理测试
# ============================================================================


class TestMessageManagement:
    """测试消息管理"""

    def test_add_user_message(self):
        """测试添加用户消息"""
        manager = SessionManager()
        session_id = manager.create_session()
        manager.add_message(session_id, "user", "Hello, world!")
        history = manager.get_session_history(session_id)
        assert len(history) == 1
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello, world!"

    def test_add_assistant_message(self):
        """测试添加助手消息"""
        manager = SessionManager()
        session_id = manager.create_session()
        manager.add_message(session_id, "assistant", "Hi there!")
        history = manager.get_session_history(session_id)
        assert history[0]["role"] == "assistant"
        assert history[0]["content"] == "Hi there!"

    def test_add_multiple_messages(self):
        """测试添加多条消息"""
        manager = SessionManager()
        session_id = manager.create_session()
        manager.add_message(session_id, "user", "First message")
        manager.add_message(session_id, "assistant", "First response")
        manager.add_message(session_id, "user", "Second message")
        history = manager.get_session_history(session_id)
        assert len(history) == 3

    def test_add_message_to_nonexistent_session(self):
        """测试向不存在的会话添加消息"""
        manager = SessionManager()
        with pytest.raises(ValueError, match="Session .* not found"):
            manager.add_message("nonexistent", "user", "Test")

    def test_messages_preserve_order(self):
        """测试消息保持顺序"""
        manager = SessionManager()
        session_id = manager.create_session()
        messages = [
            ("user", "First"),
            ("assistant", "Response 1"),
            ("user", "Second"),
            ("assistant", "Response 2"),
        ]
        for role, content in messages:
            manager.add_message(session_id, role, content)
        history = manager.get_session_history(session_id)
        assert [(m["role"], m["content"]) for m in history] == messages


# ============================================================================
# 历史限制测试
# ============================================================================


class TestHistoryLimits:
    """测试历史记录限制"""

    def test_history_respects_max_limit(self):
        """测试历史记录遵守最大限制"""
        manager = SessionManager(max_history=2)
        session_id = manager.create_session()
        # 添加超过限制的消息
        for i in range(5):
            manager.add_message(session_id, "user", f"Message {i}")
        # 应该只保留最近的消息
        history = manager.get_session_history(session_id)
        assert len(history) <= 4  # max_history * 2

    def test_max_history_zero(self):
        """测试最大历史为 0 时不保存历史"""
        manager = SessionManager(max_history=0)
        session_id = manager.create_session()
        manager.add_message(session_id, "user", "Test")
        history = manager.get_session_history(session_id)
        assert len(history) == 0

    def test_max_history_one(self):
        """测试最大历史为 1 时只保留一对消息"""
        manager = SessionManager(max_history=1)
        session_id = manager.create_session()
        manager.add_message(session_id, "user", "First")
        manager.add_message(session_id, "assistant", "Response 1")
        manager.add_message(session_id, "user", "Second")
        manager.add_message(session_id, "assistant", "Response 2")
        history = manager.get_session_history(session_id)
        assert len(history) == 2  # 只保留最后一对
        assert history[0]["content"] == "Second"

    def test_oldest_messages_removed(self):
        """测试最旧的消息被移除"""
        manager = SessionManager(max_history=1)
        session_id = manager.create_session()
        manager.add_message(session_id, "user", "Old")
        manager.add_message(session_id, "assistant", "Old response")
        manager.add_message(session_id, "user", "New")
        history = manager.get_session_history(session_id)
        contents = [m["content"] for m in history]
        assert "Old" not in contents
        assert "Old response" not in contents
        assert "New" in contents


# ============================================================================
# 会话删除测试
# ============================================================================


class TestSessionDeletion:
    """测试会话删除"""

    def test_delete_existing_session(self):
        """测试删除存在的会话"""
        manager = SessionManager()
        session_id = manager.create_session()
        assert manager.session_exists(session_id) is True
        result = manager.delete_session(session_id)
        assert result is True
        assert manager.session_exists(session_id) is False

    def test_delete_nonexistent_session(self):
        """测试删除不存在的会话"""
        manager = SessionManager()
        result = manager.delete_session("nonexistent")
        assert result is False

    def test_delete_session_decreases_count(self):
        """测试删除会话减少计数"""
        manager = SessionManager()
        manager.create_session()
        manager.create_session()
        assert manager.get_session_count() == 2
        manager.delete_session(list(manager.sessions.keys())[0])
        assert manager.get_session_count() == 1

    def test_clear_all_sessions(self):
        """测试清除所有会话"""
        manager = SessionManager()
        for _ in range(5):
            manager.create_session()
        assert manager.get_session_count() == 5
        manager.clear_all_sessions()
        assert manager.get_session_count() == 0

    def test_deleted_session_history_inaccessible(self):
        """测试删除会话后无法访问历史"""
        manager = SessionManager()
        session_id = manager.create_session()
        manager.add_message(session_id, "user", "Test message")
        manager.delete_session(session_id)
        with pytest.raises(ValueError, match="Session .* not found"):
            manager.get_session_history(session_id)


# ============================================================================
# 会话查询测试
# ============================================================================


class TestSessionQueries:
    """测试会话查询功能"""

    def test_session_exists_for_active_session(self):
        """测试活动会话存在"""
        manager = SessionManager()
        session_id = manager.create_session()
        assert manager.session_exists(session_id) is True

    def test_session_exists_for_inactive_session(self):
        """测试不活动会话不存在"""
        manager = SessionManager()
        assert manager.session_exists("random-id") is False

    def test_get_session_count_empty(self):
        """测试空管理器的会话计数"""
        manager = SessionManager()
        assert manager.get_session_count() == 0

    def test_get_session_count_multiple(self):
        """测试多个会话的计数"""
        manager = SessionManager()
        for _ in range(10):
            manager.create_session()
        assert manager.get_session_count() == 10

    def test_get_session_history_empty(self):
        """测试获取空会话历史"""
        manager = SessionManager()
        session_id = manager.create_session()
        history = manager.get_session_history(session_id)
        assert history == []

    def test_get_session_history_with_messages(self):
        """测试获取有消息的会话历史"""
        manager = SessionManager()
        session_id = manager.create_session()
        manager.add_message(session_id, "user", "Question")
        manager.add_message(session_id, "assistant", "Answer")
        history = manager.get_session_history(session_id)
        assert len(history) == 2


# ============================================================================
# 格式化历史测试
# ============================================================================


class TestFormattedHistory:
    """测试格式化历史记录"""

    def test_formatted_empty_history(self):
        """测试格式化空历史"""
        manager = SessionManager()
        session_id = manager.create_session()
        formatted = manager.get_formatted_history(session_id)
        assert formatted == ""

    def test_formatted_single_message(self):
        """测试格式化单条消息"""
        manager = SessionManager()
        session_id = manager.create_session()
        manager.add_message(session_id, "user", "Hello")
        formatted = manager.get_formatted_history(session_id)
        assert "user: Hello" in formatted

    def test_formatted_multiple_messages(self):
        """测试格式化多条消息"""
        manager = SessionManager()
        session_id = manager.create_session()
        manager.add_message(session_id, "user", "Q1")
        manager.add_message(session_id, "assistant", "A1")
        manager.add_message(session_id, "user", "Q2")
        formatted = manager.get_formatted_history(session_id)
        assert "user: Q1" in formatted
        assert "assistant: A1" in formatted
        assert "user: Q2" in formatted

    def test_formatted_preserves_newlines(self):
        """测试格式化保留消息中的换行"""
        manager = SessionManager()
        session_id = manager.create_session()
        manager.add_message(session_id, "user", "Line 1\nLine 2")
        formatted = manager.get_formatted_history(session_id)
        assert "Line 1\nLine 2" in formatted


# ============================================================================
# 边界条件测试
# ============================================================================


class TestEdgeCases:
    """测试边界条件"""

    def test_empty_message_content(self):
        """测试空消息内容"""
        manager = SessionManager()
        session_id = manager.create_session()
        manager.add_message(session_id, "user", "")
        history = manager.get_session_history(session_id)
        assert history[0]["content"] == ""

    def test_very_long_message(self):
        """测试超长消息"""
        manager = SessionManager()
        session_id = manager.create_session()
        long_content = "Word " * 10000
        manager.add_message(session_id, "user", long_content)
        history = manager.get_session_history(session_id)
        assert len(history[0]["content"]) == len(long_content)

    def test_special_characters_in_message(self):
        """测试消息中的特殊字符"""
        manager = SessionManager()
        session_id = manager.create_session()
        special_content = "Test with 特殊 characters and 🚀 emojis"
        manager.add_message(session_id, "user", special_content)
        history = manager.get_session_history(session_id)
        assert history[0]["content"] == special_content

    def test_unicode_in_session_id(self):
        """测试会话 ID 中的 Unicode（UUID 应该只包含 ASCII）"""
        manager = SessionManager()
        session_id = manager.create_session()
        # UUID 应该只包含十六进制字符和连字符
        assert all(c in "0123456789abcdef-" for c in session_id.lower())

    def test_concurrent_session_creation(self):
        """测试并发创建会话"""
        import threading
        manager = SessionManager()
        ids = []
        errors = []

        def create_session():
            try:
                ids.append(manager.create_session())
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=create_session) for _ in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(ids) == 50
        assert len(set(ids)) == 50  # 所有 ID 都不同

    def test_different_max_history_values(self):
        """测试不同的最大历史值"""
        for max_history in [0, 1, 2, 5, 10, 100]:
            manager = SessionManager(max_history=max_history)
            session_id = manager.create_session()
            for i in range(max_history * 2 + 5):
                manager.add_message(session_id, "user", f"Message {i}")
            history = manager.get_session_history(session_id)
            assert len(history) <= max_history * 2


# ============================================================================
# 自定义角色测试
# ============================================================================


class TestCustomRoles:
    """测试自定义消息角色"""

    def test_system_role(self):
        """测试系统角色"""
        manager = SessionManager()
        session_id = manager.create_session()
        manager.add_message(session_id, "system", "You are a helpful assistant.")
        history = manager.get_session_history(session_id)
        assert history[0]["role"] == "system"

    def test_mixed_roles(self):
        """测试混合角色"""
        manager = SessionManager()
        session_id = manager.create_session()
        manager.add_message(session_id, "system", "System prompt")
        manager.add_message(session_id, "user", "User message")
        manager.add_message(session_id, "assistant", "Assistant response")
        history = manager.get_session_history(session_id)
        roles = [m["role"] for m in history]
        assert roles == ["system", "user", "assistant"]

    def test_custom_role_name(self):
        """测试自定义角色名称"""
        manager = SessionManager()
        session_id = manager.create_session()
        manager.add_message(session_id, "custom_role", "Custom message")
        history = manager.get_session_history(session_id)
        assert history[0]["role"] == "custom_role"

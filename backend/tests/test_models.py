"""
数据模型单元测试

测试 Pydantic 数据模型的验证、序列化和反序列化。
"""

import pytest
from pydantic import ValidationError, BaseModel
from typing import List, Optional


# ============================================================================
# 导入测试的模型
# ============================================================================


class Lesson(BaseModel):
    """课时模型"""
    lesson_number: int
    title: str
    lesson_link: Optional[str] = None


class Course(BaseModel):
    """课程模型"""
    title: str
    course_link: Optional[str] = None
    instructor: Optional[str] = None
    lessons: List[Lesson] = []


class CourseChunk(BaseModel):
    """文本块模型"""
    content: str
    course_title: str
    lesson_number: Optional[int] = None
    chunk_index: int


# ============================================================================
# Lesson 模型测试
# ============================================================================


class TestLessonModel:
    """测试 Lesson 数据模型"""

    def test_lesson_with_all_fields(self):
        """测试包含所有字段的课时"""
        lesson = Lesson(
            lesson_number=1,
            title="Introduction to Python",
            lesson_link="https://example.com/lesson1"
        )
        assert lesson.lesson_number == 1
        assert lesson.title == "Introduction to Python"
        assert lesson.lesson_link == "https://example.com/lesson1"

    def test_lesson_without_optional_link(self):
        """测试不包含可选链接的课时"""
        lesson = Lesson(
            lesson_number=2,
            title="Variables and Data Types"
        )
        assert lesson.lesson_number == 2
        assert lesson.title == "Variables and Data Types"
        assert lesson.lesson_link is None

    def test_lesson_missing_required_field(self):
        """测试缺少必需字段时抛出验证错误"""
        with pytest.raises(ValidationError):
            Lesson(lesson_number=1)  # 缺少 title

    def test_lesson_invalid_number_type(self):
        """测试无效的课时数字类型"""
        with pytest.raises(ValidationError):
            Lesson(
                lesson_number="one",  # 应该是整数
                title="Test Lesson"
            )

    def test_lesson_serialization(self):
        """测试课时序列化为 JSON"""
        lesson = Lesson(
            lesson_number=1,
            title="Test Lesson",
            lesson_link="https://example.com"
        )
        data = lesson.model_dump()
        assert data == {
            "lesson_number": 1,
            "title": "Test Lesson",
            "lesson_link": "https://example.com"
        }


# ============================================================================
# Course 模型测试
# ============================================================================


class TestCourseModel:
    """测试 Course 数据模型"""

    def test_course_with_all_fields(self):
        """测试包含所有字段的课程"""
        course = Course(
            title="Python Programming",
            course_link="https://example.com/python",
            instructor="Jane Doe",
            lessons=[
                Lesson(lesson_number=1, title="Lesson 1"),
                Lesson(lesson_number=2, title="Lesson 2")
            ]
        )
        assert course.title == "Python Programming"
        assert course.course_link == "https://example.com/python"
        assert course.instructor == "Jane Doe"
        assert len(course.lessons) == 2

    def test_course_minimal(self):
        """测试仅包含必需字段的课程"""
        course = Course(title="Minimal Course")
        assert course.title == "Minimal Course"
        assert course.course_link is None
        assert course.instructor is None
        assert course.lessons == []

    def test_course_empty_lessons_list(self):
        """测试空课时列表"""
        course = Course(title="Course Without Lessons")
        assert course.lessons == []

    def test_course_with_multiple_lessons(self):
        """测试包含多个课时的课程"""
        lessons = [
            Lesson(lesson_number=i, title=f"Lesson {i}")
            for i in range(1, 11)
        ]
        course = Course(title="Complete Course", lessons=lessons)
        assert len(course.lessons) == 10

    def test_course_serialization(self):
        """测试课程序列化包含嵌套的课时"""
        course = Course(
            title="Test Course",
            lessons=[
                Lesson(lesson_number=1, title="L1")
            ]
        )
        data = course.model_dump()
        assert data["title"] == "Test Course"
        assert data["lessons"][0]["lesson_number"] == 1


# ============================================================================
# CourseChunk 模型测试
# ============================================================================


class TestCourseChunkModel:
    """测试 CourseChunk 数据模型"""

    def test_chunk_with_all_fields(self):
        """测试包含所有字段的文本块"""
        chunk = CourseChunk(
            content="This is a sample text chunk.",
            course_title="Introduction to Python",
            lesson_number=1,
            chunk_index=0
        )
        assert chunk.content == "This is a sample text chunk."
        assert chunk.course_title == "Introduction to Python"
        assert chunk.lesson_number == 1
        assert chunk.chunk_index == 0

    def test_chunk_without_lesson_number(self):
        """测试不包含课时的文本块"""
        chunk = CourseChunk(
            content="Generic course content",
            course_title="General Course",
            chunk_index=5
        )
        assert chunk.lesson_number is None

    def test_chunk_empty_content(self):
        """测试空内容的文本块"""
        chunk = CourseChunk(
            content="",
            course_title="Test Course",
            chunk_index=0
        )
        assert chunk.content == ""

    def test_chunk_long_content(self):
        """测试长内容的文本块"""
        long_content = "Word " * 500  # 约 3000 字符
        chunk = CourseChunk(
            content=long_content,
            course_title="Test Course",
            chunk_index=0
        )
        assert len(chunk.content) == len(long_content)

    def test_chunk_special_characters(self):
        """测试包含特殊字符的文本块"""
        special_content = "Content with 特殊字符 and émojis 🚀"
        chunk = CourseChunk(
            content=special_content,
            course_title="Test Course",
            chunk_index=0
        )
        assert chunk.content == special_content

    def test_chunk_negative_index(self):
        """测试负数的块索引（边缘情况）"""
        chunk = CourseChunk(
            content="Test content",
            course_title="Test Course",
            chunk_index=-1
        )
        assert chunk.chunk_index == -1


# ============================================================================
# 模型组合测试
# ============================================================================


class TestModelCombinations:
    """测试多个模型组合使用的情况"""

    def test_course_with_nested_lessons(self):
        """测试课程与课时的嵌套关系"""
        course = Course(
            title="Complete Python Course",
            instructor="Dr. Smith",
            lessons=[
                Lesson(
                    lesson_number=1,
                    title="Getting Started",
                    lesson_link="https://example.com/l1"
                ),
                Lesson(
                    lesson_number=2,
                    title="Advanced Topics",
                    lesson_link="https://example.com/l2"
                )
            ]
        )
        assert course.lessons[0].title == "Getting Started"
        assert course.lessons[1].lesson_number == 2

    def test_chunk_refers_to_course_and_lesson(self):
        """测试文本块引用课程和课时"""
        chunk = CourseChunk(
            content="Functions are reusable blocks of code.",
            course_title="Python Basics",
            lesson_number=3,
            chunk_index=2
        )
        assert chunk.course_title == "Python Basics"
        assert chunk.lesson_number == 3

    def test_multiple_chunks_same_lesson(self):
        """测试同一课时的多个文本块"""
        chunks = [
            CourseChunk(
                content=f"Chunk {i} content",
                course_title="Python Course",
                lesson_number=1,
                chunk_index=i
            )
            for i in range(5)
        ]
        assert all(c.course_title == "Python Course" for c in chunks)
        assert all(c.lesson_number == 1 for c in chunks)
        assert [c.chunk_index for c in chunks] == [0, 1, 2, 3, 4]


# ============================================================================
# JSON 序列化和反序列化测试
# ============================================================================


class TestJSONSerialization:
    """测试模型的 JSON 序列化和反序列化"""

    def test_lesson_to_json(self):
        """测试课时转换为 JSON"""
        lesson = Lesson(lesson_number=1, title="Test")
        json_str = lesson.model_dump_json()
        assert "lesson_number" in json_str
        assert "Test" in json_str

    def test_lesson_from_json(self):
        """测试从 JSON 创建课时"""
        json_str = '{"lesson_number": 1, "title": "Test", "lesson_link": null}'
        lesson = Lesson.model_validate_json(json_str)
        assert lesson.lesson_number == 1
        assert lesson.title == "Test"

    def test_course_to_json(self):
        """测试课程转换为 JSON"""
        course = Course(
            title="Test Course",
            lessons=[Lesson(lesson_number=1, title="L1")]
        )
        json_str = course.model_dump_json()
        assert "Test Course" in json_str

    def test_chunk_to_json(self):
        """测试文本块转换为 JSON"""
        chunk = CourseChunk(
            content="Test content",
            course_title="Test Course",
            chunk_index=0
        )
        json_str = chunk.model_dump_json()
        assert "Test content" in json_str


# ============================================================================
# 边界条件和特殊情况测试
# ============================================================================


class TestEdgeCases:
    """测试边界条件和特殊情况"""

    def test_lesson_zero_number(self):
        """测试课时时为 0"""
        lesson = Lesson(lesson_number=0, title="Pre-course")
        assert lesson.lesson_number == 0

    def test_lesson_negative_number(self):
        """测试负数的课时"""
        lesson = Lesson(lesson_number=-1, title="Intro")
        assert lesson.lesson_number == -1

    def test_course_empty_title(self):
        """测试空标题的课程"""
        course = Course(title="")
        assert course.title == ""

    def test_very_long_title(self):
        """测试超长标题"""
        long_title = "A" * 1000
        course = Course(title=long_title)
        assert len(course.title) == 1000

    def test_unicode_in_all_fields(self):
        """测试所有字段支持 Unicode"""
        lesson = Lesson(
            lesson_number=1,
            title="课程标题 中文标题",
            lesson_link="https://example.com/路径"
        )
        assert "中文" in lesson.title

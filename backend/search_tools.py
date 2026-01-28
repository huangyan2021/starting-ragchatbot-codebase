from abc import ABC, abstractmethod
from typing import Any

from vector_store import SearchResults, VectorStore


class Tool(ABC):
    """Abstract base class for all tools"""

    @abstractmethod
    def get_tool_definition(self) -> dict[str, Any]:
        """Return Anthropic tool definition for this tool"""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Execute the tool with given parameters"""
        pass


class CourseSearchTool(Tool):
    """Tool for searching course content with semantic course name matching"""

    def __init__(self, vector_store: VectorStore):
        self.store = vector_store
        self.last_sources = []  # Track sources from last search

    def get_tool_definition(self) -> dict[str, Any]:
        """Return Anthropic tool definition for this tool"""
        return {
            "name": "search_course_content",
            "description": "Search course materials with smart course name matching and lesson filtering",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "What to search for in the course content",
                    },
                    "course_name": {
                        "type": "string",
                        "description": "Course title (partial matches work, e.g. 'MCP', 'Introduction')",
                    },
                    "lesson_number": {
                        "type": "integer",
                        "description": "Specific lesson number to search within (e.g. 1, 2, 3)",
                    },
                },
                "required": ["query"],
            },
        }

    def execute(
        self, query: str, course_name: str | None = None, lesson_number: int | None = None
    ) -> str:
        """
        Execute the search tool with given parameters.

        Args:
            query: What to search for
            course_name: Optional course filter
            lesson_number: Optional lesson filter

        Returns:
            Formatted search results or error message
        """

        # Use the vector store's unified search interface
        results = self.store.search(
            query=query, course_name=course_name, lesson_number=lesson_number
        )

        # Handle errors
        if results.error:
            return results.error

        # Handle empty results
        if results.is_empty():
            filter_info = ""
            if course_name:
                filter_info += f" in course '{course_name}'"
            if lesson_number:
                filter_info += f" in lesson {lesson_number}"
            return f"No relevant content found{filter_info}."

        # Format and return results
        return self._format_results(results)

    def _format_results(self, results: SearchResults) -> str:
        """Format search results with course and lesson context"""
        formatted = []
        sources = []  # Track sources for the UI
        source_links = []  # Track links for sources

        for doc, meta in zip(results.documents, results.metadata, strict=False):
            course_title = meta.get("course_title", "unknown")
            lesson_num = meta.get("lesson_number")

            # Build context header
            header = f"[{course_title}"
            if lesson_num is not None:
                header += f" - Lesson {lesson_num}"
            header += "]"

            # Track source for the UI
            source = course_title
            if lesson_num is not None:
                source += f" - Lesson {lesson_num}"
            sources.append(source)

            # Get link for this source
            link = None
            if lesson_num is not None:
                # Try to get lesson link first
                link = self.store.get_lesson_link(course_title, lesson_num)
            if not link:
                # Fall back to course link if no lesson link
                link = self.store.get_course_link(course_title)
            source_links.append(link)

            formatted.append(f"{header}\n{doc}")

        # Store sources and links for retrieval
        self.last_sources = sources
        self.last_source_links = source_links

        return "\n\n".join(formatted)


class CourseOutlineTool(Tool):
    """Tool for retrieving course outline information including lessons"""

    def __init__(self, vector_store: VectorStore):
        self.store = vector_store
        self.last_sources = []  # Track sources from last search

    def get_tool_definition(self) -> dict[str, Any]:
        """Return Anthropic tool definition for this tool"""
        return {
            "name": "get_course_outline",
            "description": "Get course outline with complete lesson list and metadata",
            "input_schema": {
                "type": "object",
                "properties": {
                    "course_title": {
                        "type": "string",
                        "description": "Course title (partial matches work, e.g. 'MCP', 'Introduction')",
                    }
                },
                "required": ["course_title"],
            },
        }

    def execute(self, course_title: str) -> str:
        """
        Execute the course outline tool.

        Args:
            course_title: Course title to search for

        Returns:
            Formatted course outline or error message
        """

        # Get course metadata from vector store
        course_info = self.store.get_course_by_title(course_title)

        # Handle course not found
        if not course_info:
            return f"Course '{course_title}' not found. Available courses: {', '.join(self.store.get_all_course_titles())}"

        # Format and return course outline
        return self._format_course_outline(course_info)

    def _format_course_outline(self, course_info: dict[str, Any]) -> str:
        """Format course outline with lessons"""
        course_title = course_info.get("title", "Unknown Course")
        course_link = course_info.get("link", "No link available")
        instructor = course_info.get("instructor", "Unknown instructor")
        lessons = course_info.get("lessons", [])

        # Track source for the UI
        self.last_sources = [course_title]
        self.last_source_links = [course_link]

        formatted = []
        formatted.append(f"**Course:** {course_title}")
        formatted.append(f"**Instructor:** {instructor}")
        formatted.append(f"**Course Link:** {course_link}")
        formatted.append("")

        if lessons:
            formatted.append("**Lessons:**")
            for lesson in lessons:
                lesson_num = lesson.get("number", "N/A")
                lesson_title = lesson.get("title", "No title")
                lesson_link = lesson.get("link", "No link available")
                formatted.append(f"  {lesson_num}. {lesson_title}")
                if lesson_link and lesson_link != "No link available":
                    formatted.append(f"     Link: {lesson_link}")
            formatted.append("")
            formatted.append(f"**Total Lessons:** {len(lessons)}")
        else:
            formatted.append("**No lessons available**")

        return "\n".join(formatted)


class ToolManager:
    """Manages available tools for the AI"""

    def __init__(self):
        self.tools = {}

    def register_tool(self, tool: Tool):
        """Register any tool that implements the Tool interface"""
        tool_def = tool.get_tool_definition()
        tool_name = tool_def.get("name")
        if not tool_name:
            raise ValueError("Tool must have a 'name' in its definition")
        self.tools[tool_name] = tool

    def get_tool_definitions(self) -> list:
        """Get all tool definitions for Anthropic tool calling"""
        return [tool.get_tool_definition() for tool in self.tools.values()]

    def execute_tool(self, tool_name: str, **kwargs) -> str:
        """Execute a tool by name with given parameters"""
        if tool_name not in self.tools:
            return f"Tool '{tool_name}' not found"

        return self.tools[tool_name].execute(**kwargs)

    def get_last_sources(self) -> list:
        """Get sources from the last search operation"""
        # Check all tools for last_sources attribute
        for tool in self.tools.values():
            if hasattr(tool, "last_sources") and tool.last_sources:
                return tool.last_sources
        return []

    def get_last_source_links(self) -> list:
        """Get source links from the last search operation"""
        # Check all tools for last_source_links attribute
        for tool in self.tools.values():
            if hasattr(tool, "last_source_links") and tool.last_source_links:
                return tool.last_source_links
        return []

    def reset_sources(self):
        """Reset sources from all tools that track sources"""
        for tool in self.tools.values():
            if hasattr(tool, "last_sources"):
                tool.last_sources = []
            if hasattr(tool, "last_source_links"):
                tool.last_source_links = []

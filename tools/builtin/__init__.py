from tools.builtin.file_editor import EditTool
from tools.builtin.pattern_matcher import GlobTool
from tools.builtin.text_search import GrepTool
from tools.builtin.directory_listing import ListDirTool
from tools.builtin.persistent_memory import MemoryTool
from tools.builtin.file_reader import ReadFileTool
from tools.builtin.shell_executor import ShellTool
from tools.builtin.task_manager import TodosTool
from tools.builtin.web_fetcher import WebFetchTool
from tools.builtin.web_searcher import WebSearchTool
from tools.builtin.file_writer import WriteFileTool
from tools.builtin.test_generator import TestGeneratorTool
from tools.builtin.test_executor import TestExecutorTool
from tools.builtin.github_tools import GitHubIssueTool, GitHubPRTool, GitHubCodeSearchTool

__all__ = [
    "ReadFileTool",
    "WriteFileTool",
    "EditTool",
    "ShellTool",
    "ListDirTool",
    "GrepTool",
    "GlobTool",
    "WebSearchTool",
    "WebFetchTool",
    "TodosTool",
    "MemoryTool",
    "TestGeneratorTool",
    "TestExecutorTool",
    "GitHubIssueTool",
    "GitHubPRTool",
    "GitHubCodeSearchTool",
]


def get_all_builtin_tools() -> list[type]:
    return [
        ReadFileTool,
        WriteFileTool,
        EditTool,
        ShellTool,
        ListDirTool,
        GrepTool,
        GlobTool,
        WebSearchTool,
        WebFetchTool,
        TodosTool,
        MemoryTool,
        TestGeneratorTool,
        TestExecutorTool,
        GitHubIssueTool,
        GitHubPRTool,
        GitHubCodeSearchTool,
    ]

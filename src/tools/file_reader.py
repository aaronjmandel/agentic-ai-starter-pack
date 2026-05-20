"""File reader tool for reading local files."""

from pathlib import Path
from typing import Any

from src.tools.base import BaseTool


class FileReaderTool(BaseTool):
    """Read the contents of a local file."""

    @property
    def name(self) -> str:
        return "file_reader"

    @property
    def description(self) -> str:
        return "Read the contents of a file at the given path."

    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to read",
                }
            },
            "required": ["path"],
        }

    async def execute(self, **kwargs: Any) -> str:
        file_path = kwargs.get("path", "")
        if not file_path:
            return "Error: No path provided."

        path = Path(file_path)
        if not path.exists():
            return f"Error: File not found: {file_path}"
        if not path.is_file():
            return f"Error: Not a file: {file_path}"

        try:
            content = path.read_text(encoding="utf-8")
            max_chars = 10_000
            if len(content) > max_chars:
                return content[:max_chars] + f"\n\n... [truncated, {len(content)} total chars]"
            return content
        except Exception as e:
            return f"Error reading file: {e}"

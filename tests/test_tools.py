"""Tests for tool implementations."""

import pytest

from src.tools.calculator import CalculatorTool
from src.tools.file_reader import FileReaderTool
from src.tools.web_search import WebSearchTool


@pytest.fixture
def calculator() -> CalculatorTool:
    return CalculatorTool()


@pytest.fixture
def web_search() -> WebSearchTool:
    return WebSearchTool()


@pytest.fixture
def file_reader() -> FileReaderTool:
    return FileReaderTool()


class TestCalculatorTool:
    async def test_basic_addition(self, calculator: CalculatorTool) -> None:
        result = await calculator.execute(expression="2 + 3")
        assert result == "5.0"

    async def test_complex_expression(self, calculator: CalculatorTool) -> None:
        result = await calculator.execute(expression="(10 + 5) * 3 - 2")
        assert result == "43.0"

    async def test_power(self, calculator: CalculatorTool) -> None:
        result = await calculator.execute(expression="2 ** 8")
        assert result == "256.0"

    async def test_division(self, calculator: CalculatorTool) -> None:
        result = await calculator.execute(expression="10 / 3")
        assert float(result) == pytest.approx(3.333, abs=0.01)

    async def test_empty_expression(self, calculator: CalculatorTool) -> None:
        result = await calculator.execute(expression="")
        assert "Error" in result

    async def test_invalid_expression(self, calculator: CalculatorTool) -> None:
        result = await calculator.execute(expression="import os")
        assert "Error" in result

    def test_anthropic_schema(self, calculator: CalculatorTool) -> None:
        schema = calculator.to_anthropic_schema()
        assert schema["name"] == "calculator"
        assert "input_schema" in schema
        assert "expression" in schema["input_schema"]["properties"]


class TestWebSearchTool:
    async def test_returns_stub_results(self, web_search: WebSearchTool) -> None:
        result = await web_search.execute(query="test query")
        assert "test query" in result

    async def test_empty_query(self, web_search: WebSearchTool) -> None:
        result = await web_search.execute(query="")
        assert "Error" in result

    def test_anthropic_schema(self, web_search: WebSearchTool) -> None:
        schema = web_search.to_anthropic_schema()
        assert schema["name"] == "web_search"
        assert "query" in schema["input_schema"]["properties"]


class TestFileReaderTool:
    async def test_read_existing_file(self, file_reader: FileReaderTool, tmp_path: pytest.TempPathFactory) -> None:
        test_file = tmp_path / "test.txt"  # type: ignore[operator]
        test_file.write_text("hello world")
        result = await file_reader.execute(path=str(test_file))
        assert result == "hello world"

    async def test_file_not_found(self, file_reader: FileReaderTool) -> None:
        result = await file_reader.execute(path="/nonexistent/file.txt")
        assert "Error" in result

    async def test_empty_path(self, file_reader: FileReaderTool) -> None:
        result = await file_reader.execute(path="")
        assert "Error" in result

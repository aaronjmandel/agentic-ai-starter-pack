"""Prompt template loader using Jinja2."""

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

_PROMPTS_DIR = Path(__file__).parent / "templates"


def _get_env() -> Environment:
    """Create a Jinja2 environment pointing at the templates directory."""
    return Environment(
        loader=FileSystemLoader(str(_PROMPTS_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


def load_prompt(template_name: str, **variables: Any) -> str:
    """Load and render a prompt template.

    Args:
        template_name: Name of the template file (without .j2 extension).
        **variables: Variables to substitute into the template.

    Returns:
        Rendered prompt string.

    Raises:
        TemplateNotFound: If the template file doesn't exist.
    """
    env = _get_env()
    try:
        template = env.get_template(f"{template_name}.j2")
    except TemplateNotFound:
        raise TemplateNotFound(
            f"Prompt template '{template_name}.j2' not found in {_PROMPTS_DIR}"
        )
    return template.render(**variables)

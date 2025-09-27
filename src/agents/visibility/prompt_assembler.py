"""Assemble prompt payloads for model execution."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def load_template(path: Path) -> str:
    """Read a prompt template from disk."""

    return path.read_text(encoding="utf-8")


def render_template(template: str, **context: Any) -> str:
    """Render a template using naive string replacement."""

    rendered = template
    for key, value in context.items():
        placeholder = f"{{{{ {key} }}}}"
        if isinstance(value, (dict, list)):
            value = json.dumps(value, indent=2)
        rendered = rendered.replace(placeholder, str(value))
    return rendered


def build_prompt(template_path: Path, **context: Any) -> Dict[str, str]:
    """Couple a system template with runtime context for the model runner."""

    template = load_template(template_path)
    message = render_template(template, **context)
    return {
        "template": str(template_path),
        "message": message,
    }


__all__ = ["load_template", "render_template", "build_prompt"]

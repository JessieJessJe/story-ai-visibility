"""Lightweight pytest stand-in for offline testing."""

from __future__ import annotations

import importlib.util
import inspect
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Iterable, List

DEFAULT_TEST_PATH = Path("tests")


@dataclass
class TestResult:
    name: str
    passed: bool
    error: BaseException | None = None


def _iter_test_files(paths: Iterable[Path]) -> Iterable[Path]:
    for path in paths:
        if path.is_file() and path.suffix == ".py":
            yield path.resolve()
        elif path.is_dir():
            for file_path in sorted(path.rglob("test_*.py")):
                if file_path.is_file():
                    yield file_path.resolve()


def _load_module(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import test module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = module
    spec.loader.exec_module(module)
    return module


def _call_test_functions(module: ModuleType) -> List[TestResult]:
    results: List[TestResult] = []
    for name, obj in vars(module).items():
        if name.startswith("test_") and inspect.isfunction(obj):
            try:
                obj()
            except BaseException as exc:  # pragma: no cover - error path
                results.append(TestResult(name=f"{module.__name__}.{name}", passed=False, error=exc))
            else:
                results.append(TestResult(name=f"{module.__name__}.{name}", passed=True))
    return results


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    targets = [Path(arg) for arg in argv] if argv else [DEFAULT_TEST_PATH]

    all_results: List[TestResult] = []
    for file_path in _iter_test_files(targets):
        module = _load_module(file_path)
        all_results.extend(_call_test_functions(module))

    failures = [result for result in all_results if not result.passed]
    for failure in failures:
        error = failure.error
        if error is not None:
            print(f"FAILED: {failure.name}")
            print("-" * 60)
            print("Traceback (most recent call last):")
            tb_stack = getattr(error, "__traceback__", None)
            if tb_stack is not None:
                import traceback as tb  # lazy import for errors

                tb.print_tb(tb_stack)
            print(f"{error.__class__.__name__}: {error}")
            print()

    total = len(all_results)
    passed = total - len(failures)
    print(f"Ran {total} tests: {passed} passed, {len(failures)} failed.")
    return 0 if not failures else 1


__all__ = ["main", "TestResult"]

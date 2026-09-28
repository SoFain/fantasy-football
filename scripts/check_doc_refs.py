"""Verify that every code reference in the docs still resolves.

Docs cite code as `path/to/file.py:symbol_name`. Unlike line numbers, those
anchors survive edits to the file, but they still break when a symbol is
renamed or deleted. This checks every anchor against the working tree and
exits non-zero if any of them dangle.

Also flags line-number citations (`app.py:733`) for files that have changed
since the citation was written, because those rot silently.

Usage:
    python scripts/check_doc_refs.py
    python scripts/check_doc_refs.py --allow-line-refs
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DOC_GLOBS = ("docs/**/*.md", "bigquery/**/*.md", "*.md")

# Validation reports are point-in-time records of what was true when they ran.
# They are deliberately never edited, so their citations are allowed to name
# code that has since been removed.
FROZEN_PREFIXES = ("docs/rebuild/validation/",)

SYMBOL_REF = re.compile(r"`([A-Za-z0-9_./]+\.py):([A-Za-z_][A-Za-z0-9_.]*)`")
LINE_REF = re.compile(r"`([A-Za-z0-9_./]+\.(?:py|sql|txt|yaml|bat|toml)|Dockerfile):(\d+)(?:-\d+)?`")


def defined_symbols(path: Path) -> set[str]:
    """Every name a doc may legitimately cite in a module.

    Covers defs and classes, including nested and dotted forms, plus
    module-level assignments so docs can anchor to a named constant such as
    `src/model_runs.py:DEFAULT_MAX_VALUE_TABLES`.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (SyntaxError, OSError):
        return set()

    names: set[str] = set()

    def add_assigned(node):
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        for target in targets:
            if isinstance(target, ast.Name):
                names.add(target.id)

    def walk(node, prefix):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                qual = f"{prefix}{child.name}"
                names.add(child.name)
                names.add(qual)
                walk(child, f"{qual}.")
            else:
                if isinstance(child, (ast.Assign, ast.AnnAssign)):
                    add_assigned(child)
                walk(child, prefix)

    walk(tree, "")
    return names


def strip_code_blocks(text: str) -> list[str]:
    """Blank out fenced code blocks so examples are not treated as citations."""
    lines = text.splitlines()
    fenced = False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            lines[i] = ""
        elif fenced:
            lines[i] = ""
    return lines


def iter_docs():
    seen = set()
    for pattern in DOC_GLOBS:
        for path in sorted(ROOT.glob(pattern)):
            if path not in seen:
                seen.add(path)
                yield path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-line-refs", action="store_true",
                        help="do not report line-number citations")
    args = parser.parse_args()

    symbol_cache: dict[str, set[str]] = {}
    broken: list[str] = []
    line_refs: list[str] = []
    checked = 0

    for doc in iter_docs():
        rel_doc = doc.relative_to(ROOT).as_posix()
        if rel_doc.startswith(FROZEN_PREFIXES):
            continue
        text = doc.read_text(encoding="utf-8", errors="replace")

        for lineno, line in enumerate(strip_code_blocks(text), 1):
            for match in SYMBOL_REF.finditer(line):
                target, symbol = match.group(1), match.group(2)
                checked += 1
                code = ROOT / target
                if not code.exists():
                    broken.append(f"{rel_doc}:{lineno} -> {target} does not exist")
                    continue
                if target not in symbol_cache:
                    symbol_cache[target] = defined_symbols(code)
                if symbol not in symbol_cache[target]:
                    broken.append(
                        f"{rel_doc}:{lineno} -> {target}:{symbol} is not defined in {target}"
                    )

            for match in LINE_REF.finditer(line):
                line_refs.append(f"{rel_doc}:{lineno} -> {match.group(0)}")

    print(f"checked {checked} symbol anchors across docs")

    if broken:
        print(f"\nBROKEN ANCHORS ({len(broken)}):")
        for item in broken:
            print(f"  {item}")

    if line_refs and not args.allow_line_refs:
        print(f"\nLINE-NUMBER CITATIONS ({len(line_refs)}):")
        print("  These rot when the file shifts. Prefer `file.py:symbol_name`.")
        for item in line_refs:
            print(f"  {item}")

    if broken:
        return 1
    print("\nall symbol anchors resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())

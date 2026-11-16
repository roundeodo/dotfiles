#!/usr/bin/env python3
import re
import shutil
import subprocess
import sys


VERIBLE_FLAGS = [
    "--inplace",
    "--struct_union_members_alignment=align",
    "--port_declarations_alignment=align",
    "--case_items_alignment=align",
    "--assignment_statement_alignment=align",
    "--enum_assignment_statement_alignment=align",
]

LOCALPARAM_RE = re.compile(
    r"^(\s*)"
    r"(localparam\s+(?:logic(?:\s+\[[^\]]+\])?\s+)?)"
    r"([A-Za-z_][A-Za-z0-9_$]*)"
    r"\s*=\s*"
    r"(.+?)"
    r";"
    r"(\s*//.*)?$"
)

PROCEDURAL_ASSIGNMENT_RE = re.compile(
    r"^(\s*)"
    r"([A-Za-z_][A-Za-z0-9_$]*"
    r"(?:(?:\.[A-Za-z_][A-Za-z0-9_$]*)|(?:\[[^\]]+\]))*)"
    r"\s*(<=|=(?!=))\s*"
    r"(.*)$"
)


def align_localparam_blocks(text: str) -> str:
    lines = text.splitlines()
    out = []
    block = []

    def flush_block() -> None:
        nonlocal block
        if not block:
            return

        entries = []
        for line in block:
            match = LOCALPARAM_RE.match(line)
            if match is None:
                out.extend(block)
                block = []
                return
            indent, prefix, name, value, comment = match.groups()
            entries.append(
                {
                    "indent": indent,
                    "prefix": prefix,
                    "name": name,
                    "value": value.rstrip(),
                    "comment": comment or "",
                }
            )

        prefix_w = max(len(item["prefix"]) for item in entries)
        name_w = max(len(item["name"]) for item in entries)
        value_w = max(len(item["value"]) for item in entries)

        for item in entries:
            line = (
                f"{item['indent']}"
                f"{item['prefix'].ljust(prefix_w)}"
                f"{item['name'].ljust(name_w)}"
                f" = "
                f"{item['value'].ljust(value_w)};"
            )
            if item["comment"]:
                line += item["comment"]
            out.append(line.rstrip())

        block = []

    for line in lines:
        if LOCALPARAM_RE.match(line):
            block.append(line)
        else:
            flush_block()
            out.append(line)

    flush_block()
    trailing_newline = "\n" if text.endswith("\n") else ""
    return "\n".join(out) + trailing_newline


def align_procedural_assignment_blocks(text: str) -> str:
    lines = text.splitlines()
    out = []
    index = 0

    while index < len(lines):
        block = []
        cursor = index

        while cursor < len(lines):
            match = PROCEDURAL_ASSIGNMENT_RE.match(lines[cursor])
            if match is None:
                break

            indent, lhs, operator, first_rhs = match.groups()
            statement_lines = [first_rhs]
            cursor += 1

            while not any(";" in part for part in statement_lines):
                if cursor >= len(lines):
                    break
                statement_lines.append(lines[cursor])
                cursor += 1

            if not any(";" in part for part in statement_lines):
                break

            block.append(
                {
                    "indent": indent,
                    "lhs": lhs,
                    "operator": operator,
                    "rhs_lines": statement_lines,
                }
            )

        if len(block) < 2:
            out.append(lines[index])
            index += 1
            continue

        lhs_width = max(len(item["lhs"]) for item in block)
        operator_width = max(len(item["operator"]) for item in block)

        for item in block:
            prefix = (
                f"{item['indent']}"
                f"{item['lhs'].ljust(lhs_width)} "
                f"{item['operator'].ljust(operator_width)} "
            )
            out.append((prefix + item["rhs_lines"][0].strip()).rstrip())
            # Verible already indents nested expressions and wrapped lines.
            # Keep that indentation when aligning the assignment's first line.
            for continuation in item["rhs_lines"][1:]:
                out.append(continuation.rstrip())

        index = cursor

    trailing_newline = "\n" if text.endswith("\n") else ""
    return "\n".join(out) + trailing_newline


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: sv_format_wrapper.py <file>", file=sys.stderr)
        return 2

    path = sys.argv[1]
    verible = shutil.which("verible-verilog-format")
    if verible is None:
        print("verible-verilog-format not found in PATH", file=sys.stderr)
        return 127

    subprocess.run([verible, *VERIBLE_FLAGS, path], check=True)

    with open(path, "r", encoding="utf-8") as fp:
        text = fp.read()
    aligned = align_localparam_blocks(text)
    aligned = align_procedural_assignment_blocks(aligned)
    if aligned != text:
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(aligned)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Flag lines that break work-common.md's "How you document" and "How you code" rules, in the files given.

  python3 scripts/style-check.py <file> ...

Checks:
  x-not-y   the rhetorical "X, not Y" construction and its relatives ("instead of", "rather than")
  dash      en dash or em dash (the rule: hyphens only, unless the user's own words carry a dash)
  word      hedge words, epithets and difficulty words the rules forbid
  we        first person plural
  args      an argument list split across lines with several arguments on one line
            (the rule: one line, or one argument per line)

The checks are patterns: every hit needs a reader's judgement. A negation that is itself the statement
("output must not differ") is allowed, and code inside the file you edit keeps the file's own style.
"""
import re
import sys
from pathlib import Path

PATTERNS = {
    "x-not-y": re.compile(r",\s+not\s|\s-\s*not\s|\(not\s|\bnot\b[^.;]{0,80}\bbut\b|\brather than\b|\binstead of\b|\bnot only\b"),
    "dash": re.compile("[\u2013\u2014]"),
    "word": re.compile(
        r"\b(very|pretty|rather|actually|simply|just|easily|easy|obvious|obviously|straightforward|trivial|basically"
        r"|finally|honest|clever|please|kindly)\b",
        re.I,
    ),
    "we": re.compile(r"\b(we|us|our)\b", re.I),
}
C_LIKE = (".c", ".cc", ".cxx", ".cpp", ".h", ".hh", ".hpp")


def packed_argument_lines(path, lines):
    """Lines inside an open argument list that carry two or more arguments while the list spans several lines."""
    depth = 0
    in_docstring = False
    for line_i, line in enumerate(lines, 1):
        # Parentheses inside a Python docstring would throw the depth count off: skip docstring lines.
        if path.suffix == ".py" and (in_docstring or line.lstrip().startswith(('"""', "r\"\"\""))):
            quotes = line.count('"""')
            in_docstring = (quotes % 2 == 1) != in_docstring
            continue
        code = line.split("//")[0] if path.suffix in C_LIKE else line.split(" #")[0]
        code = re.sub(r'"(\\.|[^"\\])*"|\'(\\.|[^\'\\])*\'', '""', code)
        continues_list = depth > 0
        depth = max(depth + code.count("(") - code.count(")"), 0)
        leaves_list_open = depth > 0 and code.rstrip().endswith(",")
        if not (continues_list or leaves_list_open):
            continue
        level, commas = 0, 0
        for ch in code:
            if ch in "([{":
                level += 1
            elif ch in ")]}":
                level -= 1
            elif ch == "," and level <= (0 if continues_list else 1):
                commas += 1
        if commas >= 2:
            yield line_i, line


def main():
    for name in sys.argv[1:]:
        path = Path(name)
        lines = path.read_text(errors="replace").splitlines()
        for line_i, line in enumerate(lines, 1):
            for check, pattern in PATTERNS.items():
                if pattern.search(line):
                    print(f"{check}\t{name}:{line_i}\t{line.strip()[:200]}")
        if path.suffix in C_LIKE + (".py",):
            for line_i, line in packed_argument_lines(path, lines):
                print(f"args\t{name}:{line_i}\t{line.strip()[:200]}")


if __name__ == "__main__":
    main()

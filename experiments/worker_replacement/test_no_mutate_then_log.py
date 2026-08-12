"""A log line must not interpolate a value the same block just overwrote.

THE DEFECT THIS CATCHES. `RefineTaskAction.execute` assigned then logged:

    task.description = self.new_description
    updates.append(f"description updated from {task.description} to ...")

Both sides interpolate to the **same** value, so the record reads "updated from X
to X" and **the pre-refinement value is destroyed at source.** Three fields had
it — description, duration, cost. Any measurement of specification effort is a
delta, and the action log is the parsed record, so this removes the "before" side
of every such measurement. Not recoverable from the log; only from per-timestep
task snapshots, if retained.

WHY A RULE RATHER THAN THREE FIXES. This is the fifth instance of a derived
record asserting more than its input determines — `tool_calls.json`'s scope,
`success: null` conflating refused with not-attempted, the reader's `unjoined`
asserting a cause, `effective_status` claiming a composite it inherits a gap
from, and this. The general class is judgement-dependent. **This sub-pattern is
not:** mutation followed, in the same block, by a format string reading the
mutated attribute is decidable from the AST alone.

**Zero false positives across `manager_agent_gym/` when written**, flagging
exactly the three known defects. Scoping matters for that: attributes assigned
inside an `if` body are checked against that body, not the enclosing one, so
`logger.info(f"Task {task.name} …")` after a conditional rename is not flagged —
it states a current value and claims no "before".

The correct pattern already existed twenty lines below the defect, in the same
function: `additional_instructions` captures `old_instruction` before
overwriting. So this is not a missing idiom; it is an idiom applied unevenly,
which is what a mechanical check is for.
"""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "manager_agent_gym"


def _attr_key(node: ast.AST) -> str | None:
    """`obj.attr` for a simple attribute access, else None."""
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        return f"{node.value.id}.{node.attr}"
    return None


def _scan_block(body: list[ast.stmt], path: str, hits: list[tuple[str, int, int, str]]) -> None:
    """Flag reads of an attribute this same block already assigned."""
    assigned: dict[str, int] = {}
    for stmt in body:
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                key = _attr_key(target)
                if key:
                    assigned[key] = stmt.lineno
        for node in ast.walk(stmt):
            if isinstance(node, ast.FormattedValue):
                key = _attr_key(node.value)
                if key and key in assigned and stmt.lineno > assigned[key]:
                    hits.append((path, assigned[key], stmt.lineno, key))
        for node in ast.walk(stmt):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.With)):
                _scan_block(node.body, path, hits)


def find_mutate_then_log(root: Path) -> list[tuple[str, int, int, str]]:
    hits: list[tuple[str, int, int, str]] = []
    for path in sorted(root.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text())
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                _scan_block(node.body, str(path), hits)
    return sorted(set(hits))


def test_no_log_line_reads_a_value_it_just_overwrote():
    hits = find_mutate_then_log(ROOT)
    assert not hits, "\n".join(
        f"{p}:{log} interpolates {key} assigned at :{assign} "
        f"— both sides render the same value and the 'before' is lost"
        for p, assign, log, key in hits
    )


def test_the_rule_detects_the_defect_it_was_written_for():
    """The rule must fail on the original shape, or it proves nothing.

    Expected value is the source text of the defect as it stood, not the
    checker's own output — a rule tested only against a clean tree cannot be
    distinguished from a rule that never fires.
    """
    source = (
        "def execute(self, task):\n"
        "    updates = []\n"
        "    if self.new_description:\n"
        "        task.description = self.new_description\n"
        "        updates.append(\n"
        "            f'description updated from {task.description} to "
        "{self.new_description}'\n"
        "        )\n"
    )
    tree = ast.parse(source)
    hits: list[tuple[str, int, int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            _scan_block(node.body, "<defect>", hits)
    assert hits, "the rule does not detect the shape it exists to detect"
    assert any(key == "task.description" for _, _, _, key in hits)


def test_the_rule_does_not_flag_capture_before_assign():
    """The corrected idiom must pass, or the rule is unusable."""
    source = (
        "def execute(self, task):\n"
        "    updates = []\n"
        "    if self.new_description:\n"
        "        previous = task.description\n"
        "        task.description = self.new_description\n"
        "        updates.append(f'from {previous} to {self.new_description}')\n"
    )
    tree = ast.parse(source)
    hits: list[tuple[str, int, int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            _scan_block(node.body, "<fixed>", hits)
    assert not hits

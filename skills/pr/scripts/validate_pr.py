#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


COMMENT_RE = re.compile(r"(?s)<!--.*?-->")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
HEADING_RE = re.compile(r"^(#{2,3})\s+(.+?)\s*$")
CHECKBOX_RE = re.compile(r"^\s*-\s*\[([ xX])\]")
BULLET_RE = re.compile(r"^\s*[-*+]\s+\S")
NUMBERED_RE = re.compile(r"^\s*\d+[.)]\s+\S")
ISSUE_REF_RE = re.compile(
    r"(#\d+|\bhttps?://\S+/(?:issues|pulls)/\d+\b|\b[A-Z][A-Z0-9]+-\d+\b)"
)
CLOSING_RE = re.compile(r"\b(?:closes|fixes|resolves)\b", re.IGNORECASE)
REFERENCE_RE = re.compile(r"\b(?:refs?|related to|part of)\b", re.IGNORECASE)
CONVENTIONAL_RE = re.compile(r"^[a-z][a-z0-9]*(?:\([^)]+\))?!?:\s+\S")
PLACEHOLDER_RE = re.compile(
    r"\b(?:TODO|TBD|FIXME)\b|\[insert\b|<insert\b|\[placeholder\b|<placeholder\b|lorem ipsum",
    re.IGNORECASE,
)
SECRET_PATTERNS = (
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    ("GitHub fine-grained token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    (
        "JSON Web Token",
        re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    ),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
)
DEFAULT_SECTIONS = (
    ("summary", "Summary"),
    ("changes", "Changes"),
    ("issue", "Related issue"),
    ("test", "How to test"),
    ("risks", "Risks and notes"),
    ("checklist", "Checklist"),
)
TITLE_ALIASES = {
    "summary": "summary",
    "changes": "changes",
    "change": "changes",
    "related issue": "issue",
    "related issues": "issue",
    "issue": "issue",
    "issues": "issue",
    "linked issue": "issue",
    "linked issues": "issue",
    "how to test": "test",
    "testing": "test",
    "test plan": "test",
    "how has this been tested?": "test",
    "how to test / reproduce": "test",
    "risks and notes": "risks",
    "risks": "risks",
    "notes": "risks",
    "risks / notes": "risks",
    "risk": "risks",
    "checklist": "checklist",
}
NONE_VALUES = {"none", "n/a", "na", "-", ""}


@dataclass
class Issue:
    level: str
    code: str
    message: str
    location: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "level": self.level,
            "code": self.code,
            "message": self.message,
            "location": self.location,
        }


@dataclass
class Report:
    errors: list[Issue] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)
    stats: dict[str, object] = field(default_factory=dict)

    def error(self, code: str, message: str, location: str = "") -> None:
        self.errors.append(Issue("error", code, message, location))

    def warning(self, code: str, message: str, location: str = "") -> None:
        self.warnings.append(Issue("warning", code, message, location))

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "pass" if self.ok else "fail",
            "stats": self.stats,
            "errors": [issue.to_dict() for issue in self.errors],
            "warnings": [issue.to_dict() for issue in self.warnings],
        }


@dataclass
class Heading:
    line: int
    level: int
    title: str
    key: str | None


@dataclass
class Section:
    title: str
    key: str | None
    level: int
    content: str
    line: int


def mask_comments(text: str) -> str:
    return COMMENT_RE.sub(lambda match: re.sub(r"[^\n]", " ", match.group(0)), text)


def parse_headings(text: str) -> list[Heading]:
    masked = mask_comments(text)
    headings: list[Heading] = []
    in_fence = False
    for index, line in enumerate(masked.splitlines()):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = HEADING_RE.match(line)
        if not match:
            continue
        title = match.group(2).strip()
        headings.append(
            Heading(
                line=index,
                level=len(match.group(1)),
                title=title,
                key=map_title(title),
            )
        )
    return headings


def map_title(title: str) -> str | None:
    normalized = re.sub(r"\s+", " ", title.strip().rstrip(":")).lower()
    return TITLE_ALIASES.get(normalized)


def normalized_title(title: str) -> str:
    return re.sub(r"\s+", " ", title.strip().rstrip(":")).lower()


def build_sections(text: str, headings: list[Heading]) -> list[Section]:
    lines = text.splitlines()
    sections: list[Section] = []
    for index, heading in enumerate(headings):
        end = len(lines)
        for later in headings[index + 1 :]:
            if later.level <= heading.level:
                end = later.line
                break
        sections.append(
            Section(
                title=heading.title,
                key=heading.key,
                level=heading.level,
                content="\n".join(lines[heading.line + 1 : end]),
                line=heading.line,
            )
        )
    return sections


def strip_fenced_code(text: str) -> str:
    result: list[str] = []
    in_fence = False
    for line in text.splitlines(keepends=True):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            result.append("\n" if line.endswith("\n") else "")
        elif in_fence:
            result.append("\n" if line.endswith("\n") else "")
        else:
            result.append(line)
    return "".join(result)


def strip_inline_code(text: str) -> str:
    return re.sub(r"`[^`\n]+`", "", text)


def strip_comments(text: str) -> str:
    return COMMENT_RE.sub("", text)


def nonempty_content_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if re.fullmatch(r"<!--.*?-->", line):
            continue
        if line.startswith("#"):
            continue
        lines.append(line)
    return lines


def section_map(sections: Iterable[Section], report: Report) -> dict[str, Section]:
    result: dict[str, Section] = {}
    for section in sections:
        key = section.key or normalized_title(section.title)
        if key in result:
            report.error(
                "duplicate-section",
                f"The {section.title} section is defined more than once.",
                f"body:{section.line + 1}",
            )
            continue
        result[key] = section
    return result


def resolve_template_sections(template_text: str, report: Report) -> list[Heading]:
    headings = parse_headings(template_text)
    if not headings:
        report.error(
            "empty-template",
            "The template file contains no level 2 or level 3 headings.",
            "template",
        )
    return headings


def validate_heading_order(
    body_map: dict[str, Section],
    required: list[tuple[str, str]],
    report: Report,
) -> None:
    positions: list[tuple[int, str]] = []
    for key, label in required:
        section = body_map.get(key)
        if section is None:
            report.error(
                "missing-section",
                f"The body is missing the {label} section.",
                "body",
            )
            continue
        positions.append((section.line, label))
    for previous, current in zip(positions, positions[1:]):
        if current[0] <= previous[0]:
            report.error(
                "heading-order",
                f"The {current[1]} section appears before {previous[1]}.",
                "body",
            )


def validate_summary(section: Section, report: Report) -> None:
    lines = nonempty_content_lines(section.content)
    if len(lines) < 2:
        report.error(
            "thin-summary",
            "The Summary section needs at least two content lines.",
            f"body:{section.line + 1}",
        )


def validate_changes(section: Section, report: Report) -> None:
    lines = nonempty_content_lines(section.content)
    if not any(BULLET_RE.match(line) for line in lines):
        report.warning(
            "changes-no-bullets",
            "The Changes section should use a bullet list grouped by area.",
            f"body:{section.line + 1}",
        )


def validate_issue(
    section: Section,
    report: Report,
    require_issue: bool,
) -> None:
    content = section.content.strip()
    normalized = content.lower().strip()
    has_reference = bool(ISSUE_REF_RE.search(content))

    if normalized in NONE_VALUES:
        if require_issue:
            report.error(
                "missing-issue-reference",
                "The Related issue section cannot be None when an issue is required.",
                f"body:{section.line + 1}",
            )
        return

    if require_issue and not has_reference:
        report.error(
            "missing-issue-reference",
            "The Related issue section needs an issue reference.",
            f"body:{section.line + 1}",
        )
        return

    if not has_reference:
        report.warning(
            "unrecognized-issue-reference",
            "The Related issue section has no recognizable issue number or URL.",
            f"body:{section.line + 1}",
        )
        return

    if not CLOSING_RE.search(content) and not REFERENCE_RE.search(content):
        report.warning(
            "missing-issue-keyword",
            "The Related issue section should use Closes, Fixes, Resolves, Refs, or Related to.",
            f"body:{section.line + 1}",
        )


def validate_test_plan(section: Section, report: Report) -> None:
    lines = nonempty_content_lines(section.content)
    if not any(NUMBERED_RE.match(line) for line in lines):
        report.error(
            "missing-test-steps",
            "The How to test section needs at least one numbered step.",
            f"body:{section.line + 1}",
        )


def count_checkboxes(section: Section) -> tuple[int, int]:
    total = 0
    unchecked = 0
    for raw_line in section.content.splitlines():
        match = CHECKBOX_RE.match(raw_line)
        if not match:
            continue
        total += 1
        if match.group(1) == " ":
            unchecked += 1
    return total, unchecked


def validate_checklist(
    section: Section,
    report: Report,
    require_checklist: bool,
    allow_unchecked: bool,
) -> None:
    total, unchecked = count_checkboxes(section)
    report.stats["checkboxes"] = total
    report.stats["unchecked"] = unchecked
    if total < 3:
        report.error(
            "missing-checklist-items",
            "The Checklist section needs at least three checkbox items.",
            f"body:{section.line + 1}",
        )
    if unchecked and not allow_unchecked:
        message = f"The Checklist has {unchecked} unchecked item(s)."
        if require_checklist:
            report.error("unchecked-checklist", message, f"body:{section.line + 1}")
        else:
            report.warning("unchecked-checklist", message, f"body:{section.line + 1}")


def validate_sections(
    body_map: dict[str, Section],
    report: Report,
    require_issue: bool,
    require_checklist: bool,
    allow_unchecked: bool,
) -> None:
    if "summary" in body_map:
        validate_summary(body_map["summary"], report)
    if "changes" in body_map:
        validate_changes(body_map["changes"], report)
    if "issue" in body_map:
        validate_issue(body_map["issue"], report, require_issue)
    if "test" in body_map:
        validate_test_plan(body_map["test"], report)
    if "risks" in body_map:
        if not nonempty_content_lines(body_map["risks"].content):
            report.error(
                "empty-section",
                "The Risks and notes section is empty.",
                f"body:{body_map['risks'].line + 1}",
            )
    if "checklist" in body_map:
        validate_checklist(
            body_map["checklist"],
            report,
            require_checklist=require_checklist,
            allow_unchecked=allow_unchecked,
        )


def validate_required_content(
    body_map: dict[str, Section],
    required_keys: Iterable[str],
    report: Report,
) -> None:
    for key in required_keys:
        section = body_map.get(key)
        if section is None:
            continue
        if not nonempty_content_lines(section.content):
            report.error(
                "empty-section",
                f"The {section.title} section is empty.",
                f"body:{section.line + 1}",
            )


def validate_title(
    title: str | None,
    report: Report,
    require_conventional: bool,
) -> None:
    if title is None:
        if require_conventional:
            report.error(
                "missing-title",
                "--require-conventional needs --title.",
                "title",
            )
        report.stats["title_provided"] = False
        return

    cleaned = title.strip()
    report.stats["title_provided"] = True
    report.stats["title_length"] = len(cleaned)
    if not cleaned:
        report.error("missing-title", "The title is empty.", "title")
        return
    if "\n" in title or "\r" in title:
        report.error("invalid-title", "The title must be a single line.", "title")
    if cleaned.endswith("."):
        report.error("trailing-period", "The title must not end with a period.", "title")
    if len(cleaned) > 80:
        report.error(
            "title-too-long",
            f"The title has {len(cleaned)} characters; the maximum is 80.",
            "title",
        )
    elif len(cleaned) > 70:
        report.warning(
            "title-long",
            f"The title has {len(cleaned)} characters; prefer 70 or fewer.",
            "title",
        )
    if PLACEHOLDER_RE.search(cleaned):
        report.error("placeholder-title", "The title contains a placeholder.", "title")
    if require_conventional and not CONVENTIONAL_RE.match(cleaned):
        report.error(
            "invalid-conventional-title",
            "The title must follow Conventional Commits, for example feat(scope): subject.",
            "title",
        )


def scan_placeholders(text: str, report: Report) -> None:
    cleaned = strip_inline_code(strip_fenced_code(strip_comments(text)))
    for match in PLACEHOLDER_RE.finditer(cleaned):
        line = cleaned.count("\n", 0, match.start()) + 1
        report.error(
            "placeholder",
            f"The body contains unresolved placeholder {match.group(0)!r}.",
            f"body:{line}",
        )


def scan_secrets(text: str, report: Report) -> None:
    for name, pattern in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            report.error(
                "secret",
                f"The body contains a possible {name}. Redact and rotate it.",
                f"body:{line}",
            )


def validate_template_sections(
    template_headings: list[Heading],
    body_map: dict[str, Section],
    report: Report,
) -> tuple[list[str], list[tuple[str, str]]]:
    required: list[tuple[str, str]] = []
    seen: set[str] = set()
    for heading in template_headings:
        key = heading.key or normalized_title(heading.title)
        if key in seen:
            report.warning(
                "duplicate-template-heading",
                f"The template repeats the {heading.title} heading.",
                "template",
            )
            continue
        seen.add(key)
        required.append((key, heading.title))
    validate_heading_order(body_map, required, report)
    return [key for key, _ in required], required


def validate_body(
    text: str,
    report: Report,
    title: str | None = None,
    template_text: str | None = None,
    require_issue: bool = False,
    require_checklist: bool = False,
    allow_unchecked: bool = False,
    require_conventional: bool = False,
) -> None:
    headings = parse_headings(text)
    sections = build_sections(text, headings)
    body_map = section_map(sections, report)
    report.stats["sections"] = len(headings)

    if template_text is not None:
        template_headings = resolve_template_sections(template_text, report)
        required_keys, _ = validate_template_sections(template_headings, body_map, report)
        validate_required_content(body_map, required_keys, report)
    else:
        required = list(DEFAULT_SECTIONS)
        validate_heading_order(body_map, required, report)
        validate_required_content(body_map, [key for key, _ in required], report)

    validate_sections(
        body_map,
        report,
        require_issue=require_issue,
        require_checklist=require_checklist,
        allow_unchecked=allow_unchecked,
    )
    validate_title(title, report, require_conventional)
    scan_placeholders(text, report)
    scan_secrets(text, report)
    report.stats["has_issue_reference"] = bool(
        ISSUE_REF_RE.search(body_map["issue"].content)
        if "issue" in body_map
        else False
    )


def read_text(path: Path, report: Report) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        report.error("missing-file", f"Missing file: {path}", str(path))
    except OSError as error:
        report.error("unreadable-file", f"Cannot read {path}: {error}", str(path))
    return ""


def validate_file(
    path: Path,
    report: Report,
    title: str | None = None,
    template: Path | None = None,
    require_issue: bool = False,
    require_checklist: bool = False,
    allow_unchecked: bool = False,
    require_conventional: bool = False,
) -> None:
    text = read_text(path, report)
    if not text.strip():
        if not report.errors:
            report.error("empty-body", "The body file is empty.", str(path))
        return
    template_text = None
    if template is not None:
        template_text = read_text(template, report)
        if not template_text.strip():
            report.error("empty-template", "The template file is empty.", str(template))
            return
    validate_body(
        text,
        report,
        title=title,
        template_text=template_text,
        require_issue=require_issue,
        require_checklist=require_checklist,
        allow_unchecked=allow_unchecked,
        require_conventional=require_conventional,
    )


def format_issue(issue: Issue) -> str:
    location = f" ({issue.location})" if issue.location else ""
    return f"[{issue.level.upper()}] {issue.code}: {issue.message}{location}"


def print_report(report: Report, as_json: bool) -> None:
    if as_json:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
        return
    for issue in report.errors:
        print(format_issue(issue), file=sys.stderr)
    for issue in report.warnings:
        print(format_issue(issue), file=sys.stderr)
    status = "PASS" if report.ok else "FAIL"
    print(
        f"{status}: {report.stats.get('sections', 0)} section(s), "
        f"{report.stats.get('checkboxes', 0)} checklist item(s), "
        f"title {report.stats.get('title_length', 0)} char(s); "
        f"{len(report.errors)} error(s), {len(report.warnings)} warning(s)."
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a pull request title and body against the PR contract."
    )
    parser.add_argument("body", help="Path to the Markdown body file")
    parser.add_argument("--title", help="Pull request title to validate")
    parser.add_argument("--template", help="Repository PR template to validate against")
    parser.add_argument("--json", action="store_true", help="Emit a JSON report")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    parser.add_argument(
        "--require-issue",
        action="store_true",
        help="Fail when the Related issue section has no issue reference",
    )
    parser.add_argument(
        "--require-checklist",
        action="store_true",
        help="Fail when checklist items are unchecked",
    )
    parser.add_argument(
        "--allow-unchecked",
        action="store_true",
        help="Allow unchecked checklist items, as in a draft pull request",
    )
    parser.add_argument(
        "--require-conventional",
        action="store_true",
        help="Require a Conventional Commits title",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    report = Report()
    validate_file(
        Path(args.body),
        report,
        title=args.title,
        template=Path(args.template) if args.template else None,
        require_issue=args.require_issue,
        require_checklist=args.require_checklist,
        allow_unchecked=args.allow_unchecked,
        require_conventional=args.require_conventional,
    )
    print_report(report, args.json)
    if report.errors:
        return 1
    if args.strict and report.warnings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

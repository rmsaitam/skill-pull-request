from __future__ import annotations

import json
from pathlib import Path

import pytest

from validate_pr import (
    Report,
    count_checkboxes,
    main,
    map_title,
    mask_comments,
    parse_headings,
    validate_body,
    validate_file,
)


FIXTURES = Path(__file__).parent / "fixtures"
VALID = (FIXTURES / "valid_pr_body.md").read_text(encoding="utf-8")
TEMPLATE = (FIXTURES / "pull_request_template.md").read_text(encoding="utf-8")
TEMPLATE_BODY = (FIXTURES / "valid_pr_body_template.md").read_text(encoding="utf-8")


def run(text: str, **kwargs) -> Report:
    report = Report()
    validate_body(text, report, **kwargs)
    return report


def error_codes(report: Report) -> set[str]:
    return {issue.code for issue in report.errors}


def warning_codes(report: Report) -> set[str]:
    return {issue.code for issue in report.warnings}


def test_valid_body_passes() -> None:
    report = run(VALID)
    assert report.ok, [issue.message for issue in report.errors]
    assert not report.warnings
    assert report.stats["sections"] == 6
    assert report.stats["checkboxes"] == 4
    assert report.stats["unchecked"] == 0
    assert report.stats["has_issue_reference"] is True
    assert report.stats["title_provided"] is False


def test_valid_body_with_title_and_strict_options() -> None:
    report = run(
        VALID,
        title="feat(auth): add token validation",
        require_issue=True,
        require_checklist=True,
        require_conventional=True,
    )
    assert report.ok, [issue.message for issue in report.errors]
    assert not report.warnings
    assert report.stats["title_length"] == 32


def test_missing_section() -> None:
    text = VALID.replace(
        "## Risks and notes\n\n"
        "- Existing sessions with tokens older than the new expiry window must re-authenticate.\n"
        "- Reviewers should focus on the clock-skew handling in `src/auth/token.py`.\n\n",
        "",
    )
    assert "missing-section" in error_codes(run(text))


def test_duplicate_section() -> None:
    text = VALID.replace(
        "## Changes\n",
        "## Summary\n\n- Duplicate summary.\n\n## Changes\n",
        1,
    )
    assert "duplicate-section" in error_codes(run(text))


def test_heading_order() -> None:
    text = (
        "## Changes\n\n- Change.\n\n"
        "## Summary\n\n- One.\n- Two.\n\n"
        "## Related issue\n\nCloses #1\n\n"
        "## How to test\n\n1. Run.\n\n"
        "## Risks and notes\n\n- None.\n\n"
        "## Checklist\n\n- [x] A\n- [x] B\n- [x] C\n"
    )
    assert "heading-order" in error_codes(run(text))


def test_thin_summary() -> None:
    text = VALID.replace(
        "- Adds token validation to the login endpoint.\n"
        "- Rejects expired and malformed tokens before the handler runs.\n"
        "- Returns a consistent 401 error to API clients.\n",
        "- Adds token validation.\n",
    )
    assert "thin-summary" in error_codes(run(text))


def test_changes_without_bullets_warns() -> None:
    text = VALID.replace(
        "- `src/auth/token.py`: validate the token signature and expiry.\n"
        "- `src/auth/handlers.py`: return 401 for invalid tokens.\n"
        "- `tests/auth/test_token.py`: cover expired, malformed, and valid tokens.\n",
        "The token module and its handler were updated.\n",
    )
    assert "changes-no-bullets" in warning_codes(run(text))


def test_issue_required() -> None:
    text = VALID.replace("Closes #482", "None")
    report = run(text, require_issue=True)
    assert "missing-issue-reference" in error_codes(report)


def test_issue_none_is_allowed_when_not_required() -> None:
    text = VALID.replace("Closes #482", "None")
    report = run(text)
    assert report.ok
    assert "missing-issue-reference" not in error_codes(report)


def test_issue_unrecognized_reference_warns() -> None:
    text = VALID.replace("Closes #482", "See the design document.")
    assert "unrecognized-issue-reference" in warning_codes(run(text))


def test_issue_unrecognized_reference_fails_when_required() -> None:
    text = VALID.replace("Closes #482", "See the design document.")
    assert "missing-issue-reference" in error_codes(run(text, require_issue=True))


def test_issue_missing_keyword_warns() -> None:
    text = VALID.replace("Closes #482", "#482")
    assert "missing-issue-keyword" in warning_codes(run(text))


def test_issue_reference_keyword_is_accepted() -> None:
    text = VALID.replace("Closes #482", "Refs #482")
    report = run(text)
    assert report.ok
    assert not report.warnings


def test_issue_url_and_ticket_are_accepted() -> None:
    url_body = VALID.replace("Closes #482", "Closes https://github.com/org/repo/issues/482")
    assert run(url_body).ok
    ticket_body = VALID.replace("Closes #482", "Related to PROJ-123")
    assert run(ticket_body).ok


def test_test_plan_requires_numbered_steps() -> None:
    text = VALID.replace(
        "1. Run `pytest tests/auth/test_token.py`.\n"
        "2. Send a request with an expired token.\n"
        "3. Expect a 401 response with the `invalid_token` error code.\n",
        "- Run the auth tests.\n- Send an expired token.\n",
    )
    assert "missing-test-steps" in error_codes(run(text))


def test_empty_risks_section() -> None:
    text = VALID.replace(
        "- Existing sessions with tokens older than the new expiry window must re-authenticate.\n"
        "- Reviewers should focus on the clock-skew handling in `src/auth/token.py`.\n",
        "",
    )
    assert "empty-section" in error_codes(run(text))


def test_checklist_requires_three_items() -> None:
    text = VALID.replace("- [x] Documentation updated when applicable\n", "")
    text = text.replace("- [x] No secret or sensitive data included\n", "")
    assert "missing-checklist-items" in error_codes(run(text))


def test_unchecked_checklist_warns_by_default() -> None:
    text = VALID.replace("- [x] Lint and typecheck passed", "- [ ] Lint and typecheck passed")
    report = run(text)
    assert "unchecked-checklist" in warning_codes(report)
    assert "unchecked-checklist" not in error_codes(report)


def test_unchecked_checklist_fails_when_required() -> None:
    text = VALID.replace("- [x] Lint and typecheck passed", "- [ ] Lint and typecheck passed")
    assert "unchecked-checklist" in error_codes(run(text, require_checklist=True))


def test_unchecked_checklist_allowed_for_draft() -> None:
    text = VALID.replace("- [x] Lint and typecheck passed", "- [ ] Lint and typecheck passed")
    report = run(text, require_checklist=True, allow_unchecked=True)
    assert "unchecked-checklist" not in error_codes(report)
    assert "unchecked-checklist" not in warning_codes(report)


def test_title_rules() -> None:
    assert "missing-title" in error_codes(run(VALID, title="", require_conventional=True))
    assert "missing-title" in error_codes(run(VALID, require_conventional=True))
    assert "invalid-title" in error_codes(run(VALID, title="first line\nsecond line"))
    assert "trailing-period" in error_codes(run(VALID, title="feat: add validation."))
    assert "title-too-long" in error_codes(run(VALID, title="feat: " + "a" * 75))
    assert "title-long" in warning_codes(run(VALID, title="feat: " + "a" * 69))
    assert "placeholder-title" in error_codes(run(VALID, title="feat: TODO"))
    assert "invalid-conventional-title" in error_codes(
        run(VALID, title="add token validation", require_conventional=True)
    )
    assert run(VALID, title="feat(auth): add token validation", require_conventional=True).ok


def test_placeholder_in_prose_is_rejected() -> None:
    text = VALID.replace(
        "- Adds token validation to the login endpoint.",
        "- Adds token validation to the login endpoint.\n- TODO: remove this line.",
    )
    assert "placeholder" in error_codes(run(text))


def test_placeholder_in_inline_code_is_ignored() -> None:
    text = VALID.replace(
        "- Adds token validation to the login endpoint.",
        "- Adds token validation to the login endpoint.\n- The token `TODO` is documentation.",
    )
    assert "placeholder" not in error_codes(run(text))


def test_placeholder_in_fenced_code_is_ignored() -> None:
    text = VALID.replace(
        "- Adds token validation to the login endpoint.",
        "- Adds token validation to the login endpoint.\n\n```text\nTODO\n```",
    )
    assert "placeholder" not in error_codes(run(text))


def test_placeholder_in_tilde_fence_is_ignored() -> None:
    text = VALID.replace(
        "- Adds token validation to the login endpoint.",
        "- Adds token validation to the login endpoint.\n\n~~~text\nTODO\n~~~",
    )
    assert "placeholder" not in error_codes(run(text))


def test_lorem_ipsum_is_rejected() -> None:
    text = VALID.replace(
        "- Adds token validation to the login endpoint.",
        "- Lorem ipsum dolor sit amet.",
    )
    assert "placeholder" in error_codes(run(text))


def test_possible_secret_is_rejected() -> None:
    token = "ghp_" + "a" * 36
    text = VALID.replace(
        "- Adds token validation to the login endpoint.",
        f"- Adds token validation to the login endpoint.\n- Token: {token}",
    )
    assert "secret" in error_codes(run(text))


def test_private_key_is_rejected() -> None:
    text = VALID.replace(
        "- Adds token validation to the login endpoint.",
        "- Adds token validation to the login endpoint.\n\n```\n-----BEGIN RSA PRIVATE KEY-----\n```",
    )
    assert "secret" in error_codes(run(text))


def test_template_mode_passes() -> None:
    report = run(
        TEMPLATE_BODY,
        template_text=TEMPLATE,
        title="feat(auth): add token validation",
    )
    assert report.ok, [issue.message for issue in report.errors]
    assert not report.warnings


def test_template_mode_missing_heading() -> None:
    text = TEMPLATE_BODY.replace(
        "## Why\n\nExpired tokens were accepted by the handler, which allowed stale sessions.\n\n",
        "",
    )
    assert "missing-section" in error_codes(run(text, template_text=TEMPLATE))


def test_empty_template_is_rejected() -> None:
    assert "empty-template" in error_codes(run(TEMPLATE_BODY, template_text=""))


def test_template_without_headings_is_rejected() -> None:
    assert "empty-template" in error_codes(run(TEMPLATE_BODY, template_text="No headings here."))


def test_duplicate_template_heading_warns() -> None:
    template = "## What changed\n\n## What changed\n\n## Testing\n"
    body = "## What changed\n\n- Change.\n\n## Testing\n\n1. Run.\n"
    report = run(body, template_text=template)
    assert "duplicate-template-heading" in warning_codes(report)


def test_unknown_template_heading_is_required() -> None:
    template = "## Custom section\n"
    body = "## Another section\n\nContent.\n"
    assert "missing-section" in error_codes(run(body, template_text=template))


def test_parse_headings_ignores_code_and_comments() -> None:
    text = (
        "## Summary\n"
        "<!-- ## Hidden -->\n"
        "```md\n## Also hidden\n```\n"
        "## Changes\n"
    )
    titles = [heading.title for heading in parse_headings(text)]
    assert titles == ["Summary", "Changes"]


def test_map_title_aliases() -> None:
    assert map_title("What changed") is None
    assert map_title("Related Issues") == "issue"
    assert map_title("Test plan") == "test"
    assert map_title("Risks / notes") == "risks"
    assert map_title("Checklist") == "checklist"


def test_mask_comments_preserves_line_count() -> None:
    text = "line one\n<!-- hidden\nstill hidden -->\nline four\n"
    masked = mask_comments(text)
    assert masked.count("\n") == text.count("\n")


def test_count_checkboxes() -> None:
    report = run(VALID)
    assert report.stats["checkboxes"] == 4
    assert report.stats["unchecked"] == 0


def test_validate_file_reads_body_and_template(tmp_path: Path) -> None:
    body = tmp_path / "body.md"
    body.write_text(TEMPLATE_BODY, encoding="utf-8")
    template = tmp_path / "template.md"
    template.write_text(TEMPLATE, encoding="utf-8")
    report = Report()
    validate_file(body, report, title="feat: add validation", template=template)
    assert report.ok, [issue.message for issue in report.errors]


def test_validate_file_missing_body(tmp_path: Path, capsys) -> None:
    report = Report()
    validate_file(tmp_path / "missing.md", report)
    assert "missing-file" in error_codes(report)
    assert main([str(tmp_path / "missing.md")]) == 1
    captured = capsys.readouterr()
    assert "missing-file" in captured.err


def test_validate_file_empty_body(tmp_path: Path) -> None:
    body = tmp_path / "body.md"
    body.write_text("", encoding="utf-8")
    report = Report()
    validate_file(body, report)
    assert "empty-body" in error_codes(report)


def test_validate_file_empty_template(tmp_path: Path) -> None:
    body = tmp_path / "body.md"
    body.write_text(TEMPLATE_BODY, encoding="utf-8")
    template = tmp_path / "template.md"
    template.write_text("", encoding="utf-8")
    report = Report()
    validate_file(body, report, template=template)
    assert "empty-template" in error_codes(report)


def test_cli_json_pass(tmp_path: Path, capsys) -> None:
    body = tmp_path / "body.md"
    body.write_text(VALID, encoding="utf-8")
    exit_code = main(
        [
            str(body),
            "--title",
            "feat(auth): add token validation",
            "--require-issue",
            "--json",
        ]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["status"] == "pass"
    assert payload["stats"]["title_length"] == 32


def test_cli_strict_fails_on_warning(tmp_path: Path, capsys) -> None:
    body = tmp_path / "body.md"
    body.write_text(
        VALID.replace("- [x] Lint and typecheck passed", "- [ ] Lint and typecheck passed"),
        encoding="utf-8",
    )
    exit_code = main([str(body), "--strict"])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "unchecked-checklist" in captured.err


def test_cli_template_mode(tmp_path: Path, capsys) -> None:
    body = tmp_path / "body.md"
    body.write_text(TEMPLATE_BODY, encoding="utf-8")
    template = tmp_path / "template.md"
    template.write_text(TEMPLATE, encoding="utf-8")
    exit_code = main([str(body), "--template", str(template), "--title", "feat: add validation"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "PASS" in captured.out


@pytest.mark.parametrize(
    "title",
    [
        "feat: " + "a" * 75,
        "feat: add validation.",
        "feat: TODO",
    ],
)
def test_invalid_titles_are_rejected(title: str) -> None:
    assert not run(VALID, title=title).ok

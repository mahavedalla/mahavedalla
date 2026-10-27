
#!/usr/bin/env python3

TODAY_DATE = "10-27-2026"

"""
Normalize Date Entered and Last Revised values in question front matter.

Accepted input formats:
    March 30, 2025
    03-30-25
    3-30-25
    9-5-25

Target format:
    03-30-2025

Blank and unrecognized values are reported but left unchanged.
Only the two specified front matter fields may be modified.
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path


QUESTIONS_DIR = Path("questions")
REPORT_PATH = Path("scripts/md/front_matter_date_repair_report.md")
DATE_FIELDS = {"Date Entered", "Last Revised"}


def split_front_matter(lines):
    """Return the indices of the front matter, or None."""
    if not lines:
        return None

    first = lines[0].removeprefix("\ufeff").rstrip("\r\n")
    if first.strip() != "---":
        return None

    for index in range(1, len(lines)):
        if lines[index].rstrip("\r\n").strip() == "---":
            return 1, index

    return None


def normalize_date(value):
    """
    Return (normalized_value, status).

    Status is CONVERTED, ALREADY_STANDARD, BLANK, or UNRECOGNIZED.
    """
    value = value.strip()

    if not value:
        return value, "BLANK"

    # Month name, day, four-digit year: March 30, 2025
    month_name = re.fullmatch(
        r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})",
        value,
    )

    if month_name:
        try:
            parsed = date.fromisoformat(
                f"{month_name.group(3)}-"
                f"{month_name.group(1)}-"
                f"{month_name.group(2)}"
            )
        except ValueError:
            # Fall back to explicit month-name parsing below.
            from datetime import datetime

            try:
                parsed = datetime.strptime(value, "%B %d, %Y").date()
            except ValueError:
                try:
                    parsed = datetime.strptime(value, "%b %d, %Y").date()
                except ValueError:
                    return value, "UNRECOGNIZED"

        normalized = parsed.strftime("%m-%d-%Y")
        status = (
            "ALREADY_STANDARD"
            if value == normalized
            else "CONVERTED"
        )
        return normalized, status

    # Numeric month-day-year with a two- or four-digit year.
    numeric = re.fullmatch(
        r"(\d{1,2})-(\d{1,2})-(\d{2}|\d{4})",
        value,
    )

    if not numeric:
        return value, "UNRECOGNIZED"

    month, day_number, year = map(int, numeric.groups())

    # All two-digit years are interpreted as 2000-2099.
    if len(numeric.group(3)) == 2:
        year += 2000

    try:
        parsed = date(year, month, day_number)
    except ValueError:
        return value, "UNRECOGNIZED"

    normalized = parsed.strftime("%m-%d-%Y")
    status = (
        "ALREADY_STANDARD"
        if value == normalized
        else "CONVERTED"
    )
    return normalized, status


def inspect_file(path):
    """Read a file and prepare targeted front matter changes."""
    try:
        original = path.read_bytes()
        text = original.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return None, [], str(exc)

    # Keep original line endings so unrelated content stays untouched.
    lines = text.splitlines(keepends=True)
    bounds = split_front_matter(lines)

    if bounds is None:
        return original, [], None

    start, end = bounds
    changes = []
    seen = set()
    duplicate_fields = set()

    field_pattern = re.compile(
        r"^([ \t]*(Date Entered|Last Revised)[ \t]*:[ \t]*)"
        r"(.*?)([ \t]*)(\r\n|\n|\r)?$"
    )

    for index in range(start, end):
        line = lines[index]
        match = field_pattern.match(line)

        if not match:
            continue

        field = match.group(2)
        if field not in DATE_FIELDS:
            continue

        if field in seen:
            duplicate_fields.add(field)
        seen.add(field)

        original_value = match.group(3)
        normalized, status = normalize_date(original_value)

        if status == "BLANK":
            normalized = TODAY_DATE
            status = "CONVERTED"

        changes.append({
            "index": index,
            "field": field,
            "original": original_value.strip(),
            "normalized": normalized,
            "status": status,
            "prefix": match.group(1),
            "trailing": match.group(4),
            "eol": match.group(5) or "",
        })

    # If a date key occurs more than once, do not modify any occurrence
    # of that field; flag it for manual review.
    for item in changes:
        if item["field"] in duplicate_fields:
            item["status"] = "DUPLICATE FIELD"

    updated_lines = list(lines)
    convertible = False

    for item in changes:
        if item["status"] != "CONVERTED":
            continue

        convertible = True
        updated_lines[item["index"]] = (
            item["prefix"]
            + item["normalized"]
            + item["trailing"]
            + item["eol"]
        )

    updated_text = "".join(updated_lines).encode("utf-8")

    return updated_text if convertible else original, changes, None


def main():
    parser = argparse.ArgumentParser(
        description="Preview or normalize question front matter dates."
    )

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--preview",
        type=int,
        metavar="N",
        help="Show proposed changes for the first N eligible files",
    )
    mode.add_argument(
        "--apply-sample",
        type=int,
        metavar="N",
        help="Actually update the first N eligible files",
    )
    mode.add_argument(
        "--apply",
        action="store_true",
        help="Apply all recognized date conversions",
    )

    parser.add_argument(
        "--questions-dir",
        type=Path,
        default=QUESTIONS_DIR,
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=REPORT_PATH,
    )

    args = parser.parse_args()

    if args.preview is not None and args.preview < 1:
        parser.error("--preview must be a positive integer")
    if args.apply_sample is not None and args.apply_sample < 1:
        parser.error("--apply-sample must be a positive integer")

    if not args.questions_dir.is_dir():
        print(f"Error: directory not found: {args.questions_dir}",
              file=sys.stderr)
        return 1

    file_results = []
    errors = []
    scanned = 0

    paths = sorted(
        path for path in args.questions_dir.rglob("*")
        if path.is_file() and path.suffix.lower() == ".md"
    )

    for path in paths:
        original = path.read_bytes()

        updated, changes, error = inspect_file(path)
        if error:
            errors.append((path, error))
            continue

        scanned += 1
        if not changes:
            continue

        converted = [
            item for item in changes
            if item["status"] == "CONVERTED"
        ]

        if not converted and not any(
            item["status"] in {
                "BLANK", "UNRECOGNIZED", "DUPLICATE FIELD"
            }
            for item in changes
        ):
            continue

        file_results.append({
            "path": path,
            "original": original,
            "updated": updated,
            "changes": changes,
            "has_conversion": bool(converted),
        })

    eligible = [
        result for result in file_results
        if result["has_conversion"]
    ]

    if args.apply:
        selected = set(result["path"] for result in eligible)
    elif args.apply_sample is not None:
        selected = set(
            result["path"] for result in eligible[:args.apply_sample]
        )
    else:
        selected = set()

    updated_count = 0

    for result in eligible:
        if result["path"] not in selected:
            continue

        if result["updated"] == result["original"]:
            continue

        try:
            result["path"].write_bytes(result["updated"])
            updated_count += 1
        except OSError as exc:
            errors.append((result["path"], str(exc)))

    # Preview N limits console examples, not the full audit report.
    if args.preview is not None:
        shown = 0
        print("\nPROPOSED CHANGES")
        print("================")

        for result in eligible[:args.preview]:
            print(f"\n{result['path'].as_posix()}")
            for item in result["changes"]:
                if item["status"] == "CONVERTED":
                    print(
                        f"  {item['field']}: "
                        f"{item['original']} -> {item['normalized']}"
                    )
                    shown += 1

        print(f"\nFiles shown: {min(args.preview, len(eligible))}")
        print(f"Date conversions shown: {shown}")

    report_lines = [
        "# Front Matter Date Repair Report",
        "",
        "Target format: `MM-DD-YYYY`.",
        "Fields: `Date Entered`, `Last Revised`.",
        "",
        f"**Markdown files scanned:** {scanned}",
        f"**Files with convertible dates:** {len(eligible)}",
        f"**Files updated this run:** {updated_count}",
        "",
    ]

    for result in file_results:
        relevant = [
            item for item in result["changes"]
            if item["status"] != "ALREADY_STANDARD"
        ]
        if not relevant:
            continue

        report_lines.append(f"## `{result['path'].as_posix()}`")

        for item in relevant:
            if item["status"] == "CONVERTED":
                if result["path"] in selected:
                    status = "UPDATED"
                else:
                    status = "WOULD CONVERT"
                detail = (
                    f"`{item['original']}` → `{item['normalized']}`"
                )
            else:
                status = item["status"]
                detail = f"`{item['original']}`"

            report_lines.append(
                f"- **{item['field']}** ({status}): {detail}"
            )

        report_lines.append("")

    if errors:
        report_lines.extend(["## Files That Could Not Be Read or Updated", ""])
        for path, error in errors:
            report_lines.append(f"- `{path.as_posix()}` — {error}")

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        "\n".join(report_lines) + "\n",
        encoding="utf-8",
    )

    print(f"\nMarkdown files scanned: {scanned}")
    print(f"Files with convertible dates: {len(eligible)}")

    if args.apply or args.apply_sample is not None:
        print(f"Files updated: {updated_count}")
    else:
        print("Preview only; no question files were changed.")

    print(f"Files with read/write errors: {len(errors)}")
    print(f"Report written to: {args.report}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

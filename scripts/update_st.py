#!/usr/bin/env python3
"""Update CODESYS .object JSON files from Structured Text extracted by extract_st.py.

Each ``.st`` file may contain sections emitted by the extractor, for example:

    (* --- Interface --- *)
    PROGRAM PLC_PRG
    VAR
    END_VAR

The section label identifies the corresponding TextDocument in the project
object. A file with one unlabelled section is supported for objects with one
TextDocument. The script validates all labels before writing any project file.
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from st import (
    STRING_PREFIX,
    SECTION_PREFIX,
    SECTION_SUFFIX,
    DEFAULT_ROOT,
    DEFAULT_ST,
    object_name,
    fallback_from_path,
)


def find_text_documents(node, label, results):
    """Collect ``(section label, TextDocument @Value)`` pairs recursively."""
    if isinstance(node, dict):
        text_document = node.get("TextDocument")
        if isinstance(text_document, dict):
            value = text_document.get("@Value")
            if isinstance(value, dict) and "TextBlobForSerialisation" in value:
                results.append((label, value))
        for key, value in node.items():
            if key != "TextDocument":
                find_text_documents(
                    value, label if key in ("@Type", "@Value") else key, results
                )
    elif isinstance(node, list):
        for item in node:
            find_text_documents(item, label, results)


def parse_st_file(path):
    """Return section-label-to-text mappings parsed from one extracted ST file."""
    sections = []
    label = ""
    lines = []
    skip_separator = False

    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.startswith(SECTION_PREFIX) and line.endswith(SECTION_SUFFIX):
            if lines or sections:
                sections.append((label, "\n".join(lines)))
            label = line[len(SECTION_PREFIX) : -len(SECTION_SUFFIX)]
            lines = []
            skip_separator = True
        elif skip_separator and not line:
            skip_separator = False
        else:
            lines.append(line)
            skip_separator = False
    if lines or sections:
        sections.append((label, "\n".join(lines)))

    while sections and not sections[0][0] and not sections[0][1]:
        sections.pop(0)
    while sections and not sections[-1][0] and not sections[-1][1]:
        sections.pop()

    labels = [section_label for section_label, _ in sections]
    if len(labels) != len(set(labels)):
        raise ValueError("contains duplicate section labels")
    return dict(sections)


def load_object(path, root):
    """Read an object and return its source name and TextDocument map."""
    with path.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)
    documents = []
    find_text_documents(data.get("payload", {}).get("object", {}), "", documents)
    by_label = defaultdict(list)
    for label, value in documents:
        by_label[label].append(value)
    return data, object_name(data, fallback_from_path(path.relative_to(root))), by_label


def update_object(path, source_path, root, dry_run=False):
    """Apply ST sections from ``source_path`` to its matching project object."""
    data, name, documents = load_object(path, root)
    source_sections = parse_st_file(source_path)

    if "" in source_sections and len(documents) != 1:
        raise ValueError(f"{source_path}: unlabelled source is ambiguous for {path}")

    missing = set(source_sections) - set(documents)
    duplicate_targets = [
        label for label, values in documents.items() if len(values) > 1
    ]
    if missing:
        raise ValueError(
            f"{source_path}: no matching section(s): {', '.join(sorted(missing))}"
        )
    if duplicate_targets:
        raise ValueError(
            f"{path}: duplicate TextDocument label(s): {', '.join(sorted(duplicate_targets))}"
        )

    changed = 0
    for label, text in source_sections.items():
        document = documents[label][0]
        # Ensure the text ends with a newline before updating the
        # document.
        if not text.endswith("\n"):
            text += "\n"
        new_value = STRING_PREFIX + text
        if document["TextBlobForSerialisation"] != new_value:
            document["TextBlobForSerialisation"] = new_value
            changed += 1

    if changed and not dry_run:
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return name, changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root", nargs="?", default=DEFAULT_ROOT, help="project object directory"
    )
    parser.add_argument(
        "-i",
        "--input-dir",
        default=DEFAULT_ST,
        help="directory containing extracted .st files",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="report updates without writing files"
    )
    args = parser.parse_args()

    root = Path(args.root)
    input_dir = Path(args.input_dir)
    objects = {}
    for path in sorted(root.rglob("*.object")):
        try:
            _, name, documents = load_object(path, root)
        except (json.JSONDecodeError, OSError):
            continue
        if documents:
            if name in objects:
                raise SystemExit(f"update_st: duplicate object name: {name}")
            objects[name] = path

    updated = 0
    # Recursively search for all .st files in the input directory.
    # Match the source paths against the object names derived from the relative paths.
    # Remove the file extension from the relative path to get the object name.
    for source_path in sorted(input_dir.rglob("*.st")):
        object_path = objects.get(str(source_path.relative_to(input_dir).with_suffix("")))
        if object_path is None:
            print(
                f"update_st: skipping {source_path} (no matching object)",
                file=sys.stderr,
            )
            continue
        try:
            name, changed = update_object(object_path, source_path, root, args.dry_run)
        except (json.JSONDecodeError, OSError, ValueError) as error:
            raise SystemExit(f"update_st: {error}") from error
        updated += changed
        action = "would update" if args.dry_run else "updated"
        print(f"update_st: {action} {name} ({changed} section(s))")

    print(
        f"update_st: {'would update' if args.dry_run else 'updated'} {updated} section(s)",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()

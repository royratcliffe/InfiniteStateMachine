#!/usr/bin/env python3
"""Extract CODESYS Structured Text (ST) source from .object project files.

CODESYS project objects (POUs, GVLs, etc.) are stored as JSON. Any ST source
text lives in nodes shaped like:

    "TextDocument": {"@Value": {"TextBlobForSerialisation": "(string)..."}}

This walks every .object file under a root directory, pulls out those text
blobs (declaration, implementation, and similarly-shaped sections), and
writes one .st file per object.
"""

import argparse
import json
import sys
import os
from pathlib import Path

STRING_PREFIX = "(string)"

# The order in which sections should appear in the output .st file.
# Interface sections should appear before Implementation sections.
# Everything else will appear after the listed sections.
SECTION_ORDERING = ["Interface", "Implementation"]


def unwrap_string(value):
    """Strip the CODESYS "(string)" type-tag prefix used on raw string values."""
    if isinstance(value, str) and value.startswith(STRING_PREFIX):
        return value[len(STRING_PREFIX) :]
    return value


def object_name(data, fallback):
    """Return the object's declared name (payload.meta.Graph.@Value.Name), or fallback."""
    try:
        name = data["payload"]["meta"]["Graph"]["@Value"]["Name"]
    except (KeyError, TypeError):
        return fallback
    name = unwrap_string(name)
    # If the name is valid, prepend it with the fallback path.
    return f"{fallback}/{name}" if isinstance(name, str) and name else fallback


def find_text_blobs(node, label, results):
    """Recursively collect (section_label, text) pairs from any TextDocument node."""
    if isinstance(node, dict):
        text_document = node.get("TextDocument")
        if isinstance(text_document, dict):
            blob = unwrap_string(
                text_document.get("@Value", {}).get("TextBlobForSerialisation", "")
            )
            if blob:
                results.append((label, blob))
        for key, value in node.items():
            if key == "TextDocument":
                continue
            # "@Type"/"@Value" are wrapper keys, not field names; keep the enclosing label.
            find_text_blobs(
                value, label if key in ("@Type", "@Value") else key, results
            )
    elif isinstance(node, list):
        for item in node:
            find_text_blobs(item, label, results)


def extract(path):
    """Return (name, [(section_label, text), ...]) for one .object file, or None."""
    with open(path, "r", encoding="utf-8-sig") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"extract_st: skipping {path} (not valid JSON)", file=sys.stderr)
            return None
    results = []
    find_text_blobs(data.get("payload", {}).get("object", {}), "", results)
    if not results:
        return None
    # Construct the object name using the fallback derived from the file path.
    # The fallback derives from the file path by taking all parts except the first and last,
    # the last part, and joining them with "/".
    fallback = os.sep.join([part.rsplit("_", 1)[0] for part in path.parts][1:-1])
    return object_name(data, fallback), results


def write_st_file(output_dir, name, sections):
    """Write one .st file combining all extracted sections for a named object."""
    lines = []
    # Add each section in the order specified by SECTION_ORDERING, with
    # a header comment for each section.
    for label, text in sorted(
        sections,
        key=lambda x: (
            SECTION_ORDERING.index(x[0])
            if x[0] in SECTION_ORDERING
            else len(SECTION_ORDERING)
        ),
    ):
        print(f"Processing section: {label}")
        if label:
            lines.append(f"(* --- {label} --- *)")
        lines.append(text)
    dest = output_dir / f"{name}.st"
    # Avoid adding extra newlines, either in the middle or at the end of
    # the file. Ensure the parent directory exists before writing the
    # file.
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(lines), encoding="utf-8")
    return dest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root",
        nargs="?",
        default="project",
        help="directory to search for .object files",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="extracted_st",
        help="directory to write .st files to",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="print extracted text instead of writing files",
    )
    args = parser.parse_args()

    root = Path(args.root)
    output_dir = Path(args.output_dir)
    if not args.stdout:
        output_dir.mkdir(parents=True, exist_ok=True)

    # Process all .object files under the root directory. Recursively
    # search for .object files and extract their text content.
    count = 0
    for path in sorted(root.rglob("*.object")):
        extracted = extract(path)
        if extracted is None:
            continue
        name, sections = extracted
        count += 1
        if args.stdout:
            print(f"===== {name} ({path}) =====")
            for label, text in sections:
                if label:
                    print(f"(* --- {label} --- *)")
                print(text)
            print()
        else:
            dest = write_st_file(output_dir, name, sections)
            print(f"extract_st: wrote {dest}")

    print(f"extract_st: extracted {count} object(s)", file=sys.stderr)


if __name__ == "__main__":
    main()

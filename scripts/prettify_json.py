#!/usr/bin/env python3
"""Pretty-print staged .object JSON files (CODESYS project objects) before commit."""

import json
import subprocess
import sys


def staged_object_files():
    """Return a list of staged .object files."""
    # ACM stands for added-copied-modified; ignore deleted files which
    # no longer exist on disk.
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [f for f in out.splitlines() if f.endswith(".object")]


def unstaged_files():
    """Return the set of files with unstaged working-tree changes."""
    out = subprocess.run(
        ["git", "diff", "--name-only"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return set(out.splitlines())


def prettify(path):
    """Prettify a single .object JSON file."""
    print(f"pre-commit: prettifying {path}")
    # Read the file content first. Encoding "utf-8-sig" strips a BOM if
    # present, so re-saved files stay as plain UTF-8.
    with open(path, "r", encoding="utf-8-sig") as f:
        content = f.read()
    # Attempt to parse the content as JSON.
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # .object files aren't guaranteed to be JSON; leave non-JSON
        # ones untouched.
        print(f"pre-commit: skipping {path} (not valid JSON)", file=sys.stderr)
        return False
    # Compare the pretty-printed content with the original content. If
    # they differ, overwrite the file with the pretty-printed version.
    # The default dict insertion order with sort_keys=False (default)
    # preserves the original key order; indent=2 only controls
    # formatting, while ensure_ascii=False keeps non-ASCII text
    # readable.
    pretty = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if pretty == content:
        print(f"pre-commit: {path} is already pretty")
        return False
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(pretty)
    return True


def main():
    """Prettify all staged .object JSON files."""
    files = staged_object_files()
    # Reading and writing the working tree would pull in unstaged edits
    # on partially staged files, silently committing more than the user
    # staged; bail out instead.
    partially_staged = sorted(set(files) & unstaged_files())
    if partially_staged:
        print(
            "pre-commit: aborting, these staged .object files also have unstaged "
            "changes (stage fully or stash unstaged changes first):",
            file=sys.stderr,
        )
        for path in partially_staged:
            print(f"  {path}", file=sys.stderr)
        sys.exit(1)
    changed = [path for path in files if prettify(path)]
    if changed:
        # Re-stage the reformatted files so the commit captures the pretty version.
        # This will only re-stage the files that were actually changed.
        # Run `git add` to update the index with the reformatted files.
        # If there are more than 10 changed files, add them individually to avoid
        # potential command line length limits. Otherwise, add them all at once.
        if len(changed) > 10:
            for path in changed:
                subprocess.run(["git", "add", path], check=True)
        else:
            subprocess.run(["git", "add", *changed], check=True)
        print(f"pre-commit: prettified {len(changed)} .object file(s)")
    else:
        print("pre-commit: no .object files needed prettifying")


if __name__ == "__main__":
    main()

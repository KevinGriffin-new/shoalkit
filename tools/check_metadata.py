#!/usr/bin/env python3
"""Assert the package's identity agrees everywhere it is written down.

shoalkit states its version in two files and its subtitle in five. Nothing
cross-checks them, so they drift: the description said "theory gating" for a
month after the package became a drift package, and the Zenodo deposit would
have inherited that wording permanently at the next release. A minted DOI is
immutable, which makes this the one piece of metadata fussiness that is not
merely cosmetic.

This script is the fussiness, automated. Run it in CI so nobody has to
remember.

    python tools/check_metadata.py

Exits 0 if consistent, 1 with a report otherwise.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The one true subtitle. Change it HERE, then run this script; it will tell you
# every file that still disagrees.
SUBTITLE = "linear and Stokes wave transformation with Lagrangian drift"

# Subtitle wording that has been retired. Matched as the full subtitle suffix,
# NOT as a bare phrase: "theory gating" remains a real feature of the package
# and is legitimately named in README's feature list. Only its use as the
# package's identity is drift.
RETIRED = ["transformation with theory gating"]

# Files scanned for the retired wording. Excludes paper/paper.bib and the
# archived observation notes, which legitimately quote history.
PROSE = [
    "README.md",
    "pyproject.toml",
    "CITATION.cff",
    ".zenodo.json",
    "src/shoalkit/__init__.py",
    "paper/paper.md",
]


def norm(s: str) -> str:
    """Lowercase, collapse whitespace, and treat '&' as 'and'."""
    return re.sub(r"\s+", " ", s.replace("&", "and")).strip().lower()


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def version_from_init() -> str:
    m = re.search(r'^__version__\s*=\s*["\']([^"\']+)', read("src/shoalkit/__init__.py"), re.M)
    if not m:
        sys.exit("could not find __version__ in src/shoalkit/__init__.py")
    return m.group(1)


def version_from_cff() -> str:
    m = re.search(r"^version:\s*['\"]?([^'\"\s]+)", read("CITATION.cff"), re.M)
    if not m:
        sys.exit("could not find version: in CITATION.cff")
    return m.group(1)


def main() -> int:
    problems: list[str] = []

    # --- version agreement -------------------------------------------------
    # pyproject.toml is NOT checked: it declares dynamic = ["version"] and
    # hatchling reads __init__.py, so there is only one place to edit.
    init_v, cff_v = version_from_init(), version_from_cff()
    if init_v != cff_v:
        problems.append(
            f"version mismatch: __init__.py has {init_v!r}, CITATION.cff has {cff_v!r}"
        )

    # On a tag build, the tag must match too — this is the check that actually
    # protects the Zenodo deposit, since the webhook mints from the tag.
    ref = os.environ.get("GITHUB_REF", "")
    if ref.startswith("refs/tags/"):
        tag = ref.rsplit("/", 1)[-1].lstrip("v")
        if tag != init_v:
            problems.append(f"tag {tag!r} does not match __version__ {init_v!r}")

    # --- subtitle agreement ------------------------------------------------
    want = norm(SUBTITLE)
    for rel, extract in [
        ("CITATION.cff", lambda t: re.search(r'^title:\s*"(.+)"', t, re.M).group(1)),
        (".zenodo.json", lambda t: json.loads(t)["title"]),
        ("pyproject.toml", lambda t: re.search(r'^description\s*=\s*"(.+)"', t, re.M).group(1)),
        ("paper/paper.md", lambda t: re.search(r"^title:\s*'?(.+?)'?\s*$", t, re.M).group(1)),
        ("src/shoalkit/__init__.py", lambda t: t.split("\n", 1)[0]),
        ("README.md", lambda t: t),
    ]:
        try:
            got = extract(read(rel))
        except (AttributeError, KeyError, json.JSONDecodeError):
            problems.append(f"{rel}: could not extract the title/description field")
            continue
        if want not in norm(got):
            snippet = norm(got)[:90]
            problems.append(f"{rel}: subtitle missing or altered -> {snippet!r}")

    # --- retired wording ---------------------------------------------------
    for rel in PROSE:
        low = norm(read(rel))
        for phrase in RETIRED:
            if norm(phrase) in low:
                problems.append(f"{rel}: contains retired wording {phrase!r}")

    if problems:
        print("metadata is inconsistent:\n")
        for p in problems:
            print(f"  - {p}")
        print(f"\nThe canonical subtitle is defined at the top of {Path(__file__).name}.")
        return 1

    print(f"metadata consistent - version {init_v}, subtitle {SUBTITLE!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build upload packages for the skill marketplaces into dist/.

Usage:
    python3 tools/package.py              # check, then build
    python3 tools/package.py --skip-check # build without running tools/check.py
    python3 tools/package.py --out build  # write somewhere other than dist/

Builds two ZIPs and a SHA256SUMS file:

    openplantbook-skill-<version>.zip   one skill folder (openplantbook/SKILL.md ...)
                                        for claude.ai > Settings > Skills > Upload,
                                        the Claude API Skills endpoint, and skills-only tools
    openplantbook-plugin-<version>.zip  the plugin (manifests, skills/, README, LICENSE)
                                        for the OpenAI plugin portal and claude.ai > Plugins > Upload

Builds are reproducible: files are sorted and timestamps are fixed.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True  # keep tools/__pycache__ out of the tree that check.py scans

import check  # noqa: E402  (tools/ is on sys.path when run as a script)

ROOT = check.ROOT
SKILL_DIR = check.SKILL_DIR
FIXED_TIME = (1980, 1, 1, 0, 0, 0)

# Files that go into the plugin ZIP. Maintainer files (CLAUDE.md, AGENTS.md,
# adapters/, tools/, .github/) and the .agents symlink are left out on purpose.
PLUGIN_FILES = [
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    "README.md",
    "LICENSE",
]


def skill_files() -> list[Path]:
    return sorted(
        p for p in SKILL_DIR.rglob("*")
        if p.is_file() and not p.is_symlink() and "__pycache__" not in p.parts and not p.name.endswith(".pyc")
    )


def add(zf: zipfile.ZipFile, path: Path, arcname: str) -> None:
    info = zipfile.ZipInfo(arcname, FIXED_TIME)
    executable = path.stat().st_mode & 0o111
    info.external_attr = (0o755 if executable else 0o644) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    zf.writestr(info, path.read_bytes())


def build_zip(target: Path, entries: list[tuple[Path, str]]) -> None:
    with zipfile.ZipFile(target, "w") as zf:
        for path, arcname in sorted(entries, key=lambda e: e[1]):
            add(zf, path, arcname)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--out", default="dist", help="output folder (default: dist)")
    parser.add_argument("--skip-check", action="store_true", help="do not run tools/check.py first")
    args = parser.parse_args()

    if not args.skip_check:
        rep = check.run(use_claude=False)
        for msg in rep.errors:
            print(f"ERROR  {msg}")
        if rep.errors:
            print("\nFix the errors above, or use --skip-check.")
            return 1

    version = None
    fm, _ = check.read_frontmatter(check.Report())
    if fm:
        version = (fm.get("metadata") or {}).get("version")
    if not version:
        print("ERROR  could not read metadata.version from SKILL.md")
        return 1

    out = Path(args.out)
    out = out if out.is_absolute() else ROOT / out
    out.mkdir(parents=True, exist_ok=True)

    skill_zip = out / f"{check.SKILL_NAME}-skill-{version}.zip"
    plugin_zip = out / f"{check.SKILL_NAME}-plugin-{version}.zip"

    skill_entries = [(p, f"{check.SKILL_NAME}/{p.relative_to(SKILL_DIR).as_posix()}") for p in skill_files()]
    plugin_entries = [(ROOT / name, name) for name in PLUGIN_FILES]
    plugin_entries += [(p, p.relative_to(ROOT).as_posix()) for p in skill_files()]

    build_zip(skill_zip, skill_entries)
    build_zip(plugin_zip, plugin_entries)

    sums = out / "SHA256SUMS"
    sums.write_text(
        "".join(f"{sha256(z)}  {z.name}\n" for z in (skill_zip, plugin_zip)),
        encoding="utf-8",
    )

    for z, count in ((skill_zip, len(skill_entries)), (plugin_zip, len(plugin_entries))):
        print(f"built {z.relative_to(ROOT) if z.is_relative_to(ROOT) else z}  ({count} files, {z.stat().st_size // 1024 or 1} KiB)")
    print(f"wrote {sums.relative_to(ROOT) if sums.is_relative_to(ROOT) else sums}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

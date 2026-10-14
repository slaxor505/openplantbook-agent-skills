#!/usr/bin/env python3
"""Check the Open Plantbook skill and its marketplace manifests before publishing.

Usage:
    python3 tools/check.py              # run all checks
    python3 tools/check.py --tag v1.0.0 # also require the tag to match the version
    python3 tools/check.py --no-claude  # skip `claude plugin validate`

Needs PyYAML (`pip install pyyaml`). Exit code is 1 when any error is found.
The rules come from the Agent Skills spec and the Anthropic, OpenAI and ClawHub
submission checklists. See PUBLISHING.md.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required: pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
SKILL_NAME = "openplantbook"
SKILL_DIR = ROOT / "skills" / SKILL_NAME

# Agent Skills spec: https://agentskills.io/specification
SPEC_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
# metadata values must be strings, except these documented ClawHub/OpenClaw blocks.
NESTED_METADATA_KEYS = {"openclaw"}
RESERVED_NAME_WORDS = ("anthropic", "claude")

SKIP_DIRS = {".git", "dist", "node_modules"}
JUNK_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini", "__MACOSX", "__pycache__", ".env"}
JUNK_SUFFIXES = (".pyc", ".env", ".log")
ALLOWED_SYMLINKS = {".agents/skills/openplantbook": "../../skills/openplantbook"}
BINARY_OK_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".woff", ".woff2", ".ttf", ".otf"}
MAX_TEXT_BYTES = 256 * 1024  # Anthropic directory: larger files are held for review
MAX_FILES = 512  # Anthropic directory limit

SECRET_PATTERNS = [
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b|github_pat_[A-Za-z0-9_]{30,}")),
    ("API key (sk-)", re.compile(r"\bsk-[A-Za-z0-9_-]{24,}\b")),
    ("AWS key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}")),
    (
        "hard-coded credential",
        re.compile(
            r"""(?ix)(client_secret|api[_-]?key|secret|password|token)["']?\s*[:=]\s*["'][A-Za-z0-9_\-+/=]{24,}["']"""
        ),
    ),
]
LOCAL_PATH = re.compile(r"/home/[a-z][\w.-]*/|/Users/[A-Za-z][\w.-]*/")


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.notes: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def note(self, msg: str) -> None:
        self.notes.append(msg)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path, rep: Report):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        rep.error(f"{rel(path)}: file is missing")
    except json.JSONDecodeError as exc:
        rep.error(f"{rel(path)}: invalid JSON ({exc})")
    return None


def read_frontmatter(rep: Report):
    path = SKILL_DIR / "SKILL.md"
    if not path.is_file():
        rep.error(f"{rel(path)}: file is missing")
        return None, ""
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, re.DOTALL)
    if not match:
        rep.error(f"{rel(path)}: missing YAML frontmatter")
        return None, text
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        rep.error(f"{rel(path)}: frontmatter is not valid YAML ({exc})")
        return None, text
    if not isinstance(data, dict):
        rep.error(f"{rel(path)}: frontmatter must be a mapping")
        return None, text
    return data, match.group(2)


def check_skill(rep: Report) -> str | None:
    """Validate SKILL.md against the Agent Skills spec. Returns the skill version."""
    fm, body = read_frontmatter(rep)
    if fm is None:
        return None
    where = "skills/openplantbook/SKILL.md"

    extra = sorted(set(fm) - SPEC_KEYS)
    if extra:
        rep.error(f"{where}: keys outside the Agent Skills spec: {', '.join(extra)}")

    name = fm.get("name")
    if name != SKILL_NAME:
        rep.error(f"{where}: name must be {SKILL_NAME!r} to match its folder, got {name!r}")
    if isinstance(name, str):
        if len(name) > 64 or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
            rep.error(f"{where}: name must be lowercase letters, digits and single hyphens, max 64")
        if any(word in name for word in RESERVED_NAME_WORDS):
            rep.error(f"{where}: name must not contain a reserved word ({', '.join(RESERVED_NAME_WORDS)})")

    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        rep.error(f"{where}: description is required and must be text")
    else:
        if len(desc) > 1024:
            rep.error(f"{where}: description is {len(desc)} chars, max 1024")
        if re.search(r"<[^>]+>", desc):
            rep.error(f"{where}: description must not contain XML/HTML tags")
        if "use when" not in desc.lower():
            rep.warn(f"{where}: description should say when to use the skill ('Use when ...')")

    compat = fm.get("compatibility")
    if compat is None:
        rep.warn(f"{where}: add `compatibility` (needs Python 3 and network access)")
    elif not isinstance(compat, str) or not 1 <= len(compat) <= 500:
        rep.error(f"{where}: compatibility must be text of 1-500 chars")

    if not isinstance(fm.get("license"), str):
        rep.error(f"{where}: license is required for marketplace listings")

    version = None
    meta = fm.get("metadata")
    if not isinstance(meta, dict):
        rep.error(f"{where}: metadata must be a mapping")
    else:
        for key, value in meta.items():
            if key in NESTED_METADATA_KEYS:
                if not isinstance(value, dict):
                    rep.error(f"{where}: metadata.{key} must be an object")
            elif not isinstance(value, str):
                rep.error(f"{where}: metadata.{key} must be a string (quote it)")
        version = meta.get("version")
        if not isinstance(version, str):
            rep.error(f"{where}: metadata.version must be a quoted string")
            version = None

    lines = body.count("\n") + 1
    if lines > 500:
        rep.error(f"{where}: body is {lines} lines, keep SKILL.md under 500")
    if "{baseDir}" in body:
        rep.error(f"{where}: use paths relative to the skill folder instead of {{baseDir}}")

    for link in re.findall(r"`((?:scripts|references|assets)/[\w./-]+)`", body):
        target = link.split()[0]
        if "." in Path(target).name and not (SKILL_DIR / target).exists():
            rep.error(f"{where}: refers to missing file {target}")
    return version


SEMVER = re.compile(r"\d+\.\d+\.\d+(?:[-+][\w.-]+)?")


def check_manifests(rep: Report, skill_version: str | None) -> None:
    claude = load_json(ROOT / ".claude-plugin" / "plugin.json", rep)
    codex = load_json(ROOT / ".codex-plugin" / "plugin.json", rep)
    claude_mp = load_json(ROOT / ".claude-plugin" / "marketplace.json", rep)
    codex_mp = load_json(ROOT / ".agents" / "plugins" / "marketplace.json", rep)

    versions = {}
    for label, data in (("Claude", claude), ("Codex", codex)):
        if not data:
            continue
        where = f".{label.lower()}-plugin/plugin.json"
        if data.get("name") != SKILL_NAME:
            rep.error(f"{where}: name must be {SKILL_NAME!r}, got {data.get('name')!r}")
        if any(word in str(data.get("name", "")) for word in RESERVED_NAME_WORDS):
            rep.error(f"{where}: name must not contain a reserved word")
        desc = data.get("description")
        if not isinstance(desc, str) or len(desc) < 10:
            rep.error(f"{where}: description is required (10+ chars)")
        version = data.get("version")
        if not isinstance(version, str) or not SEMVER.fullmatch(version):
            rep.error(f"{where}: version must be semver, got {version!r}")
        else:
            versions[where] = version
        if data.get("license") != "MIT":
            rep.error(f"{where}: license must be MIT to match LICENSE")
        if not isinstance(data.get("author"), dict) or not data["author"].get("name"):
            rep.error(f"{where}: author.name is required")
        for field in ("homepage", "repository"):
            value = data.get(field, "")
            if not isinstance(value, str) or not value.startswith("https://"):
                rep.error(f"{where}: {field} must be an https URL")

    if skill_version:
        versions["SKILL.md metadata.version"] = skill_version
    if len(set(versions.values())) > 1:
        rep.error("versions differ: " + ", ".join(f"{k}={v}" for k, v in versions.items()))

    if claude:
        for field in ("documentationUrl", "supportUrl"):
            if not str(claude.get(field, "")).startswith("https://"):
                rep.warn(f".claude-plugin/plugin.json: {field} is missing (used by Anthropic's directory listing)")
        if not (ROOT / str(claude.get("icon", "")).lstrip("./")).is_file() or not claude.get("icon"):
            rep.note("no plugin icon: add `icon` (PNG/SVG in the repo) to .claude-plugin/plugin.json for a nicer directory listing")

    if codex:
        skills_path = ROOT / str(codex.get("skills", "")).lstrip("./")
        if not (skills_path / SKILL_NAME / "SKILL.md").is_file():
            rep.error(".codex-plugin/plugin.json: `skills` must point to a folder holding openplantbook/SKILL.md")
        iface = codex.get("interface")
        if not isinstance(iface, dict):
            rep.error(".codex-plugin/plugin.json: interface block is required for the OpenAI listing")
        else:
            for field in ("displayName", "shortDescription", "longDescription", "developerName", "category"):
                if not iface.get(field):
                    rep.error(f".codex-plugin/plugin.json: interface.{field} is required")
            if len(str(iface.get("shortDescription", ""))) > 125:
                rep.error(".codex-plugin/plugin.json: interface.shortDescription must be 125 chars or fewer")
            if not iface.get("composerIcon") or not iface.get("logo"):
                rep.note("no OpenAI icons: add interface.composerIcon and interface.logo (PNG under assets/) before submitting")
            for field in ("privacyPolicyURL", "termsOfServiceURL"):
                if not iface.get(field):
                    rep.note(f"OpenAI portal may ask for interface.{field}")

    if claude_mp:
        if not isinstance(claude_mp.get("owner"), dict) or not claude_mp["owner"].get("name"):
            rep.error(".claude-plugin/marketplace.json: owner.name is required")
        entries = claude_mp.get("plugins") or []
        if not any(p.get("name") == SKILL_NAME and p.get("source") == "./" for p in entries):
            rep.error(".claude-plugin/marketplace.json: needs an entry named openplantbook with source './'")

    if codex_mp:
        for entry in codex_mp.get("plugins") or []:
            src = entry.get("source")
            path = src.get("path") if isinstance(src, dict) else src
            target = (ROOT / str(path)).resolve()
            if not (target / ".codex-plugin" / "plugin.json").is_file():
                rep.error(f".agents/plugins/marketplace.json: {path!r} has no .codex-plugin/plugin.json")
            policy = entry.get("policy") or {}
            if not (policy.get("installation") and policy.get("authentication") and entry.get("category")):
                rep.error(".agents/plugins/marketplace.json: entry needs policy.installation, policy.authentication and category")


def check_files(rep: Report) -> None:
    readme = ROOT / "README.md"
    if not readme.is_file():
        rep.error("README.md is missing")
    else:
        prose = re.sub(r"```.*?```", "", readme.read_text(encoding="utf-8"), flags=re.DOTALL)
        words = len(re.findall(r"\w+", prose))
        if words < 40:
            rep.error(f"README.md has {words} words outside code blocks, Anthropic requires 40+")
    license_file = ROOT / "LICENSE"
    if not license_file.is_file() or "MIT License" not in license_file.read_text(encoding="utf-8"):
        rep.error("LICENSE is missing or is not the MIT license")
    for required in ("SKILL.md", "scripts/openplantbook_cli.py"):
        if not (SKILL_DIR / required).is_file():
            rep.error(f"skills/openplantbook/{required} is missing")

    count = 0
    for path in sorted(ROOT.rglob("*")):
        parts = path.relative_to(ROOT).parts
        if parts[0] in SKIP_DIRS:
            continue
        name = path.name
        r = rel(path)
        if path.is_symlink():
            expected = ALLOWED_SYMLINKS.get(r)
            if expected is None:
                rep.error(f"{r}: symlinks are rejected by marketplace validators")
            elif str(path.readlink()) != expected:
                rep.error(f"{r}: symlink must point to {expected}")
            continue
        if path.is_dir():
            if name in JUNK_NAMES:
                rep.error(f"{r}: remove this folder")
            continue
        count += 1
        if name in JUNK_NAMES or name.endswith(JUNK_SUFFIXES):
            rep.error(f"{r}: remove this file (junk, cache or credential file)")
            continue
        size = path.stat().st_size
        if path.suffix.lower() in BINARY_OK_SUFFIXES:
            continue
        if size > MAX_TEXT_BYTES:
            rep.error(f"{r}: {size // 1024} KiB, files over 256 KiB are held for manual review")
        try:
            path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            rep.error(f"{r}: binary file; marketplaces accept text, images and fonts only")
    if count > MAX_FILES:
        rep.error(f"{count} files, Anthropic's directory holds plugins over {MAX_FILES} files for review")


def check_secrets(rep: Report) -> None:
    this_file = Path(__file__).resolve()
    for path in sorted(ROOT.rglob("*")):
        parts = path.relative_to(ROOT).parts
        if parts[0] in SKIP_DIRS or path.is_symlink() or not path.is_file() or path.resolve() == this_file:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in SECRET_PATTERNS:
            if pattern.search(text):
                rep.error(f"{rel(path)}: looks like it contains a {label}")
        in_package = SKILL_DIR in path.parents and path.name != "publish-notes.md"
        if in_package and LOCAL_PATH.search(text):
            rep.error(f"{rel(path)}: contains a local filesystem path; keep these out of the packaged skill")


def check_helper(rep: Report) -> None:
    script = SKILL_DIR / "scripts" / "openplantbook_cli.py"
    if not script.is_file():
        return
    try:
        ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
    except SyntaxError as exc:
        rep.error(f"{rel(script)}: syntax error ({exc})")
        return
    try:
        proc = subprocess.run(
            [sys.executable, "-B", str(script), "--help"],
            capture_output=True, text=True, timeout=30, check=False,
        )
    except subprocess.TimeoutExpired:
        rep.error(f"{rel(script)} --help timed out")
        return
    if proc.returncode != 0:
        rep.error(f"{rel(script)} --help failed: {proc.stderr.strip()[:200]}")


def check_claude_validator(rep: Report) -> None:
    claude = shutil.which("claude")
    if not claude:
        rep.note("`claude` CLI not found: skipped `claude plugin validate`")
        return
    proc = subprocess.run(
        [claude, "plugin", "validate", str(ROOT)],
        capture_output=True, text=True, timeout=120, check=False,
    )
    output = (proc.stdout + proc.stderr).strip()
    if proc.returncode != 0:
        rep.error("`claude plugin validate` failed:\n    " + output.replace("\n", "\n    "))
    else:
        for line in output.splitlines():
            if line.strip().startswith("> root: CLAUDE.md"):
                rep.note("claude plugin validate: CLAUDE.md at the plugin root is not loaded as context (harmless)")
        rep.note("claude plugin validate passed")


def run(tag: str | None = None, use_claude: bool = True) -> Report:
    rep = Report()
    version = check_skill(rep)
    check_manifests(rep, version)
    check_files(rep)
    check_secrets(rep)
    check_helper(rep)
    if use_claude:
        check_claude_validator(rep)
    if tag is not None and version and tag.lstrip("v") != version:
        rep.error(f"tag {tag!r} does not match version {version!r}")
    return rep


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--tag", help="release tag (for example v1.0.0) that must match the version")
    parser.add_argument("--no-claude", action="store_true", help="skip `claude plugin validate`")
    args = parser.parse_args()

    rep = run(args.tag, use_claude=not args.no_claude)
    for msg in rep.errors:
        print(f"ERROR  {msg}")
    for msg in rep.warnings:
        print(f"WARN   {msg}")
    for msg in rep.notes:
        print(f"NOTE   {msg}")
    if rep.errors:
        print(f"\nFAILED: {len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
        return 1
    print(f"\nOK: no errors, {len(rep.warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

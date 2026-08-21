#!/usr/bin/env python3
"""Validate the cross-marketplace aburasashi repository without dependencies."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_NAME = "aburasashi"
PLUGIN_ROOT = ROOT / "plugins" / PLUGIN_NAME
SKILLS_ROOT = PLUGIN_ROOT / "skills"
SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
KEBAB_CASE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", re.DOTALL)


class Validator:
    def __init__(self, release: bool) -> None:
        self.release = release
        self.errors: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def load_json(self, relative_path: str) -> dict[str, Any]:
        path = ROOT / relative_path
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            self.error(f"missing {relative_path}")
            return {}
        except json.JSONDecodeError as exc:
            self.error(f"invalid JSON in {relative_path}: {exc}")
            return {}
        if not isinstance(value, dict):
            self.error(f"{relative_path} must contain a JSON object")
            return {}
        return value

    def require_text(
        self, value: dict[str, Any], key: str, context: str
    ) -> str | None:
        item = value.get(key)
        if not isinstance(item, str) or not item.strip():
            self.error(f"{context}.{key} must be a non-empty string")
            return None
        return item.strip()

    def find_plugin_entry(
        self, marketplace: dict[str, Any], context: str
    ) -> dict[str, Any]:
        plugins = marketplace.get("plugins")
        if not isinstance(plugins, list):
            self.error(f"{context}.plugins must be an array")
            return {}
        matches = [
            item
            for item in plugins
            if isinstance(item, dict) and item.get("name") == PLUGIN_NAME
        ]
        if len(matches) != 1:
            self.error(
                f"{context}.plugins must contain exactly one {PLUGIN_NAME!r} entry"
            )
            return {}
        return matches[0]

    def validate_plugin_manifests(self) -> None:
        codex = self.load_json("plugins/aburasashi/.codex-plugin/plugin.json")
        claude = self.load_json("plugins/aburasashi/.claude-plugin/plugin.json")

        for context, manifest in (("codex plugin", codex), ("claude plugin", claude)):
            if manifest.get("name") != PLUGIN_NAME:
                self.error(f"{context}.name must equal {PLUGIN_NAME!r}")
            version = self.require_text(manifest, "version", context)
            if version and not SEMVER.fullmatch(version):
                self.error(f"{context}.version must be strict semantic versioning")
            self.require_text(manifest, "description", context)
            author = manifest.get("author")
            if not isinstance(author, dict):
                self.error(f"{context}.author must be an object")
            else:
                self.require_text(author, "name", f"{context}.author")
            if manifest.get("skills") != "./skills/":
                self.error(f"{context}.skills must equal './skills/'")
            if manifest.get("license") != "MIT":
                self.error(f"{context}.license must equal 'MIT'")

        if codex.get("version") != claude.get("version"):
            self.error("Claude and Codex plugin versions must match")
        if codex.get("description") != claude.get("description"):
            self.error("Claude and Codex plugin descriptions must match")

        interface = codex.get("interface")
        if not isinstance(interface, dict):
            self.error("codex plugin.interface must be an object")
        else:
            for key in (
                "displayName",
                "shortDescription",
                "longDescription",
                "developerName",
                "category",
            ):
                self.require_text(interface, key, "codex plugin.interface")
            capabilities = interface.get("capabilities")
            if not isinstance(capabilities, list) or not all(
                isinstance(item, str) and item.strip() for item in capabilities
            ):
                self.error(
                    "codex plugin.interface.capabilities must be an array of strings"
                )
            prompts = interface.get("defaultPrompt")
            if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3:
                self.error(
                    "codex plugin.interface.defaultPrompt must contain 1 to 3 prompts"
                )
            elif not all(
                isinstance(item, str) and 1 <= len(item.strip()) <= 128
                for item in prompts
            ):
                self.error(
                    "each codex plugin default prompt must be 1 to 128 characters"
                )

    def validate_marketplaces(self) -> None:
        codex = self.load_json(".agents/plugins/marketplace.json")
        claude = self.load_json(".claude-plugin/marketplace.json")

        for context, marketplace in (
            ("codex marketplace", codex),
            ("claude marketplace", claude),
        ):
            if marketplace.get("name") != PLUGIN_NAME:
                self.error(f"{context}.name must equal {PLUGIN_NAME!r}")

        codex_entry = self.find_plugin_entry(codex, "codex marketplace")
        if codex_entry.get("source") != {
            "source": "local",
            "path": "./plugins/aburasashi",
        }:
            self.error("codex marketplace source must point to ./plugins/aburasashi")
        policy = codex_entry.get("policy")
        if not isinstance(policy, dict):
            self.error("codex marketplace policy must be an object")
        else:
            if policy.get("installation") not in {
                "AVAILABLE",
                "INSTALLED_BY_DEFAULT",
                "NOT_AVAILABLE",
            }:
                self.error("codex marketplace installation policy is invalid")
            if policy.get("authentication") not in {"ON_INSTALL", "ON_USE"}:
                self.error("codex marketplace authentication policy is invalid")
        self.require_text(codex_entry, "category", "codex marketplace plugin")

        claude_entry = self.find_plugin_entry(claude, "claude marketplace")
        if claude_entry.get("source") != "./plugins/aburasashi":
            self.error("claude marketplace source must point to ./plugins/aburasashi")
        owner = claude.get("owner")
        if not isinstance(owner, dict):
            self.error("claude marketplace.owner must be an object")
        else:
            self.require_text(owner, "name", "claude marketplace.owner")

    @staticmethod
    def frontmatter_value(frontmatter: str, key: str) -> str | None:
        match = re.search(
            rf"^(?:{re.escape(key)}):[ \t]*(.*)$", frontmatter, re.MULTILINE
        )
        if not match:
            return None
        return match.group(1).strip().strip("'\"")

    def validate_skills(self) -> int:
        if not SKILLS_ROOT.is_dir():
            self.error("plugins/aburasashi/skills must be a directory")
            return 0

        skill_dirs = sorted(
            path
            for path in SKILLS_ROOT.iterdir()
            if path.is_dir() and not path.name.startswith(".")
        )
        for skill_dir in skill_dirs:
            if not KEBAB_CASE.fullmatch(skill_dir.name):
                self.error(f"skill directory {skill_dir.name!r} must use kebab-case")
            skill_file = skill_dir / "SKILL.md"
            try:
                contents = skill_file.read_text(encoding="utf-8")
            except FileNotFoundError:
                self.error(f"{skill_dir.relative_to(ROOT)} is missing SKILL.md")
                continue
            match = FRONTMATTER.match(contents)
            if not match:
                self.error(f"{skill_file.relative_to(ROOT)} has invalid frontmatter")
                continue
            frontmatter = match.group(1)
            name = self.frontmatter_value(frontmatter, "name")
            description = self.frontmatter_value(frontmatter, "description")
            if name != skill_dir.name:
                self.error(
                    f"{skill_file.relative_to(ROOT)} name must equal {skill_dir.name!r}"
                )
            if not description:
                self.error(
                    f"{skill_file.relative_to(ROOT)} description must be non-empty"
                )
            disabled = self.frontmatter_value(
                frontmatter, "disable-model-invocation"
            ) or self.frontmatter_value(frontmatter, "disable_model_invocation")
            if disabled and disabled.lower() not in {"false", "no", "off", "0"}:
                self.error(
                    f"{skill_file.relative_to(ROOT)} must allow model invocation"
                )
            body = contents[match.end() :].strip()
            if not body:
                self.error(f"{skill_file.relative_to(ROOT)} has no instructions")
            if self.release and re.search(r"\[TODO|\bTODO:", contents, re.IGNORECASE):
                self.error(f"{skill_file.relative_to(ROOT)} contains a TODO marker")

        if self.release and not skill_dirs:
            self.error("release validation requires at least one distributable skill")
        return len(skill_dirs)

    def run(self) -> int:
        self.validate_plugin_manifests()
        self.validate_marketplaces()
        skill_count = self.validate_skills()
        if self.errors:
            for message in self.errors:
                print(f"error: {message}", file=sys.stderr)
            print(
                f"validation failed with {len(self.errors)} error(s)", file=sys.stderr
            )
            return 1
        mode = "release" if self.release else "development"
        print(f"ok: {mode} structure is valid ({skill_count} skill(s))")
        return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--release",
        action="store_true",
        help="require at least one finished skill and reject TODO markers",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return Validator(release=args.release).run()


if __name__ == "__main__":
    raise SystemExit(main())

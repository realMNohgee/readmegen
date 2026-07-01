#!/usr/bin/env python3
"""readmegen — Analyze a project directory and generate a README.md skeleton, using only Python stdlib."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def detect_languages(root: Path) -> list[str]:
    """Detect programming languages used in the project."""
    languages: set[str] = set()
    ext_map = {
        ".py": "Python",
        ".js": "JavaScript", ".mjs": "JavaScript", ".cjs": "JavaScript",
        ".ts": "TypeScript", ".tsx": "TypeScript",
        ".jsx": "JavaScript (React)",
        ".go": "Go",
        ".rs": "Rust",
        ".rb": "Ruby",
        ".java": "Java",
        ".kt": "Kotlin", ".kts": "Kotlin",
        ".swift": "Swift",
        ".c": "C", ".h": "C",
        ".cpp": "C++", ".hpp": "C++", ".cc": "C++", ".cxx": "C++",
        ".cs": "C#",
        ".php": "PHP",
        ".r": "R",
        ".sql": "SQL",
        ".sh": "Shell", ".bash": "Shell", ".zsh": "Shell",
        ".html": "HTML",
        ".css": "CSS", ".scss": "SCSS", ".sass": "Sass", ".less": "Less",
        ".vue": "Vue",
        ".svelte": "Svelte",
        ".md": "Markdown",
        ".yaml": "YAML", ".yml": "YAML",
        ".json": "JSON",
        ".toml": "TOML",
        ".xml": "XML",
    }
    for f in root.rglob("*"):
        if f.is_file():
            lang = ext_map.get(f.suffix.lower(), "")
            if lang:
                languages.add(lang)
    return sorted(languages)


def detect_test_framework(root: Path) -> str | None:
    """Detect test framework."""
    # Python
    if (root / "pytest.ini").exists() or (root / "pyproject.toml").exists():
        try:
            content = (root / "pyproject.toml").read_text()
            if "pytest" in content:
                return "pytest"
        except Exception:
            pass
    if (root / "setup.cfg").exists():
        try:
            content = (root / "setup.cfg").read_text()
            if "pytest" in content:
                return "pytest"
        except Exception:
            pass
    if list(root.glob("*test*.py")) or list(root.glob("test_*.py")):
        return "unittest/pytest"

    # JavaScript/TypeScript
    pkg_json = root / "package.json"
    if pkg_json.exists():
        try:
            data = json.loads(pkg_json.read_text())
            dev_deps = {**data.get("devDependencies", {}), **data.get("dependencies", {})}
            if "jest" in dev_deps:
                return "Jest"
            if "mocha" in dev_deps:
                return "Mocha"
            if "vitest" in dev_deps:
                return "Vitest"
            if "ava" in dev_deps:
                return "AVA"
            if "jasmine" in dev_deps:
                return "Jasmine"
        except Exception:
            pass

    # Go
    if list(root.glob("*_test.go")):
        return "Go testing"

    # Rust
    if (root / "Cargo.toml").exists():
        return "cargo test"

    # Ruby
    if (root / "Gemfile").exists():
        try:
            content = (root / "Gemfile").read_text()
            if "rspec" in content:
                return "RSpec"
            if "minitest" in content:
                return "Minitest"
        except Exception:
            pass

    return None


def detect_build_system(root: Path) -> str | None:
    """Detect build system or package manager."""
    checks = [
        ((root / "pyproject.toml"), "pip/poetry/hatch (pyproject.toml)"),
        ((root / "setup.py"), "setuptools"),
        ((root / "setup.cfg"), "setuptools"),
        ((root / "requirements.txt"), "pip (requirements.txt)"),
        ((root / "Pipfile"), "pipenv"),
        ((root / "package.json"), "npm/yarn/pnpm"),
        ((root / "yarn.lock"), "Yarn"),
        ((root / "pnpm-lock.yaml"), "pnpm"),
        ((root / "go.mod"), "Go modules"),
        ((root / "Cargo.toml"), "Cargo"),
        ((root / "Makefile"), "Make"),
        ((root / "CMakeLists.txt"), "CMake"),
        ((root / "build.gradle"), "Gradle"),
        ((root / "build.gradle.kts"), "Gradle (Kotlin DSL)"),
        ((root / "pom.xml"), "Maven"),
        ((root / "Gemfile"), "Bundler"),
        ((root / "composer.json"), "Composer"),
        ((root / "Dockerfile"), "Docker"),
        ((root / "docker-compose.yml"), "Docker Compose"),
        ((root / "docker-compose.yaml"), "Docker Compose"),
    ]
    found = []
    for path_obj, name in checks:
        if path_obj.exists():
            found.append(name)
    return ", ".join(found) if found else None


def detect_entry_points(root: Path) -> list[str]:
    """Detect potential entry point files."""
    entry_patterns = [
        "main.py", "app.py", "server.py", "run.py", "cli.py", "manage.py",
        "index.js", "main.js", "app.js", "server.js",
        "main.go", "main.rs", "main.ts",
        "index.ts", "app.ts",
    ]
    found = []
    for pattern in entry_patterns:
        matches = list(root.glob(pattern))
        for m in matches:
            found.append(str(m.relative_to(root)))
    return found[:5]  # limit to top 5


def detect_project_name(root: Path) -> str:
    """Detect project name."""
    # Try pyproject.toml
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text()
            for line in content.splitlines():
                if line.strip().startswith("name"):
                    name = line.split("=", 1)[1].strip().strip('"').strip("'")
                    return name
        except Exception:
            pass

    # Try package.json
    pkg = root / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text())
            if "name" in data:
                return data["name"]
        except Exception:
            pass

    # Try go.mod
    gomod = root / "go.mod"
    if gomod.exists():
        try:
            first_line = gomod.read_text().splitlines()[0]
            if first_line.startswith("module "):
                return first_line.split("module ")[1].strip()
        except Exception:
            pass

    # Try Cargo.toml
    cargo = root / "Cargo.toml"
    if cargo.exists():
        try:
            for line in cargo.read_text().splitlines():
                if line.strip().startswith("name"):
                    name = line.split("=", 1)[1].strip().strip('"').strip("'")
                    return name
        except Exception:
            pass

    # Fallback to directory name
    return root.resolve().name


def analyze(root: Path) -> dict:
    """Analyze a project directory and return detected info."""
    return {
        "project_name": detect_project_name(root),
        "languages": detect_languages(root),
        "test_framework": detect_test_framework(root),
        "build_system": detect_build_system(root),
        "entry_points": detect_entry_points(root),
    }


def generate_readme(root: Path) -> str:
    """Generate README.md content from analysis."""
    info = analyze(root)
    name = info["project_name"]
    langs = info["languages"]
    lang_str = ", ".join(langs) if langs else "unknown"
    test_fw = info["test_framework"] or "none detected"
    build_sys = info["build_system"] or "none detected"
    entry_pts = info["entry_points"]

    title = name.replace("-", " ").replace("_", " ").title()

    lines = []
    lines.append(f"# {title} 🏷️")
    lines.append("")
    lines.append(f"**Built with {lang_str}.** Zero dependencies (or minimal deps), pure standard library where possible.")
    lines.append("")
    lines.append(f"A project that does something useful. Detected {len(langs)} language(s) in this repository.")
    lines.append("")
    lines.append("> Part of the **Trust & Reliability Layer for Agentic AI** — provenance, economics, truth, and interop tools for people building on agentic models.")
    lines.append("")
    lines.append("## 📋 Project Overview")
    lines.append("")
    lines.append(f"- **Languages:** {lang_str}")
    lines.append(f"- **Build System:** {build_sys}")
    lines.append(f"- **Test Framework:** {test_fw}")
    if entry_pts:
        lines.append(f"- **Entry Points:** {', '.join(entry_pts)}")
    lines.append("")
    lines.append("## 🚀 Install")
    lines.append("")
    lines.append("```bash")
    lines.append(f"git clone <repo-url>")
    lines.append(f"cd {name}")
    lines.append("# Follow language-specific setup below")
    lines.append("```")
    lines.append("")

    # Language-specific install instructions
    if "Python" in langs:
        lines.append("### Python")
        lines.append("```bash")
        if info["build_system"] and "requirements.txt" in (info["build_system"] or ""):
            lines.append("pip install -r requirements.txt")
        elif info["build_system"] and "pyproject.toml" in (info["build_system"] or ""):
            lines.append("pip install -e .")
        else:
            lines.append("python3 main.py  # or the entry point script")
        lines.append("```")
        lines.append("")

    if any(l in langs for l in ["JavaScript", "TypeScript"]):
        lines.append("### Node.js")
        lines.append("```bash")
        lines.append("npm install")
        lines.append("node index.js")
        lines.append("```")
        lines.append("")

    if "Go" in langs:
        lines.append("### Go")
        lines.append("```bash")
        lines.append("go mod tidy")
        lines.append("go run main.go")
        lines.append("```")
        lines.append("")

    if "Rust" in langs:
        lines.append("### Rust")
        lines.append("```bash")
        lines.append("cargo build --release")
        lines.append("cargo run")
        lines.append("```")
        lines.append("")

    lines.append("## 📖 Usage")
    lines.append("")
    lines.append("Describe how to use the project here. Add examples, CLI flags, or API usage.")
    lines.append("")
    lines.append("```bash")
    if entry_pts:
        lines.append(f"# Example with detected entry point: {entry_pts[0]}")
    lines.append("```")
    lines.append("")
    lines.append("## 🧪 Testing")
    lines.append("")
    lines.append(f"Tests use **{test_fw}**.")
    lines.append("")
    lines.append("```bash")
    if "pytest" in (test_fw or ""):
        lines.append("pytest")
    elif "Jest" in (test_fw or ""):
        lines.append("npm test")
    elif "Go testing" in (test_fw or ""):
        lines.append("go test ./...")
    elif "cargo" in (test_fw or ""):
        lines.append("cargo test")
    else:
        lines.append("# Run your test suite")
    lines.append("```")
    lines.append("")
    lines.append("## 📄 License")
    lines.append("")
    lines.append("MIT — see [LICENSE](LICENSE).")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("🧰 **[Tool on Hermtica Marketplace](https://hermtica.com/marketplace)** — the open, agent-agnostic marketplace for AI agent tools.")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")

    parser = argparse.ArgumentParser(
        description="readmegen — Analyze a project directory and generate a README.md skeleton",
    )
    parser.add_argument("directory", nargs="?", default=".",
                        help="Project directory to analyze (default: current directory)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_generate = sub.add_parser("generate", parents=[common],
                                 help="Generate README.md content")
    p_generate.add_argument("--output", "-o", help="Write README to file instead of stdout")

    p_analyze = sub.add_parser("analyze", parents=[common],
                                help="Show detected project info")

    args = parser.parse_args()
    root = Path(args.directory).resolve()

    if not root.is_dir():
        print(f"Error: '{args.directory}' is not a directory", file=sys.stderr)
        sys.exit(1)

    if args.cmd == "analyze":
        info = analyze(root)
        if args.format == "json":
            print(json.dumps(info, indent=2))
        else:
            print(f"\nProject Analysis: {info['project_name']}\n")
            print(f"  Languages:      {', '.join(info['languages']) or 'none detected'}")
            print(f"  Test framework: {info['test_framework'] or 'none detected'}")
            print(f"  Build system:   {info['build_system'] or 'none detected'}")
            if info["entry_points"]:
                print(f"  Entry points:   {', '.join(info['entry_points'])}")

    elif args.cmd == "generate":
        readme = generate_readme(root)
        if args.output:
            out_path = Path(args.output)
            out_path.write_text(readme)
            print(f"README written to {args.output}")
        else:
            print(readme)


if __name__ == "__main__":
    main()

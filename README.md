# readmegen 🏷️
![CI](https://github.com/realMNohgee/readmegen/actions/workflows/ci.yml/badge.svg) ![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg) ![License](https://img.shields.io/badge/license-MIT-blue.svg)

**Generate a README.md skeleton from project analysis.** Zero dependencies, pure Python stdlib.

Analyzes a project directory to detect languages, test frameworks, build systems, and entry points — then generates a structured README.md template. Perfect for bootstrapping documentation in new or undocumented projects.

> Part of the **Trust & Reliability Layer for Agentic AI** — provenance, economics, truth, and interop tools for people building on agentic models.

## Why it exists

Every project needs a README, but writing one from scratch is tedious. `readmegen` analyzes what's actually in your repo and produces a sensible skeleton you can fill in — saving time and ensuring consistency.

## One tool, many domains

| Domain | What readmegen does |
|---|---|
| 🏷️ **Documentation** | Bootstraps README files for new projects |
| 🏷️ **Open Source** | Ensures consistent, complete project docs |
| 🏷️ **Onboarding** | Helps new contributors understand project structure |

## What it detects

- **Languages:** Python, JavaScript, TypeScript, Go, Rust, Ruby, Java, Kotlin, Swift, C/C++, C#, PHP, Shell, and more
- **Build systems:** pip, poetry, npm, yarn, Go modules, Cargo, Gradle, Maven, Make, CMake, Docker
- **Test frameworks:** pytest, Jest, Mocha, Vitest, Go testing, cargo test, RSpec
- **Entry points:** `main.py`, `index.js`, `main.go`, `server.py`, and common patterns

## Install
```bash
git clone git@github.com:realMNohgee/readmegen.git
cd readmegen
python3 readmegen.py --help
```

## Quick start
```bash
# Analyze current directory
python3 readmegen.py . analyze

# Generate README to stdout
python3 readmegen.py . generate

# Write to file
python3 readmegen.py . generate --output README.md

# JSON output
python3 readmegen.py . analyze --format json
```

```
Project Analysis: my-project

  Languages:      Python, TypeScript
  Test framework: pytest
  Build system:   pip/poetry/hatch (pyproject.toml), npm/yarn/pnpm
  Entry points:   main.py, cli.py
```

## License

MIT — see [LICENSE](LICENSE).

---

🧰 **[Tool on Hermtica Marketplace](https://hermtica.com/marketplace)** — the open, agent-agnostic marketplace for AI agent tools.

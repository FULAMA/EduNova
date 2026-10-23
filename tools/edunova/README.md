# EduNova Engineering CLI

The CLI can be run from a source checkout or installed as the `edunova`
console command. It runs commands against the current working directory.

## Install

From this repository:

```powershell
python -m pip install .
```

To update an installation from the repository, run the same command again in
the target environment. For a built artifact, install the newer wheel with
`python -m pip install --upgrade path\to\edunova.whl`. To uninstall the CLI,
run `python -m pip uninstall edunova` in that same environment. This removes
the Python distribution; it does not delete project files or the separate
VS Code extension.

To install the quality and test tools used by this project:

```powershell
python -m pip install ".[dev]"
```

From another Python project, install this package in that project's
environment and run `edunova` from the target project's root. Python source
checks use the conventional `src` and `tools` directories when present.

## Commands

```text
edunova --help
edunova run_tests
edunova quality
edunova security
edunova work
edunova fulama-workflow
edunova diagnose
edunova agent "Describe the engineering task"
```

`quality` runs Ruff, Mypy, and pytest. `security` runs Bandit static analysis
for available `src` and `tools` directories. It does not audit third-party
dependencies, verify deployed configuration, or replace expert review.
`work` runs quality and then security, stopping after a failed stage.
`fulama-workflow` is the reusable extension point; by default it runs the
same quality and security stages. Other projects can register their own
steps:

```python
from tools.edunova.core.command_registry import CommandRegistry
from tools.edunova.extensions import FulamaWorkflow

registry = CommandRegistry()
FulamaWorkflow.register(registry, [my_check_command, my_report_command])
```

Each step implements the existing `Command` interface and returns a
`CommandResult`.

`diagnose` runs the configured tests, Ruff and Mypy quality checks, Bandit,
and a read-only `git status --short --untracked-files=all` summary. It reports
each stage and a global result; failures remain visible and produce a non-zero
exit code. If interrupted, it records the active stage and marks the remaining
stages skipped. Git unavailable or a directory outside a Git worktree is
reported as review required. Bandit covers Python static analysis only; this
diagnostic does not claim to audit dependencies or replace manual review.
`quality` retains its existing behavior and still includes pytest.

Agent commands require configured provider credentials. They send the task
and selected project context to the configured model provider. Do not include
secrets in prompts or project files selected as context.
Install the optional provider SDKs with `python -m pip install ".[agents]"`
to enable those commands; local quality and test commands do not require them.
This distribution currently follows the ERP's Python requirement (`>=3.13,<3.14`).

Pytest uses `.pytest-work` under the current project root for temporary test
data. Add that directory to the project's ignore rules if they do not already
ignore generated test files.

Subprocesses have a 600-second timeout by default. Embedders can provide a
`ProcessRunner(timeout=seconds)` to `CliBootstrap`, or pass `timeout=None` to
disable the limit for a controlled long-running task.

## Per-project configuration

Configuration is read from the nearest ancestor `pyproject.toml`, relative to
the directory where the CLI starts. If the file or `[tool.edunova]` table is
absent, the defaults are `src/`, `tests/`, and a 600-second timeout. Paths are
resolved from that project root, checked for existence and prevented from
escaping it. Only the built-in Ruff, Mypy, pytest, and Bandit modules run;
configuration can add arguments but cannot replace them with shell commands.

```toml
[tool.edunova]
source_paths = ["app"]
test_paths = ["checks"]
timeout_seconds = 240
audit_path = ".edunova/audit.sqlite3"

[tool.edunova.commands]
ruff_args = ["check", "--select", "E,F"]
mypy_args = ["--strict"]
pytest_args = ["-q"]
bandit_args = ["-ll"]
```

Supported options are `source_paths`, `test_paths`, `timeout_seconds`, and
`audit_path` in `[tool.edunova]`; and `ruff_args`, `mypy_args`, `pytest_args`,
and `bandit_args` in `[tool.edunova.commands]`. `audit_path` is relative to
the project root and defaults to `.edunova/audit.sqlite3`; absolute paths and
paths escaping the project are rejected. The CLI controls pytest's root and
temporary directories, so `pytest_args` cannot override those settings.

The real CLI entry point persists execution-intent and execution-result audit
events in the SQLite database. The database is created only for a command
execution, not for `--help`. If the audit database cannot be initialized, the
command fails closed instead of silently falling back to in-memory audit.

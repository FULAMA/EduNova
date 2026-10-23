# FulamaWorkflow for Visual Studio Code

This local extension adds five commands to the VS Code Command Palette:

- **FulamaWorkflow: Run Tests**
- **FulamaWorkflow: Run Quality Checks**
- **FulamaWorkflow: Run Bandit Security Scan**
- **FulamaWorkflow: Run Full Workflow**
- **FulamaWorkflow: Diagnose Project**

Open the Command Palette with `Ctrl+Shift+P` and search for `FulamaWorkflow:`. The
extension runs the selected command from the chosen workspace root and streams
its output to the `FulamaWorkflow` output channel. It invokes a fixed command
argument vector with shell execution disabled.

The unified diagnostic reports tests, Ruff/Mypy, Bandit, the read-only Git
working-tree summary, each exit code, and an overall result. A failed stage
does not hide later checks. If interrupted, later stages are reported as
skipped. The command returns a non-zero code for failures or a Git summary
that needs review.

## Configure the CLI executable

The default executable is `edunova` from `PATH`. If the CLI is installed in a
project virtual environment, set `edunova.executable` in VS Code settings to
its executable path, for example:

```json
{
  "edunova.executable": "F:\\Projects\\example\\.venv\\Scripts\\edunova.exe"
}
```

The selected project's `pyproject.toml` controls source paths, test paths,
tool arguments, and process timeout. See `tools/edunova/README.md` for the
configuration format.

## Load locally

Open this `vscode-extension` folder in VS Code and press `F5` to launch an
Extension Development Host. No npm package dependencies are required.

## Update or remove

For a local source checkout, update the extension files from the newer release
and reload the Extension Development Host or VS Code window. This repository
does not currently define a Marketplace installation or update channel. To
remove the locally loaded extension, close the Extension Development Host and
remove this folder from the workspace; no separate extension installer is
present. Uninstall the Python CLI separately with `python -m pip uninstall
edunova` in the environment where it was installed.

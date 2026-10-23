const vscode = require("vscode");
const { runCli } = require("./cli-process");

const COMMANDS = Object.freeze({
  "edunova.runTests": ["run_tests", "Run Tests"],
  "edunova.runQuality": ["quality", "Run Quality Checks"],
  "edunova.runSecurity": ["security", "Run Bandit Security Scan"],
  "edunova.runFulamaWorkflow": ["fulama-workflow", "Run Fulama Workflow"],
  "edunova.diagnoseProject": ["diagnose", "Diagnose Project"],
});

function activate(context) {
  const output = vscode.window.createOutputChannel("FulamaWorkflow");
  let activeProcess = false;

  for (const [commandId, [cliCommand, title]] of Object.entries(COMMANDS)) {
    context.subscriptions.push(
      vscode.commands.registerCommand(commandId, async () => {
        if (activeProcess) {
          void vscode.window.showInformationMessage(
            "A FulamaWorkflow command is already running.",
          );
          return;
        }

        const folders = vscode.workspace.workspaceFolders ?? [];
        if (folders.length === 0) {
          void vscode.window.showWarningMessage(
            "Open a project folder before running FulamaWorkflow.",
          );
          return;
        }

        const folder =
          folders.length === 1
            ? folders[0]
            : await vscode.window.showWorkspaceFolderPick();
        if (!folder) return;

        const executable = vscode.workspace
          .getConfiguration("edunova")
          .get("executable", "edunova");

        output.show(true);
        activeProcess = true;
        try {
          const result = await runCli({
            executable,
            command: cliCommand,
            cwd: folder.uri.fsPath,
            output,
          });
          if (result.error) {
            output.appendLine(
              "Install the CLI or configure edunova.executable with a valid path.",
            );
            void vscode.window.showErrorMessage(
              "Could not start FulamaWorkflow CLI. See its Output channel.",
            );
          } else if (result.code !== 0 || result.signal) {
            void vscode.window.showWarningMessage(
              `${title} did not complete successfully. See the FulamaWorkflow Output channel.`,
            );
          }
        } finally {
          activeProcess = false;
        }
      }),
    );
  }

  context.subscriptions.push(output);
}

function deactivate() {}

module.exports = { activate, deactivate };

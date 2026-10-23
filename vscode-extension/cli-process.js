const { spawn } = require("node:child_process");

function runCli({
  executable,
  command,
  cwd,
  output,
  spawnProcess = spawn,
}) {
  output.appendLine(`> ${command}`);
  output.appendLine(`Workspace: ${cwd}`);
  output.appendLine(`Executable: ${executable}`);

  return new Promise((resolve) => {
    let child;
    let settled = false;
    const finish = (result) => {
      if (settled) return;
      settled = true;
      resolve(result);
    };

    try {
      child = spawnProcess(executable, [command], {
        cwd,
        shell: false,
        windowsHide: true,
        stdio: ["ignore", "pipe", "pipe"],
      });
    } catch (error) {
      output.appendLine(`Could not start CLI: ${error.message}`);
      output.appendLine("Exit code: 127");
      finish({ code: 127, error });
      return;
    }

    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");
    child.stdout.on("data", (chunk) => output.append(chunk));
    child.stderr.on("data", (chunk) => output.append(chunk));

    child.on("error", (error) => {
      if (settled) return;
      output.appendLine(`Could not start CLI: ${error.message}`);
      output.appendLine("Exit code: 127");
      finish({ code: 127, error });
    });

    child.on("close", (code, signal) => {
      if (settled) return;
      if (signal) output.appendLine(`Stopped by signal: ${signal}`);
      output.appendLine(`Exit code: ${code === null ? "unknown" : code}`);
      finish({ code, signal });
    });
  });
}

module.exports = { runCli };

const assert = require("node:assert/strict");
const { EventEmitter } = require("node:events");
const { PassThrough } = require("node:stream");
const test = require("node:test");
const manifest = require("../package.json");
const { runCli } = require("../cli-process");

function makeChild() {
  const child = new EventEmitter();
  child.stdout = new PassThrough();
  child.stderr = new PassThrough();
  return child;
}

function outputCollector() {
  let value = "";
  return {
    append(chunk) {
      value += chunk;
    },
    appendLine(line) {
      value += `${line}\n`;
    },
    read() {
      return value;
    },
  };
}

test("manifest contributes the unified diagnosis command", () => {
  assert.ok(
    manifest.contributes.commands.some(
      ({ command }) => command === "edunova.diagnoseProject",
    ),
  );
  assert.ok(
    manifest.activationEvents.includes("onCommand:edunova.diagnoseProject"),
  );
});

test("runs a fixed CLI argument without shell and reports success", async () => {
  const child = makeChild();
  const output = outputCollector();
  let call;
  const resultPromise = runCli({
    executable: "edunova.exe",
    command: "diagnose",
    cwd: "C:\\workspace",
    output,
    spawnProcess(...args) {
      call = args;
      return child;
    },
  });

  child.stdout.write("Overall: SUCCEEDED (exit 0)\n");
  child.stdout.end();
  child.stderr.end();
  child.emit("close", 0, null);

  const result = await resultPromise;
  assert.deepEqual(call, [
    "edunova.exe",
    ["diagnose"],
    {
      cwd: "C:\\workspace",
      shell: false,
      windowsHide: true,
      stdio: ["ignore", "pipe", "pipe"],
    },
  ]);
  assert.equal(result.code, 0);
  assert.match(output.read(), /Overall: SUCCEEDED/);
  assert.match(output.read(), /Exit code: 0/);
});

test("reports an absent CLI or invalid working directory", async () => {
  const child = makeChild();
  const output = outputCollector();
  const resultPromise = runCli({
    executable: "missing-edunova",
    command: "diagnose",
    cwd: "Z:\\missing-workspace",
    output,
    spawnProcess(_executable, _args, options) {
      assert.equal(options.cwd, "Z:\\missing-workspace");
      setImmediate(() => {
        const error = new Error("spawn ENOENT");
        error.code = "ENOENT";
        child.emit("error", error);
        child.emit("close", -2, null);
      });
      return child;
    },
  });

  const result = await resultPromise;
  assert.equal(result.code, 127);
  assert.equal(result.error.code, "ENOENT");
  assert.match(output.read(), /Could not start CLI/);
  assert.match(output.read(), /Exit code: 127/);
});

test("shows command failures and preserves their exit code", async () => {
  const child = makeChild();
  const output = outputCollector();
  const resultPromise = runCli({
    executable: "edunova",
    command: "diagnose",
    cwd: ".",
    output,
    spawnProcess: () => child,
  });

  child.stderr.write("Overall: FAILED (exit 3)\n");
  child.stdout.end();
  child.stderr.end();
  child.emit("close", 3, null);

  const result = await resultPromise;
  assert.equal(result.code, 3);
  assert.match(output.read(), /Overall: FAILED/);
  assert.match(output.read(), /Exit code: 3/);
});

test("reports an interrupted process and signal", async () => {
  const child = makeChild();
  const output = outputCollector();
  const resultPromise = runCli({
    executable: "edunova",
    command: "diagnose",
    cwd: ".",
    output,
    spawnProcess: () => child,
  });

  child.stdout.end();
  child.stderr.end();
  child.emit("close", null, "SIGINT");

  const result = await resultPromise;
  assert.equal(result.code, null);
  assert.equal(result.signal, "SIGINT");
  assert.match(output.read(), /Stopped by signal: SIGINT/);
  assert.match(output.read(), /Exit code: unknown/);
});

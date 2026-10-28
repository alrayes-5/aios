// AIOS guard for OpenCode. The policy lives in .aios/guard.py (shared with Claude Code).
// This plugin only translates OpenCode's tool call into the payload the guard reads, and blocks on exit 2.
import { spawnSync } from "node:child_process"
import { join } from "node:path"

// Find a Python that really runs: `python3` on macOS and Linux, `python` or `py` on most Windows PCs.
// (On Windows, `python3` is often only a Store shortcut that does not run, so each one is tried, not assumed.)
let python
const findPython = () => {
  if (python) return python
  for (const name of ["python3", "python", "py"]) {
    const r = spawnSync(name, ["-c", "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"], { encoding: "utf8" })
    if (!r.error && r.status === 0) return (python = name)
  }
  return undefined
}

export const AiosGuard = async ({ directory }) => {
  const guard = join(directory, ".aios", "guard.py")
  return {
    "tool.execute.before": async (input, output) => {
      const py = findPython()
      // No working Python: block every tool call, so the guard fails closed
      if (!py) throw new Error("AIOS guard: no working python3, python or py was found, so every action is blocked. Install Python 3 (see START_HERE.md).")
      const payload = JSON.stringify({
        tool_name: input.tool,
        tool_input: output.args ?? {},
        cwd: directory,
      })
      const r = spawnSync(py, [guard], { input: payload, encoding: "utf8" })
      if (r.status !== 0) {
        // exit 2 is a deliberate block; anything else (a crash) also blocks
        throw new Error(r.stderr?.trim() || "AIOS guard could not run. Blocked to be safe.")
      }
    },
  }
}

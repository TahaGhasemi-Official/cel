// VOLTEX engine worker: runs the Python calculation engine (Pyodide) off the UI thread.
import { loadPyodide } from "./pyodide/pyodide.mjs";

const base = new URL("./", import.meta.url).href;
let handle = null;

async function boot() {
  const py = await loadPyodide({ indexURL: base + "pyodide/" });
  const zip = await (await fetch(base + "engine/voltex-engine.zip")).arrayBuffer();
  py.FS.writeFile("/tmp/voltex-engine.zip", new Uint8Array(zip));
  await py.runPythonAsync('import sys\nsys.path.insert(0, "/tmp/voltex-engine.zip")\nfrom bridge import handle as _h');
  handle = py.globals.get("_h");
}

const ready = boot().then(
  () => self.postMessage({ type: "ready" }),
  (err) => self.postMessage({ type: "error", error: String(err && err.message || err) })
);

self.onmessage = async (e) => {
  const { id, payload } = e.data;
  await ready;
  if (!handle) {
    self.postMessage({ id, ok: false, error: "Engine is not available." });
    return;
  }
  try {
    const out = handle(JSON.stringify(payload));
    self.postMessage({ id, ok: true, data: out });
  } catch (err) {
    self.postMessage({ id, ok: false, error: String(err && err.message || err) });
  }
};

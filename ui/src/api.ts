import { PageConfig } from '@jupyterlab/coreutils';

export interface ClayStatus {
  status: 'running' | 'stopped' | 'error';
  pids: string[];
}

/**
 * Fetch the current Clay process status from the backend.
 */
export async function getStatus(): Promise<ClayStatus> {
  const url = PageConfig.getBaseUrl() + 'clay-preview/api/status';
  try {
    const response = await fetch(url, { method: 'GET' });
    if (!response.ok) {
      return { status: 'error', pids: [] };
    }
    return response.json();
  } catch {
    return { status: 'error', pids: [] };
  }
}

export interface RenderResult {
  ok: boolean;
  /** Human-readable error label (e.g. "render failed"). */
  error?: string;
  /** Full output from the Clojure process; shown in the error overlay. */
  detail?: string;
  /** The file path that was being rendered when the error occurred. */
  path?: string;
}

/**
 * Ask the backend to render a specific Clay source file.
 */
export async function renderFile(path: string): Promise<RenderResult> {
  const url = PageConfig.getBaseUrl() + 'clay-preview/render';
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path })
    });
    if (!response.ok) {
      const body = (await response.json().catch(() => ({}))) as {
        error?: string;
        detail?: string;
        path?: string;
      };
      return { ok: false, error: body.error, detail: body.detail, path: body.path ?? path };
    }
    return { ok: true, path };
  } catch {
    return { ok: false, error: 'Network error', path };
  }
}

/**
 * Request a Clay process restart and return the updated status.
 */
export async function requestRestart(): Promise<ClayStatus> {
  const url = PageConfig.getBaseUrl() + 'clay-preview/api/restart';
  try {
    const response = await fetch(url, { method: 'POST' });
    if (!response.ok) {
      return { status: 'error', pids: [] };
    }
    return response.json();
  } catch {
    return { status: 'error', pids: [] };
  }
}

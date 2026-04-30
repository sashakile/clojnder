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
  error?: string;
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
      const body = await response.json().catch(() => ({}));
      return { ok: false, error: (body as { error?: string }).error };
    }
    return { ok: true };
  } catch {
    return { ok: false, error: 'Network error' };
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

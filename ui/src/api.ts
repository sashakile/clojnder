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

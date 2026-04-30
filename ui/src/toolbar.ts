import { ToolbarButton } from '@jupyterlab/apputils';

import { requestRestart } from './api';

/**
 * Create a toolbar button that restarts the Clay preview server.
 *
 * @param onRestart Optional callback invoked after a successful restart
 *                  (e.g. to refresh the preview iframe).
 */
export function createRestartButton(onRestart?: () => void): ToolbarButton {
  return new ToolbarButton({
    label: 'Restart Clay',
    onClick: async () => {
      await requestRestart();
      onRestart?.();
    },
    tooltip: 'Restart the Clay preview server'
  });
}

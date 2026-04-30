import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { ICommandPalette } from '@jupyterlab/apputils';

/**
 * Clay Preview plugin for JupyterLab.
 *
 * This is the first-slice skeleton: it proves extension registration and
 * command palette wiring. File-aware preview behavior is deferred to later slices.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'clay-jupyter-proxy:plugin',
  description: 'Clay Preview JupyterLab extension',
  autoStart: true,
  optional: [ICommandPalette],
  activate: (app: JupyterFrontEnd, palette: ICommandPalette | null) => {
    const command = 'clay-preview:open';

    app.commands.addCommand(command, {
      label: 'Clay Preview: Open',
      caption: 'Open Clay Preview panel',
      execute: () => {
        console.log('[clay-preview] Open command invoked — skeleton skeleton active');
        // Minimal visible action: log to console.
        // Full panel rendering is implemented in a later slice.
      }
    });

    if (palette) {
      palette.addItem({ command, category: 'Clay' });
    }
  }
};

export default plugin;

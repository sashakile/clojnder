import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { ICommandPalette } from '@jupyterlab/apputils';

import { registerCommands } from './commands';

/**
 * Clay Preview plugin for JupyterLab.
 *
 * Opens the proxied Clay app inside a JupyterLab main-area panel (singleton).
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'clay-jupyter-proxy:plugin',
  description: 'Clay Preview JupyterLab extension',
  autoStart: true,
  optional: [ICommandPalette],
  activate: (app: JupyterFrontEnd, palette: ICommandPalette | null) => {
    registerCommands(app, palette);
  }
};

export default plugin;

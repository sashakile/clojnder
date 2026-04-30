import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { ICommandPalette } from '@jupyterlab/apputils';
import { IEditorTracker } from '@jupyterlab/fileeditor';

import { registerCommands } from './commands';
import { FollowTracker } from './tracker';

/**
 * Clay Preview plugin for JupyterLab.
 *
 * Opens the proxied Clay app inside a JupyterLab main-area panel (singleton).
 * Optionally connects to IEditorTracker to follow the active .clj file.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'clay-jupyter-proxy:plugin',
  description: 'Clay Preview JupyterLab extension',
  autoStart: true,
  optional: [ICommandPalette, IEditorTracker],
  activate: (
    app: JupyterFrontEnd,
    palette: ICommandPalette | null,
    editorTracker: IEditorTracker | null
  ) => {
    const followTracker = new FollowTracker();
    registerCommands(app, palette, followTracker, editorTracker);
  }
};

export default plugin;

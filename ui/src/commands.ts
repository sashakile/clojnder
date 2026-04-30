import { JupyterFrontEnd } from '@jupyterlab/application';
import { ICommandPalette } from '@jupyterlab/apputils';

import { ClayPreviewWidget } from './panel';

let widget: ClayPreviewWidget | null = null;

/**
 * Register the clay-preview:open command and add it to the palette.
 *
 * The command implements a singleton: re-invoking it focuses the existing
 * panel rather than opening a second one.
 */
export function registerCommands(
  app: JupyterFrontEnd,
  palette: ICommandPalette | null
): void {
  const command = 'clay-preview:open';

  app.commands.addCommand(command, {
    label: 'Clay Preview: Open',
    caption: 'Open Clay Preview panel',
    execute: () => {
      if (!widget || widget.isDisposed) {
        widget = new ClayPreviewWidget();
      }
      if (!widget.isAttached) {
        app.shell.add(widget, 'main');
      }
      app.shell.activateById(widget.id);
    }
  });

  if (palette) {
    palette.addItem({ command, category: 'Clay' });
  }
}

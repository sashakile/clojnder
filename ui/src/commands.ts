import { JupyterFrontEnd } from '@jupyterlab/application';
import { ICommandPalette } from '@jupyterlab/apputils';
import { IEditorTracker } from '@jupyterlab/fileeditor';

import { requestRestart } from './api';
import { ClayPreviewWidget } from './panel';
import { FollowTracker } from './tracker';

let widget: ClayPreviewWidget | null = null;

/**
 * Register Clay Preview commands and add them to the palette.
 *
 * - clay-preview:open        — singleton panel (focus if already open)
 * - clay-preview:restart     — restart Clay server, then refresh panel
 * - clay-preview:toggle-follow — enable/disable follow-active-file mode
 */
export function registerCommands(
  app: JupyterFrontEnd,
  palette: ICommandPalette | null,
  followTracker: FollowTracker,
  editorTracker: IEditorTracker | null
): void {
  // ── Open ────────────────────────────────────────────────────────────────
  const openCommand = 'clay-preview:open';

  app.commands.addCommand(openCommand, {
    label: 'Clay Preview: Open',
    caption: 'Open Clay Preview panel',
    execute: () => {
      if (!widget || widget.isDisposed) {
        widget = new ClayPreviewWidget();
        _wireFollowTracker(followTracker, editorTracker);
      }
      if (!widget.isAttached) {
        app.shell.add(widget, 'main');
      }
      app.shell.activateById(widget.id);
    }
  });

  if (palette) {
    palette.addItem({ command: openCommand, category: 'Clay' });
  }

  // ── Restart ─────────────────────────────────────────────────────────────
  const restartCommand = 'clay-preview:restart';

  app.commands.addCommand(restartCommand, {
    label: 'Clay Preview: Restart',
    caption: 'Restart the Clay preview server',
    execute: async () => {
      await requestRestart();
      if (widget && !widget.isDisposed) {
        widget.refresh();
      }
    }
  });

  if (palette) {
    palette.addItem({ command: restartCommand, category: 'Clay' });
  }

  // ── Toggle follow ────────────────────────────────────────────────────────
  const followCommand = 'clay-preview:toggle-follow';

  app.commands.addCommand(followCommand, {
    label: 'Clay Preview: Toggle Follow Active File',
    caption: 'Follow the currently active .clj file in the preview',
    execute: () => {
      if (widget && !widget.isDisposed) {
        widget._toggleFollow();
      }
    }
  });

  if (palette) {
    palette.addItem({ command: followCommand, category: 'Clay' });
  }
}

/**
 * Wire the FollowTracker to the panel widget and the editor tracker.
 * Called once when the panel is first created.
 */
function _wireFollowTracker(
  followTracker: FollowTracker,
  editorTracker: IEditorTracker | null
): void {
  if (!widget || widget.isDisposed) {
    return;
  }

  // Panel toggle button → tracker
  widget.onFollowModeChange = (enabled: boolean) => {
    followTracker.setFollowMode(enabled);
  };

  // Tracker → panel label
  followTracker.onTargetChange((path) => {
    if (widget && !widget.isDisposed) {
      widget.setTargetFile(path);
      // A target change (new file focused) resets any prior error state.
      widget.clearError();
    }
  });

  // Tracker → error overlay
  followTracker.onRenderError((result) => {
    if (widget && !widget.isDisposed) {
      widget.showError(result.path ?? '', result.detail ?? result.error ?? '');
    }
  });

  // Connect to JupyterLab editor tracker if available
  if (editorTracker) {
    followTracker.activate(editorTracker);
  }

  // Auto-enable follow mode so the panel tracks the active file immediately.
  followTracker.setFollowMode(true);
}

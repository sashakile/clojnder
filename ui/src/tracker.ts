import { IEditorTracker } from '@jupyterlab/fileeditor';

import { renderFile } from './api';

/**
 * Returns true if the given file path is a Clay source file (.clj).
 */
export function isClaySourceFile(path: string): boolean {
  return path.endsWith('.clj');
}

/**
 * Manages "follow mode" — re-renders the Clay preview whenever the user
 * switches to a supported editor file.
 *
 * Call `activate()` once with an IEditorTracker, then toggle follow mode
 * on/off at will. Dispose of the tracker to release the signal connection.
 */
export class FollowTracker {
  private _followMode = false;
  private _currentFile: string | null = null;
  private _onTargetChange: ((path: string | null) => void) | null = null;

  /** True when follow mode is active. */
  get followMode(): boolean {
    return this._followMode;
  }

  /** The file currently targeted for preview, or null. */
  get currentFile(): string | null {
    return this._currentFile;
  }

  /**
   * Register a callback invoked whenever the targeted file changes.
   * Called with the new path, or null when there is no supported file focused.
   */
  onTargetChange(cb: (path: string | null) => void): void {
    this._onTargetChange = cb;
  }

  /**
   * Connect to the JupyterLab editor tracker.
   * Should be called once after construction.
   */
  activate(editorTracker: IEditorTracker): void {
    editorTracker.currentChanged.connect((_tracker, widget) => {
      if (!this._followMode) {
        return;
      }
      const path = widget?.context?.path ?? null;
      if (path !== null && !isClaySourceFile(path)) {
        // Unsupported file — do not retarget
        return;
      }
      this._updateTarget(path);
    });
  }

  /** Enable or disable follow mode. */
  setFollowMode(enabled: boolean): void {
    this._followMode = enabled;
  }

  private _updateTarget(path: string | null): void {
    this._currentFile = path;
    this._onTargetChange?.(path);
    if (path !== null) {
      void renderFile(path);
    }
  }
}

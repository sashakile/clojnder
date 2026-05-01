import { IEditorTracker } from '@jupyterlab/fileeditor';
import { IDocumentWidget } from '@jupyterlab/docregistry';

import { RenderResult, renderFile } from './api';

/**
 * Returns true if the given file path is a Clay source file (.clj).
 */
export function isClaySourceFile(path: string): boolean {
  return path.endsWith('.clj');
}

/**
 * Returns a debounced version of `fn` that waits `ms` milliseconds after the
 * last call before invoking `fn`. Exposed for unit testing.
 */
export function debounce<T extends unknown[]>(
  fn: (...args: T) => void,
  ms: number
): (...args: T) => void {
  let timer: ReturnType<typeof setTimeout> | null = null;
  return (...args: T): void => {
    if (timer !== null) {
      clearTimeout(timer);
    }
    timer = setTimeout(() => {
      timer = null;
      fn(...args);
    }, ms);
  };
}

/** Minimal shape of a JupyterLab document widget needed by FollowTracker. */
interface IWatchableWidget {
  context: {
    path: string;
    saveState: {
      connect(
        handler: (sender: unknown, state: string) => void,
        thisArg?: unknown
      ): boolean;
      disconnect(
        handler: (sender: unknown, state: string) => void,
        thisArg?: unknown
      ): boolean;
    };
  };
}

/**
 * Manages "follow mode" — re-renders the Clay preview whenever the user
 * switches to a supported editor file, and automatically re-renders when
 * the targeted file is saved (debounced).
 *
 * Call `activate()` once with an IEditorTracker, then toggle follow mode
 * on/off at will. Dispose of the tracker to release the signal connections.
 */
export class FollowTracker {
  private _followMode = false;
  private _currentFile: string | null = null;
  private _currentWidget: IWatchableWidget | null = null;
  private _onTargetChange: ((path: string | null) => void) | null = null;
  private _onRenderError: ((result: RenderResult) => void) | null = null;
  private readonly _debouncedRender: (path: string) => void;
  private _editorTracker: IEditorTracker | null = null;

  constructor(debounceMs = 500) {
    this._debouncedRender = debounce((path: string) => {
      void this._render(path);
    }, debounceMs);
  }

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
   * Register a callback invoked whenever a render attempt fails.
   * The full RenderResult (with error/detail/path fields) is passed.
   */
  onRenderError(cb: (result: RenderResult) => void): void {
    this._onRenderError = cb;
  }

  /**
   * Connect to the JupyterLab editor tracker.
   * Should be called once after construction.
   */
  activate(editorTracker: IEditorTracker): void {
    this._editorTracker = editorTracker;
    console.log('[ClayTracker] activated');
    editorTracker.currentChanged.connect((_tracker, widget) => {
      const path = widget?.context?.path ?? null;
      console.log(`[ClayTracker] editor switched to: ${path ?? '(none)'}, followMode=${this._followMode}`);
      if (!this._followMode) {
        return;
      }
      if (path !== null && !isClaySourceFile(path)) {
        // Unsupported file — do not retarget
        console.log(`[ClayTracker] ignoring non-.clj file: ${path}`);
        return;
      }
      this._connectSaveWatcher(widget as IWatchableWidget | null);
      this._updateTarget(path);
    });
  }

  /** Enable or disable follow mode. */
  setFollowMode(enabled: boolean): void {
    this._followMode = enabled;
    console.log(`[ClayTracker] follow mode ${enabled ? 'enabled' : 'disabled'}`);
    if (enabled && this._editorTracker !== null) {
      // Immediately pick up the current widget so the user doesn't have to
      // switch editors after toggling follow mode on.
      const widget = this._editorTracker.currentWidget as IDocumentWidget | null;
      const path = widget?.context?.path ?? null;
      console.log(`[ClayTracker] setFollowMode: current widget path=${path ?? '(none)'}`);
      if (path !== null && isClaySourceFile(path)) {
        this._connectSaveWatcher(widget as unknown as IWatchableWidget);
        this._updateTarget(path);
      }
    }
  }

  /**
   * Swap the save-event watcher to a new document widget.
   * Disconnects from the previous widget (if any) and connects to the new one.
   */
  private _connectSaveWatcher(widget: IWatchableWidget | null): void {
    if (this._currentWidget !== null) {
      console.log(`[ClayTracker] disconnecting save watcher from: ${this._currentWidget.context.path}`);
      this._currentWidget.context.saveState.disconnect(
        this._onFileSaved,
        this
      );
    }
    this._currentWidget = widget;
    if (widget !== null) {
      console.log(`[ClayTracker] connecting save watcher to: ${widget.context.path}`);
      widget.context.saveState.connect(this._onFileSaved, this);
    } else {
      console.log('[ClayTracker] no widget to connect save watcher to');
    }
  }

  /**
   * Invoked by the Lumino signal when the targeted file is saved or reverted.
   * Triggers a debounced rerender of the Clay preview.
   */
  private _onFileSaved(_sender: unknown, state: string): void {
    console.log(`[ClayTracker] saveState=${state}, followMode=${this._followMode}, currentFile=${this._currentFile ?? '(none)'}`);
    if (state !== 'completed') {
      return;
    }
    if (!this._followMode || this._currentFile === null) {
      return;
    }
    this._debouncedRender(this._currentFile);
  }

  private _updateTarget(path: string | null): void {
    console.log(`[ClayTracker] target updated: ${path ?? '(none)'}`);
    this._currentFile = path;
    this._onTargetChange?.(path);
    if (path !== null) {
      void this._render(path);
    }
  }

  /**
   * Render the given path and propagate failures to the onRenderError callback.
   */
  private async _render(path: string): Promise<void> {
    console.log(`[ClayTracker] rendering: ${path}`);
    const result = await renderFile(path);
    if (result.ok) {
      console.log(`[ClayTracker] render succeeded: ${path}`);
    } else {
      console.warn(`[ClayTracker] render failed: ${path}`, result);
      if (this._onRenderError !== null) {
        this._onRenderError(result);
      }
    }
  }
}

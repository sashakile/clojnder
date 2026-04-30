import { IEditorTracker } from '@jupyterlab/fileeditor';

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
    fileChanged: {
      connect(
        handler: (sender: unknown, args: unknown) => void,
        thisArg?: unknown
      ): boolean;
      disconnect(
        handler: (sender: unknown, args: unknown) => void,
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
    editorTracker.currentChanged.connect((_tracker, widget) => {
      if (!this._followMode) {
        return;
      }
      const path = widget?.context?.path ?? null;
      if (path !== null && !isClaySourceFile(path)) {
        // Unsupported file — do not retarget
        return;
      }
      this._connectSaveWatcher(widget as IWatchableWidget | null);
      this._updateTarget(path);
    });
  }

  /** Enable or disable follow mode. */
  setFollowMode(enabled: boolean): void {
    this._followMode = enabled;
  }

  /**
   * Swap the save-event watcher to a new document widget.
   * Disconnects from the previous widget (if any) and connects to the new one.
   */
  private _connectSaveWatcher(widget: IWatchableWidget | null): void {
    if (this._currentWidget !== null) {
      this._currentWidget.context.fileChanged.disconnect(
        this._onFileSaved,
        this
      );
    }
    this._currentWidget = widget;
    if (widget !== null) {
      widget.context.fileChanged.connect(this._onFileSaved, this);
    }
  }

  /**
   * Invoked by the Lumino signal when the targeted file is saved or reverted.
   * Triggers a debounced rerender of the Clay preview.
   */
  private _onFileSaved(): void {
    if (!this._followMode || this._currentFile === null) {
      return;
    }
    this._debouncedRender(this._currentFile);
  }

  private _updateTarget(path: string | null): void {
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
    const result = await renderFile(path);
    if (!result.ok && this._onRenderError !== null) {
      this._onRenderError(result);
    }
  }
}

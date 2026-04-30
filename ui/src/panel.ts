import { IFrame, MainAreaWidget, ToolbarButton } from '@jupyterlab/apputils';
import { Widget } from '@lumino/widgets';
import { PageConfig } from '@jupyterlab/coreutils';

import { createRestartButton } from './toolbar';

/**
 * Clay Preview widget — embeds the proxied Clay app in the main area.
 *
 * The Clay server-proxy route is at <base-url>clay/ and is started
 * by start-clay.sh when the container launches.
 */
export class ClayPreviewWidget extends MainAreaWidget<IFrame> {
  private readonly _clayUrl: string;
  private _followMode = false;
  private readonly _followButton: ToolbarButton;
  private readonly _fileLabel: Widget;
  private readonly _errorOverlay: HTMLElement;

  constructor() {
    const iframe = new IFrame({
      sandbox: ['allow-same-origin', 'allow-scripts', 'allow-forms']
    });
    super({ content: iframe });

    this.title.label = 'Clay Preview';
    this.title.closable = true;

    this.toolbar.addItem(
      'refresh',
      new ToolbarButton({
        label: 'Refresh',
        onClick: () => this.refresh(),
        tooltip: 'Refresh Clay Preview'
      })
    );

    this.toolbar.addItem('restart', createRestartButton(() => this.refresh()));

    this._followButton = new ToolbarButton({
      label: 'Follow: off',
      onClick: () => this._toggleFollow(),
      tooltip: 'Toggle follow-active-file mode'
    });
    this.toolbar.addItem('follow', this._followButton);

    // Plain widget used as a read-only label showing the targeted file.
    this._fileLabel = new Widget();
    this._fileLabel.node.title = 'Currently targeted Clay file';
    this._fileLabel.node.style.cssText =
      'display:flex;align-items:center;padding:0 6px;font-size:var(--jp-ui-font-size1);opacity:0.7;';
    this._fileLabel.node.textContent = '—';
    this.toolbar.addItem('file', this._fileLabel);

    this._clayUrl = PageConfig.getBaseUrl() + 'clay/';

    // Error overlay — sits on top of the iframe, hidden by default.
    this._errorOverlay = document.createElement('div');
    this._errorOverlay.style.cssText = [
      'display:none',
      'position:absolute',
      'inset:0',
      'z-index:100',
      'background:var(--jp-layout-color1,#fff)',
      'color:var(--jp-ui-font-color1,#111)',
      'padding:16px',
      'overflow:auto',
      'font-family:var(--jp-code-font-family,monospace)',
      'font-size:var(--jp-code-font-size,13px)',
      'white-space:pre-wrap',
      'word-break:break-all'
    ].join(';');
    // Append after super() so `this.node` is ready.
    this.node.style.position = 'relative';
    this.node.appendChild(this._errorOverlay);

    this._load();
  }

  /** True when follow-active-file mode is on. */
  get followMode(): boolean {
    return this._followMode;
  }

  /** Update the toolbar to show which file is currently targeted. */
  setTargetFile(path: string | null): void {
    this._fileLabel.node.textContent = path ?? '—';
    this._fileLabel.node.title = path
      ? `Targeted: ${path}`
      : 'Currently targeted Clay file';
  }

  /**
   * Show an error overlay with the failed file path and detail message.
   * The iframe remains loaded underneath so the user can dismiss or retry.
   */
  showError(path: string, detail: string): void {
    const header = path ? `Render failed: ${path}\n\n` : 'Render failed\n\n';
    this._errorOverlay.textContent = header + (detail || '(no detail available)');
    this._errorOverlay.style.display = 'block';
  }

  /** Hide the error overlay (e.g. after a successful re-render or explicit retry). */
  clearError(): void {
    this._errorOverlay.style.display = 'none';
    this._errorOverlay.textContent = '';
  }

  /** Callback invoked when follow mode is toggled by the toolbar button. */
  onFollowModeChange: ((enabled: boolean) => void) | null = null;

  _toggleFollow(): void {
    this._followMode = !this._followMode;
    // Update the button label directly via its DOM node.
    const span = this._followButton.node.querySelector('span');
    if (span) {
      span.textContent = `Follow: ${this._followMode ? 'on' : 'off'}`;
    }
    this.onFollowModeChange?.(this._followMode);
  }

  private _load(): void {
    this.content.url = this._clayUrl;
  }

  refresh(): void {
    this.clearError();
    // Blank then restore forces an iframe reload even when URL is unchanged.
    this.content.url = '';
    this.content.url = this._clayUrl;
  }
}

import { IFrame, MainAreaWidget, ToolbarButton } from '@jupyterlab/apputils';
import { PageConfig } from '@jupyterlab/coreutils';

/**
 * Clay Preview widget — embeds the proxied Clay app in the main area.
 *
 * The Clay server-proxy route is at <base-url>clay/ and is started
 * by start-clay.sh when the container launches.
 */
export class ClayPreviewWidget extends MainAreaWidget<IFrame> {
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

    this._clayUrl = PageConfig.getBaseUrl() + 'clay/';
    this._load();
  }

  private readonly _clayUrl: string;

  private _load(): void {
    this.content.url = this._clayUrl;
  }

  refresh(): void {
    // Blank then restore forces an iframe reload even when URL is unchanged.
    this.content.url = '';
    this.content.url = this._clayUrl;
  }
}

import {Service} from './service'

export class Vc {
    refreshInterval = 10000
    autoRefresh = false
    timeout: any
    service: Service

    constructor() {
        this.service = new Service();
        this.refreshAndSetTimeout();
    }

    create(raw: any) {
        this.service.create(raw, this.draw.bind(this));
    }

    clearTimeout() {
        window.clearTimeout(this.timeout);
    }

    setTimeout() {
        this.timeout = window.setTimeout(
            this.refreshAndSetTimeout.bind(this),
            this.refreshInterval
        );
    }

    refreshAndSetTimeout() {
        this.refresh();
        if (this.autoRefresh) {
            this.setTimeout();
        }
    }

    setAutoRefresh(value: boolean) {
        this.autoRefresh = value;
        if (this.autoRefresh) {
            this.setTimeout();
        } else {
            this.clearTimeout();
        }
    }

    refresh() {
        this.service.refresh(this.draw.bind(this));
    }

    draw(requests: any) {
        (document.querySelector('generation-requests') as any)
            .update(requests);
    }
}

(global as any).vc = new Vc();

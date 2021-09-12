function Vc() {
    this.service = new Service(this);
    this.refreshAndSetTimeout();
}
Object.assign(Vc.prototype, {
    refreshInterval: 10000,
    autoRefresh: false,
    timeout: null,
    create(raw) {
        this.service.create(raw, this.draw.bind(this));
    },
    clearTimeout() {
        window.clearTimeout(this.timeout);
    },
    setTimeout() {
        this.timeout = window.setTimeout(
            this.refreshAndSetTimeout.bind(this),
            this.refreshInterval
        );
    },
    refreshAndSetTimeout() {
        this.refresh();
        if (this.autoRefresh) {
            this.setTimeout();
        }
    },
    setAutoRefresh(value) {
        this.autoRefresh = value;
        if (this.autoRefresh) {
            this.setTimeout();
        } else {
            this.clearTimeout();
        }
    },
    refresh() {
        this.service.refresh(this.draw.bind(this));
    },
    draw(requests) {
        document
            .querySelector('generation-requests')
            .update(requests);
    },
});
document.addEventListener('DOMContentLoaded', () => {
    window.vc = new Vc();
});

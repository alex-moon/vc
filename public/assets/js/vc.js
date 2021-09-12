function Vc() {
    this.service = new Service(this);
    this.refresh();

    // poll every ten seconds
    window.setTimeout(this.refresh.bind(this), 10000);
}
Object.assign(Vc.prototype, {
    create(raw) {
        this.service.create(raw, this.draw.bind(this));
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

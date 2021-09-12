function Vc() {
    this.manager = new Manager(this);
    this.manager.index();

    // poll every ten seconds
    window.setTimeout(
        this.manager.fetch.bind(this.manager),
        10000
    );
}
Object.assign(Vc.prototype, {
    create(e) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form)
        const request = new GenerationRequest()
        request.marshall(formData);
        this.manager.create(request);
        return false;
    },
    draw(requests) {
        document
            .querySelector('generation-requests')
            .update(requests);
    }
});
document.addEventListener('DOMContentLoaded', () => {
    window.vc = new Vc();
});

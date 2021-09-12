function Vc(window) {
    this.window = window;
    this.manager = new Manager();
    this.manager.index();
    // poll every ten seconds
    this.window.setTimeout(this.manager.fetch.bind(this.manager), 10000);
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
    marshall(formData) {

    }
});
(function(window) {
    window.vc = new Vc(window);
})(window);

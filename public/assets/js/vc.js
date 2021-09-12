function Vc(document) {
    this.document = document;
    this.manager = new Manager();
    this.manager.index();
    // poll every ten seconds
    this.document.setTimeout(this.manager.fetch.bind(this.manager), 10000);
}
Object.assign(Vc.prototype, {
    create(form) {
        console.log(form);
    }
});
(function(window, document) {
    window.vc = new Vc(document);
})(window, document);

function Service(vc) {
    this.manager = new Manager(this);
}
Object.assign(Service.prototype, {
    refresh(callback) {
        this.manager.index(callback);
    },
    create(data, callback) {
        const request = new GenerationRequest({
            spec: {
                videos: [
                    {
                        texts: [data.prompt]
                    }
                ],
            },
        });
        this.manager.create(request, callback);
    },
});

function Manager() {
    this.requests = [];
}
Object.assign(Manager.prototype, {
    base_url: 'https://vc.ajmoon.uk/generation-request',
    async fetch (url = '') {
        const response = await fetch(this.base_url + url);
        return response.json();
    },
    async post (data, url = '') {
        const response = await fetch(this.base_url + url, {
            method: 'POST',
            mode: 'no-cors',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        return response.json();
    },
    index() {
        this.fetch().then(this.handleResponse.bind(this));
    },
    create(data) {
        console.log('got data', data);
        this.post(data);
        this.index();
    },
    handleResponse(response) {
        this.load(response.data);
    },
    load(data) {
        this.requests = [];
        for (const raw of data) {
            request = new GenerationRequest(raw);
            this.requests.push(request);
        }
    },
    all() {
        return this.requests;
    }
});

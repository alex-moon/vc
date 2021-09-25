import {GenerationRequest} from "./models/generation-request";

export class Manager {
    requests: GenerationRequest[]
    isLocal: boolean
    base_url = '/api/generation-request/'

    constructor() {
        this.requests = [];

        const useDummyData = false;
        this.isLocal = useDummyData && [
            'vc.local',
            'localhost',
            '127.0.0.1',
        ].includes(window.location.hostname);
    }

    async fetch(url = '') {
        url = this.base_url + url;
        if (this.isLocal) {
            url = '/assets/latest.json';
        }
        const response = await fetch(url);
        return response.json();
    }

    async post(data: any, url = '') {
        if (this.isLocal) {
            return data;
        }
        const response = await fetch(this.base_url + url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        return response.json();
    }

    index(callback: CallableFunction) {
        this.fetch().then((response) => {
            this.load(response);
            callback(this.requests);
        });
    }

    create(request: GenerationRequest, callback: CallableFunction) {
        this.post(request).then(() => {
            this.index(callback);
        });
    }

    load(data: GenerationRequest[]) {
        this.requests = data;
    }
}

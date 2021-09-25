import {GenerationRequest} from "./models/generation-request";
import {AuthHelper} from "./helpers/auth";

export class Manager {
    requests: GenerationRequest[]
    isLocal = (window as any).env.useLocal
    host = (window as any).env.host
    base_url = '/api/generation-request/'

    constructor() {
        this.requests = [];
    }

    async fetch(url = '') {
        url = this.host + this.base_url + url;
        if (this.isLocal) {
            url = '/assets/latest.json';
        }
        const response = await fetch(url, {
            headers: {
                'Authorization': 'Bearer ' + AuthHelper.token,
                'Content-Type': 'application/json',
            },
        });
        return response.json();
    }

    async post(data: any, url = '') {
        if (this.isLocal) {
            return data;
        }
        url = this.host + this.base_url + url;
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': 'Bearer ' + AuthHelper.token,
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

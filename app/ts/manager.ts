import {GenerationRequest} from "./models/generation-request";
import {AuthHelper} from "./helpers/auth";
import {EnvHelper} from "./helpers/env";

export class Manager {
    requests: GenerationRequest[]
    isLocal = EnvHelper.useLocal
    host = EnvHelper.host
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

    async put(id: number, action: string) {
        if (this.isLocal) {
            return;
        }
        const url =  this.host + this.base_url + id + '/' + action;
        const response = await fetch(url, {
            method: 'PUT',
            headers: {
                'Authorization': 'Bearer ' + AuthHelper.token,
                'Content-Type': 'application/json',
            },
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

    cancel(id: number, callback: CallableFunction) {
        this.put(id, 'cancel').then((request: GenerationRequest) => {
            callback(request);
        });
    }

    retry(id: number, callback: CallableFunction) {
        this.put(id, 'retry').then((request: GenerationRequest) => {
            callback(request);
        });
    }

    delete(id: number, callback: CallableFunction) {
        this.put(id, 'delete').then((request: GenerationRequest) => {
            callback(request);
        });
    }

    load(data: GenerationRequest[]) {
        this.requests = data;
    }
}

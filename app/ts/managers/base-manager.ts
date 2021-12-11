import {AuthHelper} from "../helpers/auth";
import {EnvHelper} from "../helpers/env";
import {BaseModel} from "../models/base-model";

export abstract class BaseManager<M extends BaseModel> {
    protected isLocal = EnvHelper.useLocal;
    protected host = EnvHelper.host;
    protected base_url: string;

    protected async fetch(url = ''): Promise<M | M[]> {
        url = this.host + this.base_url + url;
        return new Promise((resolve, reject) => {
            fetch(url, {
                headers: {
                    'Authorization': 'Bearer ' + AuthHelper.getToken(),
                    'Content-Type': 'application/json',
                },
            }).then((response) => {
                resolve(response.json());
            })
        });
    }

    protected async post(data: M, url = ''): Promise<M> {
        url = this.host + this.base_url + url;
        return new Promise((resolve, reject) => {
            fetch(url, {
                method: 'POST',
                headers: {
                    'Authorization': 'Bearer ' + AuthHelper.getToken(),
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            }).then((response) => {
                resolve(response.json());
            });
        })
    }

    protected async put(url: string, data ?: M): Promise<M> {
        url =  this.host + this.base_url + url;
        return new Promise((resolve, reject) => {
            fetch(url, {
                method: 'PUT',
                headers: {
                    'Authorization': 'Bearer ' + AuthHelper.getToken(),
                    'Content-Type': 'application/json',
                },
            }).then((response) => {
                resolve(response.json());
            });
        });
    }
}

import {GenerationRequest} from "../models/generation-request";
import {BaseManager} from "./base-manager";

export class GenerationRequestManager extends BaseManager<GenerationRequest> {
    protected base_url = '/api/generation-request/'

    public index(): Promise<GenerationRequest[]> {
        let url = '';
        if (this.isLocal) {
            url = '/assets/latest.json';
        }
        return this.fetch(url) as Promise<GenerationRequest[]>;
    }

    public create(request: GenerationRequest) {
        return new Promise((resolve, reject) => {
            this.post(request)
                .then(this.index.bind(this))
                .then((result) => {
                    resolve(result);
                });
        });
    }

    public cancel(id: number) {
        return this.put(id +  '/cancel');
    }

    public retry(id: number) {
        return this.put(id +  '/retry');
    }

    public delete(id: number) {
        return this.put(id +  '/delete');
    }

    public publish(id: number) {
        return this.put(id +  '/publish');
    }

    public unpublish(id: number) {
        return this.put(id +  '/unpublish');
    }
}

import {GenerationRequest} from "./models/generation-request";
import {Manager} from "./manager";
import {ImageSpec} from "./models/image-spec";

export class Service {
    manager: Manager

    constructor() {
        this.manager = new Manager();
    }

    refresh(callback: CallableFunction) {
        this.manager.index((requests: GenerationRequest[]) => {
            callback(requests);
        });
    }

    create(spec: ImageSpec, callback: CallableFunction) {
        const request = {
            spec: {
                videos: [
                    {
                        steps: [spec],
                    },
                ],
            },
        } as GenerationRequest;
        this.manager.create(request, callback);
    }

    cancel(request: GenerationRequest, callback: CallableFunction) {
        this.manager.cancel(request.id, callback)
    }

    retry(request: GenerationRequest, callback: CallableFunction) {
        this.manager.retry(request.id, callback)
    }

    delete(request: GenerationRequest, callback: CallableFunction) {
        this.manager.delete(request.id, callback)
    }

    publish(request: GenerationRequest, callback: CallableFunction) {
        this.manager.publish(request.id, callback)
    }

    unpublish(request: GenerationRequest, callback: CallableFunction) {
        this.manager.unpublish(request.id, callback)
    }
}

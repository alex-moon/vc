import {GenerationRequest} from "./models/generation-request";
import {Manager} from "./manager";
import {ImageSpec} from "./models/image-spec";

export class Service {
    manager: Manager

    constructor() {
        this.manager = new Manager();
    }

    refresh(callback: CallableFunction) {
        this.manager.index(callback);
    }

    create(spec: ImageSpec, callback: CallableFunction) {
        const request = {
            spec: {
                videos: [
                    {
                        steps: [
                            {
                                spec
                            },
                        ],
                    },
                ],
            },
        } as GenerationRequest;
        console.log('creating', request);
        this.manager.create(request, callback);
    }
}

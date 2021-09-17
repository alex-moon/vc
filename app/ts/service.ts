import {GenerationRequest} from "./models/generation-request";
import {Manager} from "./manager";

export class Service {
    manager: Manager

    constructor() {
        this.manager = new Manager();
    }

    refresh(callback: CallableFunction) {
        this.manager.index(callback);
    }

    create(data: any, callback: CallableFunction) {
        const request = new GenerationRequest({
            spec: {
                videos: [
                    {
                        steps: [
                            {
                                data
                            },
                        ],
                    },
                ],
            },
        });
        console.log('creating', request);
        this.manager.create(request, callback);
    }
}

import {GenerationRequest} from "./generation-request";
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
                        texts: [data.prompt]
                    }
                ],
            },
        });
        this.manager.create(request, callback);
    }
}

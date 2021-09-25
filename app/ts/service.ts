import {GenerationRequest} from "./models/generation-request";
import {Manager} from "./manager";
import {ImageSpec} from "./models/image-spec";
import {DetailsHelper} from "./helpers/details";

export class Service {
    manager: Manager

    constructor() {
        this.manager = new Manager();
    }

    refresh(callback: CallableFunction) {
        this.manager.index((requests: GenerationRequest[]) => {
            callback(requests.filter((request) => {
                return DetailsHelper.hasDetails(request);
            }))
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
}

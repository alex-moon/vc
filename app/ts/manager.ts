import {GenerationRequest} from "./models/generation-request";

export class Manager {
    requests: GenerationRequest[]
    isLocal: boolean
    base_url = '/api/generation-request/'

    constructor() {
        this.requests = [];

        const useDummyData = true;
        this.isLocal = useDummyData && [
            'vc.local',
            'localhost',
            '127.0.0.1',
        ].includes(window.location.hostname);
    }
    async fetch (url = '') {
        if (this.isLocal) {
            return this.dummy_data;
        }
        const response = await fetch(this.base_url + url);
        return response.json();
    }
    async post (data: any, url = '') {
        if (this.isLocal) {
            this.dummy_data.push(data);
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

    dummy_data = [
        {
            "id": 1,
            "spec": {
                "images": null,
                "videos": [
                    {
                        "steps": [
                            {
                                "texts": [
                                    "A stunning professional photograph of a vast meadow of wildflowers and alpine grass with mountains in the distance",
                                ],
                                "styles": null,
                                "iterations": 75,
                                "init_iterations": 200,
                                "epochs": 250,
                                "x_velocity": 0.0,
                                "y_velocity": 0.0,
                                "z_velocity": 1.0,
                                "upscale": false,
                            },
                            {
                                "texts": [
                                    "A stunning professional photograph of the open ocean from above",
                                ],
                                "styles": null,
                                "iterations": 75,
                                "init_iterations": null,
                                "epochs": 250,
                                "x_velocity": 0.0,
                                "y_velocity": 1.0,
                                "z_velocity": 0.0,
                                "upscale": false,
                            },
                            {
                                "texts": [
                                    "A stunning professional photograph of an enormous rocky canyon from above",
                                ],
                                "styles": null,
                                "iterations": 75,
                                "init_iterations": null,
                                "epochs": 250,
                                "x_velocity": 1.0,
                                "y_velocity": 0.0,
                                "z_velocity": 0.0,
                                "upscale": false,
                            },
                        ],
                    },
                ],
            },
            "created": "2021-09-12T22:31:59.955942",
            "updated": "2021-09-13T20:53:27.756953",
            "started": "2021-09-12T22:32:03.858918",
            "completed": null,
            "failed": "2021-09-13T20:53:27.752803",
            "steps_completed": 590,
            "steps_total": 752,
            "name": "vegetable",
            "preview": "https://vc-ajmoon-uk.s3.eu-west-1.amazonaws.com/2021-09-12-22-32-03-vegetable-preview.png",
            "interim": "https://vc-ajmoon-uk.s3.eu-west-1.amazonaws.com/2021-09-13-20-31-04-output-vegetable-interim.mp4",
            "results": [],
        } as any,
    ]
}

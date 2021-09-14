function Manager() {
    this.requests = [];

    const useDummyData = true;
    this.isLocal = useDummyData && [
        'vc.local',
        'localhost',
        '127.0.0.1',
    ].includes(window.location.hostname);
}
Object.assign(Manager.prototype, {
    base_url: '/api/generation-request/',
    async fetch (url = '') {
        if (this.isLocal) {
            return window.dummy_data;
        }
        const response = await fetch(this.base_url + url);
        return response.json();
    },
    async post (data, url = '') {
        if (this.isLocal) {
            window.dummy_data.push(data);
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
    },
    index(callback) {
        this.fetch().then((response) => {
            this.load(response);
            callback(this.requests);
        });
    },
    create(request, callback) {
        this.post(request);
        this.index(callback);
    },
    load(data) {
        this.requests = [];
        for (const raw of data) {
            request = new GenerationRequest(raw);
            this.requests.push(request);
        }
    },
});

window.dummy_data = [
    {
        "id": 1,
        "spec": {
            "images": null,
            "videos": [
                {
                    "steps": [
                        {
                            "texts": [
                                "A stunning professional photograph of a vast meadow of wildflowers and alpine grass with mountains in the distance"
                            ],
                            "styles": null,
                            "iterations": 75,
                            "init_iterations": 200,
                            "epochs": 250,
                            "x_velocity": 0.0,
                            "y_velocity": 0.0,
                            "z_velocity": 1.0,
                            "upscale": false
                        },
                        {
                            "texts": [
                                "A stunning professional photograph of the open ocean from above"
                            ],
                            "styles": null,
                            "iterations": 75,
                            "init_iterations": null,
                            "epochs": 250,
                            "x_velocity": 0.0,
                            "y_velocity": 1.0,
                            "z_velocity": 0.0,
                            "upscale": false
                        },
                        {
                            "texts": [
                                "A stunning professional photograph of an enormous rocky canyon from above"
                            ],
                            "styles": null,
                            "iterations": 75,
                            "init_iterations": null,
                            "epochs": 250,
                            "x_velocity": 1.0,
                            "y_velocity": 0.0,
                            "z_velocity": 0.0,
                            "upscale": false
                        }
                    ]
                }
            ]
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
        "results": []
    }
];

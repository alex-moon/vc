function Manager() {
    this.requests = [];
}
Object.assign(Manager.prototype, {
    base_url: '/api/generation-request',
    async fetch (url = '') {
        if (window.env === 'local') {
            return {data: window.dummy_data};
        }
        const response = await fetch(this.base_url + url, {
            mode: 'no-cors',
        });
        return response.json();
    },
    async post (data, url = '') {
        if (window.env === 'local') {
            console.log('POST', data);
            return {};
        }
        const response = await fetch(this.base_url + url, {
            method: 'POST',
            mode: 'no-cors',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        return response.json();
    },
    index(callback) {
        this.fetch().then((response) => {
            this.handleResponse(response);
            callback(this.requests);
        });
    },
    create(data, callback) {
        this.post(data);
        this.index(callback);
    },
    handleResponse(response) {
        this.load(response.data);
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
        "id": 2,
        "spec": {
            "images": null,
            "videos": [
                {
                    "steps": [
                        {
                            "texts": [
                                "I walk a long a very straight inner city street at night, lit by the colours of buildings"
                            ],
                            "iterations": 75,
                            "init_iterations": 200,
                            "epochs": 10,
                            "x_velocity": 0.0,
                            "y_velocity": 0.0,
                            "z_velocity": 0.0,
                            "upscale": false
                        }
                    ]
                }
            ]
        },
        "created": "2021-09-12T18:03:45.131823",
        "updated": "2021-09-12T18:03:45.131823",
        "started": null,
        "completed": null,
        "failed": null,
        "steps_completed": null,
        "steps_total": null,
        "name": null,
        "preview": null,
        "results": []
    },
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
                            "styles": [
                                "reuters",
                                "ansel adams",
                                "national geographic"
                            ],
                            "iterations": 75,
                            "init_iterations": 200,
                            "epochs": 10,
                            "x_velocity": 0.0,
                            "y_velocity": 0.0,
                            "z_velocity": 1.0,
                            "upscale": false
                        },
                        {
                            "texts": [
                                "A stunning professional photograph of the sky at high noon"
                            ],
                            "styles": [
                                "reuters",
                                "ansel adams",
                                "national geographic"
                            ],
                            "iterations": 75,
                            "init_iterations": 200,
                            "epochs": 10,
                            "x_velocity": 0.0,
                            "y_velocity": 1.0,
                            "z_velocity": 0.0,
                            "upscale": false
                        },
                        {
                            "texts": [
                                "A stunning professional photograph of a sandy beach with grass on the left and the open ocean on the right"
                            ],
                            "styles": [
                                "reuters",
                                "ansel adams",
                                "national geographic"
                            ],
                            "iterations": 75,
                            "init_iterations": 200,
                            "epochs": 10,
                            "x_velocity": 1.0,
                            "y_velocity": 0.0,
                            "z_velocity": 0.0,
                            "upscale": false
                        }
                    ]
                }
            ]
        },
        "created": "2021-09-12T16:47:49.120632",
        "updated": "2021-09-12T18:09:25.136033",
        "started": "2021-09-12T16:47:49.433647",
        "completed": null,
        "failed": null,
        "steps_completed": 37,
        "steps_total": 92,
        "name": "comparison",
        "preview": null,
        "results": []
    }
];

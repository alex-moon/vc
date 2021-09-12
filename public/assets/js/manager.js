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
        "preview": "https://vc-ajmoon-uk.s3.eu-west-1.amazonaws.com/2021-09-12-16-47-49-comparison-preview.png",
        "results": [
            {
                "id": 1,
                "url": "https://vc-ajmoon-uk.s3.eu-west-1.amazonaws.com/2021-09-12-20-14-28-comparison-output.mp4",
                "created": "2021-09-12T20:14:28.123456",
                "updated": "2021-09-12T20:14:28.123456"
            }
        ]
    }
];

/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ "./app/ts/manager.ts":
/*!***************************!*\
  !*** ./app/ts/manager.ts ***!
  \***************************/
/***/ (function(__unused_webpack_module, exports, __webpack_require__) {


var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.Manager = void 0;
const generation_request_1 = __webpack_require__(/*! ./models/generation-request */ "./app/ts/models/generation-request.ts");
class Manager {
    constructor() {
        this.base_url = '/api/generation-request/';
        this.dummy_data = [
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
            },
        ];
        this.requests = [];
        const useDummyData = true;
        this.isLocal = useDummyData && [
            'vc.local',
            'localhost',
            '127.0.0.1',
        ].includes(window.location.hostname);
    }
    fetch(url = '') {
        return __awaiter(this, void 0, void 0, function* () {
            if (this.isLocal) {
                return this.dummy_data;
            }
            const response = yield fetch(this.base_url + url);
            return response.json();
        });
    }
    post(data, url = '') {
        return __awaiter(this, void 0, void 0, function* () {
            if (this.isLocal) {
                this.dummy_data.push(data);
                return data;
            }
            const response = yield fetch(this.base_url + url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });
            return response.json();
        });
    }
    index(callback) {
        this.fetch().then((response) => {
            this.load(response);
            callback(this.requests);
        });
    }
    create(request, callback) {
        this.post(request);
        this.index(callback);
    }
    load(data) {
        this.requests = [];
        for (const raw of data) {
            const request = new generation_request_1.GenerationRequest(raw);
            this.requests.push(request);
        }
    }
}
exports.Manager = Manager;


/***/ }),

/***/ "./app/ts/models/generation-request.ts":
/*!*********************************************!*\
  !*** ./app/ts/models/generation-request.ts ***!
  \*********************************************/
/***/ ((__unused_webpack_module, exports) => {


Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.GenerationRequest = void 0;
class GenerationRequest {
    constructor(raw = null) {
        if (raw) {
            Object.assign(this, raw);
        }
    }
}
exports.GenerationRequest = GenerationRequest;


/***/ }),

/***/ "./app/ts/service.ts":
/*!***************************!*\
  !*** ./app/ts/service.ts ***!
  \***************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {


Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.Service = void 0;
const generation_request_1 = __webpack_require__(/*! ./models/generation-request */ "./app/ts/models/generation-request.ts");
const manager_1 = __webpack_require__(/*! ./manager */ "./app/ts/manager.ts");
class Service {
    constructor() {
        this.manager = new manager_1.Manager();
    }
    refresh(callback) {
        this.manager.index(callback);
    }
    create(data, callback) {
        const request = new generation_request_1.GenerationRequest({
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
exports.Service = Service;


/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/global */
/******/ 	(() => {
/******/ 		__webpack_require__.g = (function() {
/******/ 			if (typeof globalThis === 'object') return globalThis;
/******/ 			try {
/******/ 				return this || new Function('return this')();
/******/ 			} catch (e) {
/******/ 				if (typeof window === 'object') return window;
/******/ 			}
/******/ 		})();
/******/ 	})();
/******/ 	
/************************************************************************/
var __webpack_exports__ = {};
// This entry need to be wrapped in an IIFE because it need to be isolated against other modules in the chunk.
(() => {
var exports = __webpack_exports__;
/*!**********************!*\
  !*** ./app/ts/vc.ts ***!
  \**********************/

Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.Vc = void 0;
const service_1 = __webpack_require__(/*! ./service */ "./app/ts/service.ts");
class Vc {
    constructor() {
        this.refreshInterval = 10000;
        this.autoRefresh = false;
        this.service = new service_1.Service();
    }
    connect($requests) {
        this.$requests = $requests;
        this.refreshAndSetTimeout();
    }
    create(raw) {
        this.service.create(raw, this.draw.bind(this));
    }
    clearTimeout() {
        window.clearTimeout(this.timeout);
    }
    setTimeout() {
        this.timeout = window.setTimeout(this.refreshAndSetTimeout.bind(this), this.refreshInterval);
    }
    refreshAndSetTimeout() {
        this.refresh();
        if (this.autoRefresh) {
            this.setTimeout();
        }
    }
    setAutoRefresh(value) {
        this.autoRefresh = value;
        if (this.autoRefresh) {
            this.setTimeout();
        }
        else {
            this.clearTimeout();
        }
    }
    refresh() {
        this.service.refresh(this.draw.bind(this));
    }
    draw(requests) {
        this.$requests.update(requests);
    }
}
exports.Vc = Vc;
__webpack_require__.g.vc = new Vc();

})();

/******/ })()
;
//# sourceMappingURL=data:application/json;charset=utf-8;base64,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Li9hcHAvdHMvbW9kZWxzL2dlbmVyYXRpb24tcmVxdWVzdC50cyIsIndlYnBhY2s6Ly92Yy8uL2FwcC90cy9zZXJ2aWNlLnRzIiwid2VicGFjazovL3ZjL3dlYnBhY2svYm9vdHN0cmFwIiwid2VicGFjazovL3ZjL3dlYnBhY2svcnVudGltZS9nbG9iYWwiLCJ3ZWJwYWNrOi8vdmMvLi9hcHAvdHMvdmMudHMiXSwic291cmNlc0NvbnRlbnQiOlsiXCJ1c2Ugc3RyaWN0XCI7XG52YXIgX19hd2FpdGVyID0gKHRoaXMgJiYgdGhpcy5fX2F3YWl0ZXIpIHx8IGZ1bmN0aW9uICh0aGlzQXJnLCBfYXJndW1lbnRzLCBQLCBnZW5lcmF0b3IpIHtcbiAgICBmdW5jdGlvbiBhZG9wdCh2YWx1ZSkgeyByZXR1cm4gdmFsdWUgaW5zdGFuY2VvZiBQID8gdmFsdWUgOiBuZXcgUChmdW5jdGlvbiAocmVzb2x2ZSkgeyByZXNvbHZlKHZhbHVlKTsgfSk7IH1cbiAgICByZXR1cm4gbmV3IChQIHx8IChQID0gUHJvbWlzZSkpKGZ1bmN0aW9uIChyZXNvbHZlLCByZWplY3QpIHtcbiAgICAgICAgZnVuY3Rpb24gZnVsZmlsbGVkKHZhbHVlKSB7IHRyeSB7IHN0ZXAoZ2VuZXJhdG9yLm5leHQodmFsdWUpKTsgfSBjYXRjaCAoZSkgeyByZWplY3QoZSk7IH0gfVxuICAgICAgICBmdW5jdGlvbiByZWplY3RlZCh2YWx1ZSkgeyB0cnkgeyBzdGVwKGdlbmVyYXRvcltcInRocm93XCJdKHZhbHVlKSk7IH0gY2F0Y2ggKGUpIHsgcmVqZWN0KGUpOyB9IH1cbiAgICAgICAgZnVuY3Rpb24gc3RlcChyZXN1bHQpIHsgcmVzdWx0LmRvbmUgPyByZXNvbHZlKHJlc3VsdC52YWx1ZSkgOiBhZG9wdChyZXN1bHQudmFsdWUpLnRoZW4oZnVsZmlsbGVkLCByZWplY3RlZCk7IH1cbiAgICAgICAgc3RlcCgoZ2VuZXJhdG9yID0gZ2VuZXJhdG9yLmFwcGx5KHRoaXNBcmcsIF9hcmd1bWVudHMgfHwgW10pKS5uZXh0KCkpO1xuICAgIH0pO1xufTtcbk9iamVjdC5kZWZpbmVQcm9wZXJ0eShleHBvcnRzLCBcIl9fZXNNb2R1bGVcIiwgeyB2YWx1ZTogdHJ1ZSB9KTtcbmV4cG9ydHMuTWFuYWdlciA9IHZvaWQgMDtcbmNvbnN0IGdlbmVyYXRpb25fcmVxdWVzdF8xID0gcmVxdWlyZShcIi4vbW9kZWxzL2dlbmVyYXRpb24tcmVxdWVzdFwiKTtcbmNsYXNzIE1hbmFnZXIge1xuICAgIGNvbnN0cnVjdG9yKCkge1xuICAgICAgICB0aGlzLmJhc2VfdXJsID0gJy9hcGkvZ2VuZXJhdGlvbi1yZXF1ZXN0Lyc7XG4gICAgICAgIHRoaXMuZHVtbXlfZGF0YSA9IFtcbiAgICAgICAgICAgIHtcbiAgICAgICAgICAgICAgICBcImlkXCI6IDEsXG4gICAgICAgICAgICAgICAgXCJzcGVjXCI6IHtcbiAgICAgICAgICAgICAgICAgICAgXCJpbWFnZXNcIjogbnVsbCxcbiAgICAgICAgICAgICAgICAgICAgXCJ2aWRlb3NcIjogW1xuICAgICAgICAgICAgICAgICAgICAgICAge1xuICAgICAgICAgICAgICAgICAgICAgICAgICAgIFwic3RlcHNcIjogW1xuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICB7XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBcInRleHRzXCI6IFtcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBcIkEgc3R1bm5pbmcgcHJvZmVzc2lvbmFsIHBob3RvZ3JhcGggb2YgYSB2YXN0IG1lYWRvdyBvZiB3aWxkZmxvd2VycyBhbmQgYWxwaW5lIGdyYXNzIHdpdGggbW91bnRhaW5zIGluIHRoZSBkaXN0YW5jZVwiLFxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgXSxcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIFwic3R5bGVzXCI6IG51bGwsXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBcIml0ZXJhdGlvbnNcIjogNzUsXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBcImluaXRfaXRlcmF0aW9uc1wiOiAyMDAsXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBcImVwb2Noc1wiOiAyNTAsXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBcInhfdmVsb2NpdHlcIjogMC4wLFxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgXCJ5X3ZlbG9jaXR5XCI6IDAuMCxcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIFwiel92ZWxvY2l0eVwiOiAxLjAsXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBcInVwc2NhbGVcIjogZmFsc2UsXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIH0sXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIHtcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIFwidGV4dHNcIjogW1xuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIFwiQSBzdHVubmluZyBwcm9mZXNzaW9uYWwgcGhvdG9ncmFwaCBvZiB0aGUgb3BlbiBvY2VhbiBmcm9tIGFib3ZlXCIsXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBdLFxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgXCJzdHlsZXNcIjogbnVsbCxcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIFwiaXRlcmF0aW9uc1wiOiA3NSxcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIFwiaW5pdF9pdGVyYXRpb25zXCI6IG51bGwsXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBcImVwb2Noc1wiOiAyNTAsXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBcInhfdmVsb2NpdHlcIjogMC4wLFxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgXCJ5X3ZlbG9jaXR5XCI6IDEuMCxcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIFwiel92ZWxvY2l0eVwiOiAwLjAsXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBcInVwc2NhbGVcIjogZmFsc2UsXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIH0sXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIHtcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIFwidGV4dHNcIjogW1xuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIFwiQSBzdHVubmluZyBwcm9mZXNzaW9uYWwgcGhvdG9ncmFwaCBvZiBhbiBlbm9ybW91cyByb2NreSBjYW55b24gZnJvbSBhYm92ZVwiLFxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgXSxcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIFwic3R5bGVzXCI6IG51bGwsXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBcIml0ZXJhdGlvbnNcIjogNzUsXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBcImluaXRfaXRlcmF0aW9uc1wiOiBudWxsLFxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgXCJlcG9jaHNcIjogMjUwLFxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgXCJ4X3ZlbG9jaXR5XCI6IDEuMCxcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIFwieV92ZWxvY2l0eVwiOiAwLjAsXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBcInpfdmVsb2NpdHlcIjogMC4wLFxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgXCJ1cHNjYWxlXCI6IGZhbHNlLFxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICB9LFxuICAgICAgICAgICAgICAgICAgICAgICAgICAgIF0sXG4gICAgICAgICAgICAgICAgICAgICAgICB9LFxuICAgICAgICAgICAgICAgICAgICBdLFxuICAgICAgICAgICAgICAgIH0sXG4gICAgICAgICAgICAgICAgXCJjcmVhdGVkXCI6IFwiMjAyMS0wOS0xMlQyMjozMTo1OS45NTU5NDJcIixcbiAgICAgICAgICAgICAgICBcInVwZGF0ZWRcIjogXCIyMDIxLTA5LTEzVDIwOjUzOjI3Ljc1Njk1M1wiLFxuICAgICAgICAgICAgICAgIFwic3RhcnRlZFwiOiBcIjIwMjEtMDktMTJUMjI6MzI6MDMuODU4OTE4XCIsXG4gICAgICAgICAgICAgICAgXCJjb21wbGV0ZWRcIjogbnVsbCxcbiAgICAgICAgICAgICAgICBcImZhaWxlZFwiOiBcIjIwMjEtMDktMTNUMjA6NTM6MjcuNzUyODAzXCIsXG4gICAgICAgICAgICAgICAgXCJzdGVwc19jb21wbGV0ZWRcIjogNTkwLFxuICAgICAgICAgICAgICAgIFwic3RlcHNfdG90YWxcIjogNzUyLFxuICAgICAgICAgICAgICAgIFwibmFtZVwiOiBcInZlZ2V0YWJsZVwiLFxuICAgICAgICAgICAgICAgIFwicHJldmlld1wiOiBcImh0dHBzOi8vdmMtYWptb29uLXVrLnMzLmV1LXdlc3QtMS5hbWF6b25hd3MuY29tLzIwMjEtMDktMTItMjItMzItMDMtdmVnZXRhYmxlLXByZXZpZXcucG5nXCIsXG4gICAgICAgICAgICAgICAgXCJpbnRlcmltXCI6IFwiaHR0cHM6Ly92Yy1ham1vb24tdWsuczMuZXUtd2VzdC0xLmFtYXpvbmF3cy5jb20vMjAyMS0wOS0xMy0yMC0zMS0wNC1vdXRwdXQtdmVnZXRhYmxlLWludGVyaW0ubXA0XCIsXG4gICAgICAgICAgICAgICAgXCJyZXN1bHRzXCI6IFtdLFxuICAgICAgICAgICAgfSxcbiAgICAgICAgXTtcbiAgICAgICAgdGhpcy5yZXF1ZXN0cyA9IFtdO1xuICAgICAgICBjb25zdCB1c2VEdW1teURhdGEgPSB0cnVlO1xuICAgICAgICB0aGlzLmlzTG9jYWwgPSB1c2VEdW1teURhdGEgJiYgW1xuICAgICAgICAgICAgJ3ZjLmxvY2FsJyxcbiAgICAgICAgICAgICdsb2NhbGhvc3QnLFxuICAgICAgICAgICAgJzEyNy4wLjAuMScsXG4gICAgICAgIF0uaW5jbHVkZXMod2luZG93LmxvY2F0aW9uLmhvc3RuYW1lKTtcbiAgICB9XG4gICAgZmV0Y2godXJsID0gJycpIHtcbiAgICAgICAgcmV0dXJuIF9fYXdhaXRlcih0aGlzLCB2b2lkIDAsIHZvaWQgMCwgZnVuY3Rpb24qICgpIHtcbiAgICAgICAgICAgIGlmICh0aGlzLmlzTG9jYWwpIHtcbiAgICAgICAgICAgICAgICByZXR1cm4gdGhpcy5kdW1teV9kYXRhO1xuICAgICAgICAgICAgfVxuICAgICAgICAgICAgY29uc3QgcmVzcG9uc2UgPSB5aWVsZCBmZXRjaCh0aGlzLmJhc2VfdXJsICsgdXJsKTtcbiAgICAgICAgICAgIHJldHVybiByZXNwb25zZS5qc29uKCk7XG4gICAgICAgIH0pO1xuICAgIH1cbiAgICBwb3N0KGRhdGEsIHVybCA9ICcnKSB7XG4gICAgICAgIHJldHVybiBfX2F3YWl0ZXIodGhpcywgdm9pZCAwLCB2b2lkIDAsIGZ1bmN0aW9uKiAoKSB7XG4gICAgICAgICAgICBpZiAodGhpcy5pc0xvY2FsKSB7XG4gICAgICAgICAgICAgICAgdGhpcy5kdW1teV9kYXRhLnB1c2goZGF0YSk7XG4gICAgICAgICAgICAgICAgcmV0dXJuIGRhdGE7XG4gICAgICAgICAgICB9XG4gICAgICAgICAgICBjb25zdCByZXNwb25zZSA9IHlpZWxkIGZldGNoKHRoaXMuYmFzZV91cmwgKyB1cmwsIHtcbiAgICAgICAgICAgICAgICBtZXRob2Q6ICdQT1NUJyxcbiAgICAgICAgICAgICAgICBoZWFkZXJzOiB7XG4gICAgICAgICAgICAgICAgICAgICdDb250ZW50LVR5cGUnOiAnYXBwbGljYXRpb24vanNvbicsXG4gICAgICAgICAgICAgICAgfSxcbiAgICAgICAgICAgICAgICBib2R5OiBKU09OLnN0cmluZ2lmeShkYXRhKSxcbiAgICAgICAgICAgIH0pO1xuICAgICAgICAgICAgcmV0dXJuIHJlc3BvbnNlLmpzb24oKTtcbiAgICAgICAgfSk7XG4gICAgfVxuICAgIGluZGV4KGNhbGxiYWNrKSB7XG4gICAgICAgIHRoaXMuZmV0Y2goKS50aGVuKChyZXNwb25zZSkgPT4ge1xuICAgICAgICAgICAgdGhpcy5sb2FkKHJlc3BvbnNlKTtcbiAgICAgICAgICAgIGNhbGxiYWNrKHRoaXMucmVxdWVzdHMpO1xuICAgICAgICB9KTtcbiAgICB9XG4gICAgY3JlYXRlKHJlcXVlc3QsIGNhbGxiYWNrKSB7XG4gICAgICAgIHRoaXMucG9zdChyZXF1ZXN0KTtcbiAgICAgICAgdGhpcy5pbmRleChjYWxsYmFjayk7XG4gICAgfVxuICAgIGxvYWQoZGF0YSkge1xuICAgICAgICB0aGlzLnJlcXVlc3RzID0gW107XG4gICAgICAgIGZvciAoY29uc3QgcmF3IG9mIGRhdGEpIHtcbiAgICAgICAgICAgIGNvbnN0IHJlcXVlc3QgPSBuZXcgZ2VuZXJhdGlvbl9yZXF1ZXN0XzEuR2VuZXJhdGlvblJlcXVlc3QocmF3KTtcbiAgICAgICAgICAgIHRoaXMucmVxdWVzdHMucHVzaChyZXF1ZXN0KTtcbiAgICAgICAgfVxuICAgIH1cbn1cbmV4cG9ydHMuTWFuYWdlciA9IE1hbmFnZXI7XG4iLCJcInVzZSBzdHJpY3RcIjtcbk9iamVjdC5kZWZpbmVQcm9wZXJ0eShleHBvcnRzLCBcIl9fZXNNb2R1bGVcIiwgeyB2YWx1ZTogdHJ1ZSB9KTtcbmV4cG9ydHMuR2VuZXJhdGlvblJlcXVlc3QgPSB2b2lkIDA7XG5jbGFzcyBHZW5lcmF0aW9uUmVxdWVzdCB7XG4gICAgY29uc3RydWN0b3IocmF3ID0gbnVsbCkge1xuICAgICAgICBpZiAocmF3KSB7XG4gICAgICAgICAgICBPYmplY3QuYXNzaWduKHRoaXMsIHJhdyk7XG4gICAgICAgIH1cbiAgICB9XG59XG5leHBvcnRzLkdlbmVyYXRpb25SZXF1ZXN0ID0gR2VuZXJhdGlvblJlcXVlc3Q7XG4iLCJcInVzZSBzdHJpY3RcIjtcbk9iamVjdC5kZWZpbmVQcm9wZXJ0eShleHBvcnRzLCBcIl9fZXNNb2R1bGVcIiwgeyB2YWx1ZTogdHJ1ZSB9KTtcbmV4cG9ydHMuU2VydmljZSA9IHZvaWQgMDtcbmNvbnN0IGdlbmVyYXRpb25fcmVxdWVzdF8xID0gcmVxdWlyZShcIi4vbW9kZWxzL2dlbmVyYXRpb24tcmVxdWVzdFwiKTtcbmNvbnN0IG1hbmFnZXJfMSA9IHJlcXVpcmUoXCIuL21hbmFnZXJcIik7XG5jbGFzcyBTZXJ2aWNlIHtcbiAgICBjb25zdHJ1Y3RvcigpIHtcbiAgICAgICAgdGhpcy5tYW5hZ2VyID0gbmV3IG1hbmFnZXJfMS5NYW5hZ2VyKCk7XG4gICAgfVxuICAgIHJlZnJlc2goY2FsbGJhY2spIHtcbiAgICAgICAgdGhpcy5tYW5hZ2VyLmluZGV4KGNhbGxiYWNrKTtcbiAgICB9XG4gICAgY3JlYXRlKGRhdGEsIGNhbGxiYWNrKSB7XG4gICAgICAgIGNvbnN0IHJlcXVlc3QgPSBuZXcgZ2VuZXJhdGlvbl9yZXF1ZXN0XzEuR2VuZXJhdGlvblJlcXVlc3Qoe1xuICAgICAgICAgICAgc3BlYzoge1xuICAgICAgICAgICAgICAgIHZpZGVvczogW1xuICAgICAgICAgICAgICAgICAgICB7XG4gICAgICAgICAgICAgICAgICAgICAgICB0ZXh0czogW2RhdGEucHJvbXB0XVxuICAgICAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgXSxcbiAgICAgICAgICAgIH0sXG4gICAgICAgIH0pO1xuICAgICAgICB0aGlzLm1hbmFnZXIuY3JlYXRlKHJlcXVlc3QsIGNhbGxiYWNrKTtcbiAgICB9XG59XG5leHBvcnRzLlNlcnZpY2UgPSBTZXJ2aWNlO1xuIiwiLy8gVGhlIG1vZHVsZSBjYWNoZVxudmFyIF9fd2VicGFja19tb2R1bGVfY2FjaGVfXyA9IHt9O1xuXG4vLyBUaGUgcmVxdWlyZSBmdW5jdGlvblxuZnVuY3Rpb24gX193ZWJwYWNrX3JlcXVpcmVfXyhtb2R1bGVJZCkge1xuXHQvLyBDaGVjayBpZiBtb2R1bGUgaXMgaW4gY2FjaGVcblx0dmFyIGNhY2hlZE1vZHVsZSA9IF9fd2VicGFja19tb2R1bGVfY2FjaGVfX1ttb2R1bGVJZF07XG5cdGlmIChjYWNoZWRNb2R1bGUgIT09IHVuZGVmaW5lZCkge1xuXHRcdHJldHVybiBjYWNoZWRNb2R1bGUuZXhwb3J0cztcblx0fVxuXHQvLyBDcmVhdGUgYSBuZXcgbW9kdWxlIChhbmQgcHV0IGl0IGludG8gdGhlIGNhY2hlKVxuXHR2YXIgbW9kdWxlID0gX193ZWJwYWNrX21vZHVsZV9jYWNoZV9fW21vZHVsZUlkXSA9IHtcblx0XHQvLyBubyBtb2R1bGUuaWQgbmVlZGVkXG5cdFx0Ly8gbm8gbW9kdWxlLmxvYWRlZCBuZWVkZWRcblx0XHRleHBvcnRzOiB7fVxuXHR9O1xuXG5cdC8vIEV4ZWN1dGUgdGhlIG1vZHVsZSBmdW5jdGlvblxuXHRfX3dlYnBhY2tfbW9kdWxlc19fW21vZHVsZUlkXS5jYWxsKG1vZHVsZS5leHBvcnRzLCBtb2R1bGUsIG1vZHVsZS5leHBvcnRzLCBfX3dlYnBhY2tfcmVxdWlyZV9fKTtcblxuXHQvLyBSZXR1cm4gdGhlIGV4cG9ydHMgb2YgdGhlIG1vZHVsZVxuXHRyZXR1cm4gbW9kdWxlLmV4cG9ydHM7XG59XG5cbiIsIl9fd2VicGFja19yZXF1aXJlX18uZyA9IChmdW5jdGlvbigpIHtcblx0aWYgKHR5cGVvZiBnbG9iYWxUaGlzID09PSAnb2JqZWN0JykgcmV0dXJuIGdsb2JhbFRoaXM7XG5cdHRyeSB7XG5cdFx0cmV0dXJuIHRoaXMgfHwgbmV3IEZ1bmN0aW9uKCdyZXR1cm4gdGhpcycpKCk7XG5cdH0gY2F0Y2ggKGUpIHtcblx0XHRpZiAodHlwZW9mIHdpbmRvdyA9PT0gJ29iamVjdCcpIHJldHVybiB3aW5kb3c7XG5cdH1cbn0pKCk7IiwiXCJ1c2Ugc3RyaWN0XCI7XG5PYmplY3QuZGVmaW5lUHJvcGVydHkoZXhwb3J0cywgXCJfX2VzTW9kdWxlXCIsIHsgdmFsdWU6IHRydWUgfSk7XG5leHBvcnRzLlZjID0gdm9pZCAwO1xuY29uc3Qgc2VydmljZV8xID0gcmVxdWlyZShcIi4vc2VydmljZVwiKTtcbmNsYXNzIFZjIHtcbiAgICBjb25zdHJ1Y3RvcigpIHtcbiAgICAgICAgdGhpcy5yZWZyZXNoSW50ZXJ2YWwgPSAxMDAwMDtcbiAgICAgICAgdGhpcy5hdXRvUmVmcmVzaCA9IGZhbHNlO1xuICAgICAgICB0aGlzLnNlcnZpY2UgPSBuZXcgc2VydmljZV8xLlNlcnZpY2UoKTtcbiAgICB9XG4gICAgY29ubmVjdCgkcmVxdWVzdHMpIHtcbiAgICAgICAgdGhpcy4kcmVxdWVzdHMgPSAkcmVxdWVzdHM7XG4gICAgICAgIHRoaXMucmVmcmVzaEFuZFNldFRpbWVvdXQoKTtcbiAgICB9XG4gICAgY3JlYXRlKHJhdykge1xuICAgICAgICB0aGlzLnNlcnZpY2UuY3JlYXRlKHJhdywgdGhpcy5kcmF3LmJpbmQodGhpcykpO1xuICAgIH1cbiAgICBjbGVhclRpbWVvdXQoKSB7XG4gICAgICAgIHdpbmRvdy5jbGVhclRpbWVvdXQodGhpcy50aW1lb3V0KTtcbiAgICB9XG4gICAgc2V0VGltZW91dCgpIHtcbiAgICAgICAgdGhpcy50aW1lb3V0ID0gd2luZG93LnNldFRpbWVvdXQodGhpcy5yZWZyZXNoQW5kU2V0VGltZW91dC5iaW5kKHRoaXMpLCB0aGlzLnJlZnJlc2hJbnRlcnZhbCk7XG4gICAgfVxuICAgIHJlZnJlc2hBbmRTZXRUaW1lb3V0KCkge1xuICAgICAgICB0aGlzLnJlZnJlc2goKTtcbiAgICAgICAgaWYgKHRoaXMuYXV0b1JlZnJlc2gpIHtcbiAgICAgICAgICAgIHRoaXMuc2V0VGltZW91dCgpO1xuICAgICAgICB9XG4gICAgfVxuICAgIHNldEF1dG9SZWZyZXNoKHZhbHVlKSB7XG4gICAgICAgIHRoaXMuYXV0b1JlZnJlc2ggPSB2YWx1ZTtcbiAgICAgICAgaWYgKHRoaXMuYXV0b1JlZnJlc2gpIHtcbiAgICAgICAgICAgIHRoaXMuc2V0VGltZW91dCgpO1xuICAgICAgICB9XG4gICAgICAgIGVsc2Uge1xuICAgICAgICAgICAgdGhpcy5jbGVhclRpbWVvdXQoKTtcbiAgICAgICAgfVxuICAgIH1cbiAgICByZWZyZXNoKCkge1xuICAgICAgICB0aGlzLnNlcnZpY2UucmVmcmVzaCh0aGlzLmRyYXcuYmluZCh0aGlzKSk7XG4gICAgfVxuICAgIGRyYXcocmVxdWVzdHMpIHtcbiAgICAgICAgdGhpcy4kcmVxdWVzdHMudXBkYXRlKHJlcXVlc3RzKTtcbiAgICB9XG59XG5leHBvcnRzLlZjID0gVmM7XG5nbG9iYWwudmMgPSBuZXcgVmMoKTtcbiJdLCJuYW1lcyI6W10sInNvdXJjZVJvb3QiOiIifQ==
/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ "./app/ts/service.ts":
/*!***************************!*\
  !*** ./app/ts/service.ts ***!
  \***************************/
/***/ ((__unused_webpack_module, exports) => {


Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.Service = void 0;
var Service = /** @class */ (function () {
    function Service(vc) {
        this.vc = vc;
    }
    Service.prototype.refresh = function (callback) {
    };
    Service.prototype.create = function (data, callback) {
    };
    return Service;
}());
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
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
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
var service_1 = __webpack_require__(/*! ./service */ "./app/ts/service.ts");
var Vc = /** @class */ (function () {
    function Vc() {
        this.refreshInterval = 10000;
        this.autoRefresh = false;
        this.service = new service_1.Service(this);
        this.refreshAndSetTimeout();
    }
    Vc.prototype.create = function (raw) {
        this.service.create(raw, this.draw.bind(this));
    };
    Vc.prototype.clearTimeout = function () {
        window.clearTimeout(this.timeout);
    };
    Vc.prototype.setTimeout = function () {
        this.timeout = window.setTimeout(this.refreshAndSetTimeout.bind(this), this.refreshInterval);
    };
    Vc.prototype.refreshAndSetTimeout = function () {
        this.refresh();
        if (this.autoRefresh) {
            this.setTimeout();
        }
    };
    Vc.prototype.setAutoRefresh = function (value) {
        this.autoRefresh = value;
        if (this.autoRefresh) {
            this.setTimeout();
        }
        else {
            this.clearTimeout();
        }
    };
    Vc.prototype.refresh = function () {
        this.service.refresh(this.draw.bind(this));
    };
    Vc.prototype.draw = function (requests) {
        document.querySelector('generation-requests')
            .update(requests);
    };
    return Vc;
}());
exports.Vc = Vc;
__webpack_require__.g.vc = new Vc();

})();

/******/ })()
;
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoidmMuanMiLCJtYXBwaW5ncyI6Ijs7Ozs7Ozs7OztBQUFhO0FBQ2IsOENBQTZDLEVBQUUsYUFBYSxFQUFDO0FBQzdELGVBQWU7QUFDZjtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EsQ0FBQztBQUNELGVBQWU7Ozs7Ozs7VUNmZjtVQUNBOztVQUVBO1VBQ0E7VUFDQTtVQUNBO1VBQ0E7VUFDQTtVQUNBO1VBQ0E7VUFDQTtVQUNBO1VBQ0E7VUFDQTtVQUNBOztVQUVBO1VBQ0E7O1VBRUE7VUFDQTtVQUNBOzs7OztXQ3RCQTtXQUNBO1dBQ0E7V0FDQTtXQUNBLEdBQUc7V0FDSDtXQUNBO1dBQ0EsQ0FBQzs7Ozs7Ozs7Ozs7QUNQWTtBQUNiLDhDQUE2QyxFQUFFLGFBQWEsRUFBQztBQUM3RCxVQUFVO0FBQ1YsZ0JBQWdCLG1CQUFPLENBQUMsc0NBQVc7QUFDbkM7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSxDQUFDO0FBQ0QsVUFBVTtBQUNWLHFCQUFNIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vdmMvLi9hcHAvdHMvc2VydmljZS50cyIsIndlYnBhY2s6Ly92Yy93ZWJwYWNrL2Jvb3RzdHJhcCIsIndlYnBhY2s6Ly92Yy93ZWJwYWNrL3J1bnRpbWUvZ2xvYmFsIiwid2VicGFjazovL3ZjLy4vYXBwL3RzL3ZjLnRzIl0sInNvdXJjZXNDb250ZW50IjpbIlwidXNlIHN0cmljdFwiO1xuT2JqZWN0LmRlZmluZVByb3BlcnR5KGV4cG9ydHMsIFwiX19lc01vZHVsZVwiLCB7IHZhbHVlOiB0cnVlIH0pO1xuZXhwb3J0cy5TZXJ2aWNlID0gdm9pZCAwO1xudmFyIFNlcnZpY2UgPSAvKiogQGNsYXNzICovIChmdW5jdGlvbiAoKSB7XG4gICAgZnVuY3Rpb24gU2VydmljZSh2Yykge1xuICAgICAgICB0aGlzLnZjID0gdmM7XG4gICAgfVxuICAgIFNlcnZpY2UucHJvdG90eXBlLnJlZnJlc2ggPSBmdW5jdGlvbiAoY2FsbGJhY2spIHtcbiAgICAgICAgY29uc29sZS5sb2coJ2xvbCcsIGNhbGxiYWNrKTtcbiAgICB9O1xuICAgIFNlcnZpY2UucHJvdG90eXBlLmNyZWF0ZSA9IGZ1bmN0aW9uIChkYXRhLCBjYWxsYmFjaykge1xuICAgICAgICBjb25zb2xlLmxvZygncGVudXMgd2VudXMnLCBkYXRhLCBjYWxsYmFjayk7XG4gICAgfTtcbiAgICByZXR1cm4gU2VydmljZTtcbn0oKSk7XG5leHBvcnRzLlNlcnZpY2UgPSBTZXJ2aWNlO1xuIiwiLy8gVGhlIG1vZHVsZSBjYWNoZVxudmFyIF9fd2VicGFja19tb2R1bGVfY2FjaGVfXyA9IHt9O1xuXG4vLyBUaGUgcmVxdWlyZSBmdW5jdGlvblxuZnVuY3Rpb24gX193ZWJwYWNrX3JlcXVpcmVfXyhtb2R1bGVJZCkge1xuXHQvLyBDaGVjayBpZiBtb2R1bGUgaXMgaW4gY2FjaGVcblx0dmFyIGNhY2hlZE1vZHVsZSA9IF9fd2VicGFja19tb2R1bGVfY2FjaGVfX1ttb2R1bGVJZF07XG5cdGlmIChjYWNoZWRNb2R1bGUgIT09IHVuZGVmaW5lZCkge1xuXHRcdHJldHVybiBjYWNoZWRNb2R1bGUuZXhwb3J0cztcblx0fVxuXHQvLyBDcmVhdGUgYSBuZXcgbW9kdWxlIChhbmQgcHV0IGl0IGludG8gdGhlIGNhY2hlKVxuXHR2YXIgbW9kdWxlID0gX193ZWJwYWNrX21vZHVsZV9jYWNoZV9fW21vZHVsZUlkXSA9IHtcblx0XHQvLyBubyBtb2R1bGUuaWQgbmVlZGVkXG5cdFx0Ly8gbm8gbW9kdWxlLmxvYWRlZCBuZWVkZWRcblx0XHRleHBvcnRzOiB7fVxuXHR9O1xuXG5cdC8vIEV4ZWN1dGUgdGhlIG1vZHVsZSBmdW5jdGlvblxuXHRfX3dlYnBhY2tfbW9kdWxlc19fW21vZHVsZUlkXShtb2R1bGUsIG1vZHVsZS5leHBvcnRzLCBfX3dlYnBhY2tfcmVxdWlyZV9fKTtcblxuXHQvLyBSZXR1cm4gdGhlIGV4cG9ydHMgb2YgdGhlIG1vZHVsZVxuXHRyZXR1cm4gbW9kdWxlLmV4cG9ydHM7XG59XG5cbiIsIl9fd2VicGFja19yZXF1aXJlX18uZyA9IChmdW5jdGlvbigpIHtcblx0aWYgKHR5cGVvZiBnbG9iYWxUaGlzID09PSAnb2JqZWN0JykgcmV0dXJuIGdsb2JhbFRoaXM7XG5cdHRyeSB7XG5cdFx0cmV0dXJuIHRoaXMgfHwgbmV3IEZ1bmN0aW9uKCdyZXR1cm4gdGhpcycpKCk7XG5cdH0gY2F0Y2ggKGUpIHtcblx0XHRpZiAodHlwZW9mIHdpbmRvdyA9PT0gJ29iamVjdCcpIHJldHVybiB3aW5kb3c7XG5cdH1cbn0pKCk7IiwiXCJ1c2Ugc3RyaWN0XCI7XG5PYmplY3QuZGVmaW5lUHJvcGVydHkoZXhwb3J0cywgXCJfX2VzTW9kdWxlXCIsIHsgdmFsdWU6IHRydWUgfSk7XG5leHBvcnRzLlZjID0gdm9pZCAwO1xudmFyIHNlcnZpY2VfMSA9IHJlcXVpcmUoXCIuL3NlcnZpY2VcIik7XG52YXIgVmMgPSAvKiogQGNsYXNzICovIChmdW5jdGlvbiAoKSB7XG4gICAgZnVuY3Rpb24gVmMoKSB7XG4gICAgICAgIHRoaXMucmVmcmVzaEludGVydmFsID0gMTAwMDA7XG4gICAgICAgIHRoaXMuYXV0b1JlZnJlc2ggPSBmYWxzZTtcbiAgICAgICAgY29uc29sZS5sb2coJ3BlbnVzIGxvbCcpO1xuICAgICAgICB0aGlzLnNlcnZpY2UgPSBuZXcgc2VydmljZV8xLlNlcnZpY2UodGhpcyk7XG4gICAgICAgIHRoaXMucmVmcmVzaEFuZFNldFRpbWVvdXQoKTtcbiAgICB9XG4gICAgVmMucHJvdG90eXBlLmNyZWF0ZSA9IGZ1bmN0aW9uIChyYXcpIHtcbiAgICAgICAgdGhpcy5zZXJ2aWNlLmNyZWF0ZShyYXcsIHRoaXMuZHJhdy5iaW5kKHRoaXMpKTtcbiAgICB9O1xuICAgIFZjLnByb3RvdHlwZS5jbGVhclRpbWVvdXQgPSBmdW5jdGlvbiAoKSB7XG4gICAgICAgIHdpbmRvdy5jbGVhclRpbWVvdXQodGhpcy50aW1lb3V0KTtcbiAgICB9O1xuICAgIFZjLnByb3RvdHlwZS5zZXRUaW1lb3V0ID0gZnVuY3Rpb24gKCkge1xuICAgICAgICB0aGlzLnRpbWVvdXQgPSB3aW5kb3cuc2V0VGltZW91dCh0aGlzLnJlZnJlc2hBbmRTZXRUaW1lb3V0LmJpbmQodGhpcyksIHRoaXMucmVmcmVzaEludGVydmFsKTtcbiAgICB9O1xuICAgIFZjLnByb3RvdHlwZS5yZWZyZXNoQW5kU2V0VGltZW91dCA9IGZ1bmN0aW9uICgpIHtcbiAgICAgICAgdGhpcy5yZWZyZXNoKCk7XG4gICAgICAgIGlmICh0aGlzLmF1dG9SZWZyZXNoKSB7XG4gICAgICAgICAgICB0aGlzLnNldFRpbWVvdXQoKTtcbiAgICAgICAgfVxuICAgIH07XG4gICAgVmMucHJvdG90eXBlLnNldEF1dG9SZWZyZXNoID0gZnVuY3Rpb24gKHZhbHVlKSB7XG4gICAgICAgIHRoaXMuYXV0b1JlZnJlc2ggPSB2YWx1ZTtcbiAgICAgICAgaWYgKHRoaXMuYXV0b1JlZnJlc2gpIHtcbiAgICAgICAgICAgIHRoaXMuc2V0VGltZW91dCgpO1xuICAgICAgICB9XG4gICAgICAgIGVsc2Uge1xuICAgICAgICAgICAgdGhpcy5jbGVhclRpbWVvdXQoKTtcbiAgICAgICAgfVxuICAgIH07XG4gICAgVmMucHJvdG90eXBlLnJlZnJlc2ggPSBmdW5jdGlvbiAoKSB7XG4gICAgICAgIHRoaXMuc2VydmljZS5yZWZyZXNoKHRoaXMuZHJhdy5iaW5kKHRoaXMpKTtcbiAgICB9O1xuICAgIFZjLnByb3RvdHlwZS5kcmF3ID0gZnVuY3Rpb24gKHJlcXVlc3RzKSB7XG4gICAgICAgIGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3IoJ2dlbmVyYXRpb24tcmVxdWVzdHMnKVxuICAgICAgICAgICAgLnVwZGF0ZShyZXF1ZXN0cyk7XG4gICAgfTtcbiAgICByZXR1cm4gVmM7XG59KCkpO1xuZXhwb3J0cy5WYyA9IFZjO1xuZ2xvYmFsLnZjID0gbmV3IFZjKCk7XG4iXSwibmFtZXMiOltdLCJzb3VyY2VSb290IjoiIn0=

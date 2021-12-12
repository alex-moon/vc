import {Vc} from "../vc";

export interface ElOptions {
    class ?: string;
    innerText ?: string;
    attr ?: any;

    type ?: string;
    value ?: string;
    checked ?: boolean;
}

export abstract class BaseElement extends HTMLElement {
    protected vc: Vc;

    constructor() {
        super();
        this.vc = Vc.instance;
    }

    protected el(tag: string, options: ElOptions = {}) {
        const result = document.createElement(tag);
        if (options.class) {
            result.classList.add(options.class);
        }
        if (options.type) {
            result.setAttribute('type', options.type);
        }
        if (options.value) {
            result.setAttribute('value', options.value);
        }
        if (options.checked && result instanceof HTMLInputElement) {
            result.checked = options.checked;
        }
        if (options.innerText) {
            result.innerText = options.innerText;
        }
        if (options.attr) {
            for (const [key, value] of Object.entries(options.attr)) {
                result.setAttribute(key, '' + value);
            }
        }
        return result;
    }
}

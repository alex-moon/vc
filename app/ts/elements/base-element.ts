import {Vc} from "../vc";

export abstract class BaseElement extends HTMLElement {
    protected vc: Vc;

    constructor() {
        super();
        this.vc = Vc.instance;
    }

    protected el(tag: string, cssClass: string = null) {
        const result = document.createElement(tag);
        if (cssClass) {
            result.classList.add(cssClass);
        }
        return result;
    }
}

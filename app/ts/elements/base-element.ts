import {Vc} from "../vc";

export abstract class BaseElement extends HTMLElement {
    protected vc: Vc;

    constructor() {
        super();
        this.vc = Vc.instance;
    }
}

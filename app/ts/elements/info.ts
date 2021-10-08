import {CustomElement} from 'custom-elements-ts';

@CustomElement({
    tag: 'vc-info',
    shadow: false,
    style: ``,
    template: require('./info.inc')
})
export class Info extends HTMLElement {
    $root: HTMLElement
    expanded = false;

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.info');
    }

    expand() {
        this.expanded = !this.expanded;
        if (this.expanded) {
            this.$root.classList.add('expanded');
        } else {
            this.$root.classList.remove('expanded');
        }
    }
}

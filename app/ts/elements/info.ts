import {CustomElement} from 'custom-elements-ts';

@CustomElement({
    tag: 'vc-info',
    shadow: false,
    style: ``,
    template: require('./info.inc')
})
export class Info extends HTMLElement {
    $root: HTMLElement;
    $info: HTMLElement;
    $close: HTMLButtonElement;
    expanded = false;

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.info-container');
        this.$info = this.$root.querySelector('.info');
        this.$close = this.$info.querySelector('button.close');
        this.$close.addEventListener('click', () => {
            this.expand();
        });
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

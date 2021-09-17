import {CustomElement, Prop, Watch} from 'custom-elements-ts';

@CustomElement({
  tag: 'vc-chip',
  shadow: false,
  style: ``,
  // @todo figure out how to make templateUrl work
  template: `
<div class="chip"></div>
`
})
export class Chip extends HTMLElement {
    $root: HTMLElement;

    @Prop() text: string;

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.chip');
    }

    @Watch('text')
    protected update() {
        this.$root.innerHTML = this.text;
    }
}

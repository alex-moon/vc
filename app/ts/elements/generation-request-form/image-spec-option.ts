import {
    CustomElement,
    Dispatch, DispatchEmitter,
    Listen,
    Prop,
    Toggle, Watch
} from 'custom-elements-ts';
import {BaseElement} from "../base-element";

@CustomElement({
    tag: 'vc-image-spec-option',
    shadow: false,
    style: ``,
    template: `
<div class="image-spec-option"></div>
`,
})
export class ImageSpecOption extends BaseElement {
    $root: HTMLElement;

    @Prop() label: string;
    @Prop() type: string;
    @Prop() value: string;
    @Dispatch('change.value') change: DispatchEmitter;

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.image-spec-option');
    }

    @Watch('value')
    protected update() {
        console.log('update called', this.value);
        this.$root.innerHTML = '';
        const label = this.el('label', {innerText: this.label});
        const input = this.type === 'number'
            ? this.el('input', {type: 'number', value: this.value})
            : this.el('input', {type: 'checkbox', checked: this.value === 'true'});
        input.addEventListener('change', this.onChange.bind(this));
        label.appendChild(input);
        this.$root.appendChild(label);
    }

    protected onChange(e: any) {
        console.log(e);
        e.preventDefault();
        const value = this.type === 'number'
            ? e.currentTarget.value
            : e.currentTarget.checked;
        this.change.emit({detail: value})
    }
}

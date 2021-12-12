import {
    CustomElement,
    Dispatch,
    DispatchEmitter,
    Prop,
    Watch
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
        this.$root.innerHTML = '';
        const label = this.el('label', {innerText: this.label});
        let input;
        switch (this.type) {
            case 'int':
                input = this.el('input', {
                    type: 'number',
                    value: this.value,
                    attr: {step: '1'}
                })
                break;
            case 'float':
                input = this.el('input', {
                    type: 'number',
                    value: this.value,
                    attr: {step: '0.1'}
                })
                break;
            case 'boolean':
                input = this.el('input', {
                    type: 'checkbox',
                    checked: this.value === 'true'
                });
                break;
            default:
                throw new Error('Invalid type for image spec option: ' + this.type);
        }
        input.addEventListener('change', this.onChange.bind(this));
        label.appendChild(input);
        this.$root.appendChild(label);
    }

    protected onChange(e: any) {
        e.preventDefault();
        let value;
        switch (this.type) {
            case 'int':
                value = parseInt(e.currentTarget.value, 10);
                break;
            case 'float':
                value = parseFloat(e.currentTarget.value);
                break;
            case 'boolean':
                value = e.currentTarget.checked;
                break;
            default:
                throw new Error('Invalid type for image spec option: ' + this.type);
        }
        this.change.emit({detail: value});
    }
}

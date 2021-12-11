import {CustomElement, Listen} from 'custom-elements-ts';
import {GenerationSpec} from "../models/generation-spec";
import {BaseElement} from "./base-element";

@CustomElement({
    tag: 'vc-generation-request-form',
    shadow: false,
    style: ``,
    template: `
<div class="request-form">
    <h2>
        Create virtual content
        <span class="material-icons">expand_more</span>
    </h2>
    <form>
        <div class="steps"></div>
        <div class="actions">
            <button type="submit">Save</button>
        </div>
    </form>
</div>
`,
})
export class GenerationRequestForm extends BaseElement {
    $root: HTMLElement;
    $header: HTMLElement;
    $form: HTMLElement;
    $steps: HTMLElement;

    spec: GenerationSpec;
    expanded = false;

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.request-form');

        this.$header = this.$root.querySelector('h2');
        this.$header.addEventListener('click', (e) => {
            if (this.expanded) {
                this.$form.classList.remove('expanded');
                this.$header.querySelector('span').innerHTML = 'expand_more';
                this.expanded = false;
            } else {
                this.$form.classList.add('expanded');
                this.$header.querySelector('span').innerHTML = 'expand_less';
                this.expanded = true;
            }
        });

        this.$form = this.$root.querySelector('form');
        this.$steps = this.$form.querySelector('.steps');
        this.spec = new GenerationSpec();
    }

    protected draw() {
        if (!this.spec) {
            return;
        }
        this.$steps.innerHTML = '';

    }

    @Listen('click', '.actions button')
    protected submit(e: MouseEvent) {
        e.preventDefault();
        this.vc.create(this.spec);
        this.spec = new GenerationSpec();
        this.draw();
    }
}

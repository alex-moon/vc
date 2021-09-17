import {CustomElement, Listen, Prop, Watch} from 'custom-elements-ts';
import {Vc} from "../vc";
import {ImageSpec} from "../models/image-spec";
import {Chip} from "./chip";

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
        <div class="texts">
            <div class="text-input">
                <h3>Text</h3>
                <textarea placeholder="Primary prompt"></textarea>
                <button class="material-icons">
                    add_circle
                </button>
            </div>
            <div class="chips"></div>
        </div>
        <div class="styles">
            <div class="text-input">
                <h3>Styles</h3>
                <input placeholder="Secondary prompt"/>
                <button class="material-icons">
                    add_circle
                </button>
            </div>
            <div class="chips"></div>
        </div>
        <div class="actions">
            <button type="submit">Save</button>
        </div>
    </form>
</div>
`
})
export class GenerationRequestForm extends HTMLElement {
    $root: HTMLElement
    $header: HTMLElement
    $form: HTMLElement
    $textInput: HTMLTextAreaElement
    $textChips: HTMLElement
    $styleInput: HTMLInputElement
    $styleChips: HTMLElement

    vc: Vc;

    _spec: ImageSpec;
    _expanded = false;

    constructor() {
        super();
    }

    connect(vc: Vc) {
        this.vc = vc;
    }

    connectedCallback() {
        this.$root = this.querySelector('.request-form');

        this.$header = this.$root.querySelector('h2');
        this.$header.addEventListener('click', (e) => {
            if (this._expanded) {
                this.$form.classList.remove('expanded');
                this.$header.querySelector('span').innerHTML = 'expand_more';
                this._expanded = false;
            } else {
                this.$form.classList.add('expanded');
                this.$header.querySelector('span').innerHTML = 'expand_less';
                this._expanded = true;
            }
        });

        this.$form = this.$root.querySelector('form');
        this.$textInput = this.$form.querySelector('.texts .text-input textarea');
        this.$textChips = this.$form.querySelector('.texts .chips');
        this.$styleInput = this.$form.querySelector('.styles .text-input input');
        this.$styleChips = this.$form.querySelector('.styles .chips');
        this._spec = new ImageSpec();
    }

    protected draw() {
        console.log('draw called', this._spec);
        if (!this._spec) {
            return;
        }

        this.$textChips.innerHTML = '';
        for (const text of this._spec.texts) {
            const chip = document.createElement('vc-chip') as Chip;
            this.$textChips.appendChild(chip);
            chip.setAttribute('text', text);
        }

        this.$styleChips.innerHTML = '';
        for (const style of this._spec.styles) {
            const chip = document.createElement('vc-chip') as Chip;
            this.$styleChips.appendChild(chip);
            chip.setAttribute('text', style);
        }
    }

    @Listen('click', '.actions button')
    protected submit(e: MouseEvent) {
        e.preventDefault();
        this.vc.create(this._spec);
        this._spec = new ImageSpec();
        this.draw();
    }

    @Listen('click', '.texts .text-input button')
    protected addText(e: MouseEvent) {
        e.preventDefault();
        this._spec.texts.push(this.$textInput.value);
        this.$textInput.value = '';
        this.draw();
    }

    @Listen('click', '.styles .text-input button')
    protected addStyle(e: MouseEvent) {
        e.preventDefault();
        this._spec.styles.push(this.$styleInput.value);
        this.$styleInput.value = '';
        this.draw();
    }
}

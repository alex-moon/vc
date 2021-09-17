import {CustomElement} from 'custom-elements-ts';
import {GenerationRequest} from "../models/generation-request";
import {Vc} from "../vc";

@CustomElement({
  tag: 'generation-request-form',
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
        </div>
        <div class="styles">
            <div class="text-input">
                <h3>Styles</h3>
                <input placeholder="Secondary prompt"/>
                <button class="material-icons">
                    add_circle
                </button>
            </div>
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

    vc: Vc;

    _request: GenerationRequest
    _expanded = false;

    _texts: string[];
    _styles: string[];

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
        this.$form.addEventListener("submit", (e) => {
            e.preventDefault();
            this.vc.create({
                texts: this._texts,
                styles: this._styles,
            });
        });
    }
}

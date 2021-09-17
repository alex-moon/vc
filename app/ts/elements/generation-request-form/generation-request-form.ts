import {CustomElement} from 'custom-elements-ts';
import {GenerationRequest} from "../../models/generation-request";

@CustomElement({
  tag: 'generation-request-form',
  templateUrl: 'generation-request-form.html',
  styleUrl: 'generation-request-form.scss'
})
export class GenerationRequestForm extends HTMLElement {
    $root: HTMLElement
    $header: HTMLElement
    $form: HTMLElement

    _request: GenerationRequest
    _expanded = false;

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.shadowRoot.querySelector('.request-form');

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
            // @todo do thing with vc
        });
    }
}

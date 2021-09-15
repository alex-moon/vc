import {CustomElement} from 'custom-elements-ts';

@CustomElement({
  tag: 'generation-request-form',
  templateUrl: 'generation-request-form.html',
  styleUrl: 'generation-request-form.scss'
})
export class GenerationRequestForm extends HTMLElement {
    $root
    $header
    $form

    _expanded = false;

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.request-form');

        this.$header = this.querySelector('h2');
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

        this.$form = this.querySelector('form');
        this.$form.addEventListener("submit", (e) => {
            e.preventDefault();
            // @todo do thing with vc
        });
    }
}

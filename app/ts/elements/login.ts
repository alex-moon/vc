import {CustomElement} from 'custom-elements-ts';
import {BaseElement} from "./base-element";

@CustomElement({
    tag: 'vc-login',
    shadow: false,
    style: ``,
    template: `
<div class="login">
    <form>
        <input type="text" placeholder="API key" />
    </form>
</div>
`
})
export class Login extends BaseElement {
    $root: HTMLElement;
    $form: HTMLElement;
    $input: HTMLInputElement;

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.login');
        this.$form = this.$root.querySelector('form');
        this.$form.addEventListener('submit', this.submit.bind(this));
        this.$input = this.$form.querySelector('input');
    }

    submit(event: Event) {
        event.preventDefault();
        this.vc.authenticate(this.$input.value);
    }
}

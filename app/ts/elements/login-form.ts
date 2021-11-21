import {CustomElement} from 'custom-elements-ts';
import {Login} from "./login";
import {GenerationRequestForm} from "./generation-request-form";
import {AuthHelper} from "../helpers/auth";
import {EnvHelper} from "../helpers/env";

@CustomElement({
    tag: 'vc-login-form',
    shadow: false,
    style: ``,
    template: `
<div class="login-form"></div>
`
})
export class LoginForm extends HTMLElement {
    $root: HTMLElement
    $login: Login
    $form: GenerationRequestForm

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.login-form');
        this.draw();
        AuthHelper.listen(this.draw.bind(this));
    }

    draw() {
        this.$root.innerHTML = ''
        if (AuthHelper.hasToken()) {
            this.$form = document.createElement('vc-generation-request-form') as GenerationRequestForm;
            this.$root.appendChild(this.$form);
        } else {
            this.$login = document.createElement('vc-login') as Login;
            this.$root.appendChild(this.$login);
        }
    }
}

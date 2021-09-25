import {CustomElement} from 'custom-elements-ts';
import {Vc} from "../vc";
import {Login} from "./login";
import {GenerationRequestForm} from "./generation-request-form";
import {AuthHelper} from "../helpers/auth";

@CustomElement({
    tag: 'vc-login-form',
    shadow: false,
    style: ``,
    template: `
<div class="login-form">
    <!-- vc-login></vc-login>
    <vc-generation-request-form></vc-generation-request-form -->
</div>
`
})
export class LoginForm extends HTMLElement {
    $root: HTMLElement
    $login: Login
    $form: GenerationRequestForm

    vc: Vc;

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.login-form');
        this.draw();
        AuthHelper.listen(this.draw.bind(this));
    }

    draw() {
        this.$root.innerHTML = '';

        if (AuthHelper.hasToken()) {
            this.$form = document.createElement('vc-generation-request-form') as GenerationRequestForm;
            this.$root.appendChild(this.$form);
            if (this.vc) {
                this.$form.connect(this.vc);
            }
        } else {
            this.$login = document.createElement('vc-login') as Login;
            this.$root.appendChild(this.$login);
        }
    }

    connect(vc: Vc) {
        this.vc = vc;
        if (this.$form) {
            this.$form.connect(vc);
        }
    }
}

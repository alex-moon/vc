window.templates = window.templates || {}
window.templates['generation-request-form'] = document.createElement('template');
window.templates['generation-request-form'].innerHTML = `
    <div class="request-form">
        <form>
            <input type="text" name="prompt" placeholder="prompt" />
            <button type="submit">Save</button>
        </form>
    </div>
`;

class GenerationRequestFormElement extends HTMLElement {
    constructor() {
        super();
    }

    connectedCallback() {
        const template = window.templates['generation-request-form'];
        this.appendChild(template.content.cloneNode(true));
        this.$root = this.querySelector('.request-form');
        this.$form = this.querySelector('form');

        this.$prompt = this.querySelector('input[name=prompt]');
        this.$form.addEventListener("submit", (e) => {
            e.preventDefault();
            if (!this.validate()) {
                console.log('form invalid');
                return;
            }
            window.vc.create(this.marshall());
        });
    }

    validate() {
        return !!this.$prompt.value;
    }

    marshall() {
        return {
            prompt: this.$prompt.value,
        };
    }
}

customElements.define('generation-request-form', GenerationRequestFormElement);

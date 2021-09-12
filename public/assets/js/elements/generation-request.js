window.templates = window.templates || {}
window.templates['generation-request'] = document.createElement('template');
window.templates['generation-request'].innerHTML = `
    <div class="request">
        <span></span>
    </div>
`;

class GenerationRequestElement extends HTMLElement {
    constructor() {
        super();
        this._request = null;
    }

    connectedCallback() {
        const template = window.templates['generation-request'];
        this.appendChild(template.content.cloneNode(true));
        this.$root = this.querySelector('.request');
        this.$name = this.querySelector('span');
    }

    update(request) {
        this._request = request;
        this.$name.textContent = this._request.name;
    }
}

customElements.define('generation-request', GenerationRequestElement);

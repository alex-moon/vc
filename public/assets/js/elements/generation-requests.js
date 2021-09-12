window.templates = window.templates || {}
window.templates['generation-requests'] = document.createElement('template');
window.templates['generation-requests'].innerHTML = `
    <div class="requests"></div>
`;

class GenerationRequestsElement extends HTMLElement {
    constructor() {
        super();
    }

    connectedCallback() {
        const template = window.templates['generation-requests'];
        this.appendChild(template.content.cloneNode(true));
        this.$root = this.querySelector('.requests');
    }

    update(requests) {
        this._requests = requests;

        this.$root.innerHTML = '';
        this._requests.forEach((request, index) => {
            const $request = document.createElement('generation-request');
            this.$root.appendChild($request);
            $request.update(request);
        });
    }
}

customElements.define('generation-requests', GenerationRequestsElement);

window.templates = window.templates || {}
window.templates['generation-request'] = document.createElement('template');
window.templates['generation-request'].innerHTML = `
    <div class="request">
        <div class="summary">
            <span class="name"></span>
            <span class="steps-completed"></span> steps completed out of
            <span class="steps-total"></span> total
        </div>
        <div class="panels">
            <div class="panel">
                <img class="preview" />
            </div>
            <div class="panel">
                <video class="result" width="200" height="200" controls></video>
            </div>
        </div>
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
        this.$name = this.querySelector('.name');
        this.$stepsCompleted = this.querySelector('.steps-completed');
        this.$stepsTotal  = this.querySelector('.steps-total');
        this.$preview  = this.querySelector('.preview');
        this.$result  = this.querySelector('.result');
    }

    update(request) {
        this._request = request;
        this.$name.textContent = this._request.name;
        this.$stepsCompleted.textContent = this._request.steps_completed;
        this.$stepsTotal.textContent = this._request.steps_total;
        this.$preview.src = this._request.preview || '/assets/placeholder.png';
        this.$result.innerHTML = '';
        const source = document.createElement('source');
        source.src = this._request.results[0].url;
        this.$result.appendChild(source);
    }
}

customElements.define('generation-request', GenerationRequestElement);

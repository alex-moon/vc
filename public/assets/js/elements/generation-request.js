window.templates = window.templates || {}
window.templates['generation-request'] = document.createElement('template');
window.templates['generation-request'].innerHTML = `
    <div class="request">
        <div class="summary">
            <div class="preview">
                <img />
            </div>
            <div class="progress">
                <div class="labels">
                    <div class="name"></div>
                    <div class="steps">
                        <span class="steps-completed"></span>
                        /
                        <span class="steps-total"></span>
                    </div>
                </div>
                <div class="bar">
                    <div class="completed"></div>
                </div>
            </div>
            <div class="actions">
                <span class="material-icons">
                    expand_circle_down
                </span>
            </div>
        </div>
        <div class="panels"></div>
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
        this.$stepsTotal = this.querySelector('.steps-total');
        this.$preview = this.querySelector('.preview img');
        this.$panels = this.querySelector('.panels');
    }

    update(request) {
        this._request = request;
        this.$name.textContent = this._request.name;
        this.$stepsCompleted.textContent = this._request.steps_completed;
        this.$stepsTotal.textContent = this._request.steps_total;
        this.$preview.src = this._request.preview || '/assets/placeholder.png';
        /*
            <div class="panel">
                <video class="result" width="200" height="200" controls></video>
            </div>
        */
        this.$panels.innerHtml = '';
        if (this._request.interim) {
            const panel = this.createVideoPanel(this._request.interim);
            this.$panels.appendChild(panel);
        }
        if (this._request.results) {
            this._request.results.forEach((result) => {
                const panel = this.createVideoPanel(result.url);
                this.$panels.appendChild(panel);
            });
        }
    }

    createVideoPanel(url) {
        const panel = document.createElement('div');
        panel.setAttribute('class', 'panel');

        const video = document.createElement('video');
        video.setAttribute('controls', true);
        video.setAttribute('width', 200);
        video.setAttribute('height', 200);

        const source = document.createElement('source');
        source.src = url;

        video.appendChild(source);
        panel.appendChild(video);
        return panel;
    }
}

customElements.define('generation-request', GenerationRequestElement);

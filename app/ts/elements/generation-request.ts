import {CustomElement} from 'custom-elements-ts';
import {GenerationRequest as Model} from "../models/generation-request";
import {GenerationResult} from "../models/generation-result";

@CustomElement({
  tag: 'vc-generation-request',
  shadow: false,
  style: ``,
  template: `
<div class="request">
    <div class="summary">
        <div class="preview">
            <img />
        </div>
        <div class="progress">
            <div class="labels">
                <div class="name"></div>
            </div>
            <div class="bar">
                <div class="completed"></div>
                <div class="steps">
                    <span class="steps-completed"></span>
                    /
                    <span class="steps-total"></span>
                </div>
            </div>
        </div>
        <div class="actions">
            <button class="material-icons">
                expand_more
            </button>
        </div>
    </div>
    <div class="panels"></div>
</div>
`
})
export class GenerationRequest extends HTMLElement {
    $root: HTMLElement
    $name: HTMLElement
    $stepsCompleted: HTMLElement
    $stepsTotal: HTMLElement
    $barCompleted: HTMLElement
    $preview: HTMLImageElement
    $expand: HTMLElement
    $panels: HTMLElement

    _request: Model
    _expanded = false

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.request');
        this.$name = this.querySelector('.name');
        this.$stepsCompleted = this.querySelector('.steps-completed');
        this.$stepsTotal = this.querySelector('.steps-total');
        this.$barCompleted = this.querySelector('.bar .completed');
        this.$preview = this.querySelector('.preview img');
        this.$expand = this.querySelector('.actions button');
        this.$panels = this.querySelector('.panels');

        this.$expand.addEventListener('click', (e) => {
            if (this._expanded) {
                this.$panels.classList.remove('expanded');
                this.$expand.innerHTML = 'expand_more';
                this._expanded = false;
            } else {
                this.$panels.classList.add('expanded');
                this.$expand.innerHTML = 'expand_less';
                this._expanded = true;
            }
        });
    }

    update(request: Model) {
        this._request = request;
        this.$name.textContent = this._request.name;
        this.$stepsCompleted.textContent = '' + this._request.steps_completed;
        this.$stepsTotal.textContent = '' + this._request.steps_total;
        this.updateBar(this._request.steps_completed, this._request.steps_total);
        this.$preview.src = this._request.preview || '/assets/placeholder.png';
        this.$panels.innerHTML = '';
        if (this._request.interim) {
            const panel = this.createVideoPanel(this._request.interim);
            this.$panels.appendChild(panel);
        }
        if (this._request.results) {
            this._request.results.forEach((result: GenerationResult) => {
                const panel = this.createVideoPanel(result.url);
                this.$panels.appendChild(panel);
            });
        }
        if (!this._request.interim && !(this._request.results && this._request.results.length)) {
            this.$panels.innerHTML = '<p>Results will appear here when ready.</p>';
        }
    }

    updateBar(completed: number, total: number) {
        let percentage = 0;
        if (total > 0) {
            percentage = 100 * completed / total
        }
        this.$barCompleted.setAttribute(
            'style',
            'width: ' + percentage + '%'
        )
    }

    createVideoPanel(url: string) {
        const panel = document.createElement('div');
        panel.setAttribute('class', 'panel');

        const video = document.createElement('video');
        video.setAttribute('controls', 'controls');
        video.setAttribute('width', '200');
        video.setAttribute('height', '200');

        const source = document.createElement('source');
        source.src = url;

        video.appendChild(source);
        panel.appendChild(video);
        return panel;
    }
}

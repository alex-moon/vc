import {CustomElement} from 'custom-elements-ts';

@CustomElement({
  tag: 'generation-request',
  templateUrl: 'generation-request.html',
  styleUrl: 'generation-request.scss'
})
class GenerationRequest extends HTMLElement {
    $root
    $name
    $stepsCompleted
    $stepsTotal
    $barCompleted
    $preview
    $expand
    $panels

    _request
    _expanded = false

    constructor() {
        super();
    }

    connectedCallback() {
        const template = window.templates['generation-request'];
        this.appendChild(template.content.cloneNode(true));
        this.$root = this.querySelector('.request');
        this.$name = this.querySelector('.name');
        this.$stepsCompleted = this.querySelector('.steps-completed');
        this.$stepsTotal = this.querySelector('.steps-total');
        this.$barCompleted = this.querySelector('.bar .completed');
        this.$preview = this.querySelector('.preview img');
        this.$expand = this.querySelector('.actions button');
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
        this.$panels = this.querySelector('.panels');
    }

    update(request) {
        this._request = request;
        this.$name.textContent = this._request.name;
        this.$stepsCompleted.textContent = this._request.steps_completed;
        this.$stepsTotal.textContent = this._request.steps_total;
        this.updateBar(this._request.steps_completed, this._request.steps_total);
        this.$preview.src = this._request.preview || '/assets/placeholder.png';
        this.$panels.innerHTML = '';
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
        if (!this._request.interim && !this._request.results.length) {
            this.$panels.innerHTML = '<p>Results will appear here when ready.</p>';
        }
    }

    updateBar(completed, total) {
        let percentage = 0;
        if (total > 0) {
            percentage = 100 * completed / total
        }
        this.$barCompleted.setAttribute(
            'style',
            'width: ' + percentage + '%'
        )
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

import {CustomElement, Toggle, Watch} from 'custom-elements-ts';
import {GenerationRequest as Model} from "../../models/generation-request";
import {GenerationResult} from "../../models/generation-result";

@CustomElement({
    tag: 'vc-generation-request-details',
    shadow: false,
    style: ``,
    template: `
<div class="details">
    <div class="panels"></div>
</div>
`
})
export class GenerationRequestDetails extends HTMLElement {
    $root: HTMLElement
    $panels: HTMLElement

    request: Model
    @Toggle() expanded = false

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.details');
        this.$panels = this.$root.querySelector('.panels');
    }

    update(request: Model) {
        this.request = request;
        if (this.request.interim) {
            const panel = this.createVideoPanel(this.request.interim);
            this.$panels.appendChild(panel);
        }
        if (this.request.results) {
            this.request.results.forEach((result: GenerationResult) => {
                const panel = this.createVideoPanel(result.url);
                this.$panels.appendChild(panel);
            });
        }
        if (!this.request.interim && !(this.request.results && this.request.results.length)) {
            this.$panels.innerHTML = '<p>Results will appear here when ready.</p>';
        }
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

    @Watch('expanded')
    protected onExpandedChange() {
        if (this.expanded) {
            this.$root.classList.add('expanded');
        } else {
            this.$root.classList.remove('expanded');
        }
    }
}

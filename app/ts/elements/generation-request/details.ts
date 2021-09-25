import {CustomElement, Toggle, Watch} from 'custom-elements-ts';
import {GenerationRequest as Model} from "../../models/generation-request";
import {GenerationRequestDetailsStep} from "./step";
import {DetailsHelper} from "../../helpers/details";

@CustomElement({
    tag: 'vc-generation-request-details',
    shadow: false,
    style: ``,
    template: `
<div class="details">
    <div class="preview"></div>
    <div class="steps"></div>
</div>
`
})
export class GenerationRequestDetails extends HTMLElement {
    $root: HTMLElement
    $steps: HTMLElement
    $preview: HTMLElement

    request: Model
    @Toggle() expanded = false

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.details');
        this.$steps = this.$root.querySelector('.steps');
        this.$preview = this.$root.querySelector('.preview');
    }

    update(request: Model) {
        this.request = request;

        if (this.request.spec) {
            if (this.request.spec.videos.length) {
                const steps = this.request.spec.videos[0].steps;
                for (let i = 0; i < steps.length; i++) {
                    const element = document.createElement(
                        'vc-generation-request-details-step'
                    ) as GenerationRequestDetailsStep;
                    this.$steps.appendChild(element);
                    element.update(i + 1, steps[i]);
                }
            }
        }

        let url = DetailsHelper.getResultUrl(this.request);
        if (url) {
            const panel = this.createVideoPanel(url);
            this.$preview.appendChild(panel);
        } else {
            const placeholder = document.createElement('img');
            placeholder.src = '/assets/placeholder.png';
            const panel = this.createPanel(placeholder);
            this.$preview.appendChild(panel);
        }
    }

    createVideoPanel(url: string) {
        const video = document.createElement('video');
        video.setAttribute('controls', 'controls');
        video.setAttribute('width', '800');
        video.setAttribute('height', '800');

        const source = document.createElement('source');
        source.src = url;

        video.appendChild(source);
        return this.createPanel(video);
    }

    createPanel(element: HTMLElement) {
        const panel = document.createElement('div');
        panel.setAttribute('class', 'panel');
        panel.appendChild(element);
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

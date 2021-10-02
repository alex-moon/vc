import {CustomElement, Toggle, Watch} from 'custom-elements-ts';
import {GenerationRequest as Model} from "../../models/generation-request";
import {GenerationRequestDetailsStep} from "./step";
import {DetailsHelper, ImageCounter} from "../../helpers/details";
import {Chipset} from "../chipset";

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
    }

    draw() {
        if (!this.expanded) {
            this.$preview.innerHTML = '';
            this.$steps.innerHTML = '';
            return;
        }

        if (this.request.spec) {
            const images = this.request.spec.images;
            if (images && images.length) {
                for (let i = 0; i < images.length; i++) {
                    const element = document.createElement(
                        'vc-generation-request-details-step'
                    ) as GenerationRequestDetailsStep;
                    this.$steps.appendChild(element);
                    element.update(i + 1, images[i]);
                }
            }

            const videos = this.request.spec.videos;
            if (videos && videos.length) {
                for (const video of videos) {
                    const steps = video.steps;
                    for (let i = 0; i < steps.length; i++) {
                        const element = document.createElement(
                            'vc-generation-request-details-step'
                        ) as GenerationRequestDetailsStep;
                        this.$steps.appendChild(element);
                        element.update(i + 1, steps[i]);
                    }
                }
            }
        }

        let urls = DetailsHelper.getResultUrls(this.request);
        if (urls.length) {
            let counter = {next(): string[] { return []; }};
            if (this.request.spec) {
                counter = new ImageCounter(this.request.spec.images);
            }
            let panel;
            for (const url of urls) {
                if (url.substr(-4) === '.png') {
                    panel = this.createImagePanel(url, counter.next());
                } else {
                    panel = this.createVideoPanel(url);
                }
                this.$preview.appendChild(panel);
            }
        } else {
            const panel = this.createImagePanel('/assets/placeholder.png');
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

    createImagePanel(url: string, chips: string[] = []) {
        const img = document.createElement('img');
        img.src = url;
        const panel = this.createPanel(img);
        const chipset = document.createElement('vc-chipset') as Chipset;
        panel.appendChild(chipset);
        chipset.update(chips.filter(text => text));
        return panel;
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
        this.draw();
    }
}

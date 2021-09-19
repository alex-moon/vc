import {CustomElement, Toggle, Watch} from 'custom-elements-ts';
import {GenerationRequest as Model} from "../../models/generation-request";
import {Chipset} from "../chipset";

@CustomElement({
    tag: 'vc-generation-request-details',
    shadow: false,
    style: ``,
    template: `
<div class="details">
    <div class="spec">
        <h3>Texts</h3>
        <vc-chipset class="texts"></vc-chipset>
        <h3>Styles</h3>
        <vc-chipset class="styles"></vc-chipset>    
    </div>
    <div class="preview"></div>
</div>
`
})
export class GenerationRequestDetails extends HTMLElement {
    $root: HTMLElement
    $spec: HTMLElement
    $texts: Chipset;
    $styles: Chipset;
    $preview: HTMLElement

    request: Model
    @Toggle() expanded = false

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.details');
        this.$spec = this.$root.querySelector('.spec');
        this.$texts = this.$spec.querySelector('.texts');
        this.$styles = this.$spec.querySelector('.styles');
        this.$preview = this.$root.querySelector('.preview');
    }

    update(request: Model) {
        this.request = request;
        this.$texts.update(this.request.spec.videos[0].steps[0].texts);
        this.$styles.update(this.request.spec.videos[0].steps[0].styles);
        if (this.request.results && this.request.results.length) {
            const result = this.request.results[0];
            const panel = this.createVideoPanel(result.url);
            this.$preview.appendChild(panel);
        } else if (this.request.interim) {
            const panel = this.createVideoPanel(this.request.interim);
            this.$preview.appendChild(panel);
        }
    }

    createVideoPanel(url: string) {
        const panel = document.createElement('div');
        panel.setAttribute('class', 'panel');

        const video = document.createElement('video');
        video.setAttribute('controls', 'controls');
        video.setAttribute('width', '400');
        video.setAttribute('height', '400');

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

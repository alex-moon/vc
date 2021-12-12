import {CustomElement} from 'custom-elements-ts';
import {VideoSpec} from "../../models/video-spec";

@CustomElement({
    tag: 'vc-video-spec-form',
    shadow: false,
    style: ``,
    template: `
<div class="video-spec-form">
    <div class="steps">
        <p>@todo video steps</p>
    </div>
</div>
`,
})
export class VideoSpecForm extends HTMLElement {
    $root: HTMLElement

    spec: VideoSpec;
    expanded = false;

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.video-spec-form');
    }

    public update(spec: VideoSpec) {
        this.spec = spec;
        this.draw();
    }

    protected draw() {
        if (!this.spec) {
            return;
        }
    }
}

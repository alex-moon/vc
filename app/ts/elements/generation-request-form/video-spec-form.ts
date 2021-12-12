import {CustomElement} from 'custom-elements-ts';
import {VideoSpec} from "../../models/video-spec";
import {ImageSpec} from "../../models/image-spec";
import {ImageSpecForm} from "./image-spec-form";
import {BaseElement} from "../base-element";
import {AddVideoStep} from "./add-video-step";

@CustomElement({
    tag: 'vc-video-spec-form',
    shadow: false,
    style: ``,
    template: `
<div class="video-spec-form">
    <h3>Video</h3>
    <div class="steps">
</div>
`,
})
export class VideoSpecForm extends BaseElement {
    $root: HTMLElement;
    $steps: HTMLElement;

    spec: VideoSpec;
    expanded = false;

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.video-spec-form');
        this.$steps = this.$root.querySelector('.steps');
    }

    public update(spec: VideoSpec) {
        this.spec = spec;
        this.draw();
    }

    protected draw() {
        if (!this.spec) {
            return;
        }
        this.$steps.innerHTML = '';

        for (const spec of this.spec.steps || []) {
            this.addImageSpecForm(spec);
        }

        this.addAddSpec();
    }

    protected addImageSpecForm(spec: ImageSpec) {
        const form = this.el('vc-image-spec-form', {
            attr: {video: true},
        }) as ImageSpecForm;
        this.$steps.appendChild(form);
        form.update(spec);
    }

    protected addAddSpec() {
        const addSpec = this.el('vc-add-video-step') as AddVideoStep;
        this.$steps.appendChild(addSpec);
        addSpec.update(this.spec);
        addSpec.addEventListener('added.image', (event) => {
            this.spec.steps = this.spec.steps || [];
            this.spec.steps.push(new ImageSpec());
            addSpec.update(this.spec);
            this.draw();
        });
    }
}

import {
    CustomElement,
    Dispatch,
    DispatchEmitter,
    Listen
} from 'custom-elements-ts';
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
    <div class="spec-header">
        <h3>Video</h3>
        <button class="material-icons">
            highlight_off
        </button>
    </div>
    <div class="steps">
</div>
`,
})
export class VideoSpecForm extends BaseElement {
    $root: HTMLElement;
    $steps: HTMLElement;

    spec: VideoSpec;
    expanded = false;

    @Dispatch('spec.remove') onRemove: DispatchEmitter;

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

    @Listen('click', '.spec-header button')
    protected onRemoveClicked(e: any) {
        this.onRemove.emit();
    }

    protected addImageSpecForm(spec: ImageSpec) {
        const form = this.el('vc-image-spec-form', {
            attr: {video: true},
        }) as ImageSpecForm;
        form.addEventListener('spec.remove', () => {
            this.spec.steps.splice(this.spec.steps.indexOf(spec), 1);
            this.draw();
        });
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

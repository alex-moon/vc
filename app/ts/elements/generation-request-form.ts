import {CustomElement, Listen} from 'custom-elements-ts';
import {GenerationSpec} from "../models/generation-spec";
import {BaseElement} from "./base-element";
import {AddSpec} from "./generation-request-form/add-spec";
import {ImageSpec} from "../models/image-spec";
import {VideoSpec} from "../models/video-spec";
import {ImageSpecForm} from "./generation-request-form/image-spec-form";
import {VideoSpecForm} from "./generation-request-form/video-spec-form";

@CustomElement({
    tag: 'vc-generation-request-form',
    shadow: false,
    style: ``,
    template: `
<div class="request-form">
    <h2>
        <span class="greeting"></span>
        <span class="expand">
            Create
            <span class="material-icons">expand_more</span>
        </span>
    </h2>
    <form>
        <div class="steps"></div>
        <div class="actions">
            <button type="submit">Save</button>
        </div>
    </form>
</div>
`,
})
export class GenerationRequestForm extends BaseElement {
    $root: HTMLElement;
    $header: HTMLElement;
    $greeting: HTMLElement;
    $form: HTMLElement;
    $steps: HTMLElement;

    spec: GenerationSpec;
    expanded = false;

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.request-form');

        this.$header = this.$root.querySelector('h2');
        this.$header.addEventListener('click', (e) => {
            if (this.expanded) {
                this.$form.classList.remove('expanded');
                this.$header.querySelector('.expand span').innerHTML = 'expand_more';
                this.expanded = false;
            } else {
                this.$form.classList.add('expanded');
                this.$header.querySelector('.expand span').innerHTML = 'expand_less';
                this.expanded = true;
            }
        });
        this.$greeting = this.$header.querySelector('.greeting');

        this.$form = this.$root.querySelector('form');
        this.$steps = this.$form.querySelector('.steps');
        this.spec = new GenerationSpec();
        this.draw();
    }

    protected draw() {
        this.$greeting.innerText = 'Hello, ' + this.vc.userManager.user.name + '!';
        this.$steps.innerHTML = '';

        for (const spec of this.spec.images || []) {
            this.addImageSpecForm(spec);
        }

        for (const spec of this.spec.videos || []) {
            this.addVideoSpecForm(spec);
        }

        this.addAddSpec();
    }

    protected addImageSpecForm(spec: ImageSpec) {
        const form = this.el('vc-image-spec-form') as ImageSpecForm;
        this.$steps.appendChild(form);
        form.update(spec);
        // @todo bind listeners
    }

    protected addVideoSpecForm(spec: VideoSpec) {
        const form = this.el('vc-video-spec-form') as VideoSpecForm;
        this.$steps.appendChild(form);
        form.update(spec);
        // @todo bind listeners
    }

    protected addAddSpec() {
        const addSpec = this.el('vc-add-spec') as AddSpec;
        this.$steps.appendChild(addSpec);
        addSpec.update(this.spec);
        addSpec.addEventListener('added.image', (event) => {
            this.spec.images = this.spec.images || [];
            this.spec.images.push(new ImageSpec());
            addSpec.update(this.spec);
            this.draw();
        });
        addSpec.addEventListener('added.video', (event) => {
            this.spec.videos = this.spec.videos || [];
            this.spec.videos.push(new VideoSpec());
            addSpec.update(this.spec);
            this.draw();
        });
    }

    @Listen('click', '.actions button')
    protected submit(e: MouseEvent) {
        e.preventDefault();
        this.vc.create(this.spec);
        this.spec = new GenerationSpec();
        this.draw();
    }
}

import {
    CustomElement,
    Dispatch,
    DispatchEmitter,
    Listen
} from 'custom-elements-ts';
import {VideoSpec} from "../../models/video-spec";

@CustomElement({
    tag: 'vc-add-video-step',
    shadow: false,
    style: ``,
    template: `
<div class="add-video-step">
    <div class="add-image">
        Add step
        <img src="../../../assets/add-image.png" />
    </div>
</div>
`,
})
export class AddVideoStep extends HTMLElement {
    $root: HTMLElement
    private spec: VideoSpec;

    @Dispatch() addedImage: DispatchEmitter;

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.add-spec');
    }

    @Listen('click', '.add-image')
    addImage() {
        this.addedImage.emit();
    }

    update(spec: VideoSpec) {
        this.spec = spec;
        this.draw();
    }

    draw() {

    }
}

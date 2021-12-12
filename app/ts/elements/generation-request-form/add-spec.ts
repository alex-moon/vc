import {
    CustomElement,
    Dispatch,
    DispatchEmitter,
    Listen
} from 'custom-elements-ts';
import {GenerationSpec} from "../../models/generation-spec";

@CustomElement({
    tag: 'vc-add-spec',
    shadow: false,
    style: ``,
    template: `
<div class="add-spec">
    <div class="add-image">
        Add image
        <img src="../../../assets/add-image.png" />
    </div>
    <div class="add-video">
        Add video
        <img src="../../../assets/add-video.png" />
    </div>
</div>
`,
})
export class AddSpec extends HTMLElement {
    $root: HTMLElement
    private spec: GenerationSpec;

    @Dispatch() addedImage: DispatchEmitter;
    @Dispatch() addedVideo: DispatchEmitter;

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

    @Listen('click', '.add-video')
    addVideo() {
        this.addedVideo.emit();
    }

    update(spec: GenerationSpec) {
        this.spec = spec;
        this.draw();
    }

    draw() {

    }
}

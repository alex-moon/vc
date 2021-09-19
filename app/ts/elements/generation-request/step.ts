import {CustomElement, Toggle} from 'custom-elements-ts';
import {Chipset} from "../chipset";
import {ImageSpec} from "../../models/image-spec";

@CustomElement({
    tag: 'vc-generation-request-details-step',
    shadow: false,
    style: ``,
    template: `
<div class="step">
    <div class="number"></div>
    <div class="spec">
        <h3>Texts</h3>
        <vc-chipset class="texts"></vc-chipset>
        <h3>Styles</h3>
        <vc-chipset class="styles"></vc-chipset>    
    </div>
</div>
`
})
export class GenerationRequestDetailsStep extends HTMLElement {
    $root: HTMLElement
    $number: HTMLElement
    $spec: HTMLElement
    $texts: Chipset;
    $styles: Chipset;

    spec: ImageSpec
    @Toggle() expanded = false

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.step');
        this.$number = this.$root.querySelector('.number');
        this.$spec = this.$root.querySelector('.spec');
        this.$texts = this.$spec.querySelector('.texts');
        this.$styles = this.$spec.querySelector('.styles');
    }

    update(number: number, spec: ImageSpec) {
        this.spec = spec;
        this.$number.innerHTML = number + '.';
        this.$texts.update(this.spec.texts);
        this.$styles.update(this.spec.styles);
    }
}

import {CustomElement, Toggle} from 'custom-elements-ts';
import {Chipset} from "../chipset";
import {ImageSpec} from "../../models/image-spec";
import {DetailsHelper} from "../../helpers/details";
import {BaseElement} from "../base-element";

@CustomElement({
    tag: 'vc-generation-request-details-step',
    shadow: false,
    style: ``,
    template: `
<div class="step">
    <div class="number"><span></span></div>
    <div class="spec">
        <div class="text-chipset">
            <h3>Texts</h3>
            <vc-chipset class="texts"></vc-chipset>
        </div>
        <div class="text-chipset">
            <h3>Styles</h3>
            <vc-chipset class="styles"></vc-chipset>
        </div>
        <div class="fields"></div>
    </div>
</div>
`
})
export class GenerationRequestDetailsStep extends BaseElement {
    $root: HTMLElement
    $number: HTMLElement
    $spec: HTMLElement
    $texts: Chipset;
    $styles: Chipset;
    $fields: HTMLElement;

    number: number;
    spec: ImageSpec
    @Toggle() expanded = false

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.step');
        this.$number = this.$root.querySelector('.number span');
        this.$spec = this.$root.querySelector('.spec');
        this.$texts = this.$spec.querySelector('.texts');
        this.$styles = this.$spec.querySelector('.styles');
        this.$fields = this.$spec.querySelector('.fields');
    }

    update(number: number, spec: ImageSpec) {
        this.spec = spec;
        this.number = number;
        this.draw();
    }

    draw() {
        this.$number.innerHTML = this.number + '.';
        this.$texts.update(this.spec.texts);
        this.$styles.update(this.spec.styles);
        this.drawFields();
    }

    drawFields() {
        for (const field of DetailsHelper.getFields()) {
            if (field.field in this.spec) {
                const fieldValue = (this.spec as any)[field.field];
                if (fieldValue) {
                    const div = this.el('div', {class: 'field'});
                    const label = this.el('label', {
                        innerText: field.label,
                    });
                    const span = this.el('span', {
                        innerText: '' + fieldValue,
                    });
                    div.appendChild(label);
                    div.appendChild(span);
                    this.$fields.appendChild(div);
                }
            }
        }
    }
}

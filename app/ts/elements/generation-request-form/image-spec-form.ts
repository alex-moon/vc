import {
    CustomElement,
    Dispatch,
    DispatchEmitter,
    Listen,
    Toggle
} from 'custom-elements-ts';
import {Chipset} from "../chipset";
import {ImageSpec} from "../../models/image-spec";
import {DetailsHelper} from "../../helpers/details";
import {BaseElement} from "../base-element";
import {ImageSpecOption} from "./image-spec-option";

@CustomElement({
    tag: 'vc-image-spec-form',
    shadow: false,
    style: ``,
    template: `
<div class="image-spec-form">
    <div class="spec-header">
        <h3></h3>
        <button class="material-icons">
            highlight_off
        </button>
    </div>
    <div class="texts">
        <div class="text-input">
            <label>
                Add text
                <textarea id="texts-input" placeholder="e.g. A medieval cathedral interior"></textarea>
            </label>
            <button class="material-icons">
                add_circle
            </button>
        </div>
        <vc-chipset removable></vc-chipset>
    </div>
    <div class="styles">
        <div class="text-input">
            <label>
                Add style
                <input placeholder="e.g. reuters"/>
            </label>
            <button class="material-icons">
                add_circle
            </button>
        </div>
        <vc-chipset removable></vc-chipset>
    </div>
    <div class="options"></div>
</div>
`,
})
export class ImageSpecForm extends BaseElement {
    $root: HTMLElement;
    $h3: HTMLElement;
    $options: HTMLElement;
    $textInput: HTMLTextAreaElement;
    $textChips: Chipset;
    $styleInput: HTMLInputElement;
    $styleChips: Chipset;

    spec: ImageSpec;
    expanded = false;

    @Dispatch('spec.remove') onRemove: DispatchEmitter;

    @Toggle() video: boolean = false;
    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.image-spec-form');
        this.$h3 = this.$root.querySelector('h3');
        this.$options = this.$root.querySelector('.options');

        this.$textInput = this.$root.querySelector('.texts .text-input textarea');
        this.$textChips = this.$root.querySelector('.texts vc-chipset');
        this.$styleInput = this.$root.querySelector('.styles .text-input input');
        this.$styleChips = this.$root.querySelector('.styles vc-chipset');
    }

    public update(spec: ImageSpec) {
        this.spec = spec;
        this.draw();
    }

    protected draw() {
        if (!this.spec) {
            return;
        }
        this.$h3.innerText = this.video ? 'Step' : 'Image';
        this.$textChips.update(this.spec.texts);
        this.$styleChips.update(this.spec.styles);

        this.$options.innerHTML = '';
        for (const field of DetailsHelper.getFields(this.video)) {
            const option = this.el('vc-image-spec-option', {
                attr: {
                    label: field.label,
                    type: field.type,
                    value: (this.spec as any)[field.field] || field.default,
                },
            }) as ImageSpecOption;
            option.addEventListener('change.value', (e: any) => {
                this.onOptionChange(field.field, e.detail);
            });
            this.$options.appendChild(option);
        }
    }

    protected onOptionChange(field: string, value: boolean|number) {
        const spec = (this.spec as any);
        spec[field] = value;
        this.draw();
    }

    @Listen('click', '.spec-header button')
    protected onRemoveClicked(e: any) {
        this.onRemove.emit();
    }

    @Listen('keydown', '.texts textarea')
    protected onTextsKeydown(e: KeyboardEvent) {
        if (e.key === 'Enter') {
            e.preventDefault();
            this.addText()
        }
    }

    @Listen('blur', '.texts textarea')
    protected onTextsBlur(e: FocusEvent) {
        const target = e.target as HTMLTextAreaElement;
        if (target.value) {
            e.preventDefault();
            this.addText()
        }
    }

    @Listen('keydown', '.styles input')
    protected onStylesKeydown(e: KeyboardEvent) {
        if (e.key === 'Enter') {
            e.preventDefault();
            this.addStyle()
        }
    }

    @Listen('blur', '.styles input')
    protected onStylesBlur(e: FocusEvent) {
        const target = e.target as HTMLInputElement;
        if (target.value) {
            e.preventDefault();
            this.addStyle()
        }
    }

    @Listen('click', '.texts .text-input button')
    protected onTextsClick(e: MouseEvent) {
        e.preventDefault();
        this.addText();
    }

    @Listen('click', '.styles .text-input button')
    protected onStylesClick(e: MouseEvent) {
        e.preventDefault();
        this.addStyle();
    }

    @Listen('chipset.remove', '.styles vc-chipset')
    protected onStylesRemove(e: any) {
        this.spec.styles.splice(this.spec.styles.indexOf(e.detail), 1);
        this.draw();
    }

    @Listen('chipset.remove', '.texts vc-chipset')
    protected onTextsRemove(e: any) {
        this.spec.texts.splice(this.spec.texts.indexOf(e.detail), 1);
        this.draw();
    }

    protected addText() {
        const value = this.$textInput.value.trim();
        if (value) {
            this.spec.texts.push(value);
            this.$textInput.value = '';
            this.draw();
        }
    }

    protected addStyle() {
        const value = this.$styleInput.value.trim();
        if (value) {
            this.spec.styles.push(value);
            this.$styleInput.value = '';
            this.draw();
        }
    }
}

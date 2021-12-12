import {CustomElement, Listen} from 'custom-elements-ts';
import {Chipset} from "../chipset";
import {ImageSpec} from "../../models/image-spec";

@CustomElement({
    tag: 'vc-image-spec-form',
    shadow: false,
    style: ``,
    template: `
<div class="image-spec-form">
    <div class="texts">
        <div class="text-input">
            <h3>Add text</h3>
            <textarea placeholder="e.g. A medieval cathedral interior"></textarea>
            <button class="material-icons">
                add_circle
            </button>
        </div>
        <vc-chipset removable></vc-chipset>
    </div>
    <div class="styles">
        <div class="text-input">
            <h3>Add style</h3>
            <input placeholder="e.g. reuters"/>
            <button class="material-icons">
                add_circle
            </button>
        </div>
        <vc-chipset removable></vc-chipset>
    </div>
</div>
`,
})
export class ImageSpecForm extends HTMLElement {
    $root: HTMLElement
    $textInput: HTMLTextAreaElement
    $textChips: Chipset
    $styleInput: HTMLInputElement
    $styleChips: Chipset

    spec: ImageSpec;
    expanded = false;

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.image-spec-form');

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

        this.$textChips.update(this.spec.texts);
        this.$styleChips.update(this.spec.styles);
    }

    @Listen('keyup', '.texts textarea')
    protected onTextsKeyup(e: KeyboardEvent) {
        if (e.key === 'Enter') {
            e.preventDefault();
            this.addText()
        }
    }

    @Listen('keyup', '.styles input')
    protected onStylesKeyup(e: KeyboardEvent) {
        if (e.key === 'Enter') {
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

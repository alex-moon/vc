import {CustomElement, Listen} from 'custom-elements-ts';
import {Vc} from "../vc";
import {ImageSpec} from "../models/image-spec";
import {Chipset} from "./chipset";
import {VcRemoveEvent} from "./chip";

@CustomElement({
    tag: 'vc-generation-request-form',
    shadow: false,
    style: ``,
    template: `
<div class="request-form">
    <h2>
        Create virtual content
        <span class="material-icons">expand_more</span>
    </h2>
    <form>
        <div class="texts">
            <div class="text-input">
                <h3>Text</h3>
                <textarea placeholder="Primary prompt"></textarea>
                <button class="material-icons">
                    add_circle
                </button>
            </div>
            <vc-chipset removable></vc-chipset>
        </div>
        <div class="styles">
            <div class="text-input">
                <h3>Styles</h3>
                <input placeholder="Secondary prompt"/>
                <button class="material-icons">
                    add_circle
                </button>
            </div>
            <vc-chipset removable></vc-chipset>
        </div>
        <div class="actions">
            <button type="submit">Save</button>
        </div>
    </form>
</div>
`
})
export class GenerationRequestForm extends HTMLElement {
    $root: HTMLElement
    $header: HTMLElement
    $form: HTMLElement
    $textInput: HTMLTextAreaElement
    $textChips: Chipset
    $styleInput: HTMLInputElement
    $styleChips: Chipset

    vc: Vc;
    spec: ImageSpec;
    expanded = false;

    constructor() {
        super();
    }

    connect(vc: Vc) {
        this.vc = vc;
    }

    connectedCallback() {
        this.$root = this.querySelector('.request-form');

        this.$header = this.$root.querySelector('h2');
        this.$header.addEventListener('click', (e) => {
            if (this.expanded) {
                this.$form.classList.remove('expanded');
                this.$header.querySelector('span').innerHTML = 'expand_more';
                this.expanded = false;
            } else {
                this.$form.classList.add('expanded');
                this.$header.querySelector('span').innerHTML = 'expand_less';
                this.expanded = true;
            }
        });

        this.$form = this.$root.querySelector('form');
        this.$textInput = this.$form.querySelector('.texts .text-input textarea');
        this.$textChips = this.$form.querySelector('.texts vc-chipset');
        this.$styleInput = this.$form.querySelector('.styles .text-input input');
        this.$styleChips = this.$form.querySelector('.styles vc-chipset');
        this.spec = new ImageSpec();
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

    @Listen('click', '.actions button')
    protected submit(e: MouseEvent) {
        e.preventDefault();
        this.vc.create(this.spec);
        this.spec = new ImageSpec();
        this.draw();
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
    protected onStylesRemove(e: VcRemoveEvent) {
        this.spec.styles.splice(this.spec.styles.indexOf(e.text), 1);
        this.draw();
    }

    @Listen('chipset.remove', '.texts vc-chipset')
    protected onTextsRemove(e: VcRemoveEvent) {
        this.spec.texts.splice(this.spec.texts.indexOf(e.text), 1);
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

import {CustomElement, Toggle, Listen, Dispatch, DispatchEmitter, addEventListeners} from 'custom-elements-ts';
import {VcRemoveEvent} from "./chip";

@CustomElement({
    tag: 'vc-chipset',
    shadow: false,
    style: `
    .chipset {
        display: flex;
        justify-content: flex-start;
    }
`,
    template: `
<div class="chipset"></div>
`
})
export class Chipset extends HTMLElement {
    texts: string[];

    $root: HTMLElement;

    @Toggle() removable: boolean;
    @Dispatch('chipset.remove') onRemove: DispatchEmitter;

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.chipset');
    }

    update(texts: string[]) {
        this.$root.innerHTML = '';

        this.texts = texts;

        for (const text of this.texts) {
            const chip = document.createElement('vc-chip');
            chip.setAttribute('text', text);
            if (this.removable) {
                chip.setAttribute('removable', '');
                chip.addEventListener('chip.remove', this.onChipRemove.bind(this));
            }
            this.$root.appendChild(chip);
        }
    }

    protected onChipRemove(e: VcRemoveEvent) {
        this.onRemove.emit(e);
    }
}

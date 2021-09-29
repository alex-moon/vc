import {CustomElement, Dispatch, DispatchEmitter, Toggle} from 'custom-elements-ts';

@CustomElement({
    tag: 'vc-chipset',
    shadow: false,
    style: ``,
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

        if (this.texts) {
            this.populateChips();
        }
    }

    update(texts: string[]) {
        this.texts = texts || [];

        if (this.$root) {
            this.populateChips();
        }
    }

    populateChips() {
        this.$root.innerHTML = '';

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

    protected onChipRemove(e: Event) {
        this.onRemove.emit(e);
    }
}

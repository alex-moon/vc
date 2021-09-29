import {CustomElement, Dispatch, DispatchEmitter, Listen, Prop, Toggle, Watch} from 'custom-elements-ts';

@CustomElement({
    tag: 'vc-chip',
    shadow: false,
    style: ``,
    template: `
<div class="chip"></div>
`
})
export class Chip extends HTMLElement {
    $root: HTMLElement;

    @Prop() text: string;
    @Toggle() removable: boolean;
    @Dispatch('chip.remove') onRemove: DispatchEmitter;

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.chip');
    }

    @Watch('text')
    protected update() {
        this.$root.innerHTML = this.text;
        if (this.removable) {
            const remove = document.createElement('button');
            remove.classList.add('remove');
            remove.classList.add('material-icons');
            remove.innerHTML = 'highlight_off';
            remove.addEventListener('click', this.onRemoveClick.bind(this));
            this.$root.appendChild(remove);
        }
    }

    @Listen('click', '.remove')
    protected onRemoveClick(e: MouseEvent) {
        e.preventDefault();
        this.onRemove.emit({detail: this.text})
    }
}

import {
    CustomElement,
    CustomEventOptions,
    Dispatch,
    DispatchEmitter,
    Listen,
    Prop,
    Toggle,
    Watch
} from 'custom-elements-ts';

export interface VcRemoveEvent extends CustomEventOptions, Event {
    text ?: string;
    bubbles: boolean;
    composed: boolean;
}

@CustomElement({
    tag: 'vc-chip',
    shadow: false,
    style: `
    .chip {
        font-family: sans-serif;  
        background-color: #535c69;
        color: #f9f8ef;
        border-radius: 8px;
        padding: 8px;
        opacity: 0.8;
        width: auto;
        margin-right: 8px;
        display: flex;
        align-items: center;
    }
    .remove {
    margin-left: 4px;
        color: #f9f8ef !important;
    }
`,
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
        this.onRemove.emit({text: this.text} as VcRemoveEvent)
    }
}

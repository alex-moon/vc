import {CustomElement, Listen} from 'custom-elements-ts';
@CustomElement({
    tag: 'vc-add-step',
    shadow: false,
    style: ``,
    template: `
<div class="add-step">
</div>
`,
})
export class GenerationRequestForm extends HTMLElement {
    $root: HTMLElement

    constructor() {
        super();
    }

    connectedCallback() {

    }
}

import {CustomElement, Listen} from 'custom-elements-ts';
import {GenerationRequest as Model} from "../models/generation-request";
import {GenerationRequestSummary} from "./generation-request/summary";
import {GenerationRequestDetails} from "./generation-request/details";

@CustomElement({
    tag: 'vc-generation-request',
    shadow: false,
    style: ``,
    template: `
<div class="request">
    <vc-generation-request-summary></vc-generation-request-summary>
    <vc-generation-request-details></vc-generation-request-details>
</div>
`
})
export class GenerationRequest extends HTMLElement {
    $root: HTMLElement
    $summary: GenerationRequestSummary
    $details: GenerationRequestDetails

    request: Model
    expanded = false

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.request');
        this.$summary = this.$root.querySelector('vc-generation-request-summary');
        this.$details = this.$root.querySelector('vc-generation-request-details');
    }

    update(request: Model) {
        this.request = request;
        this.$summary.update(this.request);
    }

    @Listen('summary.expand', 'vc-generation-request-summary')
    protected onExpand(e: any) {
        this.$details.update(this.request);
        this.$details.setAttribute('expanded', e.detail);
    }
}

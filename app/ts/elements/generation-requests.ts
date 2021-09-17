import {CustomElement} from 'custom-elements-ts';
import {GenerationRequest as Model} from "../models/generation-request";
import {GenerationRequest} from "./generation-request";
import {Vc} from "../vc";

@CustomElement({
  tag: 'generation-requests',
  shadow: false,
  style: ``,
  // @todo figure out how to make templateUrl work
  template: `
<div class="requests"></div>
`
})
export class GenerationRequests extends HTMLElement {
    $root: HTMLElement;

    _requests: Model[]

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.requests');
    }

    update(requests: any) {
        this._requests = requests;

        this.$root.innerHTML = '';
        this._requests.forEach((request: Model) => {
            const $request = document.createElement('generation-request') as GenerationRequest;
            this.$root.appendChild($request);
            $request.update(request);
        });
    }
}

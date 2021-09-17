import {CustomElement} from 'custom-elements-ts';
import {GenerationRequest as Model} from "../../models/generation-request";
import {GenerationRequest} from "../generation-request/generation-request";
import {Vc} from "../../vc";

@CustomElement({
  tag: 'generation-requests',
  templateUrl: 'generation-requests.html',
  styleUrl: 'generation-requests.scss'
})
export class GenerationRequests extends HTMLElement {
    $root: HTMLElement;

    vc: Vc;
    _requests: Model[]

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.shadowRoot.querySelector('.requests');
        this.vc = (global as any).vc;
        this.vc.connect(this);
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

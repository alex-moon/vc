import {CustomElement} from 'custom-elements-ts';

@CustomElement({
  tag: 'generation-requests',
  templateUrl: 'generation-requests.html',
  styleUrl: 'generation-requests.scss'
})
export class GenerationRequests extends HTMLElement {
    $root
    _requests
    $request

    constructor() {
        super();
    }

    connectedCallback() {
        this.appendChild(template.content.cloneNode(true));
        this.$root = this.querySelector('.requests');
    }

    update(requests) {
        this._requests = requests;

        this.$root.innerHTML = '';
        this._requests.forEach((request, index) => {
            const $request = document.createElement('generation-request');
            this.$root.appendChild($request);
            ($request as any).update(request);
        });
    }
}

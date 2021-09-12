class GenerationRequestElement extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    const shadowRoot = this.attachShadow({ mode: 'closed' });
    shadowRoot.appendChild(document.getElementById('generation-request').content);
  }
}

customElements.define('generation-request', GenerationRequestElement);

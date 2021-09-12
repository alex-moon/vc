class Request extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    const shadowRoot = this.attachShadow({ mode: 'closed' });
    shadowRoot.appendChild(document.getElementById('request').content);
  }
}

customElements.define('request', Request);

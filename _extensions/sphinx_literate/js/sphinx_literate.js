
const litRefStyle = `
a:hover {
	color: var(--color-link--hover);
	-webkit-text-decoration-color: var(--color-link-underline--hover);
	text-decoration-color: var(--color-link-underline--hover);
}
a {
	color: var(--color-link);
	text-decoration: underline;
	text-decoration-color: currentcolor;
	-webkit-text-decoration-color: var(--color-link-underline);
	text-decoration-color: var(--color-link-underline);
}
a {
	background-color: transparent;
}
`;

class LitRef extends HTMLSpanElement {
	constructor() {
		super();
	}

	connectedCallback() {
		const shadow = this.attachShadow({ mode: "open" });

		const open = document.createTextNode("{{\u00a0");

		const close = document.createTextNode("\u00a0}}");

		const link = document.createElement("a");
		link.textContent = this.getAttribute("name");
		link.href = this.getAttribute("href");

		const style = document.createElement("style");
		style.textContent = litRefStyle;

		shadow.append(style, open, link, close);
	}
}

class LitBlockInfo extends HTMLDivElement {
	constructor() {
		super();
	}

	connectedCallback() {
		const shadow = this.attachShadow({ mode: "open" });

		const open = document.createTextNode("{{\u00a0");

		const close = document.createTextNode("\u00a0}}");

		const link = document.createElement("a");
		link.textContent = this.getAttribute("name");
		link.href = this.getAttribute("permalink");

		const style = document.createElement("style");
		style.textContent = litRefStyle;

		shadow.append(style, open, link, close);
	}
}


customElements.define("lit-ref", LitRef, { extends: "span" });

customElements.define("lit-block-info", LitBlockInfo, { extends: "div" });


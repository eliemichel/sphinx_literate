// NB: This style has been designed for the Furo theme.

const config = {
	//begin_ref: "{{\u00a0",
	//end_ref: "\u00a0}}",
	begin_ref: "{{",
	end_ref: "}}",
};

const commonStyle = `
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

const litRefStyle = `
`;

const litBlockInfoStyle = `
.wrapper {
	text-align: right;
	font-size: 0.8em;
	position: absolute;
	bottom: -0.7em;
	right: 0.5em;
	margin-top: 0;
	color: rgba(0, 0, 0, 0.39);
	background-color: #3e3d35;
	border-radius: 0.3em;
	padding: 0 0.3em;
}

.wrapper a.lit-name {
	color: rgba(0, 0, 0, 0.94);
}
`;

class LitRef extends HTMLSpanElement {
	constructor() {
		super();
	}

	connectedCallback() {
		const shadow = this.attachShadow({ mode: "open" });

		const open = document.createTextNode(config.begin_ref);

		const close = document.createTextNode(config.end_ref);

		const link = document.createElement("a");
		link.textContent = this.getAttribute("name");
		link.href = this.getAttribute("href");

		const style = document.createElement("style");
		style.textContent = commonStyle + litRefStyle;

		shadow.append(style, open, link, close);
	}
}

customElements.define("lit-ref", LitRef, { extends: "span" });

class LitBlockInfo extends HTMLDivElement {
	constructor() {
		super();
	}

	connectedCallback() {
		const data = JSON.parse(this.getAttribute("data"));
		const shadow = this.attachShadow({ mode: "open" });

		console.log(data);

		const wrapper = document.createElement("div");
		wrapper.setAttribute("class", "wrapper");

		wrapper.append(...this.createLitLink(data.name, data.permalink, "lit-name"));

		const details = ['replaced by', 'completed in', 'completing', 'replacing', 'referenced in'];
		details.map(section => {
			if (data[section].length > 0) {
				wrapper.append(document.createTextNode(" " + section + " "));
				data[section].map(lit => {
					wrapper.append(...this.createLitLink(lit.name, lit.url));
				});
			}
		});

		const style = document.createElement("style");
		style.textContent = commonStyle + litBlockInfoStyle;

		shadow.append(style, wrapper);
	}

	createLitLink(name, url, className) {
		const open = document.createTextNode(config.begin_ref);

		const close = document.createTextNode(config.end_ref);

		const link = document.createElement("a");
		link.textContent = name;
		link.href = url;
		if (className !== undefined) {
			link.setAttribute("class", className);
		}

		return [open, link, close];
	}
}

customElements.define("lit-block-info", LitBlockInfo, { extends: "div" });


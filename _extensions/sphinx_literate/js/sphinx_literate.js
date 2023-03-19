// NB: This style has been designed for the Furo theme.

const config = {
	//begin_ref: "{{\u00a0",
	//end_ref: "\u00a0}}",
	begin_ref: "{{",
	end_ref: "}}",
};

const lightStyleVariables = `
--color-background-lit-info: #d5eca8;
--color-foreground-lit-info: rgb(113, 138, 26);
`;

const darkStyleVariables = `
--color-background-lit-info: #3e3d35;
//--color-foreground-lit-info: rgba(0, 0, 0, 0.39);
--color-foreground-lit-info: rgb(142, 142, 142);
`;

// Reproduce Furo's light/dark theme mechanism
const styleVariables = `
body {
	${lightStyleVariables}
}

@media not print {
body[data-theme="dark"] {
	${darkStyleVariables}
}

@media (prefers-color-scheme: dark) {
body:not([data-theme="light"]) {
	${darkStyleVariables}
}
}
}
`;

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
	color: var(--color-foreground-lit-info);
	background-color: var(--color-background-lit-info);
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

		const wrapper = document.createElement("div");
		wrapper.setAttribute("class", "wrapper");
		wrapper.setAttribute("data-theme", "dark");

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

// Inject in Furo theme
function onDOMContentLoaded() {
	console.log("onDOMContentLoaded");
	const style = document.createElement("style");
	style.textContent = styleVariables;
	document.head.append(style);

	const x = document.querySelectorAll(".content-icon-container");
	console.log(x);
}
document.addEventListener('DOMContentLoaded', onDOMContentLoaded, {once: true});
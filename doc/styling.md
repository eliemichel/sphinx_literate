Styling
=======

The HTML inserted by this extension is wrapped into custom HTML element, for which you can define a custom definition. A default behavior is defined in `js/sphinx_literate.js`. To create a custom one, copy this file, edit it and disable the original one by turning the `lit_use_default_style` option to `False`.

**NB:** The default style has been designed for the Furo theme.

For instance, a reference to another block looks likt this:

```HTML
<lit-ref name="Block title" href="#lit-12">
	<!-- [...] Fallback standard HTML -->
</lit-ref>
```

The customization JavaScript code for this looks like this:

```JavaScript
// Style block references to look like <<Some other block>>
class LitRef extends HTMLElement {
	connectedCallback() {
		const shadow = this.attachShadow({ mode: "open" });

		const link = document.createElement("a");
		link.textContent = "<<" + this.getAttribute("name") + ">>";
		link.href = this.getAttribute("href");

		shadow.append(link);
	}
}

customElements.define("lit-ref", LitRef);
```

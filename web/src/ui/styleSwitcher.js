import { STYLES } from "../styles/styles.js";

/**
 * Wires the #style-switcher DOM buttons (index.html) to `styleManager`.
 * One button per STYLES entry, in registry order.
 */
export function mountStyleSwitcher(container, styleManager) {
  const buttons = new Map();

  for (const [name, style] of Object.entries(STYLES)) {
    const button = document.createElement("button");
    button.textContent = style.label;
    button.setAttribute("aria-pressed", String(name === styleManager.getCurrentStyle()));
    button.addEventListener("click", () => {
      styleManager.applyStyle(name);
      for (const [otherName, otherButton] of buttons) {
        otherButton.setAttribute("aria-pressed", String(otherName === name));
      }
    });
    buttons.set(name, button);
    container.appendChild(button);
  }
}

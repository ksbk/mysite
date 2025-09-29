import "./style.css";
import { mountHello } from "./components/Hello";

function boot() {
  // Auto-mount components by data attributes, e.g. <div data-component="Hello" data-name="Alice"></div>
  document.querySelectorAll<HTMLElement>("[data-component]").forEach((el) => {
    const name = el.dataset.component;
    switch (name) {
      case "Hello":
        mountHello(el, el.dataset.name);
        break;
      // add more components here
      default:
        break;
    }
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", boot);
} else {
  boot();
}

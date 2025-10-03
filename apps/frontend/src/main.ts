import "./style.css";
import { mountHello } from "./components/Hello";
import { mountContactForm } from "./components/ContactForm";

function boot() {
  // Auto-mount components by data attributes, e.g. <div data-component="Hello" data-name="Alice"></div>
  const elements = document.querySelectorAll<HTMLElement>("[data-component]");
  console.log(`Found ${elements.length} components to mount`);

  elements.forEach((el) => {
    const name = el.dataset.component;
    console.log(`Mounting component: ${name} with data:`, el.dataset);

    switch (name) {
      case "Hello":
        mountHello(el, el.dataset.name);
        console.log(`Hello component mounted with name: ${el.dataset.name}`);
        break;
      case "ContactForm":
        mountContactForm(el);
        console.log(`ContactForm component mounted`);
        break;
      // add more components here
      default:
        console.log(`Unknown component: ${name}`);
        break;
    }
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", boot);
} else {
  boot();
}

// Also ensure at least one Hello component is visible as fallback
setTimeout(() => {
  const helloElement = document.querySelector('[data-component="Hello"]');
  if (helloElement && !helloElement.innerHTML.trim()) {
    console.log("Fallback: Mounting Hello component directly");
    mountHello(
      helloElement as HTMLElement,
      (helloElement as HTMLElement).dataset.name,
    );
  }
}, 100);

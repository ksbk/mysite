export function mountHello(el: HTMLElement, name = "World") {
    el.innerHTML = `👋 Hello, ${name}!`;
}

import hljs from "highlight.js";
import * as bootstrap from "bootstrap";
import initTabSwitches from "../components/code-switch";

hljs.highlightAll();

if (document.readyState !== "loading") {
  createToc();
}
document.addEventListener("DOMContentLoaded", function () {
  createToc();
});

function createToc() {
  const tocContainer = document.getElementById("toc");
  if (!tocContainer) return;

  const headings = document.querySelectorAll("main h2, main h3");

  const nav = document.createElement("nav");
  nav.className = "nav nav-pills flex-column small";
  nav.id = "tocNav";

  headings.forEach((h) => {
    if (!h.id) {
      h.id = h.textContent
        .trim()
        .toLowerCase()
        .replace(/[^a-zA-Z ]/g, "");
    }
    const link = document.createElement("a");
    link.className = "nav-link ps-" + (h.tagName === "H3" ? "4" : "2");
    link.href = "#" + h.id;
    link.textContent = h.textContent;
    nav.appendChild(link);
  });

  tocContainer.appendChild(nav);

  // Re-initialize scrollspy after injecting nav
  bootstrap.ScrollSpy.getInstance(document.body)?.refresh() ||
    new bootstrap.ScrollSpy(document.body, { target: "#tocNav", offset: 80 });
}

initTabSwitches();

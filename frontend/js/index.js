import "./main.js";
import "../scss/main.scss";

// Look for <body data-page="...">
const page = document.body.dataset.page;

async function loadPage(page) {
  switch (page) {
    case "login":
      await import("./pages/login.js");
      break;
    case "register":
      await import("./pages/register.js");
      break;
    case "dashboard":
      await import("./pages/dashboard/index.js");
      break;
    case "docs":
      await import("./pages/docs.js");
      break;
    default:
      break; // no page-specific JS
  }
}

loadPage(page);

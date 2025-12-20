if (document.readyState !== "loading") {
  verify();
} else {
  document.addEventListener("DOMContentLoaded", verify());
}

async function verify() {
  try {
    const code = new URLSearchParams(document.location.search).get("code");

    if (code === null) {
      window.location.href = "/register";
    }

    const url =
      "/auth/v1/verify?" + new URLSearchParams({ code: code }).toString();
    const response = await fetch(url);

    if (!response.ok) {
      showError("Error: " + (await response.json()["detail"]));
    }

    window.location.href = "/login";
  } catch (e) {
    showError("Error: See console");
    console.error("Verification Error " + e);
  }
}

function showError(message) {
  const alertPlaceholder = document.getElementById("errorPlaceholder");

  const wrapper = document.createElement("div");
  wrapper.innerHTML = [
    '<div class="alert alert-danger alert-dismissible" role="alert">',
    `   <div class="small">${message}</div>`,
    '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
    "</div>",
  ].join("");

  alertPlaceholder.append(wrapper);
}

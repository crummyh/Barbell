document
  .getElementById("loginForm")
  .addEventListener("submit", async function (e) {
    e.preventDefault();

    const username = document.getElementById("emailInput").value;
    const password = document.getElementById("pwInput").value;

    try {
      const response = await fetch("auth/v1/token", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          username,
          password,
        }),
        credentials: "include",
      });

      const data = await response.json();

      if (!response.ok) {
        const errorMessage = data?.detail || "An error occurred";
        showError("Login failed: " + errorMessage);
        return;
      }

      window.location.href = "/dashboard";
    } catch (err) {
      console.error("Login error:", err);
      showError("Login failed. See console for details.");
    }
  });

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

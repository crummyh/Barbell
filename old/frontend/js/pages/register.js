const loginForm = document.getElementById("registerForm");
if (loginForm) {
  loginForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = document.getElementById("emailInput").value;
    const username = document.getElementById("usernameInput").value;
    const password = document.getElementById("pwInput").value;

    try {
      const response = await fetch("auth/v1/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: username,
          email: email,
          password: password,
        }),
      });

      if (!response.ok) {
        let data = await response.json();

        const errorMessage = data?.detail || "An error occurred";
        showError("Registration failed: " + errorMessage);
        return;
      }

      showEmailMsg();
    } catch (err) {
      console.error("Registration error:", err);
      showError("Registration failed. See console for details.");
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
}

function showEmailMsg() {
  const registerContainer = document.getElementById("registerContainer");
  if (registerContainer === null) {
    return;
  }
  registerContainer.innerHTML = `
    <a href="/">
        <img
            src="/static/images/logo.svg"
            alt=""
            width="64px"
            class="mb-3 d-block mx-auto"
    /></a>
    <h3 class="text-center">Account Created!</h3>
    <p class="text-center">Check your email for a verification link</p>
    `;
}

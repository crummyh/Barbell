document
  .getElementById("logoutLink")
  .addEventListener("click", async function (e) {
    e.preventDefault();
    try {
      await fetch("/auth/v1/logout", {
        method: "GET",
        credentials: "include",
      });
      window.location.href = "/login";
    } catch (err) {
      console.error("Logout failed", err);
    }
  });

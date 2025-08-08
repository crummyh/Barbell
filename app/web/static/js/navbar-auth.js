const accountHolderDiv = document.getElementById("accountHolder");

async function getCurrentUser() {
  const token = localStorage.getItem("access_token");
  const response = await fetch("/auth/v1/users/me", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (response.status === 401) {
    return null;
  }

  return await response.json();
}

async function navbarLogic() {
  if (accountHolderDiv) {
    const userData = await getCurrentUser();
    if (userData !== null) {
      accountHolderDiv.classList += " dropdown";
      accountHolderDiv.innerHTML = [
        '<button class="btn btn-link nav-link dropdown-toggle d-flex align-items-center py-2 px-2" type="button" aria-expanded="false" data-bs-toggle="dropdown" data-bs-display="static">',
        '<iconify-icon icon="bi:person-circle" width="16" height="16"></iconify-icon>',
        "</button>",
        '<span class="d-lg-none ms-2">Account</span>',
        '<ul class="dropdown-menu">',
        '<li><a href="account" class="dropdown-item">My Account</a></li>',
        '<li><a href="#" class="dropdown-item" id="logoutLink">Logout</a></li>',
        "</ul>",
      ].join("");
      const logout = document.getElementById("logoutLink");
      logout.addEventListener("click", (event) => {
        localStorage.removeItem("access_token");
        window.location.href = "/";
      });
    }
  }
}
navbarLogic();

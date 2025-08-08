async function getUser() {
  const token = localStorage.getItem("access_token");
  const response = await fetch("/auth/v1/users/me", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (response.status === 401) {
    window.location.href = "/login";
  }

  return await response.json();
}

getUser();

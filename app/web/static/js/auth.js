async function exampleFetchProtectedResource() {
  const token = localStorage.getItem("access_token");
  const response = await fetch("https://yourapi.com/protected-endpoint", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (response.status === 401) {
    throw new Error("Not authorized");
  }

  return await response.json();
}

function logout() {
  localStorage.removeItem("access_token");
}

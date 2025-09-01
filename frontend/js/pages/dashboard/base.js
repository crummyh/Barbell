import { getRandomInt } from "../../utils/numbers";
import { Toast } from "bootstrap";

export async function showToast(
  icon = false,
  title = false,
  isError = false,
  body,
  id,
) {
  const dashboardToastContainer = document.getElementById(
    "dashboardToastContainer",
  );

  if (dashboardToastContainer) {
    let toastHtml = `
      <div id="${id}" class="${isError ? "bg-danger-subtle border border-danger border-2 " : ""}toast" role="alert" aria-live="assertive" aria-atomic="true">
      `;

    if (icon || title) {
      toastHtml += `
        <div class="toast-header bg-danger-subtle">
      `;
    }

    if (icon) {
      toastHtml += `
        <iconify-icon icon="${icon}" width="16" height="16" class="me-2 no-padding"></iconify-icon>
      `;
    }

    if (title) {
      toastHtml += `
        <strong class="me-auto">${title}</strong>
      `;
    }

    if (icon || title) {
      toastHtml += `
        <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
      `;
    }

    toastHtml += `
      <div class="toast-body">
      ${body}
      </div>
    `;

    if (!icon && !title) {
      toastHtml += `
        <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      `;
    }

    toastHtml += `
      </div>
    `;

    dashboardToastContainer.innerHTML += toastHtml;
    const toastBootstrap = Toast.getOrCreateInstance(
      document.getElementById(id),
    );
    toastBootstrap.show();
  }
}

/**
 * Call a backend endpoint with error handling
 * @param {string} url - The URL to call
 * @param {object} options - The options to pass to fetch
 * @param {object} errorResponses - Markup to be displayed for status codes
 */
export async function callBackend(url, options, errorResponses = {}) {
  options.credentials = "include";

  const response = await fetch(url, options);

  if (response.status === 401) {
    window.location.replace("/login");
  } else if (response.status !== 200) {
    const message = errorResponses.hasOwnProperty(response.status)
      ? errorResponses[response.status]
      : {
          title: "An error occurred",
          body: 'Try again later, or <a href="https://github.com/crummyh/Barbell/issues">submit and issue</a>',
        };

    showToast(
      "bi:exclamation-triangle-fill",
      message.title,
      true,
      message.body,
      `${url}-${options.method}-${response.status}-error-${getRandomInt(0, 100)}`,
    );
  } else {
    try {
      return response;
    } catch (err) {
      showToast(
        "bi:exclamation-triangle-fill",
        "An error occurred",
        true,
        'Try again later, or <a href="https://github.com/crummyh/Barbell/issues">submit and issue</a>',
        `${url}-${method}-${response.status}-error-${getRandomInt(0, 100)}`,
      );
      throw err;
    }
  }
}

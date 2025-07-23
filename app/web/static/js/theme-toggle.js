/*!
 * Color mode toggler for Bootstrap's docs (https://getbootstrap.com/)
 * Copyright 2011-2025 The Bootstrap Authors
 * Licensed under the Creative Commons Attribution 3.0 Unported License.
 *
 * Modified by Elijah Crum
 */

(() => {
  "use strict";

  const getStoredTheme = () => localStorage.getItem("theme");
  const setStoredTheme = (theme) => localStorage.setItem("theme", theme);

  const getPreferredTheme = () => {
    const storedTheme = getStoredTheme();
    if (storedTheme) {
      return storedTheme;
    }

    return window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  };

  const setTheme = (theme) => {
    if (theme === "auto") {
      document.documentElement.setAttribute(
        "data-bs-theme",
        window.matchMedia("(prefers-color-scheme: dark)").matches
          ? "dark"
          : "light",
      );
    } else {
      document.documentElement.setAttribute("data-bs-theme", theme);
    }
  };

  const getOppositeTheme = (theme) => {
    if (theme === "dark") {
      return "light";
    }
    if (theme === "light") {
      return "dark";
    } else {
      theme = getPreferredTheme();
      if (theme === "dark") {
        return "light";
      }
      if (theme === "light") {
        return "dark";
      }
    }
  };

  setTheme(getPreferredTheme());

  window
    .matchMedia("(prefers-color-scheme: dark)")
    .addEventListener("change", () => {
      const storedTheme = getStoredTheme();
      if (storedTheme !== "light" && storedTheme !== "dark") {
        setTheme(getPreferredTheme());
      }
    });

  window.addEventListener("DOMContentLoaded", () => {
    const toggle = document.getElementById("bd-theme");
    if (getPreferredTheme() === "dark") {
      toggle.classList.add("theme-toggle--toggled");
    }
    toggle.addEventListener("click", () => {
      const theme = getOppositeTheme(
        toggle.getAttribute("data-bs-theme-value"),
      );
      toggle.classList.toggle("theme-toggle--toggled");
      setStoredTheme(theme);
      setTheme(theme);
    });
  });
})();

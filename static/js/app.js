"use strict";

const mobileNavigationQuery = window.matchMedia("(max-width: 900px)");

function setNavigationOpen(isOpen, restoreFocus = false) {
  const appShell = document.querySelector(".app-shell");
  if (!appShell) return;

  const sidebar = appShell.querySelector(".app-sidebar");
  const backdrop = appShell.querySelector("[data-sidebar-close]");
  const toggleButton = appShell.querySelector("[data-sidebar-toggle]");
  const shouldOpen = isOpen && mobileNavigationQuery.matches;

  appShell.classList.toggle("sidebar-open", shouldOpen);
  if (sidebar) {
    sidebar.inert = mobileNavigationQuery.matches && !shouldOpen;
    if (mobileNavigationQuery.matches && !shouldOpen) {
      sidebar.setAttribute("aria-hidden", "true");
    } else {
      sidebar.removeAttribute("aria-hidden");
    }
  }
  if (backdrop) backdrop.hidden = !shouldOpen;
  if (toggleButton) {
    toggleButton.setAttribute("aria-expanded", String(shouldOpen));
    toggleButton.setAttribute("aria-label", shouldOpen ? "Close navigation menu" : "Open navigation menu");
  }
  if (shouldOpen) sidebar?.querySelector(".sidebar-link")?.focus();
  if (restoreFocus) toggleButton?.focus();
}

setNavigationOpen(false);
mobileNavigationQuery.addEventListener("change", () => setNavigationOpen(false));

document.addEventListener("click", (event) => {
  const dismissButton = event.target.closest("[data-dismiss-alert]");
  if (dismissButton) {
    dismissButton.closest(".message-alert")?.remove();
    return;
  }

  const toggleButton = event.target.closest("[data-sidebar-toggle]");
  const closeButton = event.target.closest("[data-sidebar-close]");
  const appShell = document.querySelector(".app-shell");
  if (!appShell) return;

  if (toggleButton) {
    setNavigationOpen(!appShell.classList.contains("sidebar-open"));
    return;
  }

  if (closeButton) {
    setNavigationOpen(false, true);
  }
});

document.addEventListener("change", (event) => {
  const input = event.target;
  if (!(input instanceof HTMLInputElement) || input.type !== "file") return;

  const field = input.closest(".form-field");
  const fileName = field?.querySelector("[data-file-name]");
  if (fileName) fileName.textContent = input.files?.[0]?.name || "No file selected";
});

document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") return;

  const appShell = document.querySelector(".app-shell.sidebar-open");
  if (!appShell) return;
  setNavigationOpen(false, true);
});

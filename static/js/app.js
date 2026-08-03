(() => {
  "use strict";

  const sidebar = document.querySelector("#sidebar");
  const sidebarToggle = document.querySelector("[data-sidebar-toggle]");
  sidebarToggle?.addEventListener("click", () => sidebar?.classList.toggle("is-open"));
  document.addEventListener("click", (event) => {
    if (!sidebar || !sidebar.classList.contains("is-open")) return;
    if (sidebar.contains(event.target) || sidebarToggle?.contains(event.target)) return;
    sidebar.classList.remove("is-open");
  });

  const dateNode = document.querySelector("[data-current-date]");
  if (dateNode) {
    dateNode.textContent = new Intl.DateTimeFormat("es-CR", {
      weekday: "long",
      day: "numeric",
      month: "long",
    }).format(new Date());
  }

  document.querySelectorAll("[data-password-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      const input = button.parentElement?.querySelector("input");
      if (!input) return;
      const show = input.type === "password";
      input.type = show ? "text" : "password";
      button.textContent = show ? "Ocultar" : "Ver";
      button.setAttribute("aria-label", show ? "Ocultar contraseña" : "Mostrar contraseña");
    });
  });

  window.CoffeeTrace = {
    getCsrfToken() {
      const cookie = document.cookie
        .split(";")
        .map((item) => item.trim())
        .find((item) => item.startsWith("csrftoken="));
      return cookie ? decodeURIComponent(cookie.split("=")[1]) : "";
    },
    notify(title, message = "", type = "success") {
      const region = document.querySelector("[data-toast-region]");
      if (!region) return;
      const toast = document.createElement("div");
      toast.className = `toast ${type === "error" ? "is-error" : ""}`;
      const icon = document.createElement("span");
      icon.textContent = type === "error" ? "!" : "✓";
      const copy = document.createElement("div");
      const heading = document.createElement("strong");
      heading.textContent = title;
      const paragraph = document.createElement("p");
      paragraph.textContent = message;
      copy.append(heading, paragraph);
      toast.append(icon, copy);
      region.append(toast);
      window.setTimeout(() => toast.remove(), 4300);
    },
    async apiFetch(url, options = {}) {
      const headers = new Headers(options.headers || {});
      headers.set("Accept", "application/json");
      if (options.body && !(options.body instanceof FormData)) {
        headers.set("Content-Type", "application/json");
      }
      const method = (options.method || "GET").toUpperCase();
      if (!["GET", "HEAD", "OPTIONS"].includes(method)) {
        headers.set("X-CSRFToken", window.CoffeeTrace.getCsrfToken());
      }
      return fetch(url, { credentials: "same-origin", ...options, headers });
    },
  };
})();

/* SocialNest navigation and small progressive enhancements. */
(() => {
  "use strict";

  const nav = document.querySelector("#navmenu");
  const toggle = document.querySelector(".mobile-nav-toggle");
  const links = nav ? nav.querySelector("ul") : null;

  if (toggle && links) {
    toggle.addEventListener("click", () => {
      const isOpen = links.classList.toggle("navmenu-active");
      toggle.setAttribute("aria-expanded", String(isOpen));
      const icon = toggle.querySelector("i");
      if (icon) icon.className = isOpen ? "bi bi-x-lg" : "bi bi-list";
    });

    links.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        links.classList.remove("navmenu-active");
        toggle.setAttribute("aria-expanded", "false");
        const icon = toggle.querySelector("i");
        if (icon) icon.className = "bi bi-list";
      });
    });

    document.addEventListener("click", (event) => {
      if (!nav.contains(event.target)) {
        links.classList.remove("navmenu-active");
        toggle.setAttribute("aria-expanded", "false");
        const icon = toggle.querySelector("i");
        if (icon) icon.className = "bi bi-list";
      }
    });
  }
})();

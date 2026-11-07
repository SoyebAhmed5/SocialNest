/* SocialNest responsive navigation */
(() => {
  "use strict";

  const nav = document.querySelector("#navmenu.app-navmenu");
  if (!nav) return;

  const toggle = nav.querySelector(".mobile-nav-toggle");
  const menu = nav.querySelector(":scope > ul");
  if (!toggle || !menu) return;

  const isMobile = () => window.matchMedia("(max-width: 1199px)").matches;

  const closeMenu = () => {
    nav.classList.remove("is-open");
    menu.classList.remove("navmenu-active");
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Open navigation menu");
    const icon = toggle.querySelector("i");
    if (icon) icon.className = "bi bi-list";
  };

  const openMenu = () => {
    nav.classList.add("is-open");
    menu.classList.add("navmenu-active");
    toggle.setAttribute("aria-expanded", "true");
    toggle.setAttribute("aria-label", "Close navigation menu");
    const icon = toggle.querySelector("i");
    if (icon) icon.className = "bi bi-x-lg";
  };

  toggle.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
    if (nav.classList.contains("is-open")) closeMenu();
    else openMenu();
  });

  menu.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      if (isMobile()) closeMenu();
    });
  });

  menu.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", closeMenu);
  });

  document.addEventListener("click", (event) => {
    if (isMobile() && nav.classList.contains("is-open") && !nav.contains(event.target)) {
      closeMenu();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeMenu();
  });

  window.addEventListener("resize", () => {
    if (!isMobile()) closeMenu();
  });

  closeMenu();
})();

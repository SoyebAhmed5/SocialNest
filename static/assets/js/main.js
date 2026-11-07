/* SocialNest accessible responsive navigation */
(() => {
  "use strict";
  const nav = document.querySelector("#navmenu.app-navmenu");
  if (!nav) return;
  const toggle = nav.querySelector(".mobile-nav-toggle");
  const menu = nav.querySelector(":scope > ul");
  if (!toggle || !menu) return;

  const mobileQuery = window.matchMedia("(max-width: 1199px)");
  const icon = toggle.querySelector("i");

  const closeMenu = () => {
    nav.classList.remove("is-open");
    menu.classList.remove("navmenu-active");
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Open navigation menu");
    menu.setAttribute("aria-hidden", mobileQuery.matches ? "true" : "false");
    if (icon) icon.className = "bi bi-list";
  };

  const openMenu = () => {
    menu.scrollTop = 0;
    nav.classList.add("is-open");
    menu.classList.add("navmenu-active");
    toggle.setAttribute("aria-expanded", "true");
    toggle.setAttribute("aria-label", "Close navigation menu");
    menu.setAttribute("aria-hidden", "false");
    if (icon) icon.className = "bi bi-x-lg";
  };

  toggle.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
    nav.classList.contains("is-open") ? closeMenu() : openMenu();
  });

  menu.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => { if (mobileQuery.matches) closeMenu(); });
  });
  menu.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", closeMenu);
  });

  document.addEventListener("click", (event) => {
    if (mobileQuery.matches && nav.classList.contains("is-open") && !nav.contains(event.target)) closeMenu();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && nav.classList.contains("is-open")) {
      closeMenu();
      toggle.focus();
    }
  });

  const onBreakpointChange = () => {
    closeMenu();
    menu.setAttribute("aria-hidden", mobileQuery.matches ? "true" : "false");
  };
  if (mobileQuery.addEventListener) mobileQuery.addEventListener("change", onBreakpointChange);
  else mobileQuery.addListener(onBreakpointChange);

  closeMenu();
})();

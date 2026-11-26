// Mobile navigation toggle and keyboard/touch-friendly dropdowns. No dependencies.
(function () {
  "use strict";

  function setExpanded(button, target, expanded) {
    button.setAttribute("aria-expanded", String(expanded));
    target.classList.toggle("is-open", expanded);
  }

  // Main (hamburger) toggle
  var navToggle = document.querySelector(".nav-toggle");
  var nav = navToggle && document.getElementById(navToggle.getAttribute("aria-controls"));
  if (navToggle && nav) {
    navToggle.addEventListener("click", function () {
      setExpanded(navToggle, nav, navToggle.getAttribute("aria-expanded") !== "true");
    });
  }

  // Dropdown toggles
  var submenuToggles = document.querySelectorAll(".submenu-toggle");
  submenuToggles.forEach(function (button) {
    var submenu = document.getElementById(button.getAttribute("aria-controls"));
    if (!submenu) return;
    // Open the active section by default on mobile.
    if (button.parentElement.classList.contains("is-active") && window.matchMedia("(max-width: 47.99rem)").matches) {
      setExpanded(button, submenu, true);
    }
    button.addEventListener("click", function () {
      setExpanded(button, submenu, button.getAttribute("aria-expanded") !== "true");
    });
  });

  // Escape closes open dropdowns and the mobile menu.
  document.addEventListener("keydown", function (event) {
    if (event.key !== "Escape") return;
    submenuToggles.forEach(function (button) {
      var submenu = document.getElementById(button.getAttribute("aria-controls"));
      if (submenu && submenu.classList.contains("is-open")) {
        setExpanded(button, submenu, false);
        button.focus();
      }
    });
  });
})();

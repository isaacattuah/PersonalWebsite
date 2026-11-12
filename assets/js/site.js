/* isaacattuah.com v3. No dependencies.
   Theme: follows the system setting until the visitor picks one; the choice is kept in localStorage. */
(function () {
  var root = document.documentElement;
  var KEY = "theme";

  function stored() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }
  function effective() {
    return root.getAttribute("data-theme") ||
      (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  }
  function label(button) {
    var next = effective() === "dark" ? "light" : "dark";
    button.setAttribute("aria-label", "Switch to " + next + " theme");
    button.setAttribute("title", "Switch to " + next + " theme");
  }

  var saved = stored();
  if (saved === "dark" || saved === "light") root.setAttribute("data-theme", saved);

  document.addEventListener("DOMContentLoaded", function () {
    var button = document.querySelector("[data-theme-toggle]");
    if (button) {
      label(button);
      button.addEventListener("click", function () {
        var next = effective() === "dark" ? "light" : "dark";
        root.setAttribute("data-theme", next);
        try { localStorage.setItem(KEY, next); } catch (e) { /* private mode: keep the choice for this page only */ }
        label(button);
      });
    }
    // TL;DR view (home page only). Linkable as /#tldr.
    var viewToggle = document.querySelector("[data-view-toggle]");
    var full = document.querySelector('[data-view="full"]');
    var tldr = document.querySelector('[data-view="tldr"]');
    if (viewToggle && full && tldr) {
      var setView = function (short, updateHash) {
        full.hidden = short;
        tldr.hidden = !short;
        viewToggle.setAttribute("aria-pressed", String(short));
        viewToggle.textContent = short ? "Full page" : "TL;DR";
        if (updateHash) history.replaceState(null, "", short ? "#tldr" : location.pathname + location.search);
        if (short) window.scrollTo(0, 0);
      };
      viewToggle.hidden = false;
      viewToggle.addEventListener("click", function () { setView(tldr.hidden, true); });
      var back = document.querySelector("[data-view-full]");
      if (back) back.addEventListener("click", function () { setView(false, true); window.scrollTo(0, 0); });
      // A link to a section of the full page leaves the TL;DR view first.
      document.addEventListener("click", function (event) {
        var link = event.target.closest && event.target.closest('a[href^="#"]');
        if (!link || tldr.hidden) return;
        var target = document.getElementById(link.getAttribute("href").slice(1));
        if (target && full.contains(target)) setView(false, false);
      });
      window.addEventListener("hashchange", function () {
        if (location.hash === "#tldr") setView(true, false);
        else if (!tldr.hidden) {
          var target = document.getElementById(location.hash.slice(1));
          if (target && full.contains(target)) { setView(false, false); target.scrollIntoView(); }
        }
      });
      if (location.hash === "#tldr") setView(true, false);
    }

    var year = document.querySelector("[data-year]");
    if (year) year.textContent = new Date().getFullYear();
  });
})();

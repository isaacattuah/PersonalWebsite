/* Adds a small bar to each prototype for hopping between directions.
   Hidden when the page is shown inside the switcher's own preview frame. */
(function () {
  if (window.self !== window.top) return;
  var here = document.documentElement.getAttribute("data-demo");
  var items = [
    ["../", "All directions", ""],
    ["../../", "Flagship", "flagship"],
    ["../stack-blue/", "Stack in blue", "stack-blue"],
    ["../blueprint/", "Blueprint", "blueprint"],
    ["../strip/", "Strip", "strip"],
    ["../reading-room/", "Reading Room", "reading-room"]
  ];
  var bar = document.createElement("nav");
  bar.setAttribute("aria-label", "Design directions");
  bar.style.cssText = "position:fixed;left:50%;bottom:12px;transform:translateX(-50%);z-index:999;display:flex;gap:2px;padding:4px;background:#111;border-radius:999px;font:500 13px/1 system-ui,sans-serif;max-width:calc(100vw - 16px);overflow-x:auto;box-shadow:0 4px 18px rgba(0,0,0,.28)";
  items.forEach(function (it) {
    var a = document.createElement("a");
    a.href = it[0];
    a.textContent = it[1];
    var on = it[2] === here;
    a.style.cssText = "padding:9px 13px;border-radius:999px;white-space:nowrap;text-decoration:none;color:" + (on ? "#111" : "#fff") + ";background:" + (on ? "#fff" : "transparent");
    if (on) a.setAttribute("aria-current", "page");
    bar.appendChild(a);
  });
  document.body.appendChild(bar);
  document.body.style.paddingBottom = "64px";
})();

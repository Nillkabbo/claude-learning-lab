/* nav.js — the shared top navigation, loaded by every page.
   One file to change the nav on all pages. Auto-highlights the current page. */
(function () {
  "use strict";
  var LINKS = [
    ["The Lab", "index.html"],
    ["Story", "reference/story-roadmap.html"],
    ["Architect", "reference/claude-architect-roadmap.html"],
    ["CC Guide", "reference/claude-code-guide-roadmap.html"],
    ["Sprints", "reference/tracker-sprints.html"],
    ["Drills", "reference/drill-bank.html"],
    ["Cheats", "reference/cheatsheets.html"],
    ["Code", "reference/code-examples.html"]
  ];
  // Compute the relative prefix from the current page to the site root.
  var path = location.pathname.split("/");
  var depth = 0;
  for (var i = path.length - 2; i > 0; i--) {
    if (path[i] !== "" && path[i] !== "claude-learning-lab") depth++;
  }
  // If we're in a subdirectory (lessons/, reference/), go up one level.
  var lastSeg = path[path.length - 2];
  if (lastSeg && lastSeg !== "" && lastSeg !== "claude-learning-lab") {
    depth = 1; // we're one level deep
  } else {
    depth = 0; // we're at root
  }
  var prefix = depth === 1 ? "../" : "";

  var nav = document.createElement("nav");
  nav.className = "topnav";
  nav.innerHTML = '<span class="brand">CLAUDE LAB</span>';

  var currentFile = location.pathname.split("/").pop() || "index.html";

  LINKS.forEach(function (pair) {
    var a = document.createElement("a");
    a.href = prefix + pair[1];
    a.textContent = pair[0];
    var targetFile = pair[1].split("/").pop();
    if (targetFile === currentFile) {
      a.setAttribute("aria-current", "page");
    }
    nav.appendChild(a);
  });

  // Insert as the first child of <body>
  document.body.insertBefore(nav, document.body.firstChild);
})();

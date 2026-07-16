/* Collapsible tree behaviour for the Case superset matrix.
 *
 * Each row carries data-path / data-depth / data-parent / data-children.
 * A row is visible iff none of its ancestors are collapsed. The per-row +/-
 * toggle, the Expand-all / Collapse-all buttons, and the "show to depth N"
 * buttons all just mutate a set of collapsed paths and re-render.
 */
(function () {
  function initMatrix(root) {
    const rows = Array.from(root.querySelectorAll("tr.appl-row"));
    if (!rows.length) return;

    const byPath = new Map();
    rows.forEach((r) => byPath.set(r.dataset.path, r));
    const childCount = (path) => parseInt(byPath.get(path)?.dataset.children || "0", 10);
    const hasChildren = (path) => childCount(path) > 0;
    const collapsed = new Set();

    function recompute() {
      rows.forEach((r) => {
        // Visible unless some ancestor is collapsed.
        let visible = true;
        let parent = r.dataset.parent;
        while (parent) {
          if (collapsed.has(parent)) {
            visible = false;
            break;
          }
          parent = byPath.get(parent)?.dataset.parent || "";
        }
        r.style.display = visible ? "" : "none";

        const path = r.dataset.path;
        const isCollapsed = collapsed.has(path);
        r.classList.toggle("is-collapsed", isCollapsed);

        // Show the toggle affordance on any row that has one or more nested
        // attributes; leaf rows keep a hidden placeholder so names stay aligned.
        const btn = r.querySelector(".appl-row-toggle");
        if (btn) {
          btn.style.visibility = hasChildren(path) ? "visible" : "hidden";
        }
      });
    }

    root.querySelectorAll(".appl-row-toggle").forEach((btn) => {
      btn.addEventListener("click", () => {
        const path = btn.closest("tr").dataset.path;
        if (collapsed.has(path)) collapsed.delete(path);
        else collapsed.add(path);
        recompute();
      });
    });

    const controls = root.querySelector(".appl-matrix-controls");
    if (controls) {
      controls.addEventListener("click", (e) => {
        const btn = e.target.closest("button");
        if (!btn) return;
        if (btn.dataset.applExpand) {
          collapsed.clear();
        } else if (btn.dataset.applCollapse) {
          rows.forEach((r) => {
            if (hasChildren(r.dataset.path)) collapsed.add(r.dataset.path);
          });
        } else if (btn.dataset.applLevel) {
          const level = parseInt(btn.dataset.applLevel, 10);
          collapsed.clear();
          rows.forEach((r) => {
            if (hasChildren(r.dataset.path) && parseInt(r.dataset.depth, 10) >= level - 1) {
              collapsed.add(r.dataset.path);
            }
          });
        }
        controls.querySelectorAll("button").forEach((b) => b.classList.remove("is-active"));
        if (btn.dataset.applLevel) btn.classList.add("is-active");
        recompute();
      });
    }

    recompute();
  }

  function init() {
    document.querySelectorAll(".appl-matrix").forEach(initMatrix);
  }

  // Material for MkDocs exposes document$ (an RxJS subject) that fires on every
  // page load, including instant navigation. Fall back to DOMContentLoaded.
  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(init);
  } else {
    document.addEventListener("DOMContentLoaded", init);
  }
})();

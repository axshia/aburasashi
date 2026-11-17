// Focused Screen Captures: backdrop + outline overlay for screenshots.
//
// Evaluate this file in the page (Playwright `page.addScriptTag({ path })` or
// `page.evaluate(source)`, Chrome DevTools `Runtime.evaluate`), then call:
//
//   window.__focusCapture.hideDevOverlays();          // optional
//   window.__focusCapture.apply({ targets: [
//     '.alert-banner',                                  // CSS selector (all matches, unioned)
//     { selector: '.side-panel-item', text: '公開ステータス' }, // selector filtered by visible text
//     ['.field-a', '.field-b'],                        // several targets drawn as one frame
//   ] });
//   // take a viewport screenshot
//   window.__focusCapture.clear();
//
// The overlay uses `position: fixed` and viewport coordinates measured when
// `apply` runs, so scroll first and call `apply` right before the screenshot.
(() => {
  const OVERLAY_ID = '__focus-capture-overlay';
  const SVG_NS = 'http://www.w3.org/2000/svg';
  const hidden = [];

  const toElements = (target) => {
    if (typeof target === 'string') return [...document.querySelectorAll(target)];
    if (Array.isArray(target)) return target.flatMap(toElements);
    if (target && typeof target === 'object' && target.selector) {
      const all = [...document.querySelectorAll(target.selector)];
      if (!target.text) return all;
      const matches = all.filter((el) => (el.innerText || '').includes(target.text));
      // Prefer the innermost matches so a container does not swallow its child.
      return matches.filter((el) => !matches.some((other) => other !== el && el.contains(other)));
    }
    return [];
  };

  const unionRect = (elements) => {
    const rects = elements.map((el) => el.getBoundingClientRect()).filter((r) => r.width > 0 && r.height > 0);
    if (rects.length === 0) return null;
    const left = Math.min(...rects.map((r) => r.left));
    const top = Math.min(...rects.map((r) => r.top));
    const right = Math.max(...rects.map((r) => r.right));
    const bottom = Math.max(...rects.map((r) => r.bottom));
    return { x: left, y: top, width: right - left, height: bottom - top };
  };

  const clear = () => document.getElementById(OVERLAY_ID)?.remove();

  const apply = ({
    targets,
    padding = 8,
    dim = 'rgba(0, 0, 0, 0.55)',
    stroke = '#E5484D',
    strokeWidth = 3,
    radius = 8,
  } = {}) => {
    clear();
    const frames = [];
    const missing = [];
    (targets || []).forEach((target, index) => {
      const rect = unionRect(toElements(target));
      if (rect) frames.push(rect);
      else missing.push(index);
    });
    if (missing.length > 0) {
      throw new Error(`focus-overlay: no visible element for targets ${missing.join(', ')}`);
    }

    const width = window.innerWidth;
    const height = window.innerHeight;
    const svg = document.createElementNS(SVG_NS, 'svg');
    svg.id = OVERLAY_ID;
    svg.setAttribute('width', width);
    svg.setAttribute('height', height);
    Object.assign(svg.style, {
      position: 'fixed', left: '0', top: '0', width: `${width}px`, height: `${height}px`,
      zIndex: '2147483647', pointerEvents: 'none',
    });

    const box = (r) => ({ x: r.x - padding, y: r.y - padding, w: r.width + padding * 2, h: r.height + padding * 2 });
    const holes = frames.map((r) => {
      const b = box(r);
      return `<rect x="${b.x}" y="${b.y}" width="${b.w}" height="${b.h}" rx="${radius}" fill="black"/>`;
    }).join('');
    const outlines = frames.map((r) => {
      const b = box(r);
      return `<rect x="${b.x}" y="${b.y}" width="${b.w}" height="${b.h}" rx="${radius}" fill="none" stroke="${stroke}" stroke-width="${strokeWidth}"/>`;
    }).join('');
    svg.innerHTML =
      `<defs><mask id="${OVERLAY_ID}-mask"><rect width="100%" height="100%" fill="white"/>${holes}</mask></defs>` +
      `<rect width="100%" height="100%" fill="${dim}" mask="url(#${OVERLAY_ID}-mask)"/>${outlines}`;
    document.body.appendChild(svg);
    return frames.map((r) => ({ x: Math.round(r.x), y: Math.round(r.y), width: Math.round(r.width), height: Math.round(r.height) }));
  };

  // Hide fixed-position developer overlays (debug menus, profilers). Pass extra
  // patterns to match against an element's id, class, or text.
  const hideDevOverlays = (patterns = [/profiler/i, /debug/i, /herb/i, /devtools/i]) => {
    document.querySelectorAll('body *').forEach((el) => {
      if (getComputedStyle(el).position !== 'fixed' || el.id === OVERLAY_ID) return;
      const label = `${el.id} ${el.className} ${(el.innerText || '').slice(0, 80)}`;
      if (patterns.some((pattern) => pattern.test(label))) {
        hidden.push([el, el.style.visibility]);
        el.style.visibility = 'hidden';
      }
    });
    return hidden.length;
  };

  const restoreDevOverlays = () => {
    while (hidden.length > 0) {
      const [el, visibility] = hidden.pop();
      el.style.visibility = visibility;
    }
  };

  window.__focusCapture = { apply, clear, hideDevOverlays, restoreDevOverlays };
})();

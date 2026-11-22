// Count-up on the dashboard stat tiles. The server already renders the final numbers,
// so without JavaScript (or with reduced motion) the tiles simply show them.
(function () {
  if (!window.matchMedia || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  var tiles = document.querySelectorAll(".jd-stat__value");
  tiles.forEach(function (el) {
    var target = parseInt(el.textContent, 10);
    if (!(target > 0)) return;
    var duration = Math.min(900, 400 + target * 40), start = null;
    el.textContent = "0";
    function step(now) {
      if (start === null) start = now;
      var t = Math.min(1, (now - start) / duration);
      el.textContent = String(Math.round(target * (1 - Math.pow(1 - t, 3))));
      if (t < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  });
})();

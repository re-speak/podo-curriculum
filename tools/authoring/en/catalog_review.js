(function () {
  "use strict";
  // Keep the original key so comments made in the former all-in-one catalog
  // survive the move to generated per-track pages.
  var KEY = "podo-en-review-v1";
  var state = { items: {}, general: "" };
  try { state = Object.assign(state, JSON.parse(localStorage.getItem(KEY) || "{}")); } catch (_) {}
  if (!state.items) state.items = {};
  Object.keys(window.PODO_REVIEW_INDEX || {}).forEach(function (id) {
    if (!state.items[id]) return;
    state.items[id].title = window.PODO_REVIEW_INDEX[id].title;
    state.items[id].primary = window.PODO_REVIEW_INDEX[id].primary;
  });

  var saved = document.querySelector(".review-saved");
  var timer;
  function record(id) { return state.items[id] || (state.items[id] = { flag: false, note: "" }); }
  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (_) {}
    if (saved) {
      saved.textContent = "saved";
      clearTimeout(timer);
      timer = setTimeout(function () { saved.textContent = ""; }, 1400);
    }
    tally();
  }

  var lessons = Array.prototype.slice.call(document.querySelectorAll(".lesson[data-review-id]"));
  lessons.forEach(function (lesson) {
    var id = lesson.dataset.reviewId;
    var item = record(id);
    item.title = lesson.dataset.reviewTitle;
    item.primary = lesson.dataset.reviewPrimary;
    var flag = lesson.querySelector(".flag-control");
    var comment = lesson.querySelector(".comment-control");
    var note = lesson.querySelector(".review-note");
    note.value = item.note || "";
    flag.setAttribute("aria-pressed", item.flag ? "true" : "false");
    comment.setAttribute("aria-expanded", "false");
    lesson.classList.toggle("flagged", !!item.flag);
    lesson.classList.toggle("has-note", !!(item.note || "").trim());
    note.hidden = true;

    flag.addEventListener("click", function () {
      item.flag = flag.getAttribute("aria-pressed") !== "true";
      flag.setAttribute("aria-pressed", item.flag ? "true" : "false");
      lesson.classList.toggle("flagged", item.flag);
      save();
    });
    comment.addEventListener("click", function () {
      var open = note.hidden;
      note.hidden = !open;
      comment.setAttribute("aria-expanded", open ? "true" : "false");
      if (open) {
        lesson.classList.add("open");
        lesson.querySelector(".lrow-btn").setAttribute("aria-expanded", "true");
        note.focus();
      }
    });
    note.addEventListener("input", function () {
      item.note = note.value;
      lesson.classList.toggle("has-note", !!note.value.trim());
      save();
    });
  });

  var general = document.getElementById("general");
  if (general) {
    general.value = state.general || "";
    general.addEventListener("input", function () { state.general = general.value; save(); });
  }

  function counts() {
    var flagged = 0, commented = 0;
    Object.keys(state.items).forEach(function (id) {
      if (state.items[id].flag) flagged++;
      if ((state.items[id].note || "").trim()) commented++;
    });
    return { flagged: flagged, commented: commented };
  }
  function tally() {
    var count = counts();
    var label = document.querySelector(".review-tally");
    if (label) label.innerHTML = count.flagged || count.commented
      ? "<b>" + count.flagged + "</b> flagged · <b>" + count.commented + "</b> commented"
      : "Nothing marked yet";
  }
  function report() {
    var count = counts(), lines = ["PODO ENGLISH CURRICULUM — NATIVE REVIEW",
      "303 items · " + count.flagged + " flagged · " + count.commented + " commented", ""];
    if ((state.general || "").trim()) lines.push("## GENERAL", state.general.trim(), "");
    var flagged = [], comments = [];
    Object.keys(state.items).sort(function (a, b) {
      var pa = a.split("-"), pb = b.split("-");
      return pa[0].localeCompare(pb[0]) || Number(pa[1]) - Number(pb[1]);
    }).forEach(function (id) {
      var item = state.items[id], note = (item.note || "").trim();
      if (!item.flag && !note) return;
      var text = id + "  " + (item.title || "") + "\n    says: " + (item.primary || "");
      if (note) text += "\n    → " + note.replace(/\n/g, "\n      ");
      (item.flag ? flagged : comments).push(text);
    });
    if (flagged.length) lines.push("## FLAGGED — " + flagged.length, flagged.join("\n\n"), "");
    if (comments.length) lines.push("## COMMENTS, not flagged — " + comments.length, comments.join("\n\n"), "");
    if (!flagged.length && !comments.length && !(state.general || "").trim()) lines.push("(nothing marked)");
    return lines.join("\n");
  }
  function showCopy(button) {
    var text = report(), old = button.textContent;
    function done() { button.textContent = "Copied ✓"; setTimeout(function () { button.textContent = old; }, 1600); }
    function fallback() {
      var output = document.getElementById("review-output");
      output.value = text; output.classList.add("on"); output.focus(); output.select();
      try { document.execCommand("copy"); done(); } catch (_) { button.textContent = "Copy the text below"; }
    }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, fallback);
    else fallback();
  }
  document.querySelectorAll(".copy-review").forEach(function (button) {
    button.addEventListener("click", function () { showCopy(button); });
  });
  var show = document.querySelector(".show-review");
  if (show) show.addEventListener("click", function () {
    var output = document.getElementById("review-output");
    output.value = report(); output.classList.toggle("on");
  });
  var clear = document.querySelector(".clear-review");
  if (clear) clear.addEventListener("click", function () {
    if (!confirm("Clear every English catalog flag and comment?")) return;
    try { localStorage.removeItem(KEY); } catch (_) {}
    location.reload();
  });
  save();
})();

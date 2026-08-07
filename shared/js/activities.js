/* ================================================================
   ACTIVITIES · 화이트보드 없이 손가락만으로 푸는 활동 (공유 스크립트)

   한 과가 쓰는 활동 마크업은 이 네 가지가 전부다. 새 과를 만들 때
   자바스크립트를 쓸 일은 없다 — 아래 클래스만 얹으면 배선은 여기가 한다.

     .slot            점선 알약 → 타이핑하는 칸. 안에 적힌 글자가 정답이 된다.
                      <span class="slot" data-sync-id="p1-fill-student">이에요</span>
     .answer-space    답이 적혀 있으면 채점하는 칸, 비어 있으면 자유 작문 칸.
     .choice          .task-block 안의 칩 → 아래 pool 로 내려가고 .answer-space
                      가 칩을 받는 트레이(.build-zone)가 된다. 문장 만들기.
     .choose-row .opt 둘 중 하나를 눌러 고르기. data-correct 가 정답 쪽.
     .mission li      체크리스트 토글.

   채점은 언제나 각자 화면에서 다시 계산한다 — 정답은 오가지 않는다.
   보드 밖(로컬에서 파일을 직접 열 때)에서는 lessonSync 가 없으므로 아무것도
   하지 않는 스텁으로 대체해, 덱 자체는 그대로 동작하게 둔다.

   로드 순서: 페이저(pager.js)보다 먼저. 페이저의 티칭 모드가 여기서 만든
   window.__revealAnswers 를 부른다.
   ================================================================ */

/* ---------- lessonSync 스텁 ----------
   전송(스냅샷·늦은 입장·에코 차단·수렴)은 전부 레몬보드가 한다. 문서는
   "무엇이 공유되는지"만 선언한다 — data-sync-id 가 있는 요소만 공유된다. */
window.lessonSync = window.lessonSync || {
  kinds: {},
  register: function (name, handlers) { this.kinds[name] = handlers; return this; },
  push: function () {}
};

(function () {
  'use strict';

  var sync = window.lessonSync;
  var MAX_TEXT = 2000;                 // 붙여넣기 한 번으로 문서가 부풀지 않게

  // 띄어쓰기·문장부호는 채점에서 무시한다 ("학생이에요?" == "학생이에요")
  function norm(s) { return (s || "").replace(/[\s　?？.。!！,、·~〜…]/g, ""); }

  /* 칩 안에는 한국어 말고 발음 표기(.yomi)도 들어 있다. 채점이 보는 것은
     한국어뿐이라, 읽는 데 도우라고 붙인 가나가 답에 섞이면 안 된다.
     (textContent 는 display:none 인 것까지 읽으므로, ア 를 껐다고 통과하는
     일도 없다 — 켜든 끄든 같은 문자열이어야 한다.) */
  function koText(el) {
    var s = "";
    for (var n = el.firstChild; n; n = n.nextSibling) {
      if (n.nodeType === 3) s += n.nodeValue;
      else if (n.nodeType === 1 && !n.classList.contains("yomi")) s += koText(n);
    }
    return s;
  }

  var reorder = new WeakMap();         // build zone -> {pool, answer, chips}

  /* ---------- (1) typed blanks ---------- */
  function grade(input, commit) {
    if (input.classList.contains("correct")) return;
    var space = input.closest(".answer-space");
    if (norm(input.value) === norm(input.dataset.answer) && input.value.trim()) {
      input.classList.remove("wrong");
      input.classList.add("correct");
      input.readOnly = true;
      input.placeholder = "";          // 맞힌 칸에는 유령 답을 다시 띄우지 않는다
      if (space) space.classList.add("correct");
    } else if (commit && input.value.trim()) {
      input.classList.add("wrong");
      setTimeout(function () { input.classList.remove("wrong"); }, 700);
    }
  }

  // 여기서는 보내지 않는다. 보드가 input 이벤트를 보고 값을 다시 읽어
  // 내보낸다(IME 조합 중에는 붙잡아 둔다). 이 함수는 채점만 한다.
  function wireInput(input) {
    input.addEventListener("input", function () { grade(input, false); });
    input.addEventListener("blur", function () { grade(input, true); });
    input.addEventListener("keydown", function (e) {
      if (e.key === "Enter") { e.preventDefault(); grade(input, true); }
    });
  }

  /* 자유 작문 칸은 쓴 만큼 자란다 — 답이 몇 줄이 될지 우리가 미리 알 수 없다.
     스크롤바가 생기면 학생이 방금 쓴 줄이 화면 밖으로 밀려나고, 튜터 화면에서는
     더 나쁘다: 학생이 말한 문장 전체가 한눈에 안 들어온다.
     높이를 재기 전에 auto 로 되돌리는 것이 줄어드는 쪽을 만든다(지운 만큼 다시
     작아진다). 아래 한계는 시트의 min-height 가 잡으므로 여기서 세지 않는다. */
  function grow(ta) {
    if (!ta.offsetParent) return;      // 지금 장이 아니다 — display:none 은 잴 수 없다
    ta.style.height = "auto";
    ta.style.height = ta.scrollHeight + "px";
  }

  // 그래서 장이 바뀔 때 페이저가 이 줄을 부른다. 숨어 있는 동안 상대가 써 넣은
  // 글도, 화면에 나오는 그 순간 제 높이를 찾는다.
  window.__resizeInputs = function () {
    document.querySelectorAll(".free-input").forEach(grow);
  };

  // 타이핑만이 아니라 보드가 상대의 글을 넣어 줄 때도 자라야 한다. 그쪽은
  // value 에 바로 쓰고 input 을 쏘지 않으므로, 이 칸의 value 만 가로챈다.
  function autoGrow(ta) {
    var desc = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, "value");
    Object.defineProperty(ta, "value", {
      configurable: true,
      get: function () { return desc.get.call(this); },
      set: function (v) { desc.set.call(this, v); grow(this); }
    });
    ta.addEventListener("input", function () { grow(ta); });
    grow(ta);
  }

  // data-sync-id 는 살아 있는 요소 하나에만 있어야 한다. 자리를 대신하는
  // 껍데기가 진짜 입력칸으로 바뀔 때 id 를 넘겨준다.
  function transferSync(source, target) {
    if (!source.dataset.syncId) return;
    target.dataset.syncId = source.dataset.syncId;
    if (source.dataset.syncKind) target.dataset.syncKind = source.dataset.syncKind;
    source.removeAttribute("data-sync-id");
    source.removeAttribute("data-sync-kind");
  }

  /* 답을 실제로 그려 보고 그 너비를 잰다. 글자 수 × 상수로 어림하면 한글
     글자마다 다른 자폭이 뭉개져 30~40px 씩 남아돌고, 그 남는 폭이 한 줄에
     들어갈 칸을 아랫줄로 밀어낸다.
     재는 span 은 body 에 붙인다 — 장(.section)은 페이저가 도달하기 전까지
     display:none 이라 그 안에서는 아무것도 잴 수 없지만, 칸의 computed font
     는 숨어 있어도 읽히므로 같은 글꼴을 밖에서 재면 된다. */
  var ruler = document.createElement("span");
  ruler.style.cssText = "position:absolute;left:-9999px;top:0;visibility:hidden;white-space:pre";
  document.body.appendChild(ruler);

  var sized = [];

  function sizeToAnswer(input) {
    var cs = getComputedStyle(input);
    ruler.style.font = cs.fontStyle + " " + cs.fontWeight + " " + cs.fontSize + " " + cs.fontFamily;
    ruler.style.letterSpacing = cs.letterSpacing;
    ruler.textContent = input.dataset.answer;
    var pad = parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight);
    // 10px 은 글자가 테두리에 닿지 않을 만큼의 여유. 답보다 긴 답을 쓰는
    // 학생은 어차피 이 폭을 넘기므로 여기서 미리 벌어 두지 않는다.
    input.style.width = Math.ceil(ruler.getBoundingClientRect().width + pad) + 10 + "px";
  }

  /* Pretendard 는 CDN 웹폰트다. 처음 재는 시점에는 아직 대체 글꼴일 수 있고,
     그 폭으로 굳으면 글꼴이 바뀐 뒤 칸만 어긋난 채 남는다. 폰트가 정해지면
     한 번 더 잰다(이미 캐시돼 있으면 같은 값이 나오므로 화면은 그대로다). */
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(function () { sized.forEach(sizeToAnswer); });
  }

  // 점선 알약(.slot) → 타이핑하는 칸. 답 길이에 맞춰 폭을 잡는다.
  document.querySelectorAll(".slot").forEach(function (slot) {
    var answer = slot.textContent.trim();
    if (!answer) return;
    var input = document.createElement("input");
    input.type = "text";
    input.className = "slot-input";
    input.autocomplete = "off";
    input.spellcheck = false;
    input.dataset.answer = answer;
    transferSync(slot, input);
    slot.replaceWith(input);
    // 시트의 max-width 는 낱말용이라 한 문장짜리 칸을 잘라 낸다.
    // 폭은 붙인 뒤에 잰다 — 그래야 상속된 글꼴이 잡힌다.
    input.style.maxWidth = "none";
    sizeToAnswer(input);
    sized.push(input);
    wireInput(input);
  });

  /* ---------- (3) reorder: 칩을 문장 자리에 놓는다 ----------
     .task-block 안의 .choice 칩이 아래 pool 로 내려가고, 답 자리는
     칩을 받는 트레이가 된다. 먼저 처리해야 아래 .answer-space 루프가
     이 트레이를 입력칸으로 바꾸지 않는다. */
  function settleOrder(zone) {
    var block = reorder.get(zone);
    if (!block) return;
    zone.classList.remove("wrong");
    // 한 조각이라도 놓은 순간부터 되돌릴 수 있어야 한다 — 맞았든 틀렸든
    // 반쯤 놓았든. 다 놓고 나서야 나타나면, 두 번째 칩을 잘못 놓은 사람은
    // 남은 칩을 마저 놓아 틀린 문장을 완성해야 다시 시작할 수 있다.
    if (block.reset) block.reset.hidden = !zone.children.length;
    if (block.pool.children.length) return;      // 아직 다 놓지 않았다
    var built = Array.prototype.map.call(zone.children, function (c) {
      return koText(c).trim();
    }).join(" ");
    zone.classList.add(norm(built) === norm(block.answer) ? "correct" : "wrong");
  }

  document.querySelectorAll(".task-block").forEach(function (block) {
    var chips = [].slice.call(block.querySelectorAll(":scope > .choice"));
    if (!chips.length) return;
    var zone = block.querySelector(".answer-space");
    var answer = zone.textContent.trim();
    zone.textContent = "";
    zone.classList.add("build-zone");
    zone.setAttribute("data-a", answer);         // 티칭 모드의 유령 답

    /* 조각과 그것으로 짓는 문장은 한 물건이라, 트레이는 답 칸 밖이 아니라
       答 상자 안에 붙는다 — 힌트 띠와 같은 자리, 같은 회색. 칸이 상자의
       가운데 띠가 되면서 오답의 붉은 칠이 상자의 둥근 모서리에 잘리던 것도
       같이 사라진다: 이제 위아래가 모두 각진 이웃이다. */
    var tray = document.createElement("div");
    tray.className = "chip-tray";
    var pool = document.createElement("div");
    pool.className = "chip-pool";
    var reset = document.createElement("button");
    reset.type = "button";
    reset.className = "build-reset";
    reset.textContent = "やり直す";
    reset.hidden = true;
    tray.appendChild(pool);
    tray.appendChild(reset);
    (zone.parentElement || block).appendChild(tray);

    reorder.set(zone, { pool: pool, answer: answer, chips: chips, reset: reset });
    zone.dataset.syncKind = "order";             // 아래에서 register 한다
    chips.forEach(function (chip) {
      pool.appendChild(chip);
      chip.addEventListener("click", function () {
        if (zone.classList.contains("correct")) return;
        zone.classList.remove("wrong");
        (chip.parentElement === pool ? zone : pool).appendChild(chip);
        settleOrder(zone);
      });
    });

    // 맞힌 뒤에도 눌린다 — 다시 해 보는 것을 막을 이유가 없다.
    // 칩을 원래 순서대로 되돌리므로 처음 화면과 똑같은 상태가 된다.
    reset.addEventListener("click", function () {
      chips.forEach(function (c) { pool.appendChild(c); });
      zone.classList.remove("correct", "wrong");
      reset.hidden = true;
    });
  });

  // 답이 적혀 있으면 채점하는 칸, 비어 있으면 자유롭게 쓰는 칸
  document.querySelectorAll(".answer-space").forEach(function (space) {
    if (space.classList.contains("build-zone")) return;
    var answer = space.textContent.trim();
    space.textContent = "";
    space.classList.add("as-input");
    if (answer) {
      var input = document.createElement("input");
      input.type = "text";
      input.className = "space-input";
      input.autocomplete = "off";
      input.spellcheck = false;
      input.dataset.answer = answer;
      transferSync(space, input);
      space.appendChild(input);
      wireInput(input);
    } else {
      var ta = document.createElement("textarea");
      ta.className = "free-input";
      ta.rows = 2;
      ta.spellcheck = false;
      ta.maxLength = MAX_TEXT;
      transferSync(space, ta);
      space.appendChild(ta);
      autoGrow(ta);
    }
  });

  /* ---------- (2) tap one of two ----------
     공유되는 것은 "고른 쪽"(.chosen) 뿐이다. 맞았는지 틀렸는지는
     양쪽 화면이 각자 data-correct 로 다시 계산한다. */
  document.querySelectorAll(".choose-row").forEach(function (row) {
    var opts = [].slice.call(row.querySelectorAll(".opt"));
    if (!opts.length) return;
    opts.forEach(function (opt) {
      opt.setAttribute("role", "button");
      opt.addEventListener("click", function () {
        if (row.dataset.done) return;
        // 형제의 표시를 먼저 지우는 것이 "하나만 고르기"를 만든다.
        // 보드는 집합만 볼 뿐이고, 그 규칙은 이 문서에 있다.
        opts.forEach(function (o) { o.classList.remove("chosen"); });
        opt.classList.add("chosen");
        if (opt.hasAttribute("data-correct")) {
          row.dataset.done = "1";
          opt.classList.add("correct");
          opts.forEach(function (o) { if (o !== opt) o.classList.add("dim"); });
        } else {
          opt.classList.add("wrong");
          setTimeout(function () { opt.classList.remove("wrong"); }, 700);
        }
      });
    });
  });

  /* ---------- mission checklist ---------- */
  document.querySelectorAll(".mission li").forEach(function (li) {
    li.addEventListener("click", function (e) {
      if (e.target.closest(".hint")) return;
      li.classList.toggle("checked");
    });
  });

  /* ---------- 티칭 모드에서 답을 유령으로 띄운다 ----------
     CSS 는 input 안까지 들어가지 못하므로, 타이핑 칸만 여기서 처리한다.
     나머지(고르기·문장 만들기)는 시트에 있다. 공유하지 않는다. */
  window.__revealAnswers = function (on) {
    document.querySelectorAll("input[data-answer], .free-input").forEach(function (el) {
      if (el.classList.contains("correct")) return;
      el.placeholder = on ? (el.dataset.answer || "") : "";
    });
  };

  /* ---------- 조립 중인 문장은 DOM 만으로 읽히지 않는다 ----------
     칩의 "순서"가 상태라서, 이 문서가 read/apply 를 들고 온다. 칸은
     위치가 아니라 칩의 이름(data-item-id)으로 지칭한다. */
  sync.register("order", {
    read: function (zone) {
      return {
        itemIds: Array.prototype.map.call(zone.children, function (c) {
          return c.dataset.itemId;
        }).filter(Boolean)
      };
    },
    apply: function (zone, state) {
      if (!state || !Array.isArray(state.itemIds)) return;
      var block = reorder.get(zone);
      if (!block || zone.classList.contains("correct")) return;
      var known = {};
      block.chips.forEach(function (c) { known[c.dataset.itemId] = c; });
      var seen = {};
      for (var i = 0; i < state.itemIds.length; i++) {
        var id = state.itemIds[i];
        // 이 활동이 선언한 칩만, 한 번씩만 (§8)
        if (typeof id !== "string" || !known[id] || seen[id]) return;
        seen[id] = 1;
      }
      state.itemIds.forEach(function (id) { zone.appendChild(known[id]); });
      block.chips.forEach(function (chip) {
        if (!seen[chip.dataset.itemId]) block.pool.appendChild(chip);
      });
      settleOrder(zone);
    }
  });
})();

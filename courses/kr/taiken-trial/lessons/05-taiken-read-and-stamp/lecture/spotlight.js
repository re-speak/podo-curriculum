/* ================================================================
   SPOTLIGHT · 손가락 포인터 — "여기 보세요" 를 상대 화면에 비춘다
   ----------------------------------------------------------------
   레몬보드 위에선 자유롭게 그릴 수 없으니, 튜터(또는 학생)가 무엇을
   가리키는지 상대 화면에 똑같이 켠다. 대칭이다 — 누가 눌러도 상대에게 간다.

   레몬보드의 data-sync 계약을 그대로 탄다. 보드 수정도 배포도 없다:
     · 공유되는 상태는 딱 하나 — "지금 몇 번째 블록이 켜졌나"({ spot }).
       클릭(이벤트)이 아니라 결과 상태라, 늦게 들어오거나 새로고침해도
       스냅샷 하나로 따라온다. 메시지가 유실돼도 다음 탭에서 수렴한다.
     · data-spot 은 로드 때 덱 전체에 순서대로(전역 인덱스) 매긴다. 두 사람의
       DOM 이 똑같으니 "n 번째" 가 양쪽에서 같은 요소다 — page-id 가 없는
       스크롤 덱에서도 그대로 동작한다.
     · 탭-타일·키패드·입력 등 자기 클릭을 이미 쓰는 위젯([data-sync-id],
       버튼, 입력…)은 포인터에서 제외한다. 내용 블록(제목·말풍선·카드·글자
       카드…)만 켠다.

   한 덱에 <script src> 한 줄이면 붙는다. lessonSync 가 없으면(파일 직접 열기)
   스텁으로 대체돼, 덱은 그대로 동작하되 동기화만 안 한다.
   ================================================================ */
(function () {
  "use strict";

  var phone = document.querySelector(".phone");
  if (!phone) return;

  // 보드가 lessonSync 를 주입하지 않았으면(로컬) 스텁으로 대체한다.
  var sync = (window.lessonSync = window.lessonSync || {
    kinds: {},
    register: function (name, handlers) { this.kinds[name] = handlers; return this; },
    push: function () {}
  });

  // 가리킬 수 있는 "내용 블록" — 모든 트라이얼 덱이 공유하는 컴포넌트 어휘.
  // 여기에 없는 클래스는 그 덱에서 그냥 안 잡힌다(무해). 활동(정답을 고르거나
  // 채우는 것)은 일부러 뺀다.
  var SPOT = [
    ".section-title", ".transition-title", ".transition-copy", ".brand-title",
    ".brand-sub", ".section-subtitle", ".bubble", ".card", ".pattern-card",
    ".note-box", ".hook-quote", ".tip", ".row", ".hint-chip", ".nchip",
    ".known-row", ".model-line", ".lab", ".lv-badge",
    ".letter-card", ".pair-side", ".read-chip", ".blk", ".blk-item", ".part",
    ".kana", ".syl", ".combo > span", ".word-card", ".sign", ".payoff",
    ".mouth", ".brand-mascot"
  ].join(",");

  // 자기 클릭을 이미 소유한 것들 — 절대 가로채지 않는다. 활동은 전부
  // data-sync 로 묶여 있거나 네이티브 컨트롤이라, 이 한 줄로 일반적으로 걸러진다.
  var INTERACTIVE =
    "button,a,input,textarea,select,label,[contenteditable]," +
    "[data-sync-id],[data-sync-option],[data-ok]";

  // ---- 전역 인덱스 매기기 ----
  // 문서 순서대로 번호를 매긴다. 인터랙티브 안에 든 것은 건너뛴다.
  (function stamp() {
    var n = 0;
    var nodes = phone.querySelectorAll(SPOT);
    for (var i = 0; i < nodes.length; i++) {
      if (nodes[i].closest(INTERACTIVE)) continue;
      nodes[i].setAttribute("data-spot", String(n++));
    }
  })();

  var current = null; // 지금 켜진 블록의 인덱스(number) | null

  function clearLit() {
    var prev = phone.querySelector(".is-spot");
    if (prev) prev.classList.remove("is-spot");
  }

  // 정확히 하나만 켜거나, 아무것도 안 켠다. 멱등: 같은 인자 → 같은 결과.
  function light(spot) {
    clearLit();
    current = null;
    if (spot == null) return;
    var el = phone.querySelector('[data-spot="' + spot + '"]');
    if (!el) return;                       // 이 덱에 없는 인덱스면 조용히 무시
    el.classList.add("is-spot");
    current = spot;
  }

  /* 공유 상태는 블록 인덱스 하나. 페이저와 똑같이 레슨이 자기 kind 를 들고 온다. */
  sync.register("spotlight", {
    read: function () { return { spot: current }; },
    apply: function (_el, state) {
      light(state && typeof state.spot === "number" ? state.spot : null);
    }
  });

  // sync-id 를 달아 둘 껍데기. 상태는 클로저에 있으니 요소 자체는 비어 있어도 된다.
  var carrier = document.createElement("div");
  carrier.setAttribute("data-sync-id", "deck-spotlight");
  carrier.setAttribute("data-sync-kind", "spotlight");
  carrier.style.display = "none";
  document.body.appendChild(carrier);

  // ---- 대칭 입력: 누가 블록을 누르든 상대에게 켜 준다 ----
  // 같은 블록을 다시 누르면 끈다. 인터랙티브 위젯은 자기 핸들러로 흘려보낸다.
  phone.addEventListener("click", function (e) {
    var t = e.target;
    if (!t || !t.closest) return;
    if (t.closest(INTERACTIVE)) return;
    var el = t.closest("[data-spot]");
    if (!el) return;                        // 빈 공간 → 그대로 둔다
    var spot = parseInt(el.getAttribute("data-spot"), 10);
    light(current === spot ? null : spot);  // 같은 걸 또 누르면 끄기
    sync.push(carrier);
  });

  // ---- 페이지를 넘기면 포인터를 끈다 ----
  // 페이저가 pg-on 을 옮기면(로컬이든 원격 적용이든) 감지해서 지운다. 스크롤 덱엔
  // pg-on 이 없어 아무 일도 안 한다. 지운 상태도 발행해, 늦게 들어온 사람이
  // 이미 떠난 페이지의 낡은 포인터를 되살리지 않게 한다.
  var lastActive = phone.querySelector(".pg-on");
  var observer = new MutationObserver(function () {
    var now = phone.querySelector(".pg-on");
    if (now === lastActive) return;         // pg-on 이 실제로 바뀐 배치만 처리
    lastActive = now;
    if (current != null) {
      light(null);
      sync.push(carrier);
    }
  });
  observer.observe(phone, { subtree: true, attributes: true, attributeFilter: ["class"] });
})();

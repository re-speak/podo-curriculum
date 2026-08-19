#!/bin/bash
# Render check for newly written decks: worst intrinsic page height, stray
# .yomi (a reading in a container the stylesheet never declares a rule for),
# and horizontal overflow inside the 480px .phone.
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
READY='(() => document.fonts.status)()'
P='(() => {
  const phone=document.querySelector(".phone"); if(!phone) return "no phone";
  const pages=[...phone.children].filter(p=>p.hasAttribute("data-page-id"));
  const was=phone.querySelector(".pg-on");
  let worst={id:null,h:0}, stray=[], over=[];
  pages.forEach(p=>{
    pages.forEach(q=>q.classList.toggle("pg-on",q===p));
    // stray yomi: font-size at or above body size means no rule matched it
    p.querySelectorAll(".yomi").forEach(y=>{
      const fs=parseFloat(getComputedStyle(y).fontSize);
      if(fs>=15) stray.push(p.dataset.pageId+" "+fs+"px "+y.textContent.slice(0,12));
    });
    // horizontal overflow against the phone box
    const pr=phone.getBoundingClientRect();
    p.querySelectorAll("*").forEach(el=>{
      const r=el.getBoundingClientRect();
      if(r.width>0 && (r.right>pr.right+1||r.left<pr.left-1))
        over.push(p.dataset.pageId+" "+el.className+" "+Math.round(r.width));
    });
    if(!p.classList.contains("section")){
      const prev=p.style.minHeight; p.style.minHeight="0px";
      const r=p.getBoundingClientRect(); const need=Math.round(r.height+r.top);
      p.style.minHeight=prev; if(need>worst.h) worst={id:p.dataset.pageId,h:need};
    }
  });
  pages.forEach(q=>q.classList.toggle("pg-on",q===was));
  return JSON.stringify({worst:worst,stray:stray.slice(0,6),over:over.slice(0,6)});
})()'
for f in "$@"; do
  orca goto --url "file://$PWD/$f" --json >/dev/null 2>&1
  for i in $(seq 1 12); do
    st=$(orca eval --expression "$READY" --json 2>/dev/null | python3 -c "import json,sys;print(json.load(sys.stdin).get('result',{}).get('result',''))" 2>/dev/null)
    [ "$st" = "loaded" ] && break
    sleep 0.4
  done
  out=$(orca eval --expression "$P" --json 2>&1 | python3 -c "import json,sys;print(json.load(sys.stdin).get('result',{}).get('result','ERR'))" 2>/dev/null)
  echo "$(basename $(dirname $f)) fonts=$st"
  echo "$out" | python3 -m json.tool 2>/dev/null || echo "$out"
done

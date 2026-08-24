#!/usr/bin/env python3
"""Build the English trial decks.

A trial deck is a *trial wrapper* — cover, greeting, ニーズ把握, report, closing — with
pages lifted verbatim out of an already-proofread lesson deck. The lesson pages are never
re-typed here, so their `data-sync` ids and answer keys cannot drift from the lesson they
came from; re-run this script after the source lesson changes and the trial follows.

    python3 tools/authoring/en/build_trial_decks.py            # all of them
    python3 tools/authoring/en/build_trial_decks.py trial-1    # just one

Written for the Japanese market (LANG_TYPE=EN, COUNTRY_CODE=JP), which is a different
product from the Korea-market English trial that podo-app already renders. The ladder
these decks report against is sandbox/drafts/en/trial/plan-logic.md, and the tables that
implement it are shared/js/report-en.js.

Why a generator rather than four checked-in HTML files: the wrapper is roughly a thousand
lines of report markup that has to be identical in every deck. Copied by hand it stops
being identical the first time one of them is fixed.
"""

import argparse
import io
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
TRACKS = ROOT / "sandbox/drafts/en/tracks"
OUT_DIR = ROOT / "sandbox/drafts/en/trial/decks"
CONTENT_VERSION = "2026-08-21"


# ============================================================================
# Lifting pages out of a lesson deck
# ============================================================================

def pages(path):
    """Split a deck into {page-id: html}. Pages are flat siblings under .phone."""
    s = io.open(path, encoding="utf-8").read()
    body = s.split('<div class="phone">', 1)[1]
    out, depth, buf, cur = {}, 0, [], None
    # walk div-by-div at depth 1
    for tok in re.split(r'(<div\b[^>]*>|</div>)', body):
        if tok.startswith("<div"):
            if depth == 0:
                m = re.search(r'data-page-id="([^"]+)"', tok)
                cur = m.group(1) if m else None
                buf = []
            depth += 1
        elif tok == "</div>":
            depth -= 1
            if depth == 0:
                if cur:
                    out[cur] = "".join(buf) + tok
                cur, buf = None, []
                continue
            if depth < 0:
                break
        if cur is not None:
            buf.append(tok)
    return out

# ============================================================================
# The trial wrapper — shared by every deck
#
# Learner-facing text is Japanese; the target language (English) is the only English the
# learner reads. Tutor-facing text — the level check, the five axis questions, tutor notes,
# the save button — is English, because the tutor of an English trial is an English speaker.
# The one crossing point is `data-say`: the tutor picks an English row, but the sentence
# that lands in the learner's report is its Japanese, so `data-say` is Japanese throughout.
# ============================================================================


def take(src, ids):
    p = pages(src)
    missing = [i for i in ids if i not in p]
    if missing:
        sys.exit("missing pages in %s: %s" % (src, missing))
    return {i: rebase(p[i], src.parent) for i in ids}


def rebase(html, src_dir):
    """Re-point relative asset paths from the source deck's depth to the trial deck's.

    A lesson deck sits nine directories down and reaches the shared trial artwork with
    seven `../`; a trial deck sits five down and needs four. A page lifted between them
    keeps whatever its source wrote, so the path silently resolves outside the repo and
    the image is simply missing — no error, nothing in the console but a 404.

    Only FT-89's 会話スタイル page trips this today (two report icons that still live
    under kr/trial/assets and did not move when English got its own trial folder). It is
    done here rather than patched into that one page because the next lesson lifted into
    a trial will have the same problem and no reason to expect it.
    """
    def fix(m):
        attr, rel = m.group(1), m.group(2)
        target = (src_dir / rel).resolve()
        try:
            return '%s="%s"' % (attr, os.path.relpath(target, OUT_DIR))
        except ValueError:            # different drive on Windows; leave it alone
            return m.group(0)
    return re.sub(r'\b(src|href)="(\.\./[^"]*)"', fix, html)


ICON = ('<span class="avatar icon"><svg viewBox="0 0 24 24" aria-hidden="true">'
        '<path fill="currentColor" d="M12 12a5 5 0 1 0 0-10 5 5 0 0 0 0 10Zm0 2.5c-4.7 0-8.5 2.6-8.5 5.8V22h17v-1.7c0-3.2-3.8-5.8-8.5-5.8Z"/>'
        '</svg></span>')


def head(lesson_id, level, title, cover, version=None):
    version = version or CONTENT_VERSION
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="google" content="notranslate">
  <meta name="podo:target-language" content="en">
  <meta name="podo:report-language" content="ja">
  <meta name="podo:lesson-id" content="{lesson_id}">
  <meta name="podo:level" content="{level}">
  <meta name="podo:content-version" content="{version}">
  <meta name="podo:title-ko" content="{title['ko']}">
  <meta name="podo:title-en" content="{title['en']}">
  <meta name="podo:title-ja" content="{title['ja']}">
  <title>{title['en']} — PODO English</title>
  <link rel="stylesheet" href="../../../../../shared/css/lesson-card.css">
  <link rel="stylesheet" href="../../../../../shared/css/trial.css">
</head>
<body>
  <div class="phone">

    <!-- ============ COVER ============ -->
    <div class="brand-page" data-page-id="cover">
      <span class="podo-badge"><span class="logo">PODO</span><span class="tag">体験レッスン</span></span>
      <h1 class="brand-title">{cover}</h1>
    </div>
'''


def greeting(turns):
    """The scripted trial opening — 初級 only.

    `turns` is a list of (who, ja, en, cue) with who in me/other. Every English line the
    learner says is written out for them, because at A1 the alternative to a script is
    silence.

    Above A1 use `open_greeting` instead. The Korean product settled this: its 한글 and
    패턴 trials are scripted and its 상황 and 자유 대화 trials are not, and the split is by
    track rather than by taste — a learner who can already hold a conversation reads a
    fill-in-the-blank "I'm ___" as being talked down to, and the tutor learns nothing about
    them from a line they were handed."""
    out = ['''
    <!-- ============ GREETING ============
         The learner speaks English in the first minute. The tutor's own name goes in a
         text box so the same deck works for every tutor, and the learner's name is the
         first English sentence they say today. -->
    <div class="section" data-page-id="greeting">
      <h2 class="section-title">Hello! <span class="title-ja">(はじめまして！)</span></h2>
      <p class="section-subtitle"><span class="ko">Let's say hello to each other first.</span><span class="ja">まずは、軽くあいさつしてみましょう。</span></p>
      <div class="tutor-note">Say your line, then wait for the learner to answer before moving on.</div>''']
    for i, group in enumerate(turns):
        style = ' style="margin-top:var(--item-gap);"' if i else ''
        out.append(f'\n      <div class="dialogue"{style}>')
        for who, ja, en, cue in group:
            me = who == "me"
            name = "Me" if me else "Tutor"
            cue_html = f'<span class="cue">{cue}</span>' if cue else ''
            out.append(
                f'<div class="turn {"me" if me else "other"}"><span class="who">{ICON}'
                f'<span class="who-name">{name}</span></span>'
                f'<div class="bubble{" me" if me else ""} intro">'
                f'<span class="translation">{ja}</span>'
                f'<span class="korean">{en}</span>{cue_html}</div></div>')
        out.append('</div>')
    out.append('\n    </div>\n')
    return "".join(out)


def open_greeting(asks):
    """The unscripted trial opening — 中級 and above.

    The tutor asks; the learner answers in their own words and the tutor types what they
    actually said. `asks` is a list of (en, ja, task_ja, sync_id): the tutor's question in
    English with its Japanese underneath, the one-line Japanese prompt over the answer box,
    and the sync id that carries the answer to the other screen.

    This page is also the first thing the tutor scores on. Five unscripted answers before
    the lesson starts is more evidence of level than the whole lesson that follows, because
    nothing here has been handed to the learner.
    """
    out = ['''
    <!-- ============ GREETING ============
         Unscripted. The tutor asks, the learner answers in their own words, and the tutor
         types the answer into the box so both screens hold the same sentence — which is
         also the first thing the tutor has to score on. The tutor's own name goes in a
         text box so the same deck works for every tutor. -->
    <div class="section" data-page-id="greeting">
      <h2 class="section-title">Hello! <span class="title-ja">(はじめまして！)</span></h2>
      <p class="section-subtitle"><span class="ko">Let&#x27;s say hello and introduce ourselves. Please answer in your own words.</span><span class="ja">まずは、軽くあいさつと自己紹介をしましょう。自分のことばで答えてください。</span></p>
      <div class="tutor-note">Ask these in order and type what the learner actually says. If an answer is short, ask once more before moving on — this page is your first read on their level.</div>''']
    for i, (en, ja, task, sid) in enumerate(asks):
        style = ' style="margin-top:var(--item-gap);"' if i else ''
        out.append(
            f'\n      <div class="dialogue"{style}>'
            f'<div class="turn other"><span class="who">{ICON}'
            f'<span class="who-name">Tutor</span></span>'
            f'<div class="bubble"><span class="korean">{en}</span>'
            f'<span class="translation">{ja}</span></div></div>'
            f'<div class="turn me"><span class="who">{ICON}'
            f'<span class="who-name">Me</span></span>'
            f'<div class="bubble me"><div class="answer-box tall">'
            f'<span class="answer-label task">{task}</span>'
            f'<span class="answer-space as-input">'
            f'<textarea class="free-input" data-sync-id="{sid}" rows="2" spellcheck="false" maxlength="2000"></textarea>'
            f'</span></div></div></div></div>')
    out.append('\n    </div>\n')
    return "".join(out)


NEEDS = '''
    <!-- ============ ニーズ把握 ============
         Three questions, and all three feed the report: the motive picks which contextual
         course is laid down, the goal sets the distance, the pace drives the month count.
         The English trial has no consultation after the report, so these answers are the
         only thing that makes the plan this learner's rather than anyone's. -->
    <div class="brand-page bleed" data-page-id="needs-intro">
      <h2 class="brand-title">ニーズ把握</h2>
      <p class="brand-sub">あなたのことを教えてください。答えに合わせて、最後のプランが変わります。</p>
      <img class="brand-art" src="../assets/podo-character-ask.png" alt="">
    </div>

    <div class="section needs-jp" data-page-id="needs-why">
      <h2 class="section-title">学ぶきっかけ <span class="title-ja">(What brings you here)</span></h2>
      <p class="section-subtitle"><span class="ko">Why do you want to speak English? Pick as many as you like.</span><span class="ja">どうして英語を話せるようになりたいですか？<br>いくつ選んでも大丈夫です。</span></p>
      <div class="opt-list" data-group="why" data-pick="multi" data-sync-id="needs-why" data-sync-kind="selection" data-sync-state="on">
        <button class="opt-row" data-val="work" data-sync-option="work"><img class="r-ico" src="../assets/reasons/work.png" alt=""><span class="opt-body"><span class="opt-main">仕事で使う</span><span class="opt-sub">Using English at work</span></span></button>
        <button class="opt-row" data-val="assign" data-sync-option="assign"><img class="r-ico" src="../assets/reasons/assign.png" alt=""><span class="opt-body"><span class="opt-main">海外出張・駐在</span><span class="opt-sub">Business trips or relocation</span></span></button>
        <button class="opt-row" data-val="travel" data-sync-option="travel"><img class="r-ico" src="../assets/reasons/travel.png" alt=""><span class="opt-body"><span class="opt-main">旅行</span><span class="opt-sub">Travel</span></span></button>
        <button class="opt-row" data-val="exam" data-sync-option="exam"><img class="r-ico" src="../assets/reasons/exam.png" alt=""><span class="opt-body"><span class="opt-main">TOEIC・試験</span><span class="opt-sub">TOEIC or another exam</span></span></button>
        <button class="opt-row" data-val="self" data-sync-option="self"><img class="r-ico" src="../assets/reasons/self.png" alt=""><span class="opt-body"><span class="opt-main">自己啓発</span><span class="opt-sub">For myself</span></span></button>
        <button class="opt-row" data-val="other" data-sync-option="other"><img class="r-ico" src="../assets/reasons/other.png" alt=""><span class="opt-body"><span class="opt-main">その他（先生に教えてください）</span><span class="opt-sub">Something else</span></span></button>
      </div>
    </div>

    <div class="section needs-jp" id="p-goal" data-page-id="needs-goal">
      <h2 class="section-title">ゴール <span class="title-ja">(Where you want to get to)</span></h2>
      <p class="section-subtitle"><span class="ko">What do you want to be able to do in English? Pick one.</span><span class="ja">英語で何ができるようになりたいですか？<br>1つだけ選んでください。</span></p>
      <!-- ================================================================
           The goal is distance, not topic. Two people who both said "travel"
           may want different distances — ordering a coffee, or holding the
           conversation that follows. One card is one arrival level.
           The keys stay t3/t5/t7/t9: podo-app's zod schema enumerates exactly
           those four when it re-renders a saved report. Only the level each
           one arrives at is English (4 / 6 / 8 / 10, see report-en.js).
           ================================================================ -->
      <div class="goal-list" data-group="goal" data-pick="single" data-sync-id="needs-goal" data-sync-kind="selection" data-sync-state="on">

        <button class="glc" data-val="t3" data-sync-option="t3">
          <span class="glc-h"><span class="glc-b" aria-hidden="true"><i class="on"></i><i></i><i></i><i></i></span><span class="glc-n">言いたいことを、短い文で伝える<small>Say what you mean in short sentences</small></span></span>
          </button>

        <button class="glc" data-val="t5" data-sync-option="t5">
          <span class="glc-h"><span class="glc-b" aria-hidden="true"><i class="on"></i><i class="on"></i><i></i><i></i></span><span class="glc-n">慣れた話題なら、会話が続く<small>Keep a conversation going on familiar topics</small></span></span>
          </button>

        <button class="glc" data-val="t7" data-sync-option="t7">
          <span class="glc-h"><span class="glc-b" aria-hidden="true"><i class="on"></i><i class="on"></i><i class="on"></i><i></i></span><span class="glc-n">意見も理由も、英語で言える<small>Give an opinion and the reason for it</small></span></span>
          </button>

        <button class="glc" data-val="t9" data-sync-option="t9">
          <span class="glc-h"><span class="glc-b" aria-hidden="true"><i class="on"></i><i class="on"></i><i class="on"></i><i class="on"></i></span><span class="glc-n">どんな話題でも、自由に話せる<small>Speak freely on any topic</small></span></span>
          </button>

      </div>
    </div>

    <div class="section needs-jp" id="p-pace" data-page-id="needs-pace">
      <h2 class="section-title">学習ペース <span class="title-ja">(How often)</span></h2>
      <p class="section-subtitle"><span class="ko">How many lessons a week would you like?</span><span class="ja">1週間に何回、<br>レッスンを受けたいですか？</span></p>
      <div class="opt-list" data-group="pace" data-pick="single" data-sync-id="needs-pace" data-sync-kind="selection" data-sync-state="on">
        <button class="opt-row" data-val="1" data-sync-option="1"><span class="emo">🐢</span><span class="opt-body"><span class="opt-main">週1 <span class="title-ja">／once</span></span><span class="opt-sub">まずは無理なく</span></span></button>
        <button class="opt-row" data-val="2" data-sync-option="2"><span class="emo">🚶</span><span class="opt-body"><span class="opt-main">週2 <span class="title-ja">／twice</span></span><span class="opt-sub">こつこつ</span></span></button>
        <button class="opt-row" data-val="3" data-sync-option="3"><span class="emo">🏃</span><span class="opt-body"><span class="opt-main">週3 <span class="title-ja">／three times</span></span><span class="opt-sub">しっかり</span></span></button>
        <button class="opt-row" data-val="4" data-sync-option="4"><span class="emo">⚡</span><span class="opt-body"><span class="opt-main">週4 <span class="title-ja">／four times</span></span><span class="opt-sub">ぐんぐん</span></span></button>
        <button class="opt-row" data-val="5" data-sync-option="5"><span class="emo">🚀</span><span class="opt-body"><span class="opt-main">週5以上 <span class="title-ja">／five or more</span></span><span class="opt-sub">最短で</span></span></button>
      </div>
    </div>
'''


def trial_intro(promise):
    return f'''
    <div class="brand-page divider" data-page-id="trial-intro">
      <h2 class="brand-title">Trial lesson<span class="ja">体験レッスン</span></h2>
      <p class="brand-sub">{promise}</p>
      <img class="brand-art study" src="../assets/podo-character-study.png" alt="">
    </div>
'''


# ---- the report --------------------------------------------------------------

def _rung(val, on, tutor_en, say_ja):
    pips = "".join('<i class="on"></i>' if i < on else "<i></i>" for i in range(4))
    say = f' data-say="{say_ja}"' if say_ja else ""
    return (f'<button type="button" class="rung-row" data-val="{val}" data-sync-option="{val}"{say}>'
            f'<span class="rung" aria-hidden="true">{pips}</span>'
            f'<span class="rung-t">{tutor_en}</span></button>')


LEVEL_RUNGS = [
    (1, 0, "Single words and set phrases — I supplied most of the meaning", None),
    (3, 1, "Short sentences on familiar topics, but stalled often and forms slipped", None),
    (5, 2, "Kept going on familiar topics, but stopped when the topic changed", None),
    (7, 3, "Gave an opinion with a reason, even on a topic they hadn't seen", None),
    (9, 4, "Followed me at my normal speed and answered straight back", None),
]

AXES = [
    ("acc", "Accuracy", "How were the grammar and word forms?", [
        (1, 0, "Strung words together; I inferred the meaning", "簡単な語と文法で、基本的な意味は伝えられます"),
        (3, 1, "Tense, articles and endings often wrong", "文が長くなると、時制や冠詞がよく揺れます"),
        (5, 2, "Slipped only on longer sentences", "複雑な文のときだけ、語順や文法がときどき揺れます"),
        (7, 3, "Very few errors", "場面に合う語と文法を、おおむね正確に使えます"),
        (9, 4, "Hard to find an error", "語・文法・語順が文脈に合って正確です"),
    ]),
    ("voc", "Vocabulary", "How much could they reach for?", [
        (1, 0, "Stopped often for want of a word", "ごく簡単な語で、言いたいことを伝えられます"),
        (3, 1, "Talked around it with easy words", "言いたいことに合う語を、二つ三つほど知っています"),
        (5, 2, "Found words that fitted what they meant", "言いたいことに合う語を選んで使えます"),
        (7, 3, "Said the same thing more than one way", "言いたいことを、いろいろな語に言い換えられます"),
        (9, 4, "Chose the expression that fitted exactly", "場面に合う多様な語と表現を自由に使えます"),
    ]),
    ("flu", "Fluency", "How far did the talking run?", [
        (1, 0, "Stopped and restarted often", "慣れた話題なら、たどたどしく話せます"),
        (3, 1, "Long pauses between phrases", "慣れた話題なら、ゆっくり話をやりとりできます"),
        (5, 2, "Paused sometimes, but kept going", "慣れた話題なら、ためらわずに話せます"),
        (7, 3, "Barely stopped; carried the conversation", "はじめての話題でも、ためらわずに話せます"),
        (9, 4, "As comfortable as a native speaker", "どんな話題でも、速く楽に話せます"),
    ]),
    ("pron", "Pronunciation", "How easy were they to understand?", [
        (1, 0, "Pronunciation made them hard to follow", "知っている語でも、気をつけて話さないと聞き取れません"),
        (3, 1, "Sometimes hard to follow", "知っている語は言えますが、はじめての語は発音が難しいです"),
        (5, 2, "Understandable and mostly clear", "知っている語は滑らかで、はじめての語も声に出して読めます"),
        (7, 3, "Very clear", "発音が滑らかで、抑揚とリズムも合っています"),
        (9, 4, "Sounded like a native speaker", "発音が明瞭で、抑揚とリズムまで自然です"),
    ]),
    ("lis", "Listening", "How much did you slow down for them?", [
        (1, 0, "Barely caught what I said", "ゆっくりはっきり話しても、聞き取るのが難しいです"),
        (3, 1, "Only with very slow speech", "ゆっくりはっきり話せば、聞き取れます"),
        (5, 2, "A little slower and they got it", "少し速度を落とせば、全体の内容を聞き取れます"),
        (7, 3, "Only slightly slower than normal", "普通の速さでも、ニュアンスまで理解できます"),
        (9, 4, "Understood me at my normal speed", "ネイティブの速さでも、ニュアンスまで正確に聞き取れます"),
    ]),
]


def tutor_score():
    """The tutor's scoring page — the last page in the deck, after the goodbye.

    The learner never reads a report inside the trial. An English trial is taught by an
    English-speaking tutor, and the report is written in Japanese, so walking a learner
    through it is something the tutor cannot reliably do — least of all the beginner who
    needs it most. So the trial ends as a lesson ends: goodbye. The learner then goes to
    the chat, and the report is waiting there, in their own language.

    That leaves the tutor's judgement, which still has to be captured. It sits **after**
    the farewell so the tutor can take their time with it once the learner has gone.
    All three blocks below (.lvcheck, .axsteps, .rep-send) are `display:none` outside
    teaching mode, so a learner who is still in the room when the tutor pages forward
    lands on nothing but the sign-off line.
    """
    lv = "".join(_rung(v, o, t, s) for v, o, t, s in LEVEL_RUNGS)
    axq = ""
    for k, name, q, rows in AXES:
        opts = "".join(_rung(v, o, t, s) for v, o, t, s in rows)
        axq += f'''
        <div class="axq" data-ax="{k}">
          <p class="axq-h">{name}<small>{q}</small></p>
          <div class="axq-opts" data-group="ax-{k}" data-pick="single" data-sync-id="ax-{k}" data-sync-kind="selection" data-sync-state="on">
            {opts}
          </div>
        </div>'''

    return f'''
    <div class="section" data-page-id="tutor-score" data-act="Wrapping up">
      <h2 class="section-title">See you next time <span class="title-ja">(また会いましょう)</span></h2>
      <p class="section-subtitle"><span class="ko">That&#x27;s everything for today. Thank you!</span><span class="ja">今日はここまでです。ありがとうございました！</span></p>
      <div class="tutor-note">Score the learner once they have left — there is no rush. What you pick here is what builds the report waiting for them in the chat.</div>

      <div class="lvcheck">
        <span class="lvcheck-h">Level check <small>tutor only</small></span>
        <p class="lvcheck-q">How was the learner in today&#x27;s lesson?</p>
        <div class="lvpick" data-group="level" data-pick="single" data-sync-id="plan-level" data-sync-kind="selection" data-sync-state="on">
          {lv}
        </div>
        <button class="lvcheck-redo" type="button">Choose again</button>
      </div>

      <div class="axsteps">
        <div class="axst-chips"></div>{axq}
        <p class="axq-done">All five done. Tap above to change any of them.</p>
      </div>

      <div class="rep-send">
        <span class="rep-send-h">Save report <small>tutor only</small></span>
        <button class="rs-btn" type="button" disabled>Save this report</button>
        <p class="rs-msg"></p>
      </div>
    </div>
'''


CLOSING = '''
    <div class="brand-page end bleed" data-page-id="closing">
      <svg class="end-arch" viewBox="0 0 480 300" aria-hidden="true">
        <path id="endArch" d="M 70 255 Q 237 135 404 258" fill="none"></path>
        <text><textPath href="#endArch" startOffset="50%" text-anchor="middle">本日はお疲れさまでした！</textPath></text>
      </svg>
      <img class="end-art" src="../assets/podo-3d-bye.png" alt="">
      <div class="end-card">
        <div class="end-bar"><span>Welcome to PODO</span><span class="end-check">✓</span></div>
        <p class="end-title"><span class="hl">体験レッスン</span>は<br>ここまでです！</p>
        <p class="end-copy">今日はお話しできて楽しかったです。<br><strong>次はもっと気楽に、もっとたくさん話せるようになります ;)</strong></p>
        <div class="end-report">
          <span class="badge-dark">このあとのチャットで</span>
          <span class="t">あなただけの英語 診断レポート</span>
          <span class="s">担当スタッフがお届けします。</span>
        </div>
      </div>
    </div>
'''


def tail(freetalk=False):
    """Everything after the last page. `freetalk` adds the script FT decks need.

    freetalk-activities.js wires the no-right-answer pickers (.opt-list[data-pick]) that
    only the 自由対話 lesson has — the 会話スタイル page. It deliberately skips lists
    carrying data-group, which is every list the ニーズ把握 pages own, so it and report.js
    do not both bind the same button. That guard was written for exactly this deck; the
    comment at the top of the file says so.
    """
    ft = ('\n  <!-- FREETALK ACTIVITIES · 正解のない選び。会話スタイルのページが使う。\n'
          '       activities.js のあとに来ること — 空の答え欄は向こうで自由作文欄になる。 -->\n'
          '  <script src="../../../../../shared/js/freetalk-activities.js"></script>\n') if freetalk else ''
    return '''
  </div>

  <!-- ACTIVITIES · 点線の枠 · 選ぶ · 文を組み立てる。共有スクリプト。
       ページャより先に来ること — ティーチングモードがここで作る幽霊の答えを使う。 -->
  <script src="../../../../../shared/js/activities.js"></script>
  <script src="../../../../../shared/js/feedback.js"></script>
''' + ft + '''

  <!-- ================================================================
       PAGER · 一枚ずつめくるモード
       ================================================================ -->
  <nav class="pager" data-sync-id="deck-page" data-sync-kind="page">
    <input class="pg-scrub" type="range" min="0" max="0" step="1" value="0" aria-label="ページ移動">
    <button class="pg-btn pg-prev" type="button" aria-label="前のページ">←</button>
    <div class="pg-mid">
      <span class="pg-label"><b class="pg-act">—</b><span class="pg-n">—</span></span>
    </div>
    <button class="pg-btn pg-teach" type="button" aria-label="ティーチングモード">T</button>
    <button class="pg-btn pg-next" type="button" aria-label="次のページ">→</button>
  </nav>

  <!-- REPORT LOCALE · 英語体験のレベル表・コース表。**report.js より先**に
       読み込むこと — report.js は起動時に一度だけこの表を読むので、あとから
       置いても効かない。根拠は sandbox/drafts/en/trial/plan-logic.md。 -->
  <script src="../../../../../shared/js/report-en.js"></script>

  <!-- REPORT · レポートページの配線。共有スクリプト。 -->
  <script src="../../../../../shared/js/report.js"></script>

  <!-- REPORT SUBMIT · レポートをそのままバックエンドに残すボタン。スナップショットを
       report.js が作るので、必ずそのあとに来ること。共有スクリプト。 -->
  <script src="../../../../../shared/js/report-submit.js"></script>

  <script src="../../../../../shared/js/pager.js"></script>

  <!-- SCRIPT LINES · セリフを文単位で組にして立てる。ハイライトより先。 -->
  <script src="../../../../../shared/js/script-lines.js"></script>

  <!-- SPOTLIGHT · 共有ポインタ（描く代わりに「ここを見てください」）。共有スクリプト。 -->
  <script src="../../../../../shared/js/spotlight.js"></script>

  <!-- TUTOR NOTES · ページごとのメモ欄。ページャのあとに置くのが大事 —
       ページを数え終えたあとで欄を差し込む必要がある。 -->
  <script src="../../../../../shared/js/tutor-notes.js"></script>

  <!-- HIGHLIGHT · 文字に引く蛍光ペン。引いた跡は相手の画面にも残る。 -->
  <script src="../../../../../shared/js/highlight.js"></script>

  <!-- STAMP · よくできました。stamp.js がこの絵をページごとに複製する。
       .phone の外に置くのが大事 — 中に入れると空のページが一つ増える。 -->
  <img class="stamp-art" src="../assets/good-job.svg" alt="">
  <script src="../../../../../shared/js/stamp.js"></script>

  <!-- yomi.js は読み込まない。英語デッキはカタカナの読みを一切持たない
       (sandbox/drafts/en/AGENTS.md) — ラテン文字は学習者が初日から読めるので
       読み仮名は何も支えず、モーラ拍のカタカナ英語を教え込むだけになる。 -->

</body>
</html>
'''


# ============================================================================
# The decks
# ============================================================================

DECKS = {}


def register(key, **spec):
    DECKS[key] = spec


# ============================================================================
# WHAT EACH BAND TEACHES
#
# One real lesson per band, lifted whole out of the track it belongs to. The four
# together are the same ladder the Korean trial climbs — patterns, situation, situation,
# free talk — minus the rung Korean needs and English does not, because a Japanese
# learner reads the Latin alphabet on day one and there is no 한글 course to sit below
# Core (sandbox/drafts/en/trial/plan-logic.md §1).
#
#   初級    A1     CORE-12  I start work at nine                      1-core-patterns
#   中級    B1     CTX-5    Ask for directions and confirm the route  2-contextual · travel
#   中上級  B2     CTX-47   Disagree with a senior colleague           2-contextual · business
#   上級    C1     FT-89    What you would really do if you won        3-freetalking
#
# All four sources are `proofread-status: complete` and their declared levels match the
# band they sit in (A1 / A2-B1 / B2 / B2-C1). The four course.yaml descriptions were
# written against these lessons before the lessons were wired in, which is why 中上級
# already promises 仕事の場面で意見を伝えて and 上級 already says フリートーキング.
#
# 初級 is trimmed to roughly 60% of its source; the other three are lifted whole. The
# reason is not that the beginner deck matters less — it is that a pattern lesson has to
# be walked in order, so a trial that runs out of clock mid-pattern ends on a drill. The
# other three degrade gracefully: a situation lesson can drop its last transfer scene and
# the free-talk lesson is explicitly a question *pool* whose own tutor note says to skip
# freely and leave 2–3 minutes for feedback. Where the clock stops is the tutor's call
# there, and the deck already tells them how to make it.
# ============================================================================


# ---------------------------------------------------------------------------
# 初級 · CORE-12
#
# 25 minutes, and the report takes the last seven of them. So the lesson body is roughly
# 60% of the standard deck: pattern 1 keeps its full arc, pattern 2 is taught and drilled
# only as far as the conversation needs, and the conversation itself is kept whole —
# it is the page that makes a trial feel like a lesson rather than an exercise sheet.
# Dropped from the source deck: p1-rule, p1-fill, p1-translate, p2-rule, p2-reorder,
# p2-fill, p2-translate, p2-write, in-the-wild.
# ---------------------------------------------------------------------------

T1_SOURCE = "1-core-patterns/courses/core-first-exchanges-2/lessons/12-i-start-work-at-nine/lesson.html"

T1_LESSON = ["words-you-know",
          "part1-intro", "p1-teach", "p1-read", "p1-choose", "p1-reorder", "p1-write",
          "part2-intro", "p2-teach", "p2-read", "p2-choose",
          "part3-intro", "p3-model", "p3-complete", "p3-freetalk",
          "native-tip"]

T1_GREETING = [
    [("other", "こんにちは！お会いできてうれしいです。", "Hello! Nice to meet you.", None),
     ("me", "こんにちは！", "Hello!", "先生のことばに、返事してみましょう！")],
    [("other", "私は（名前）です。お名前は何ですか？",
      'I\'m <input class="slot-input" data-sync-id="greeting-tutor-name" placeholder="name" aria-label="tutor name" autocomplete="off">. '
      "What&#x27;s your name?", None),
     ("me", "私は ＿(名前)＿ です。",
      'I\'m <input class="slot-input" data-sync-id="greeting-student-name" placeholder="name" aria-label="student name" autocomplete="off">.',
      "お名前を入れて言ってみましょう！")],
    [("other", "では、今日のレッスンを始めますね。", "OK, let&#x27;s start today&#x27;s lesson.", None),
     ("me", "はい、お願いします！", "Yes, let&#x27;s go!", "先生のことばに、返事してみましょう！")],
]

T1_PROMISE = ("ここから25分。終わるころには、自分の一日の始まりと終わりを英語で言えて、"
              "相手にも聞けるようになります。約束します！")

T1_LESSON_GOAL = '''
    <div class="transition-page" data-page-id="lesson-goal" data-act="Talking about your day">
      <span class="transition-kicker">GOAL</span>
      <h2 class="transition-title">Today&#x27;s goal <span class="title-ja">(今日のゴール)</span></h2>
      <p class="section-subtitle"><span class="ko">By the end of today, you&#x27;ll be able to talk about your day like this.</span><span class="ja">今日が終わるころには、こんなふうに自分の一日を話せるようになります。</span></p>
      <div class="tutor-note">Read the three lines aloud once so the learner hears the shape, then move on.</div>
      <div class="known lines">
        <div class="known-row"><span class="k">What time do you start work?</span><span class="j">何時に仕事を始めますか？</span></div>
        <div class="known-row"><span class="k">I start work at nine.</span><span class="j">9時に仕事を始めます</span></div>
        <div class="known-row"><span class="k">I usually finish work around six.</span><span class="j">ふだん6時ごろ仕事を終えます</span></div>
      </div>
    </div>
'''

T1_RESULT = '''
    <div class="section" data-page-id="todays-result">
      <h2 class="section-title">Today&#x27;s result <span class="title-ja">(今日の成果)</span></h2>
      <p class="section-subtitle"><span class="ko">Twenty-five minutes ago you had none of these.</span><span class="ja">25分前は、まだ1つもありませんでした。</span></p>
      <div class="payoff">
        <span class="eqline">動作 4 × 時刻 6</span>
        <span class="big">24</span>
        <span class="cap">今日言えるようになった文の数</span>
      </div>
    </div>
'''


# ---------------------------------------------------------------------------
# The unscripted greeting — every band above 初級
#
# Four questions, and none of the answers are written down. The last one doubles as a
# lead-in to ニーズ把握: a learner who has just said out loud when they actually need
# English answers 学ぶきっかけ two pages later with that already in mind.
# ---------------------------------------------------------------------------

OPEN_GREETING = [
    ('Hello! I&#x27;m <input class="slot-input" data-sync-id="greeting-tutor-name" placeholder="name" aria-label="tutor name" autocomplete="off">. '
     "It&#x27;s nice to meet you.",
     "こんにちは！私は＿＿＿です。お会いできてうれしいです。",
     "あいさつを返してみましょう", "greeting-hello"),
    ("What&#x27;s your name? Please tell me a little about yourself.",
     "お名前は何ですか？かんたんに自己紹介もお願いします。",
     "名前と、自分のことを言ってみましょう", "greeting-selfintro"),
    ("How long have you been studying English, and how do you study now?",
     "英語の勉強はどのくらいですか？最近はどうやって勉強していますか？",
     "勉強の期間と、今のやり方を言ってみましょう", "greeting-study"),
    ("When do you actually need English?",
     "実際に英語が必要になるのは、どんなときですか？",
     "英語を使う場面を言ってみましょう", "greeting-need"),
]


# ---------------------------------------------------------------------------
# 中級 · CTX-5 · Ask for directions and confirm the route
#
# Lifted whole. The one page dropped is the source's own lesson-goal, which reads the
# lesson title aloud; the trial replaces it with the promise below, because a learner who
# has not bought anything yet needs to be told what they will walk out able to do, not
# what the lesson is called.
#
# Travel rather than business at this band on purpose. The trial is booked before anyone
# knows the learner's motive — 学ぶきっかけ is asked four pages earlier and is not read
# by the deck — so the middle band has to be the situation with the widest floor.
# Travel opens at Core 47 and Business not until Core 70 (plan-logic.md §1).
# ---------------------------------------------------------------------------

T2_SOURCE = ("2-contextual-english/courses/ctx-travel-arrivals-transport"
             "/lessons/05-ask-for-directions-and-confirm-the-route/lesson.html")

T2_LESSON = ["scene", "understand", "expressions",
             "part1-intro", "p1-teach", "p1-read", "p1-rule", "p1-reorder", "p1-fill",
             "p1-translate", "p1-write",
             "part2-intro", "p2-teach", "p2-read", "p2-rule", "p2-reorder", "p2-fill",
             "p2-translate", "p2-write",
             "part3-intro", "p3-model", "p3-complete", "p3-freetalk",
             "transfer-scene"]

T2_PROMISE = ("ここから25分。終わるころには、英語で道をたずねて、"
              "教わった行き方をその場で確認できるようになります。約束します！")

T2_LESSON_GOAL = '''
    <div class="transition-page" data-page-id="lesson-goal" data-act="Asking the way">
      <span class="transition-kicker">GOAL</span>
      <h2 class="transition-title">Today&#x27;s goal <span class="title-ja">(今日のゴール)</span></h2>
      <p class="section-subtitle"><span class="ko">By the end of today, you&#x27;ll be able to ask the way and check the route like this.</span><span class="ja">今日が終わるころには、こんなふうに道をたずねて、行き方を確認できるようになります。</span></p>
      <div class="tutor-note">Read the three lines aloud once so the learner hears the shape, then move on.</div>
      <div class="known lines">
        <div class="known-row"><span class="k">Can I help you find something?</span><span class="j">どこかお探しですか？</span></div>
        <div class="known-row"><span class="k">How do I get to the museum?</span><span class="j">美術館にはどう行けばいいですか？</span></div>
        <div class="known-row"><span class="k">Do I take the north exit first?</span><span class="j">最初に北口を出ますか？</span></div>
      </div>
    </div>
'''

# 2 patterns × 4 fillers each: How do I get to {the museum, the hotel, the airport,
# the bus stop}? and Do I {take the north exit, cross the road, turn left, take the bus}
# first? The numbers are counted off the source deck's own drill pages — if the lesson
# changes its fillers, this page has to change with it.
T2_RESULT = '''
    <div class="section" data-page-id="todays-result">
      <h2 class="section-title">Today&#x27;s result <span class="title-ja">(今日の成果)</span></h2>
      <p class="section-subtitle"><span class="ko">Twenty-five minutes ago you had none of these.</span><span class="ja">25分前は、まだ1つもありませんでした。</span></p>
      <div class="payoff">
        <span class="eqline">聞き方 2 × 行き先・手順 4</span>
        <span class="big">8</span>
        <span class="cap">今日言えるようになった文の数</span>
      </div>
    </div>
'''


# ---------------------------------------------------------------------------
# 中上級 · CTX-47 · Disagree with a senior colleague constructively
#
# Lifted whole, source lesson-goal excepted, same as 中級.
#
# This is the band where a trial has to prove it is not a conversation class. The learner
# can already talk; what they cannot do is disagree with someone senior without either
# softening it into nothing or giving offence, and that is a thing a curriculum teaches
# and a chat partner does not.
# ---------------------------------------------------------------------------

T3_SOURCE = ("2-contextual-english/courses/ctx-business-meetings-decisions"
             "/lessons/47-disagree-with-a-senior-colleague-constructively/lesson.html")

T3_LESSON = ["scene", "understand", "expressions",
             "part1-intro", "p1-teach", "p1-read", "p1-fill", "p1-translate", "p1-write",
             "part2-intro", "p2-teach", "p2-read", "p2-fill", "p2-translate", "p2-write",
             "part3-intro", "p3-model", "p3-complete", "p3-freetalk",
             "native-tip", "transfer-scene"]

T3_PROMISE = ("ここから25分。終わるころには、目上の相手の考えをきちんと認めたうえで、"
              "気になる点を英語で具体的に伝えられるようになります。約束します！")

T3_LESSON_GOAL = '''
    <div class="transition-page" data-page-id="lesson-goal" data-act="Disagreeing constructively">
      <span class="transition-kicker">GOAL</span>
      <h2 class="transition-title">Today&#x27;s goal <span class="title-ja">(今日のゴール)</span></h2>
      <p class="section-subtitle"><span class="ko">By the end of today, you&#x27;ll be able to push back on a senior colleague like this.</span><span class="ja">今日が終わるころには、こんなふうに目上の同僚に異議を伝えられるようになります。</span></p>
      <div class="tutor-note">Read the three lines aloud once so the learner hears the shape, then move on.</div>
      <div class="known lines">
        <div class="known-row"><span class="k">We can meet the date if we skip the final test.</span><span class="j">最終テストを省けば日程に間に合います。</span></div>
        <div class="known-row"><span class="k">I see your point, but the timing concerns me.</span><span class="j">おっしゃることは分かりますが、日程が気になります。</span></div>
        <div class="known-row"><span class="k">The part I&#x27;m not comfortable with is skipping the final test.</span><span class="j">私が不安に思うのは、最終テストを省く点です。</span></div>
      </div>
    </div>
'''

# 2 openings × 4 concerns each: I see your point, but {the timing, the cost, the evidence,
# the client impact} concerns me. / The part I'm not comfortable with is {skipping the
# final test, reducing the review time, using unverified data, telling the client later}.
T3_RESULT = '''
    <div class="section" data-page-id="todays-result">
      <h2 class="section-title">Today&#x27;s result <span class="title-ja">(今日の成果)</span></h2>
      <p class="section-subtitle"><span class="ko">Twenty-five minutes ago you had none of these.</span><span class="ja">25分前は、まだ1つもありませんでした。</span></p>
      <div class="payoff">
        <span class="eqline">切り出し方 2 × 懸念 4</span>
        <span class="big">8</span>
        <span class="cap">今日言えるようになった文の数</span>
      </div>
    </div>
'''


# ---------------------------------------------------------------------------
# 上級 · FT-89 · What you would really do if you won the lottery
#
# The whole lesson, its own lesson-goal included — so this band alone has no wrapper goal
# page. A free-talk lesson has no pattern to promise, and a "by the end of today you'll
# be able to say these three sentences" page would be a lie about what the lesson is.
# The Korean 자유 대화 trial reaches the same conclusion and goes straight from the
# promise to the article.
#
# It also has no 今日の成果 page. The payoff of the other three bands is a count of
# sentences the learner could not say an hour ago; here there is nothing to count, and a
# number about effort rather than new ability would undercut the three that mean it.
# The lesson ends where it should — on the tutor's feedback.
#
# The `full` variant, not `accessible`: the band is C1 and full is declared B2-C1.
# ---------------------------------------------------------------------------

T4_SOURCE = ("3-freetalking/courses/talk-what-if-full"
             "/lessons/89-what-you-would-really-do-if-you-won-the-lottery/lesson.html")

T4_LESSON = ["lesson-goal", "article", "lesson-style", "talk-intro",
             "warm-1", "warm-2",
             "q1", "q2", "q3", "q4", "q5", "q6",
             "feedback"]

T4_PROMISE = ("ここから25分。テーマは「宝くじに当たったら」。終わるころには、"
              "思いついたことを英語でそのまま話し、その場で直してもらえます。約束します！")


# ============================================================================
# The four decks
# ============================================================================

register(
    "trial-1",
    id="trial-1-elementary",
    level="A1",
    cover="初級",
    title={"ko": "체험 레슨 · 초급", "en": "Trial lesson · Elementary", "ja": "体験レッスン 初級"},
    source=T1_SOURCE,
    lesson=T1_LESSON,
    greeting=greeting(T1_GREETING),
    promise=T1_PROMISE,
    lesson_goal=T1_LESSON_GOAL,
    result=T1_RESULT,
)

register(
    "trial-2",
    id="trial-2-intermediate",
    level="B1",
    cover="中級",
    title={"ko": "체험 레슨 · 중급", "en": "Trial lesson · Intermediate", "ja": "体験レッスン 中級"},
    source=T2_SOURCE,
    lesson=T2_LESSON,
    greeting=open_greeting(OPEN_GREETING),
    promise=T2_PROMISE,
    lesson_goal=T2_LESSON_GOAL,
    result=T2_RESULT,
)

register(
    "trial-3",
    id="trial-3-upper-intermediate",
    level="B2",
    cover="中上級",
    title={"ko": "체험 레슨 · 중고급", "en": "Trial lesson · Upper-intermediate", "ja": "体験レッスン 中上級"},
    source=T3_SOURCE,
    lesson=T3_LESSON,
    greeting=open_greeting(OPEN_GREETING),
    promise=T3_PROMISE,
    lesson_goal=T3_LESSON_GOAL,
    result=T3_RESULT,
)

register(
    "trial-4",
    id="trial-4-advanced",
    level="C1",
    cover="上級",
    title={"ko": "체험 레슨 · 고급", "en": "Trial lesson · Advanced", "ja": "体験レッスン 上級"},
    source=T4_SOURCE,
    lesson=T4_LESSON,
    greeting=open_greeting(OPEN_GREETING),
    promise=T4_PROMISE,
    lesson_goal="",
    result="",
    freetalk=True,
)


def build(key):
    spec = DECKS[key]
    pg = take(TRACKS / spec["source"], spec["lesson"])
    out = [
        head(spec["id"], spec["level"], spec["title"], spec["cover"]),
        spec["greeting"],
        NEEDS,
        trial_intro(spec["promise"]),
        # Empty on 上級 — a free-talk lesson has no pattern to promise, so it carries the
        # source deck's own lesson-goal as its first page instead.
        spec["lesson_goal"],
    ]
    for pid in spec["lesson"]:
        out.append("\n    " + pg[pid] + "\n")
    # Empty result on 上級 too: nothing countable came out of a conversation.
    out += [spec["result"], CLOSING, tutor_score(), tail(spec.get("freetalk", False))]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    target = OUT_DIR / (spec["id"] + ".html")
    io.open(target, "w", encoding="utf-8").write("".join(out))
    return target


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("decks", nargs="*", help="deck keys to build (default: all)")
    args = ap.parse_args()
    wanted = args.decks or sorted(DECKS)
    unknown = [d for d in wanted if d not in DECKS]
    if unknown:
        sys.exit("unknown deck(s): %s — known: %s" % (unknown, sorted(DECKS)))
    for key in wanted:
        print("wrote", build(key).relative_to(ROOT))


if __name__ == "__main__":
    main()

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
CONTENT_VERSION = "2026-08-26"


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


def check_complete(src, spec):
    """Fail if the source has a page this band neither uses nor declares it is skipping.

    `take` already catches the easy direction — a listed page that no longer exists stops
    the build. This is the other direction, and it is the one that bit us: a source lesson
    rewritten under a *stable* page set drifts away from a hand-written page list without
    anything failing at all. 初級 shipped three days of a superseded CORE-12 that way.

    So a band must account for every page in its source. Dropping one is allowed and
    sometimes right — say so in `omit`, next to the page list, where the next person
    reading the band can see the cut and its cost together.
    """
    extra = sorted(set(pages(src)) - set(spec["lesson"]) - set(spec.get("omit", ())))
    if extra:
        sys.exit(
            "%s: source has page(s) this band neither uses nor omits: %s\n"
            "  The source lesson has probably been reworked. Re-read the band's page list "
            "against it, then either add the page to `lesson` or name it in `omit`."
            % (spec["id"], ", ".join(extra)))


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
      <img class="brand-art mid" src="../assets/podo-character-happy.png" alt="">
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
    actually said. `asks` is a list of (lines, task_ja, sync_id), where `lines` is one or
    more (en, ja) tutor bubbles sharing a single answer box: the tutor's questions in
    English with their Japanese underneath, the one-line Japanese prompt over the answer
    box, and the sync id that carries the answer to the other screen.

    `lines` is a list because of the greeting. The hello and the question after it are one
    move by the tutor and take one answer, but said in a single bubble they make a block of
    text the learner has to find the question inside. Two short bubbles, one answer box.

    This page is also the first thing the tutor scores on. Three unscripted answers before
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
    for i, (lines, task, sid) in enumerate(asks):
        style = ' style="margin-top:var(--item-gap);"' if i else ''
        out.append(f'\n      <div class="dialogue"{style}>')
        for en, ja in lines:
            out.append(
                f'<div class="turn other"><span class="who">{ICON}'
                f'<span class="who-name">Tutor</span></span>'
                f'<div class="bubble"><span class="korean">{en}</span>'
                f'<span class="translation">{ja}</span></div></div>')
        out.append(
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
         only thing that makes the plan this learner's rather than anyone's.

         The divider says it in both languages. It carried Japanese only until 2026-08-26,
         which left an English-speaking tutor with nothing to read at the moment they have
         to ask a learner for personal information — the first version of this fix hid the
         English in a tutor-only note, but a line the learner is allowed to hear does not
         need hiding, and the page already pairs its languages everywhere else. -->
    <div class="brand-page bleed" data-page-id="needs-intro">
      <h2 class="brand-title">ニーズ把握<span class="en" style="display:block;margin-top:5px;font-size:21px;font-weight:800;color:rgba(28,28,28,.56);letter-spacing:-.01em;line-height:1.25;">Needs Analysis</span></h2>
      <p class="brand-sub">学習のニーズについて、少し教えてください。<span class="en" style="display:block;margin-top:3px;font-size:13px;font-weight:600;color:rgba(28,28,28,.5);line-height:1.45;">Please tell me a little about your learning needs.</span></p>
      <div class="tutor-note" style="text-align:left;">Read both lines, then move on — the questions are on the next three pages, not this one.</div>
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


TRIAL_INTRO = '''
    <div class="brand-page divider" data-page-id="trial-intro">
      <h2 class="brand-title">体験レッスン<span class="en" style="display:block;margin-top:5px;font-size:21px;font-weight:800;color:rgba(28,28,28,.56);letter-spacing:-.01em;line-height:1.25;">Trial lesson</span></h2>
      <p class="brand-sub">ここから体験レッスンです。通常のレッスンより少し短めです。<span class="en" style="display:block;margin-top:3px;font-size:13px;font-weight:600;color:rgba(28,28,28,.5);line-height:1.45;">We&#x27;ll start the trial lesson now. It&#x27;s a little shorter than a regular class.</span></p>
      <img class="brand-art study" src="../assets/podo-character-study.png" alt="">
    </div>
'''
# The page that starts the clock, and the only thing it has to do is start it. Both
# languages are on it because the tutor of an English trial cannot read a Japanese
# promise aloud; before 2026-08-26 this page was Japanese only and the tutor had no line
# for the moment the lesson begins.
#
# It carried a per-band can-do promise until 2026-08-26 — "by the end you'll be able
# to disagree with a senior colleague", and so on, one per band, ending in 約束します！.
# Cut in the trial review: the tutor should say the class is starting and that it runs
# short, and nothing else. The trade is real and was made deliberately — this was the
# deck's one sales moment.
#
# For a day the 初級 goal page inherited that job, and no other band had anything in its
# place. Unifying the goal pages with the lessons removed it there too, so no trial deck
# now promises an outcome: the learner sees the lesson's title, exactly as an enrolled
# learner does, and what they get is demonstrated over the next thirty pages rather than
# stated on page eight. If the promise has to come back, it belongs here — one page, all
# four bands — not in a goal page that then stops matching the lesson it was lifted from.


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
    the farewell, so it is filled in once the learner has gone. Both blocks below
    (.lvcheck and .axsteps) are `display:none` outside teaching mode, so a learner who is
    still in the room when the tutor pages forward lands on nothing but the sign-off line.

    The note used to say "there is no rush". It was true and it was the wrong thing to
    say: a tutor told there is no rush does it later, and later is never — the report the
    learner is waiting on in the chat cannot be built until this page is submitted.

    Two sentences, and both of them earn their place: score it now, and here is what a dead
    Submit button means. The second one is not padding — the button is disabled by 学ぶきっかけ
    and ゴール two-thirds of the way back through the deck (report.js `missing()`), and
    nothing on this page says so. A longer version of this note was tried and cut; a tutor
    reads a note like this once, at the end of a class, with the learner just gone.
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
      <div class="tutor-note">Score this right after class — the learner&#x27;s report is built from what you pick. If Submit won&#x27;t click, something here or on the ニーズ把握 pages is unanswered.</div>

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
        <div class="rep-send">
          <span class="rep-send-h">Ready to submit? <small>tutor only</small></span>
          <p class="rs-confirm">Check any answer above, then submit this diagnosis.</p>
          <button class="rs-btn" type="button" disabled>Submit diagnosis</button>
          <p class="rs-msg"></p>
        </div>
      </div>
    </div>
'''


# The goodbye. Japanese leads and the English rides under each line, because this card is a
# Figma design the learner reads, not a teaching page — putting English on top of it turned
# the sign-off into a lesson. The tutor still gets every line they have to say.
#
# The arch is the exception and is English outright: it is one short exclamation over the
# mascot, and a second line curved along the same path would be unreadable.
#
# The report block keeps Japanese only. It tells the learner about a chat message that
# arrives after class — nobody performs it in the room — so its English is in the tutor note
# instead, which is also why that note sits inside the card: the closing page positions the
# arch, the mascot and the card absolutely, so a note in the page's own flow would render on
# top of the arch rather than under the thing it explains.
CLOSING = '''
    <div class="brand-page end bleed" data-page-id="closing">
      <svg class="end-arch" viewBox="0 0 480 300" aria-hidden="true">
        <path id="endArch" d="M 70 255 Q 237 135 404 258" fill="none"></path>
        <text><textPath href="#endArch" startOffset="50%" text-anchor="middle">Great work today!</textPath></text>
      </svg>
      <img class="end-art" src="../assets/podo-3d-bye.png" alt="">
      <div class="end-card">
        <div class="end-bar"><span>Welcome to PODO</span><span class="end-check">✓</span></div>
        <p class="end-title"><span class="hl">体験レッスン</span>は<br>ここまでです！<span class="en" style="display:block;margin-top:7px;font-size:14px;font-weight:800;color:#6f7568;letter-spacing:0;line-height:1.3;">That&#x27;s our trial lesson!</span></p>
        <p class="end-copy">今日はお話しできて楽しかったです。<span class="en" style="display:block;margin-top:2px;font-size:11.5px;font-weight:600;color:#8b9084;line-height:1.45;">I really enjoyed talking with you today.</span><strong style="display:block;margin-top:10px;">次はもっと気楽に、もっとたくさん話せるようになります ;)</strong><span class="en" style="display:block;margin-top:2px;font-size:11.5px;font-weight:600;color:#8b9084;line-height:1.45;">Next time you&#x27;ll speak more easily, and a lot more.</span></p>
        <div class="end-report">
          <span class="badge-dark">このあとのチャットで</span>
          <span class="t">あなただけの英語 診断レポート</span>
          <span class="s">担当スタッフがお届けします。</span>
        </div>
        <div class="tutor-note" style="text-align:left;">Green box: &quot;Your own English report arrives in the chat after class.&quot;</div>
      </div>
    </div>
'''


def tail(freetalk=False):
    """Everything after the last page. `freetalk` adds the script FT decks need.

    freetalk-activities.js wires the no-right-answer pickers (.opt-list[data-pick]) that
    the three conversation decks have on their 会話スタイル page. It deliberately skips lists
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
# One real lesson per band, lifted whole out of the track it belongs to. 初級 demonstrates
# the pattern curriculum; the three speaking bands use the topics selected for the Japan
# trial launch by the English team lead. A Japanese learner reads the Latin alphabet on day
# one, so English has no 한글 course below Core (sandbox/drafts/en/trial/plan-logic.md §1).
#
#   初級    A1     CORE-12  I start work at nine                      1-core-patterns
#   中級    B1     FT-3     A Japanese food everyone should try       3-freetalking · accessible
#   中上級  B2     FT-113   Life in the city or the countryside?      3-freetalking · accessible
#   上級    C1     FT-5     A place you would show a visitor          3-freetalking · full
#
# All four are lifted whole, lesson-goal included. 初級 substituted its own goal page —
# 今日のゴール over three preview lines — until 2026-08-26; it was the only page in any of
# the four decks not lifted from a lesson, and the only English goal page in the corpus
# with that shape. A trial is the lesson, so its opening is the lesson's opening: the
# lesson's own title, read aloud once. See the 初級 section below for what that costs.
#
# No band has a 今日の成果 payoff page. Three of them did until 2026-08-26 — a lime card
# reading 動作 4 × 時刻 6 = 24, or 聞き方 2 × 行き先 4 = 8. The multiplication was the
# problem: it counted sentences the learner had never said, off filler lists in the source
# deck, and presented the product as what they walked out with. 上級 never had one because
# a conversation has nothing to count, which was the tell. Cut in the trial review; the
# deck now goes from the last lesson page straight to the goodbye.
#
# None of them is cut to fit 25 minutes, and that is deliberate. A trial deck is not a
# 25-minute lesson; it is the lesson, with the tutor deciding live how far to get. Cutting
# it here would move that judgement from the person in the room to whoever last edited
# this file, and the decks already tell the tutor how to make it: the free-talk lesson is
# explicitly a question *pool* whose tutor note says to skip freely and leave 2–3 minutes
# for feedback, and the situation lessons end on a transfer scene that is the natural
# thing to drop when the clock is short.
#
# 初級 was the exception until 2026-08-24 for reasons that turned out not to be reasons.
# See its section below.
# ============================================================================


# ---------------------------------------------------------------------------
# 初級 · CORE-12 · I start work at nine
#
# Lifted whole, exactly like the other three — including the source lesson-goal, since
# 2026-08-26. What it replaced is described in the band table above.
#
# This band carried a 16-page cut until 2026-08-24, described here as a deliberate 60%
# trim. It was not one. The list was written on 08-21 against a lesson that was still
# being finished: `d0129074d` (08-22) fixed the alternating answer positions and
# `3b2507165` (08-23) moved all sixteen activity pages onto the approved shared activity
# script — including all eight the cut dropped. Nobody revisited the list afterwards, so
# the trial spent three days showing a version of CORE-12 that had been superseded, and
# the comment explaining why read as a decision about a lesson that did not exist yet.
#
# The general point, which is why this is written down rather than quietly fixed: the
# generator keeps page *content* current automatically — that is the whole reason it
# exists — but the page *list* is frozen prose, and nothing checks it against the source.
# A lesson that gains or loses a page fails loudly in `take()`; a lesson that is rewritten
# under a stable page set does not fail at all. When a source lesson is reworked, re-read
# the band's page list. Do not trust a rationale in this file over the source's own log.
# ---------------------------------------------------------------------------

T1_SOURCE = "1-core-patterns/courses/core-first-exchanges-2/lessons/12-i-start-work-at-nine/lesson.html"

T1_LESSON = ["lesson-goal", "words-you-know",
             "part1-intro", "p1-teach", "p1-read", "p1-rule", "p1-choose", "p1-reorder",
             "p1-fill", "p1-translate", "p1-write",
             "part2-intro", "p2-teach", "p2-read", "p2-rule", "p2-choose", "p2-reorder",
             "p2-fill", "p2-translate", "p2-write",
             "part3-intro", "p3-model", "p3-complete", "p3-freetalk",
             "in-the-wild", "native-tip"]

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


# ---------------------------------------------------------------------------
# The unscripted greeting — every band above 初級
#
# Three questions, and none of the answers are written down. The last one doubles as a
# lead-in to ニーズ把握: a learner who has just said out loud when they actually need
# English answers 学ぶきっかけ two pages later with that already in mind.
#
# The hello and the name are two bubbles under ONE answer box. Until 2026-08-26 they were
# two bubbles under two boxes, and the first box had nothing in it to say — the tutor said
# hello, waited for a written "Hello!", then said hello's other half. Andrew cut that box
# in the trial review: the greeting is one move by the tutor, and the learner's first real
# turn is the self-introduction. Merging the two bubbles as well was a step too far — one
# bubble carrying a greeting, a name and a request for a self-introduction reads as a wall,
# and the question the learner has to answer is buried at the end of it.
# ---------------------------------------------------------------------------

OPEN_GREETING = [
    ([('Hello! I&#x27;m <input class="slot-input" data-sync-id="greeting-tutor-name" placeholder="name" aria-label="tutor name" autocomplete="off">. '
      "It&#x27;s nice to meet you.",
      "こんにちは！私は＿＿＿です。お会いできてうれしいです。"),
      ("What&#x27;s your name? Please tell me a little about yourself.",
       "お名前は何ですか？かんたんに自己紹介もお願いします。")],
     "名前と、自分のことを言ってみましょう", "greeting-selfintro"),
    ([("How long have you been studying English, and how do you study now?",
       "英語の勉強はどのくらいですか？最近はどうやって勉強していますか？")],
     "勉強の期間と、今のやり方を言ってみましょう", "greeting-study"),
    ([("When do you actually need English?",
       "実際に英語が必要になるのは、どんなときですか？")],
     "英語を使う場面を言ってみましょう", "greeting-need"),
]


# ---------------------------------------------------------------------------
# 中級 · FT-3 accessible · A Japanese food everyone should try
#
# The English team lead selected the accessible version of lesson 03 for the Japan trial.
# It is lifted whole, including its goal, article, conversation-style choice, question pool,
# and feedback page.
# ---------------------------------------------------------------------------

T2_SOURCE = ("3-freetalking/courses/talk-between-two-countries-accessible"
             "/lessons/03-a-japanese-food-everyone-should-try/lesson.html")

T2_LESSON = ["lesson-goal", "article", "lesson-style", "talk-intro",
             "warm-1", "warm-2",
             "q1", "q2", "q3", "q4", "q5", "q6",
             "feedback"]



# ---------------------------------------------------------------------------
# 中上級 · FT-113 accessible · Life in the city or the countryside?
#
# The English team lead selected the accessible version of Balance Games lesson 113 for
# the Japan trial. It is lifted whole for the same reason as 中級.
# ---------------------------------------------------------------------------

T3_SOURCE = ("3-freetalking/courses/talk-balance-games-accessible"
             "/lessons/113-life-in-the-city-or-the-countryside/lesson.html")

T3_LESSON = ["lesson-goal", "article", "lesson-style", "talk-intro",
             "warm-1", "warm-2",
             "q1", "q2", "q3", "q4", "q5", "q6",
             "feedback"]



# ---------------------------------------------------------------------------
# 上級 · FT-5 full · A place you would show a visitor
#
# The whole lesson, its own lesson-goal included — so this band alone has no wrapper goal
# page. A free-talk lesson has no pattern to promise, and a "by the end of today you'll
# be able to say these three sentences" page would be a lie about what the lesson is.
# The Korean 자유 대화 trial reaches the same conclusion and goes straight from the
# promise to the article.
#
# The lesson ends where it should — on the tutor's feedback.
#
# The English team lead selected the Advanced (full) version of lesson 05. The `full`
# variant matches this band: it is declared B2-C1.
# ---------------------------------------------------------------------------

T4_SOURCE = ("3-freetalking/courses/talk-between-two-countries-full"
             "/lessons/05-a-place-you-would-show-a-visitor/lesson.html")

T4_LESSON = ["lesson-goal", "article", "lesson-style", "talk-intro",
             "warm-1", "warm-2",
             "q1", "q2", "q3", "q4", "q5", "q6",
             "feedback"]




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
    lesson_goal="",
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
    lesson_goal="",
    freetalk=True,
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
    lesson_goal="",
    freetalk=True,
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
    lesson_goal="",
    freetalk=True,
)


def build(key):
    spec = DECKS[key]
    src = TRACKS / spec["source"]
    check_complete(src, spec)
    pg = take(src, spec["lesson"])
    out = [
        head(spec["id"], spec["level"], spec["title"], spec["cover"]),
        spec["greeting"],
        NEEDS,
        TRIAL_INTRO,
        # Empty on every band: all four carry the source lesson's own goal page, lifted
        # with the rest. Kept as a seam — a band that ever needs a wrapper goal puts it
        # here, ahead of the lifted pages, and names lesson-goal in `omit`.
        spec["lesson_goal"],
    ]
    for pid in spec["lesson"]:
        out.append("\n    " + pg[pid] + "\n")
    out += [CLOSING, tutor_score(), tail(spec.get("freetalk", False))]

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

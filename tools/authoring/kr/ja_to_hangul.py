#!/usr/bin/env python3
"""Write a Japanese kana string in Hangul, per 국립국어원 외래어 표기법 제2장 표4.

This exists for one line in the deck: .anchor-ko, the reading under the
Japanese in a 뜻과 쓰임 box. A Korean tutor is asked to say that Japanese out
loud, and we do not assume they read kana. The reading is a crutch for the
tutor, not a pronunciation model for the learner — the learner already knows
the Japanese and is looking at it directly.

Following 표기법 rather than transcribing by ear is the whole point: it is a
rule, so 164 anchors come out consistent, and it happens to be closer to the
Japanese anyway. か word-initially is 가, not 카, because Japanese /k/ there is
unaspirated and Korean ㄱ is the nearer sound. Transcribing by ear is what
produces 카모시레나이, and then the next author writes 가모시레나이 and the deck
has two spellings of the same word.

What it will NOT do is kanji: 聞く has a reading only a reader knows. Those come
back as None with the kanji named, and are written by hand — see KANJI below
for the ones this curriculum actually uses.

  python3 tools/authoring/kr/ja_to_hangul.py '~かもしれない'      → 가모시레나이
  python3 tools/authoring/kr/ja_to_hangul.py --self-test
"""
import re
import sys

# ---- 표4. か행과 た행만 어두/어중이 갈린다 ---------------------------------
#      (어두, 어중·어말).  나머지는 두 자리가 같다.
MORA = {
    "あ": ("아", "아"), "い": ("이", "이"), "う": ("우", "우"), "え": ("에", "에"), "お": ("오", "오"),
    "か": ("가", "카"), "き": ("기", "키"), "く": ("구", "쿠"), "け": ("게", "케"), "こ": ("고", "코"),
    "さ": ("사", "사"), "し": ("시", "시"), "す": ("스", "스"), "せ": ("세", "세"), "そ": ("소", "소"),
    "た": ("다", "타"), "ち": ("지", "치"), "つ": ("쓰", "쓰"), "て": ("데", "테"), "と": ("도", "토"),
    "な": ("나", "나"), "に": ("니", "니"), "ぬ": ("누", "누"), "ね": ("네", "네"), "の": ("노", "노"),
    "は": ("하", "하"), "ひ": ("히", "히"), "ふ": ("후", "후"), "へ": ("헤", "헤"), "ほ": ("호", "호"),
    "ま": ("마", "마"), "み": ("미", "미"), "む": ("무", "무"), "め": ("메", "메"), "も": ("모", "모"),
    "や": ("야", "야"), "ゆ": ("유", "유"), "よ": ("요", "요"),
    "ら": ("라", "라"), "り": ("리", "리"), "る": ("루", "루"), "れ": ("레", "레"), "ろ": ("로", "로"),
    "わ": ("와", "와"), "を": ("오", "오"),
    "が": ("가", "가"), "ぎ": ("기", "기"), "ぐ": ("구", "구"), "げ": ("게", "게"), "ご": ("고", "고"),
    "ざ": ("자", "자"), "じ": ("지", "지"), "ず": ("즈", "즈"), "ぜ": ("제", "제"), "ぞ": ("조", "조"),
    "だ": ("다", "다"), "ぢ": ("지", "지"), "づ": ("즈", "즈"), "で": ("데", "데"), "ど": ("도", "도"),
    "ば": ("바", "바"), "び": ("비", "비"), "ぶ": ("부", "부"), "べ": ("베", "베"), "ぼ": ("보", "보"),
    "ぱ": ("파", "파"), "ぴ": ("피", "피"), "ぷ": ("푸", "푸"), "ぺ": ("페", "페"), "ぽ": ("포", "포"),
    # 요음
    "きゃ": ("갸", "캬"), "きゅ": ("규", "큐"), "きょ": ("교", "쿄"),
    "ぎゃ": ("갸", "갸"), "ぎゅ": ("규", "규"), "ぎょ": ("교", "교"),
    "しゃ": ("샤", "샤"), "しゅ": ("슈", "슈"), "しょ": ("쇼", "쇼"),
    "じゃ": ("자", "자"), "じゅ": ("주", "주"), "じょ": ("조", "조"),
    "ちゃ": ("자", "차"), "ちゅ": ("주", "추"), "ちょ": ("조", "초"),
    "にゃ": ("냐", "냐"), "にゅ": ("뉴", "뉴"), "にょ": ("뇨", "뇨"),
    "ひゃ": ("햐", "햐"), "ひゅ": ("휴", "휴"), "ひょ": ("효", "효"),
    "びゃ": ("뱌", "뱌"), "びゅ": ("뷰", "뷰"), "びょ": ("뵤", "뵤"),
    "ぴゃ": ("퍄", "퍄"), "ぴゅ": ("퓨", "퓨"), "ぴょ": ("표", "표"),
    "みゃ": ("먀", "먀"), "みゅ": ("뮤", "뮤"), "みょ": ("묘", "묘"),
    "りゃ": ("랴", "랴"), "りゅ": ("류", "류"), "りょ": ("료", "료"),
    # katakana extensions, written with a small vowel. They only appear in
    # loanwords (ティッシュ, イェ) but a deck glossing 휴지 needs them.
    "いぇ": ("예", "예"), "てぃ": ("티", "티"), "でぃ": ("디", "디"),
    "とぅ": ("투", "투"), "どぅ": ("두", "두"), "ふぁ": ("파", "파"),
    "ふぃ": ("피", "피"), "ふぇ": ("페", "페"), "ふぉ": ("포", "포"),
    "うぃ": ("위", "위"), "うぇ": ("웨", "웨"), "うぉ": ("워", "워"),
    "ヴぁ": ("바", "바"), "しぇ": ("셰", "셰"), "じぇ": ("제", "제"),
    "ちぇ": ("체", "체"), "つぁ": ("차", "차"), "つぉ": ("초", "초"),
}

# the vowel each mora ends on, for the 장음 rule
VOWEL = {}
for _k in MORA:
    VOWEL[_k] = "aiueo"["あいうえお".index(_k[-1])] if _k[-1] in "あいうえお" else \
                {"や": "a", "ゆ": "u", "よ": "o", "ゃ": "a", "ゅ": "u", "ょ": "o",
                 "わ": "a", "を": "o"}.get(_k[-1], "aiueo"[
                     "かさたなはまらがざだばぱ".find(_k[-1]) % 5] if _k[-1] in "かさたなはまらがざだばぱ" else "a")
# the table above is fiddly for the base rows; state them outright instead
for _row, _v in (("あかさたなはまやらわがざだばぱ", "a"),
                 ("いきしちにひみりぎじぢびぴ", "i"),
                 ("うくすつぬふむゆるぐずづぶぷ", "u"),
                 ("えけせてねへめれげぜでべぺ", "e"),
                 ("おこそとのほもよろをごぞどぼぽ", "o")):
    for _c in _row:
        VOWEL[_c] = _v
for _k in MORA:
    if len(_k) == 2:
        VOWEL[_k] = {"ゃ": "a", "ゅ": "u", "ょ": "o",
                     "ぁ": "a", "ぃ": "i", "ぅ": "u", "ぇ": "e", "ぉ": "o"}[_k[1]]

# 받침. 촉음 っ은 'ㅅ', 발음(撥音) ん은 'ㄴ' — 표기법이 예외 없이 하나로 정한다.
JONG = {"っ": 19, "ん": 4}

KATA = {chr(c): chr(c - 0x60) for c in range(0x30A1, 0x30F7)}

# 표기법 transcribes the sound, and the particle は is said /wa/. Which は is a
# particle is grammar, not kana, so this does not guess: は counts as a particle
# only directly after one of these, which covers every anchor in the corpus
# (ことは · のは · ては · では). Any other non-initial は is reported for a human
# — 「やはり」 is 야하리, and a blanket rule would have written 야와리.
PARTICLE_AFTER = set("のてでと")

# The kanji this curriculum's anchors actually use. Kept here rather than in a
# general dictionary because the point is coverage of these decks, and a wrong
# reading is worse than no reading — anything absent comes back as None and
# gets written by a person.
# Kanji, written as KANA — not as Hangul. Storing the Hangul directly looked
# simpler and silently bypassed every positional rule in the table above: 来た
# came out 쿠타 because the entry said 来 is くる's 쿠, and 帰ります came out
# 카에리마스 when 표기법 wants 가에리마스 word-initially. Kana goes back through
# the same engine, so 어두/어중, 촉음 and 장음 all apply for free.
#
# Keyed on whole words wherever okurigana decides the reading — 来る/来た, 降り,
# 差し上げ. A word absent here comes back unresolved; a wrong reading is worse
# than no reading, so this never guesses.
KANJI = {
    "名詞": "めいし", "動詞": "どうし", "形容詞": "けいようし",
    "後": "あと", "前": "まえ", "時間": "じかん", "時": "とき", "人": "ひと",
    "方": "ほう", "何": "なに", "誰": "だれ", "中": "なか", "上手": "じょうず",
    "上": "うえ", "下": "した", "外": "そと", "私": "わたし",
    "聞き": "きき", "聞く": "きく", "聞いて": "きいて",
    "知っている": "しっている", "知らない": "しらない", "知る": "しる",
    "知り": "しり", "知": "し",
    "行き": "いき", "行く": "いく", "行って": "いって", "行った": "いった",
    "思って": "おもって", "思": "おも", "言い": "いい", "言う": "いう",
    "終えたら": "おえたら", "見る": "みる", "見て": "みて",
    "来る": "くる", "来た": "きた", "来ました": "きました", "来て": "きて",
    "食べ": "たべ", "話": "はなし", "作": "つく", "使": "つか",
    "持": "も", "待": "ま", "帰り": "かえり", "帰る": "かえる",
    "出": "で", "入": "はい", "住": "す", "働": "はたら", "休み": "やすみ",
    "途中": "とちゅう", "最中": "さいちゅう", "大丈夫": "だいじょうぶ",
    "一番": "いちばん", "一度": "いちど", "一緒": "いっしょ",
    "本当": "ほんとう", "自分": "じぶん", "気": "き", "度": "ど", "回": "かい",
    "予定": "よてい", "必要": "ひつよう", "必ず": "かならず",
    "会": "あ", "個": "こ", "分": "ふん", "名": "めい",
    "差し上げ": "さしあげ", "召し上が": "めしあが", "申し上げ": "もうしあげ",
    "上げ": "あげ",
    "何個": "なんこ", "何名": "なんめい", "何月": "なんがつ", "何日": "なんにち",
    "何曜日": "なんようび", "曜日": "ようび", "月": "がつ", "日": "にち",
    "全然": "ぜんぜん", "何も": "なにも", "運動": "うんどう", "勉強": "べんきょう",
    "同じ": "おなじ", "価値": "かち", "代わり": "かわり", "別": "べつ",
    "兼ねて": "かねて",
    # vocabulary the read pages gloss
    "早く": "はやく", "早": "はや", "少し": "すこし", "午前": "ごぜん",
    "午後": "ごご", "半": "はん", "祝日": "しゅくじつ", "遠い": "とおい",
    "近い": "ちかい", "近く": "ちかく", "向かい側": "むかいがわ", "茶": "ちゃ",
    "安い": "やすい", "果物": "くだもの", "乗り換え": "のりかえ", "手": "て",
    "箸": "はし", "毎月": "まいつき", "頻度": "ひんど", "今週末": "こんしゅうまつ",
    "今度": "こんど", "約束": "やくそく", "実は": "じつわ",   # 조사 は 는 わ 로 소리 난다 "新年": "しんねん",
    "頑張って": "がんばって", "風邪": "かぜ", "愛着": "あいちゃく",
    "解消": "かいしょう", "存じ": "ぞんじ", "覧": "らん",
    "降り": "ふり", "降": "ふ",
}


def compose(syl, jong):
    """put a 받침 under an already-formed hangul syllable"""
    code = ord(syl) - 0xAC00
    if code < 0 or code > 11171 or code % 28:
        return syl
    return chr(0xAC00 + code + jong)


def reading(text):
    """(hangul, unresolved) — unresolved lists kanji this cannot read"""
    text = "".join(KATA.get(c, c) for c in text)
    text = text.replace("〜", "").replace("~", "").strip()

    # a bare は as the whole string is the particle, said /wa/ — the anchor
    # ~は is the topic marker, not the first mora of a word like はず
    if text == "は":
        return "와", []

    # expand kanji to kana first, so the positional rules below see one script
    # Each character remembers which segment it came from: author-typed kana, or
    # one kanji's expansion. The 장음 rule needs it. おう is a long vowel inside a
    # word (とうきょう → 도쿄) but not across a morpheme boundary: の+上 is のうえ
    # and collapsing it gives 노에, 思(おも)+う gives 오모나라. Same segment only.
    unresolved = []
    expanded, seg, i, sid = "", [], 0, 0
    while i < len(text):
        c = text[i]
        if "一" <= c <= "鿿":
            sid += 1
            for size in (5, 4, 3, 2, 1):
                if text[i:i + size] in KANJI:
                    r = KANJI[text[i:i + size]]
                    expanded += r
                    seg += [sid] * len(r)
                    i += size
                    break
            else:
                unresolved.append(c)
                expanded += "?"
                seg.append(sid)
                i += 1
            sid += 1
        else:
            expanded += c
            seg.append(0)
            i += 1
    text = expanded

    out = []
    i = 0
    prev_vowel = None
    prev_seg = None
    while i < len(text):
        c = text[i]

        # 받침
        if c in JONG:
            if out and out[-1]:
                out[-1] = out[-1][:-1] + compose(out[-1][-1], JONG[c])
            prev_vowel = None
            prev_seg = seg[i]
            i += 1
            continue

        # 장음부호는 적지 않는다
        if c == "ー":
            i += 1
            continue

        if c == "は" and out and text[i - 1] in PARTICLE_AFTER:
            out.append("와")
            prev_vowel = "a"
            i += 1
            continue
        if c == "は" and out:
            unresolved.append("は(조사인지 확인)")

        mora = text[i:i + 2] if text[i:i + 2] in MORA else c
        if mora not in MORA:
            # punctuation, ・, latin — pass it through untouched
            out.append(c)
            prev_vowel = None
            i += 1
            continue

        # 장음: おう / うう / おお 를 적지 않는다 — 같은 형태소 안에서만
        # おお only inside a kanji reading, where this file wrote the kana and
        # knows it is a long vowel (遠い = とおい). In author-typed kana the same
        # two characters are usually a word boundary — ~のおかげで is の + おかげ,
        # and collapsing it gave 노카게데.
        if seg[i] == prev_seg and ((mora == "う" and prev_vowel in ("o", "u"))
                                   or (mora == "お" and prev_vowel == "o"
                                       and seg[i] != 0)):
            i += 1
            continue

        head, tail = MORA[mora]
        # 어두는 문장 첫 자리, 그리고 ・ 로 나뉜 각 낱말의 첫 자리
        at_start = not out or out[-1] in ("・", "·", " ", "/")
        out.append(head if at_start else tail)
        prev_vowel = VOWEL[mora]
        prev_seg = seg[i]
        i += len(mora)

    return "".join(out), unresolved


CASES = [
    ("かもしれない", "가모시레나이"),   # か word-initial → 가, not 카
    ("はずがない", "하즈가나이"),
    ("してみてください", "시테미테쿠다사이"),
    ("とうきょう", "도쿄"),             # 장음 두 군데
    ("さっぽろ", "삿포로"),             # 촉음 → ㅅ 받침
    ("しんぶん", "신분"),               # 발음 → ㄴ 받침
    ("ではありません", "데와아리마센"),   # 조사 は
    ("やはり", "야하리"),               # 조사가 아닌 は
    ("は", "와"),                       # 조사 하나만 있는 앵커
    ("しなくてもいいです", "시나쿠테모이이데스"),
    ("がっこう", "갓코"),      # 촉음은 예외 없이 ㅅ
    ("きょうしつ", "교시쓰"),           # 어두 요음도 か행 규칙을 따른다 (京都 = 교토)
    ("~の上に", "노우에니"),             # の + 上 — 형태소가 달라 장음이 아니다
    ("~しようと思うなら", "시요토오모우나라"),  # 思(おも) + う — 여기도 마찬가지
    ("本当に", "혼토니"),               # 한 형태소 안이라 장음이 맞다
    ("遠い", "도이"),                  # 한자 안의 おお 장음
    ("~のおかげで", "노오카게데"),        # の + おかげ — 장음이 아니다
    ("~と言う", "도이우"),              # いう 는 장음이 아니다
]


def self_test():
    bad = 0
    for src, want in CASES:
        got, _ = reading(src)
        ok = got == want
        bad += not ok
        print(f"  {'ok ' if ok else 'FAIL'} {src:<18}{got:<16}{'' if ok else '≠ ' + want}")
    print(f"\n{len(CASES) - bad}/{len(CASES)} pass")
    return 1 if bad else 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    for arg in sys.argv[1:]:
        got, un = reading(arg)
        print(got + (f"   ← 한자 미해결: {un}" if un else ""))

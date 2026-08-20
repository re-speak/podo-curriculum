#!/usr/bin/env python3
"""Generate the explicit CORE-60--70 Careful Interaction batch."""

from __future__ import annotations

import argparse
import contextlib
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import generate_core_course_batch as core
import generate_core_experience_and_ideas_batch as approved
import new_lesson


ROOT = new_lesson.REPO
TRACK = new_lesson.ENGLISH / "tracks/1-core-patterns"
COURSE = "core-careful-interaction"
PILOT = TRACK / "courses/core-first-exchanges-2/lessons/20-asking-for-help/lesson.html"

# Sentence-length answer keys cannot remain visible in a one-line <input> at
# 360px. Keep this repair narrow to this batch: render sentence controls as
# genuine multi-line values and let the control grow with wrapped content. New
# batch wrappers should copy this static-source pattern until the shared
# renderer can migrate without changing already-reviewed deck bytes.
NARROW_GROWING_INPUT_CSS = """/* CORE60--70: keep complete learner answers visible at phone widths. */
textarea.space-input,
textarea.free-input,
textarea.phrase-input {
  box-sizing: border-box;
  field-sizing: content;
  block-size: auto;
  min-block-size: 2.75em;
  max-block-size: none;
  overflow: hidden;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  resize: none;
}
textarea.phrase-input {
  margin-block: 4px;
}
"""


def rows(*items):
    return items


def semantic_spec(meanings, writes, choices, rules, tip):
    return dict(meanings=meanings, writes=writes, choices=choices, rules=rules, tip=tip)


LESSONS = {
    60: dict(
        slug="would-you-mind-opening-the-window", title="Would you mind opening the window?", ko="창문을 열어 주시겠어요?", ja="窓を開けていただけますか？",
        goal=("Make the same request at two levels of care.", "同じお願いを、丁寧さの違う二つの形で伝えましょう。"),
        p1=rows(
            ("{t}Could you open{/t} the window?", "窓を{t}開けてもらえますか{/t}？", "Could you|open|the window?"),
            ("{t}Could you close{/t} the door?", "ドアを{t}閉めてもらえますか{/t}？", "Could you|close|the door?"),
            ("{t}Could you check{/t} the file?", "ファイルを{t}確認してもらえますか{/t}？", "Could you|check|the file?"),
            ("{t}Could you send{/t} the email?", "メールを{t}送ってもらえますか{/t}？", "Could you|send|the email?"),
        ),
        p2=rows(
            ("{t}Would you mind opening{/t} the window?", "窓を{t}開けていただけますか{/t}？", "Would you mind|opening|the window?"),
            ("{t}Would you mind closing{/t} the door?", "ドアを{t}閉めていただけますか{/t}？", "Would you mind|closing|the door?"),
            ("{t}Would you mind checking{/t} the file?", "ファイルを{t}確認していただけますか{/t}？", "Would you mind|checking|the file?"),
            ("{t}Would you mind sending{/t} the email?", "メールを{t}送っていただけますか{/t}？", "Would you mind|sending|the email?"),
        ),
        rules=(("Use could plus a plain verb for a polite everyday request.", "日常的な丁寧なお願いでは、could の後ろに動詞の原形を置きます。"), ("After Would you mind, use the -ing form, not to plus a verb.", "Would you mind の後ろは to＋動詞ではなく、-ing 形にします。")),
        prompt=("Ask me to do one small thing, then ask the same favor more carefully.", "小さなお願いを一つしてから、同じことをさらに丁寧に頼んでください。"),
    ),
    61: dict(
        slug="do-you-mind-if-i-sit-here", title="Do you mind if I sit here?", ko="여기 앉아도 괜찮으세요?", ja="ここに座ってもよろしいですか？",
        goal=("Request permission and answer without a polarity mistake.", "許可を求め、意味を取り違えずに答えましょう。"),
        p1=rows(
            ("{t}Do you mind if I sit{/t} here?", "ここに{t}座ってもよろしいですか{/t}？", "Do you mind|if I|sit|here?"),
            ("{t}Do you mind if I open{/t} the window?", "窓を{t}開けてもよろしいですか{/t}？", "Do you mind|if I|open|the window?"),
            ("{t}Do you mind if I use{/t} this chair?", "この椅子を{t}使ってもよろしいですか{/t}？", "Do you mind|if I|use|this chair?"),
            ("{t}Do you mind if I take{/t} a photo?", "写真を{t}撮ってもよろしいですか{/t}？", "Do you mind|if I|take|a photo?"),
        ),
        p2=rows(
            ("{t}Not at all, go ahead{/t}.", "{t}全く構いません。どうぞ{/t}。", "Not at all,|go ahead."),
            ("{t}Not at all, please do{/t}.", "{t}全く構いません。どうぞ{/t}。", "Not at all,|please do."),
            ("{t}Not at all, use it{/t}.", "{t}全く構いません。使ってください{/t}。", "Not at all,|use it."),
            ("{t}Not at all, take one{/t}.", "{t}全く構いません。一枚撮ってください{/t}。", "Not at all,|take one."),
        ),
        omit_reorder=(2,),
        rules=(("Keep normal statement order after if I: if I sit, not if sit I.", "if I の後ろは普通の文の語順にし、if I sit とします。"), ("Not at all means there is no problem, so the permission answer is positive.", "Not at all は「全く構いません」という意味なので、許可する答えです。")),
        prompt=("Answer one permission request from me, then ask permission for one action.", "私からの許可のお願いに答えてから、自分の行動について許可を求めてください。"),
    ),
    62: dict(
        slug="do-you-know-where-it-is", title="Do you know where it is?", ko="어디 있는지 아세요?", ja="どこにあるか分かりますか？",
        goal=("Ask for place and time information without sounding abrupt.", "ぶしつけに聞こえないように、場所と時刻をたずねましょう。"),
        p1=rows(
            ("{t}Do you know where the station is{/t}?", "{t}駅がどこにあるか分かりますか{/t}？", "Do you know|where|the station is?"),
            ("{t}Do you know where the bank is{/t}?", "{t}銀行がどこにあるか分かりますか{/t}？", "Do you know|where|the bank is?"),
            ("{t}Do you know where the café is{/t}?", "{t}カフェがどこにあるか分かりますか{/t}？", "Do you know|where|the café is?"),
            ("{t}Do you know where the meeting room is{/t}?", "{t}会議室がどこにあるか分かりますか{/t}？", "Do you know|where|the meeting room is?"),
        ),
        p2=rows(
            ("{t}Could you tell me when the next train leaves{/t}?", "{t}次の電車がいつ出るか教えてもらえますか{/t}？", "Could you tell me|when|the next train leaves?"),
            ("{t}Could you tell me when the shop opens{/t}?", "{t}店がいつ開くか教えてもらえますか{/t}？", "Could you tell me|when|the shop opens?"),
            ("{t}Could you tell me when the meeting starts{/t}?", "{t}会議がいつ始まるか教えてもらえますか{/t}？", "Could you tell me|when|the meeting starts?"),
            ("{t}Could you tell me when the café closes{/t}?", "{t}カフェがいつ閉まるか教えてもらえますか{/t}？", "Could you tell me|when|the café closes?"),
        ),
        rules=(("After Do you know where, return to statement order: the station is.", "Do you know where の後ろは普通の語順に戻し、the station is とします。"), ("After when, keep the complete subject before its verb: the next train leaves.", "when の後ろは、主語全体を動詞の前に置き、the next train leaves とします。")),
        prompt=("Ask me where one place is, then ask when one event starts.", "場所を一つたずねてから、出来事がいつ始まるか聞いてください。"),
    ),
    63: dict(
        slug="i-generally-prefer-coffee", title="I generally prefer coffee", ko="저는 대체로 커피를 더 좋아해요", ja="私はたいていコーヒーのほうが好きです",
        goal=("State a general preference and something you usually avoid.", "一般的な好みと、ふだん避けるものを話しましょう。"),
        p1=rows(
            ("{t}I generally prefer coffee to{/t} tea.", "{t}私はたいてい紅茶よりコーヒーのほうが好きです{/t}。", "I generally prefer|coffee|to|tea."),
            ("{t}I generally prefer trains to{/t} buses.", "{t}私はたいていバスより電車のほうが好きです{/t}。", "I generally prefer|trains|to|buses."),
            ("{t}I generally prefer cafés to{/t} restaurants.", "{t}私はたいていレストランよりカフェのほうが好きです{/t}。", "I generally prefer|cafés|to|restaurants."),
            ("{t}I generally prefer mornings to{/t} evenings.", "{t}私はたいてい夜より朝のほうが好きです{/t}。", "I generally prefer|mornings|to|evenings."),
        ),
        p2=rows(
            ("{t}I tend to avoid{/t} crowded places.", "私は{t}混んだ場所を避けることが多いです{/t}。", "I tend to|avoid|crowded places."),
            ("{t}I tend to avoid{/t} noisy places.", "私は{t}騒がしい場所を避けることが多いです{/t}。", "I tend to|avoid|noisy places."),
            ("{t}I tend to avoid{/t} expensive places.", "私は{t}高い店を避けることが多いです{/t}。", "I tend to|avoid|expensive places."),
            ("{t}I tend to avoid{/t} busy places.", "私は{t}人の多い場所を避けることが多いです{/t}。", "I tend to|avoid|busy places."),
        ),
        rules=(("For a general preference, use no article with non-count nouns and plural count nouns.", "一般的な好みでは、数えられない名詞と複数名詞に冠詞を付けません。"), ("Use a plural noun with no article when you mean places in general.", "場所全般を指すときは、冠詞を付けずに複数形を使います。")),
        prompt=("Compare two things you genuinely like, then name a kind of place you avoid.", "本当に好きなものを二つ比べてから、避ける場所の種類を一つ話してください。"),
    ),
    64: dict(
        slug="it-wont-turn-on", title="It won't turn on", ko="전원이 안 켜져요", ja="電源が入りません",
        goal=("Describe a malfunction and suggest one first check.", "不具合を説明し、最初に試すことを一つ提案しましょう。"),
        p1=rows(
            ("My laptop {t}won't turn on{/t}.", "ノートパソコンの{t}電源が入りません{/t}。", "My laptop|won't|turn on."),
            ("My printer {t}won't print{/t}.", "プリンターが{t}印刷してくれません{/t}。", "My printer|won't|print."),
            ("My phone {t}won't charge{/t}.", "携帯が{t}充電できません{/t}。", "My phone|won't|charge."),
            ("The door {t}won't open{/t}.", "ドアが{t}開きません{/t}。", "The door|won't|open."),
        ),
        p2=rows(
            ("{t}Have you tried restarting{/t} it?", "{t}再起動してみましたか{/t}？", "Have you tried|restarting|it?"),
            ("{t}Have you tried checking{/t} the cable?", "ケーブルを{t}確認してみましたか{/t}？", "Have you tried|checking|the cable?"),
            ("{t}Have you tried charging{/t} it?", "{t}充電してみましたか{/t}？", "Have you tried|charging|it?"),
            ("{t}Have you tried opening{/t} it another way?", "別の方法で{t}開けてみましたか{/t}？", "Have you tried|opening|it another way?"),
        ),
        rules=(("For a thing that refuses to work, use won't plus a plain verb; this is not future time.", "物がどうしても動かないときは、未来ではなく won't＋動詞の原形を使います。"), ("After Have you tried, use the -ing form for a possible fix.", "Have you tried の後ろは、試す対処を -ing 形にします。")),
        prompt=("Suggest one fix for my problem, then ask for help with another problem.", "私の不具合に対処法を一つ提案してから、別の不具合について助けを求めてください。"),
    ),
    65: dict(
        slug="my-wallet-was-stolen", title="My wallet was stolen", ko="지갑을 도난당했어요", ja="財布を盗まれました",
        goal=("Report what happened to a possession and where it was taken from.", "持ち物に何が起き、どこから取られたかを伝えましょう。"),
        p1=rows(
            ("My wallet {t}was stolen{/t}.", "財布を{t}盗まれました{/t}。", "My wallet|was stolen."),
            ("My phone {t}was stolen{/t}.", "携帯を{t}盗まれました{/t}。", "My phone|was stolen."),
            ("My ticket {t}was stolen{/t}.", "チケットを{t}盗まれました{/t}。", "My ticket|was stolen."),
            ("My bag {t}was stolen{/t}.", "かばんを{t}盗まれました{/t}。", "My bag|was stolen."),
        ),
        p2=rows(
            ("It {t}was taken from{/t} my bag.", "それはかばん{t}から取られました{/t}。", "It|was taken from|my bag."),
            ("It {t}was taken from{/t} my pocket.", "それはポケット{t}から取られました{/t}。", "It|was taken from|my pocket."),
            ("It {t}was taken from{/t} the desk.", "それは机{t}から取られました{/t}。", "It|was taken from|the desk."),
            ("It {t}was taken from{/t} the car.", "それは車{t}から取られました{/t}。", "It|was taken from|the car."),
        ),
        omit_reorder=(1,),
        rules=(("Use was plus the past participle when the unknown person who did it is not the point.", "した人が不明または重要でないときは、was＋過去分詞を使います。"), ("Keep taken from together to name the source or location.", "取られた元の場所を言うときは taken from をひとまとまりで使います。")),
        prompt=("Make an imagined theft report, then say where the item was taken from.", "想像上の盗難届を作り、品物がどこから取られたか伝えてください。"),
    ),
    66: dict(
        slug="if-i-had-more-time-id-travel", title="If I had more time, I'd travel", ko="시간이 더 있다면 여행할 텐데요", ja="もっと時間があれば、旅行するのですが",
        goal=("Discuss an imaginary present situation and its result.", "今の現実とは違う想像の状況と、その結果を話しましょう。"),
        p1=rows(
            ("{t}If I had more time{/t}, {t}I'd travel{/t} more.", "{t}もっと時間があれば{/t}、もっと{t}旅行します{/t}。", "If I had|more time,|I'd travel|more."),
            ("{t}If I had more money{/t}, {t}I'd move{/t} to Osaka.", "{t}もっとお金があれば{/t}、大阪へ{t}引っ越します{/t}。", "If I had|more money,|I'd move|to Osaka."),
            ("{t}If I had a free month{/t}, {t}I'd study{/t} abroad.", "{t}1か月休みがあれば{/t}、海外で{t}勉強します{/t}。", "If I had|a free month,|I'd study|abroad."),
            ("{t}If I had a bigger room{/t}, {t}I'd work{/t} at home.", "{t}もっと広い部屋があれば{/t}、家で{t}働きます{/t}。", "If I had|a bigger room,|I'd work|at home."),
        ),
        p2=rows(
            ("{t}What would you do if you won{/t}?", "{t}もし当たったら何をしますか{/t}？", "What would you do|if|you won?"),
            ("{t}What would you do if you had a free month{/t}?", "{t}1か月休みがあったら何をしますか{/t}？", "What would you do|if|you had a free month?"),
            ("{t}What would you do if you had more time{/t}?", "{t}もっと時間があったら何をしますか{/t}？", "What would you do|if|you had more time?"),
            ("{t}What would you do if you could work anywhere{/t}?", "{t}どこでも働けたら何をしますか{/t}？", "What would you do|if|you could work anywhere?"),
        ),
        rules=(("For an unreal situation now, use a past form after if and would in the result.", "今の非現実的な想像では、if の後ろに過去形、結果に would を使います。"), ("Keep What would you do at the front, then put the imaginary condition after if.", "What would you do を文頭に置き、その後ろに if＋想像の条件を続けます。")),
        prompt=("Imagine one change to your life, then ask what I would do in another imaginary situation.", "生活の変化を一つ想像してから、別の想像の状況で私なら何をするか聞いてください。"),
    ),
    67: dict(
        slug="i-wish-i-could-drive", title="I wish I could drive", ko="운전할 수 있으면 좋겠어요", ja="運転できたらいいのにと思います",
        goal=("Express dissatisfaction with something that is not true now.", "今は実現していないことへの不満や願いを伝えましょう。"),
        p1=rows(
            ("{t}I wish I had more free time{/t}.", "{t}もっと自由な時間があればいいのに{/t}。", "I wish|I had|more free time."),
            ("{t}I wish I had more energy{/t}.", "{t}もっと元気があればいいのに{/t}。", "I wish|I had|more energy."),
            ("{t}I wish I had a quieter room{/t}.", "{t}もっと静かな部屋があればいいのに{/t}。", "I wish|I had|a quieter room."),
            ("{t}I wish I had a better schedule{/t}.", "{t}もっとよい予定があればいいのに{/t}。", "I wish|I had|a better schedule."),
        ),
        p2=rows(
            ("{t}I wish I could drive{/t}.", "{t}運転できたらいいのに{/t}。", "I wish|I could|drive."),
            ("{t}I wish I could cook better{/t}.", "{t}もっと上手に料理できたらいいのに{/t}。", "I wish|I could|cook better."),
            ("{t}I wish I could travel more{/t}.", "{t}もっと旅行できたらいいのに{/t}。", "I wish|I could|travel more."),
            ("{t}I wish I could work from home{/t}.", "{t}在宅勤務ができたらいいのに{/t}。", "I wish|I could|work from home."),
        ),
        rules=(("After wish, use had for a present situation that is not true now.", "wish の後ろでは、今は事実でない状況を had で表します。"), ("Use could plus a plain verb for an ability or possibility you do not have now.", "今はない能力や可能性には could＋動詞の原形を使います。")),
        prompt=("Name one thing you wish you had and one thing you wish you could do.", "あればいいと思うものと、できればいいと思うことを一つずつ話してください。"),
    ),
    68: dict(
        slug="he-must-be-busy", title="He must be busy", ko="그는 분명 바쁜가 봐요", ja="彼はきっと忙しいのでしょう",
        goal=("Distinguish a strong conclusion from a possibility.", "強い推測と、単なる可能性を言い分けましょう。"),
        p1=rows(
            ("He {t}must be busy{/t}.", "彼は{t}きっと忙しいのでしょう{/t}。", "He|must be|busy."),
            ("She {t}must be tired{/t}.", "彼女は{t}きっと疲れているのでしょう{/t}。", "She|must be|tired."),
            ("He {t}must be asleep{/t}.", "彼は{t}きっと寝ているのでしょう{/t}。", "He|must be|asleep."),
            ("She {t}must be at work{/t}.", "彼女は{t}きっと仕事中なのでしょう{/t}。", "She|must be|at work."),
        ),
        p2=rows(
            ("Or he {t}might just be out{/t}.", "それとも、彼は{t}ただ外出中なのかもしれません{/t}。", "Or|he might just be|out."),
            ("Or she {t}might just be tired{/t}.", "それとも、彼女は{t}ただ疲れているだけかもしれません{/t}。", "Or|she might just be|tired."),
            ("Or he {t}might just be late{/t}.", "それとも、彼は{t}ただ遅れているだけかもしれません{/t}。", "Or|he might just be|late."),
            ("Or she {t}might just be at lunch{/t}.", "それとも、彼女は{t}ただ昼食中なのかもしれません{/t}。", "Or|she might just be|at lunch."),
        ),
        rules=(("Here, must means a strong conclusion from evidence, not an obligation.", "ここでの must は義務ではなく、根拠のある強い推測です。"), ("Use might for a real possibility; just makes the alternative sound simple.", "本当にあり得る可能性には might を使い、just で単純な別の見方を示します。")),
        prompt=("Make one strong guess about a situation, then add a possible alternative.", "状況について強く推測してから、別の可能性を一つ加えてください。"),
    ),
    69: dict(
        slug="she-said-she-was-busy", title="She said she was busy", ko="그녀는 바쁘다고 말했어요", ja="彼女は忙しいと言っていました",
        goal=("Report a statement and what someone said they would do.", "人の発言と、その人がすると言った行動を伝えましょう。"),
        p1=rows(
            ("{t}She said she was busy{/t}.", "{t}彼女は忙しいと言っていました{/t}。", "She said|she was|busy."),
            ("{t}He said he was tired{/t}.", "{t}彼は疲れていると言っていました{/t}。", "He said|he was|tired."),
            ("{t}She said she was late{/t}.", "{t}彼女は遅れると言っていました{/t}。", "She said|she was|late."),
            ("{t}He said he was at home{/t}.", "{t}彼は家にいると言っていました{/t}。", "He said|he was|at home."),
        ),
        p2=rows(
            ("{t}He told me he'd call back{/t}.", "{t}彼は折り返すと私に言いました{/t}。", "He told me|he'd|call back."),
            ("{t}She told me she'd send an email{/t}.", "{t}彼女はメールすると私に言いました{/t}。", "She told me|she'd|send an email."),
            ("{t}He told me he'd come later{/t}.", "{t}彼は後で来ると私に言いました{/t}。", "He told me|he'd|come later."),
            ("{t}She told me she'd help tomorrow{/t}.", "{t}彼女は明日手伝うと私に言いました{/t}。", "She told me|she'd|help tomorrow."),
        ),
        omit_choice=(1,),
        rules=(("After a past reporting verb, step am or is back to was when you report the earlier words.", "過去の発言を伝えるときは、am・is を was に一段戻します。"), ("Tell needs a person: told me. Then use would, often contracted to 'd, for the later action.", "tell には人が必要なので told me とします。その後の行動は would（通常 'd）で表します。")),
        prompt=("Report one thing someone said, then one thing they said they would do.", "誰かが言ったことと、その人がすると言ったことを一つずつ伝えてください。"),
    ),
    70: dict(
        slug="she-told-me-to-wait", title="She told me to wait", ko="그녀가 기다리라고 했어요", ja="彼女に待つよう言われました",
        goal=("Relay a positive instruction and a negative request.", "するようにという指示と、しないようにというお願いを伝えましょう。"),
        p1=rows(
            ("{t}She told me to wait{/t} here.", "{t}彼女はここで待つよう私に言いました{/t}。", "She told me|to wait|here."),
            ("{t}He told me to call back{/t} later.", "{t}彼は後で折り返すよう私に言いました{/t}。", "He told me|to call back|later."),
            ("{t}She told me to come{/t} early.", "{t}彼女は早く来るよう私に言いました{/t}。", "She told me|to come|early."),
            ("{t}He told me to check{/t} the email.", "{t}彼はメールを確認するよう私に言いました{/t}。", "He told me|to check|the email."),
        ),
        p2=rows(
            ("{t}He asked me not to mention{/t} it.", "{t}彼はそのことを言わないよう私に頼みました{/t}。", "He asked me|not to mention|it."),
            ("{t}She asked me not to share{/t} the file.", "{t}彼女はファイルを共有しないよう私に頼みました{/t}。", "She asked me|not to share|the file."),
            ("{t}He asked me not to call{/t} today.", "{t}彼は今日電話しないよう私に頼みました{/t}。", "He asked me|not to call|today."),
            ("{t}She asked me not to open{/t} the door.", "{t}彼女はドアを開けないよう私に頼みました{/t}。", "She asked me|not to open|the door."),
        ),
        rules=(("Tell needs the person before to plus the instruction: told me to wait.", "tell は人を必要とし、told me to wait の順にします。"), ("For a negative request, put not before to plus the plain verb: asked me not to mention it.", "否定のお願いは、to＋動詞の前に not を置き、asked me not to mention it とします。")),
        prompt=("Relay one instruction you received, then one thing someone asked you not to do.", "受けた指示と、しないよう頼まれたことを一つずつ伝えてください。"),
    ),
}


def standard_spec(number, meaning1, meaning2, write1, write2, choice1, choice2, rule1, rule2, tip):
    return semantic_spec((meaning1, meaning2), (write1, write2), (choice1, choice2), (rule1, rule2), tip)


SPECS = {
    60: standard_spec(60,
        ("Use this for a polite everyday request.", "日常的に丁寧なお願いをするときに使います。"), ("Use this when you want to add another level of care.", "さらに配慮してお願いしたいときに使います。"),
        ("Ask me to do one small thing.", "小さなことを一つ私に頼んでください。"), ("Make the same kind of request with Would you mind.", "Would you mind を使って同じ種類のお願いをしてください。"),
        (("窓を{t}開けて{/t}もらえますか？", "Could you ", "open", "opening", " the window?"), ("ドアを{t}閉めて{/t}もらえますか？", "Could you ", "close", "closing", " the door?"), ("ファイルを{t}確認して{/t}もらえますか？", "Could you ", "check", "checking", " the file?"), ("メールを{t}送って{/t}もらえますか？", "Could you ", "send", "sending", " the email?")),
        tuple((jp, "Would you mind ", good, bad, tail) for jp, good, bad, tail in (("窓を{t}開けて{/t}いただけますか？", "opening", "to open", " the window?"), ("ドアを{t}閉めて{/t}いただけますか？", "closing", "to close", " the door?"), ("ファイルを{t}確認して{/t}いただけますか？", "checking", "to check", " the file?"), ("メールを{t}送って{/t}いただけますか？", "sending", "to send", " the email?"))),
        ("Modal plus plain verb", "助動詞＋動詞の原形", "Could you + <b>plain verb</b>?", "Polite everyday request", "日常的な丁寧なお願い", ("Could you <b>open</b> the window?", "Could you <b>check</b> the file?")),
        ("Mind plus -ing", "mind＋-ing", "Would you mind + 動詞<b>-ing</b>?", "More careful request", "さらに配慮したお願い", ("Would you mind <b>opening</b> the window?", "Would you mind <b>checking</b> the file?")),
        ("A small favor or a low-priority favor?", "小さなお願い・急がないお願い", "Use “if it's not too much trouble” when the favor may impose. Use “whenever you get a chance” when it is not urgent.", "負担をかけそうなら「if it's not too much trouble」を使います。急がないなら「whenever you get a chance」を使います。", ("Possible burden", "負担になりそう", "Could you check this, if it's not too much trouble?", "ご面倒でなければ、これを確認してもらえますか？"), ("Not urgent", "急がない", "Could you check this whenever you get a chance?", "お時間のあるときに、これを確認してもらえますか？"))),
    61: standard_spec(61,
        ("Use this to check whether your action would bother someone.", "自分の行動が相手の迷惑にならないか確認するときに使います。"), ("Use this to say clearly that there is no problem and give permission.", "全く問題ないと明確に伝え、許可するときに使います。"),
        ("Ask permission for one real action.", "実際にしたいことを一つ聞いてください。"), ("Give a clear positive permission answer.", "はっきり許可する答えを言ってください。"),
        tuple((jp, "Do you mind if ", "I", "me", tail) for jp, tail in (("{t}私が{/t}ここに座ってもよろしいですか？", " sit here?"), ("{t}私が{/t}窓を開けてもよろしいですか？", " open the window?"), ("{t}私が{/t}この椅子を使ってもよろしいですか？", " use this chair?"), ("{t}私が{/t}写真を撮ってもよろしいですか？", " take a photo?"))),
        tuple((jp, "", "Not at all", "Yes, I mind", tail) for jp, tail in (("{t}全く構いません{/t}。どうぞ。", ", go ahead."), ("{t}全く構いません{/t}。どうぞ。", ", please do."), ("{t}全く構いません{/t}。使ってください。", ", use it."), ("{t}全く構いません{/t}。一枚撮ってください。", ", take one."))),
        ("Normal order after if", "if の後ろは普通の語順", "Do you mind if + <b>I + plain verb</b>?", "Ask about your action", "自分の行動を確認", ("Do you mind if <b>I sit</b> here?", "Do you mind if <b>I open</b> the window?")),
        ("No problem means permission", "問題なし＝許可", "<b>Not at all</b>, + permission", "Positive answer", "許可する答え", ("<b>Not at all</b>, go ahead.", "<b>Not at all</b>, please do.")),
        ("Go ahead or please do?", "go ahead と please do", "Both give permission. “Go ahead” is common and conversational; “please do” sounds a little warmer.", "どちらも許可を表します。「go ahead」は会話的でよく使い、「please do」は少し温かい響きです。", ("Common and conversational", "会話でよく使う", "Not at all, go ahead.", "全く構いません。どうぞ。"), ("A little warmer", "少し温かい", "Not at all, please do.", "全く構いません。ぜひどうぞ。"))),
    62: standard_spec(62,
        ("Use this to ask politely where something is.", "場所を丁寧にたずねるときに使います。"), ("Use this to ask politely when something happens.", "時刻を丁寧にたずねるときに使います。"),
        ("Ask where one useful place is.", "役に立つ場所を一つたずねてください。"), ("Ask when one real event starts or finishes.", "実際の予定がいつ始まるか終わるか聞いてください。"),
        (("Do you know where the station is? の内側は{t}主語が先{/t}。", "Do you know where the station is? Inside: ", "subject first", "verb first", "."), ("Do you know where the bank is? の内側は{t}主語が先{/t}。", "Do you know where the bank is? Inside: ", "subject first", "verb first", "."), ("Do you know where the café is? の内側は{t}主語が先{/t}。", "Do you know where the café is? Inside: ", "subject first", "verb first", "."), ("Do you know where the meeting room is? の内側は{t}主語が先{/t}。", "Do you know where the meeting room is? Inside: ", "subject first", "verb first", ".")),
        (("Could you tell me when the next train leaves? の内側は{t}主語が先{/t}。", "Could you tell me when the next train leaves? Inside: ", "subject first", "verb first", "."), ("Could you tell me when the shop opens? の内側は{t}主語が先{/t}。", "Could you tell me when the shop opens? Inside: ", "subject first", "verb first", "."), ("Could you tell me when the meeting starts? の内側は{t}主語が先{/t}。", "Could you tell me when the meeting starts? Inside: ", "subject first", "verb first", "."), ("Could you tell me when the café closes? の内側は{t}主語が先{/t}。", "Could you tell me when the café closes? Inside: ", "subject first", "verb first", ".")),
        ("Undo question order inside", "中では疑問文の語順を戻す", "Do you know where + 主語 + <b>is</b>?", "Embedded place question", "文に埋め込まれた場所の質問", ("Do you know where <b>the station is</b>?", "Do you know where <b>the bank is</b>?")),
        ("Keep subject before verb", "主語を動詞の前に", "Could you tell me when + 主語 + 動詞?", "Embedded time question", "文に埋め込まれた時刻の質問", ("Could you tell me when <b>the train leaves</b>?", "Could you tell me when <b>the meeting starts</b>?")),
        ("An apology or a soft possibility?", "おわび・控えめな可能性", "Start with “sorry to bother you” when interrupting. Add “by any chance” when the person may not know.", "話しかけて邪魔をするときは「sorry to bother you」を使います。相手が知らないかもしれないときは「by any chance」を加えます。", ("Interrupting", "話しかける", "Sorry to bother you. Do you know where the station is?", "お邪魔してすみません。駅がどこか分かりますか？"), ("They may not know", "知らないかもしれない", "Do you know where the station is, by any chance?", "もしかして、駅がどこか分かりますか？"))),
    63: standard_spec(63,
        ("Use this to compare your usual preference, not one choice today.", "今日一回の選択ではなく、普段の好みを比べるときに使います。"), ("Use this to name a kind of place you usually stay away from.", "ふだん避ける場所の種類を言うときに使います。"),
        ("Compare two things you genuinely like.", "本当に好きなものを二つ比べてください。"), ("Name a kind of place you usually avoid.", "ふだん避ける場所の種類を一つ言ってください。"),
        (("飲み物全般の好み：私は{t}コーヒー{/t}のほうが好きです。", "I generally prefer ", "coffee", "the coffee", " to tea."), ("乗り物全般の好み：私は{t}電車{/t}のほうが好きです。", "I generally prefer ", "trains", "the train", " to buses."), ("店全般の好み：私は{t}カフェ{/t}のほうが好きです。", "I generally prefer ", "cafés", "the café", " to restaurants."), ("時間帯全般の好み：私は{t}朝{/t}のほうが好きです。", "I generally prefer ", "mornings", "the morning", " to evenings.")),
        (("場所全般：私は{t}混んだ場所{/t}を避けます。", "I tend to avoid ", "crowded places", "the crowded place", "."), ("場所全般：私は{t}騒がしい場所{/t}を避けます。", "I tend to avoid ", "noisy places", "the noisy place", "."), ("場所全般：私は{t}高い店{/t}を避けます。", "I tend to avoid ", "expensive places", "the expensive place", "."), ("場所全般：私は{t}人の多い場所{/t}を避けます。", "I tend to avoid ", "busy places", "the busy place", ".")),
        ("General things take no article", "一般的な物には冠詞なし", "prefer + <b>coffee / plural nouns</b> + to ...", "General preference", "一般的な好み", ("I prefer <b>coffee</b> to tea.", "I prefer <b>trains</b> to buses.")),
        ("General places are plural", "場所全般は複数形", "avoid + 形容詞 + <b>plural noun</b>", "A type, not one known place", "特定の一か所ではない", ("I avoid <b>crowded places</b>.", "I avoid <b>noisy places</b>.")),
        ("Coffee in general or this café's coffee?", "コーヒー全般・この店のコーヒー", "No article means coffee in general. “The coffee here” means the specific coffee served in this place.", "冠詞なしならコーヒー全般です。「the coffee here」はこの店で出す特定のコーヒーです。", ("In general", "全般", "I prefer coffee to tea.", "私は紅茶よりコーヒーのほうが好きです。"), ("Specific here", "この場所の特定のもの", "I like the coffee here.", "ここのコーヒーが好きです。"))),
    64: standard_spec(64,
        ("Use this when a device or object refuses to work.", "機器や物がどうしても動かないときに使います。"), ("Use this to suggest a first troubleshooting step.", "最初の対処法を提案するときに使います。"),
        ("Describe one device or object that will not work.", "動かない機器や物を一つ説明してください。"), ("Ask whether one possible fix has been tried.", "対処法を一つ試したか聞いてください。"),
        (("携帯が{t}充電できません{/t}。", "My phone ", "won't", "will", " charge."), ("プリンターが{t}印刷してくれません{/t}。", "My printer ", "won't", "will", " print."), ("ドアが{t}開きません{/t}。", "The door ", "won't", "will", " open."), ("パソコンの{t}電源が入りません{/t}。", "My laptop ", "won't", "will", " turn on.")),
        (("{t}再起動して{/t}みましたか？", "Have you tried ", "restarting", "restart", " it?"), ("ケーブルを{t}確認して{/t}みましたか？", "Have you tried ", "checking", "check", " the cable?"), ("{t}充電して{/t}みましたか？", "Have you tried ", "charging", "charge", " it?"), ("別の方法で{t}開けて{/t}みましたか？", "Have you tried ", "opening", "open", " it another way?")),
        ("Won't for refusal to work", "動かない物の won't", "物 + <b>won't</b> + 動詞の原形", "Malfunction now", "今の不具合", ("My laptop <b>won't turn on</b>.", "The door <b>won't open</b>.")),
        ("Try plus -ing", "try＋-ing", "Have you tried + 動詞<b>-ing</b>?", "Possible troubleshooting step", "対処法の提案", ("Have you tried <b>restarting</b> it?", "Have you tried <b>checking</b> the cable?")),
        ("Acting strangely or fixed?", "調子が悪い・直った", "“It's playing up” names unreliable behavior. “That did the trick” says the fix worked.", "「It's playing up」は調子が悪い状態を表します。「That did the trick」は対処が効いたことを表します。", ("Problem continues", "不具合が続く", "My laptop is playing up.", "ノートパソコンの調子が悪いです。"), ("Fix worked", "対処が効いた", "Restarting it did the trick.", "再起動したら直りました。"))),
    65: standard_spec(65,
        ("Use this to report a theft when the thief is unknown or unimportant.", "犯人が不明または重要でない盗難を伝えるときに使います。"), ("Use this to name the place the item came from.", "品物が取られた元の場所を言うときに使います。"),
        ("Make an imagined report about one possession.", "持ち物について想像上の報告をしてください。"), ("Say where that item was taken from.", "その品物がどこから取られたか言ってください。"),
        (("My wallet was stolen. は{t}受け身{/t}。", "My wallet was stolen. This sentence is ", "passive", "active", "."), ("Someone stole my phone. は{t}能動態{/t}。", "Someone stole my phone. This sentence is ", "active", "passive", "."), ("My ticket was stolen. は{t}受け身{/t}。", "My ticket was stolen. This sentence is ", "passive", "active", "."), ("Someone stole my bag. は{t}能動態{/t}。", "Someone stole my bag. This sentence is ", "active", "passive", ".")),
        (("かばん{t}から{/t}取られました。", "It was taken ", "from", "at", " my bag."), ("ポケット{t}から{/t}取られました。", "It was taken ", "from", "at", " my pocket."), ("机{t}から{/t}取られました。", "It was taken ", "from", "at", " the desk."), ("車{t}から{/t}取られました。", "It was taken ", "from", "at", " the car.")),
        ("Focus on what happened", "起きたことに焦点", "物 + <b>was + past participle</b>", "Doer unknown or irrelevant", "した人が不明・重要でない", ("My wallet <b>was stolen</b>.", "My phone <b>was stolen</b>.")),
        ("Keep taken from together", "taken from をひとまとまりに", "It + was + <b>taken from</b> + 場所", "Source location", "取られた元の場所", ("It was <b>taken from my bag</b>.", "It was <b>taken from my pocket</b>.")),
        ("Apparently or it turns out?", "apparently と it turns out", "Use “apparently” for information you heard. Use “it turns out” when a later fact changes what you thought.", "聞いた情報には「apparently」を使います。後で分かった事実が見方を変えるときは「it turns out」を使います。", ("Reported information", "聞いた情報", "Apparently, it was taken on the train.", "どうやら電車で取られたそうです。"), ("Later discovery", "後で判明", "It turns out it was at home.", "結局、家にあったことが分かりました。"))),
    66: standard_spec(66,
        ("Use this for an imaginary change to the present and its result.", "今の現実とは違う変化と、その結果を想像するときに使います。"), ("Use this to ask about another person's imaginary result.", "相手なら想像上の状況で何をするか聞くときに使います。"),
        ("Imagine one change and its result.", "変化とその結果を一つ想像してください。"), ("Ask what I would do in one imaginary situation.", "想像の状況で私なら何をするか聞いてください。"),
        (("今は時間が足りない。もっと時間が{t}あれば{/t}。", "If I ", "had", "have", " more time, I'd travel more."), ("今はお金が足りない。もっとお金が{t}あれば{/t}。", "If I ", "had", "have", " more money, I'd move to Osaka."), ("今は1か月休みがない。休みが{t}あれば{/t}。", "If I ", "had", "have", " a free month, I'd study abroad."), ("今は広い部屋がない。広い部屋が{t}あれば{/t}。", "If I ", "had", "have", " a bigger room, I'd work at home.")),
        (("想像の話：もし当たったら{t}何をしますか{/t}？", "What ", "would", "will", " you do if you won?"), ("想像の話：1か月休みなら{t}何をしますか{/t}？", "What ", "would", "will", " you do if you had a free month?"), ("想像の話：もっと時間があれば{t}何をしますか{/t}？", "What ", "would", "will", " you do if you had more time?"), ("想像の話：どこでも働けたら{t}何をしますか{/t}？", "What ", "would", "will", " you do if you could work anywhere?")),
        ("Past form marks the unreal condition", "過去形で非現実を示す", "If + 過去形, + <b>would</b> + 動詞の原形", "Imaginary present", "今の想像", ("If I <b>had</b> more time, I<b>'d travel</b>.", "If I <b>had</b> more money, I<b>'d move</b>.")),
        ("Question first, condition second", "質問、条件の順", "What would you do + <b>if + past form</b>?", "Ask about an imagined result", "想像の結果を聞く", ("What would you do <b>if you won</b>?", "What would you do <b>if you had time</b>?")),
        ("Dream first or realistic limit?", "理想・現実的な制限", "Use “in a perfect world” to introduce the ideal. Use “realistically” before the practical limit.", "理想を出すなら「in a perfect world」を使います。現実的な制約の前には「realistically」を使います。", ("Ideal", "理想", "In a perfect world, I'd travel all year.", "理想を言えば、一年中旅行します。"), ("Practical reality", "現実", "Realistically, I'd take one month off.", "現実的には、1か月休みます。"))),
    67: standard_spec(67,
        ("Use this for a thing or situation you do not have now.", "今はない物や状況を願うときに使います。"), ("Use this for an ability or possibility you do not have now.", "今はない能力や可能性を願うときに使います。"),
        ("Name one thing you wish you had.", "あればいいと思うものを一つ言ってください。"), ("Name one thing you wish you could do.", "できればいいと思うことを一つ言ってください。"),
        tuple((jp, "I wish I ", "had", "have", tail) for jp, tail in (("もっと自由な時間が{t}あればいいのに{/t}。", " more free time."), ("もっと元気が{t}あればいいのに{/t}。", " more energy."), ("もっと静かな部屋が{t}あればいいのに{/t}。", " a quieter room."), ("もっとよい予定が{t}あればいいのに{/t}。", " a better schedule."))),
        tuple((jp, "I wish I ", "could", "can", tail) for jp, tail in (("運転{t}できたらいいのに{/t}。", " drive."), ("もっと上手に料理{t}できたらいいのに{/t}。", " cook better."), ("もっと旅行{t}できたらいいのに{/t}。", " travel more."), ("在宅勤務が{t}できたらいいのに{/t}。", " work from home."))),
        ("Wish plus a past form", "wish＋過去形", "I wish I + <b>had</b> + ...", "Not true now", "今は事実でない", ("I wish I <b>had more time</b>.", "I wish I <b>had more energy</b>.")),
        ("Wish plus could", "wish＋could", "I wish I + <b>could</b> + 動詞の原形", "Ability missing now", "今はできない", ("I wish I <b>could drive</b>.", "I wish I <b>could travel</b> more.")),
        ("If only or oh well?", "if only と oh well", "“If only” makes the wish stronger. “Oh well” accepts that the situation will not change now.", "「if only」は願いを強めます。「oh well」は今は変えられない状況を受け入れます。", ("Stronger wish", "強い願い", "If only I had more free time.", "もっと自由な時間さえあればなあ。"), ("Accept it for now", "今は受け入れる", "I wish I had more time. Oh well.", "もっと時間があればいいのですが。まあ仕方ないですね。"))),
    68: standard_spec(68,
        ("Use this for a strong conclusion based on what you can see or know.", "見聞きした根拠から強く推測するときに使います。"), ("Use this for another explanation that is only possible.", "別の説明が単なる可能性にすぎないときに使います。"),
        ("Make one strong evidence-based guess.", "根拠のある強い推測を一つしてください。"), ("Add one possible alternative.", "別の可能性を一つ加えてください。"),
        (("明かりが消え、返事がない。彼は{t}きっと寝ている{/t}。", "He ", "must", "might", " be asleep."), ("机に仕事が山積みだ。彼は{t}きっと忙しい{/t}。", "He ", "must", "might", " be busy."), ("何度もあくびをしている。彼女は{t}きっと疲れている{/t}。", "She ", "must", "might", " be tired."), ("かばんが職場にある。彼女は{t}きっと仕事中だ{/t}。", "She ", "must", "might", " be at work.")),
        (("ただ外出中{t}かもしれません{/t}。", "Or he ", "might", "must", " just be out."), ("ただ疲れているだけ{t}かもしれません{/t}。", "Or she ", "might", "must", " just be tired."), ("ただ遅れているだけ{t}かもしれません{/t}。", "Or he ", "might", "must", " just be late."), ("ただ昼食中{t}かもしれません{/t}。", "Or she ", "might", "must", " just be at lunch.")),
        ("Must can mean strong deduction", "must＝強い推測", "人 + <b>must be</b> + 状態", "Fairly sure", "かなり確信", ("He <b>must be busy</b>.", "She <b>must be tired</b>.")),
        ("Might marks possibility", "might＝可能性", "人 + <b>might just be</b> + 状態", "One possible explanation", "あり得る説明の一つ", ("He <b>might just be out</b>.", "She <b>might just be tired</b>.")),
        ("I bet or who knows?", "I bet と who knows", "“I bet” introduces a confident guess. “Who knows?” leaves the question open.", "「I bet」は自信のある推測を導きます。「Who knows?」は答えを決めずに残します。", ("Confident guess", "自信のある推測", "I bet he's busy.", "きっと忙しいのでしょう。"), ("Open uncertainty", "分からないまま", "He might be out. Who knows?", "外出中かもしれません。分かりませんね。"))),
    69: standard_spec(69,
        ("Use this to report a person's earlier statement with the usual backshift.", "人の前の発言を、通常の時制のずらしとともに伝えるときに使います。"), ("Use told plus a person to report an action they said they would do.", "すると言った行動を伝えるときは、told＋人を使います。"),
        ("Report one thing someone said about their situation.", "誰かが自分の状況について言ったことを伝えてください。"), ("Report one thing someone told you they would do.", "誰かがするとあなたに言ったことを伝えてください。"),
        (),
        (("彼は折り返すと{t}私に言いました{/t}。", "He ", "told me", "said me", " he'd call back."), ("彼女はメールすると{t}私に言いました{/t}。", "She ", "told me", "said me", " she'd send an email."), ("彼は後で来ると{t}私に言いました{/t}。", "He ", "told me", "said me", " he'd come later."), ("彼女は明日手伝うと{t}私に言いました{/t}。", "She ", "told me", "said me", " she'd help tomorrow.")),
        ("Step the reported verb back", "伝える動詞を一段戻す", "She said + she <b>was</b> + ...", "Earlier words", "前の発言", ("She said she <b>was busy</b>.", "He said he <b>was tired</b>.")),
        ("Tell needs a person", "tell には人が必要", "He <b>told me</b> + he'd + 動詞", "Report a later action", "後の行動を伝える", ("He <b>told me he'd call back</b>.", "She <b>told me she'd help</b>.")),
        ("A summary or the exact words?", "要約・一字一句", "Use ordinary reported speech for a summary. Add “word for word” only when the wording is exact.", "普通の間接話法は要約です。言葉が完全に同じときだけ「word for word」を加えます。", ("Summary", "要約", "She said she was busy.", "彼女は忙しいと言っていました。"), ("Exact wording", "一字一句同じ", "That's what she said, word for word.", "それが彼女の言った言葉そのままです。"))),
    70: standard_spec(70,
        ("Use told plus a person and to for a positive instruction.", "するようにという指示には、told＋人＋to を使います。"), ("Use asked plus a person and not to for a negative request.", "しないようにというお願いには、asked＋人＋not to を使います。"),
        ("Relay one instruction someone gave you.", "誰かから受けた指示を一つ伝えてください。"), ("Relay one thing someone asked you not to do.", "しないよう頼まれたことを一つ伝えてください。"),
        (("彼女は待つよう{t}私に言いました{/t}。", "She ", "told me", "said me", " to wait here."), ("彼は後で折り返すよう{t}私に言いました{/t}。", "He ", "told me", "said me", " to call back later."), ("彼女は早く来るよう{t}私に言いました{/t}。", "She ", "told me", "said me", " to come early."), ("彼はメールを確認するよう{t}私に言いました{/t}。", "He ", "told me", "said me", " to check the email.")),
        (("彼はそのことを{t}言わないよう{/t}私に頼みました。", "He asked me ", "not to mention", "to mention", " it."), ("彼女はファイルを{t}共有しないよう{/t}私に頼みました。", "She asked me ", "not to share", "to share", " the file."), ("彼は今日{t}電話しないよう{/t}私に頼みました。", "He asked me ", "not to call", "to call", " today."), ("彼女はドアを{t}開けないよう{/t}私に頼みました。", "She asked me ", "not to open", "to open", " the door.")),
        ("Tell, person, then instruction", "tell、人、指示の順", "人 + <b>told me to</b> + 動詞", "Positive instruction", "するようにという指示", ("She <b>told me to wait</b>.", "He <b>told me to call</b>.")),
        ("Not comes before to", "not は to の前", "人 + <b>asked me not to</b> + 動詞", "Negative request", "しないようにというお願い", ("He <b>asked me not to mention it</b>.", "She <b>asked me not to open it</b>.")),
        ("Told me to or asked me to?", "told me to と asked me to", "Use “told me to” for an instruction. Use “asked me to” for a request, which usually sounds less forceful.", "指示を伝えるときは「told me to」を使います。お願いなら「asked me to」を使い、通常は少し柔らかく聞こえます。", ("Instruction", "指示", "She told me to wait.", "彼女は待つよう私に言いました。"), ("Request", "お願い", "She asked me to wait.", "彼女は待つよう私に頼みました。"))),
}


VOCAB = {
    60: dict(new="window|窓; close|閉める; open|開ける; mind|気にする; could|〜してもらえる; would|〜していただける", recycled="", assumed="door|ドア; check|確認する; file|ファイル; send|送る; email|メール; thanks|ありがとう; thank you|ありがとう; no rush|急ぎではない", receptive="favor|お願い; impose|負担をかける; urgent|緊急の"),
    61: dict(new="chair|椅子; go ahead|どうぞ; please do|ぜひどうぞ", recycled="window|窓|CORE-60; mind|気にする|CORE-60; open|開ける|CORE-60", assumed="sit|座る; use|使う; photo|写真; take|撮る; rather|むしろ; keep it closed|閉めたままにする; sorry|すみません; perfect|ちょうどよい; thank you|ありがとう; of course|もちろん; go through|先へ進む", receptive="permission|許可; bother|迷惑をかける; sorry, someone's sitting there|すみません、そこには人が座っています"),
    62: dict(new="meeting room|会議室; next train|次の電車; leaves|出発する; know|分かる; tell|教える", recycled="could|〜してもらえる|CORE-60; station|駅|CORE-7; bank|銀行|CORE-7; café|カフェ|CORE-7; shop|店|CORE-10; meeting|会議|CORE-30; upstairs|2階|CORE-56", assumed="opens|開く; starts|始まる; closes|閉まる; blocks away|ブロック先; departure time|出発時刻; help|助け; thank you|ありがとう; great|分かった; perfect|よかった; go|行く", receptive="sorry to bother you|お邪魔してすみません; by any chance|もしかして; platform|ホーム"),
    63: dict(new="generally|たいてい; tea|紅茶; noisy|騒がしい; avoid|避ける; tend|傾向がある; busy|人が多い", recycled="prefer|〜のほうが好き|CORE-42; coffee|コーヒー|CORE-9; café|カフェ|CORE-7; restaurant|レストラン|CORE-10; crowded|混んでいる|CORE-44; expensive|高い|CORE-19", assumed="train|電車; buses|バス; mornings|朝; evenings|夜; places|場所; kinds|種類; strong preference|強い好み; great|よかった; go in|中に入る; take it|それに乗る", receptive="in general|一般に; as a rule|概して"),
    64: dict(new="laptop|ノートパソコン; charge|充電する; cable|ケーブル; restart|再起動する; turn on|電源が入る; tried|試した; won't|どうしても〜しない", recycled="print|印刷する|CORE-41", assumed="phone|携帯; door|ドア; open|開く; check|確認する; another way|別の方法; broken|壊れている; works|動く; handout|資料; let you know|知らせる; other handle|別の取っ手; nothing|何もない; great|よかった", receptive="malfunction|不具合; it's playing up|調子が悪い; that did the trick|それで直った"),
    65: dict(new="stolen|盗まれた; taken from|から取られた; pocket|ポケット; desk|机", recycled="wallet|財布|CORE-55; ticket|チケット|CORE-5; bag|かばん|CORE-5; please|お願いします|CORE-9", assumed="phone|携帯; car|車; lost|なくした; something important|大切な物; call|電話する; find|見つける; everything|すべて; know|分かる; thank you|ありがとう", receptive="theft|盗難; apparently|どうやら; it turns out|結局分かる"),
    66: dict(new="more time|もっと時間; more money|もっとお金; free month|1か月の休み; abroad|海外; bigger|より広い; anywhere|どこでも; would|〜するだろう; could|〜できたら", recycled="move|引っ越す|CORE-37", assumed="won|当たった; travel|旅行する; study|勉強する; work at home|家で働く; room|部屋; Osaka|大阪; sounds fun|楽しそう; sounds peaceful|落ち着きそう", receptive="imaginary|想像上の; in a perfect world|理想を言えば; realistically|現実的には"),
    67: dict(new="free time|自由な時間; energy|元気; quieter|より静かな; schedule|予定; wish|願う", recycled="could|〜できたら|CORE-66; drive|運転する|CORE-14; work from home|在宅勤務をする|CORE-25", assumed="would|〜してくれたら; cook|料理する; travel|旅行する; better|より上手に; room|部屋; nothing comes to mind|何も思いつかない; good idea|いい考え; help a lot|とても助かる", receptive="dissatisfaction|不満; if only|さえあれば; oh well|まあ仕方ない"),
    68: dict(new="asleep|寝ている; must|きっと〜だ", recycled="might|〜かもしれない|CORE-39; busy|忙しい|CORE-30; tired|疲れた|CORE-30", assumed="out|外出中; late|遅れて; at work|仕事中; at lunch|昼食中; call later|後で電話する; check again|もう一度確認する; happened|起きた; think|思う; agreed|同意した", receptive="deduction|推測; I bet|きっと; who knows|分からないね; evidence|根拠"),
    69: dict(new="call back|折り返す; said|言った; told|伝えた", recycled="busy|忙しい|CORE-30; tired|疲れた|CORE-30", assumed="say|言う; tell|伝える; late|遅れる; home|家; email|メール; tomorrow|明日; at home|家に; send an email|メールする; come later|後で来る; help tomorrow|明日手伝う; check later|後で確認する; after dinner|夕食後; recently|最近; memorable|印象に残る", receptive="backshift|時制のずらし; apparently|どうやら; promised|約束した; word for word|一字一句"),
    70: dict(new="mention|言及する; share|共有する; asked|頼んだ", recycled="call back|折り返す|CORE-69; window|窓|CORE-60; told|伝えた|CORE-69", assumed="ask|頼む; email|メール; door|ドア; file|ファイル; wait|待つ; later|後で; come early|早く来る; check the email|メールを確認する; call today|今日電話する; open the door|ドアを開ける; instruction|指示; recently|最近; thank you|ありがとう; great|よかった; know|分かる; wanted|望んだ; gave|与えた", receptive="word has it|うわさでは; strictly speaking|厳密に言えば"),
}


KNOWN_WORDS = {
    60: (("ドア", "door"), ("ファイル", "file"), ("メール", "email")),
    61: (("写真", "photo"), ("窓", "window"), ("開ける", "open")),
    62: (("駅", "station"), ("カフェ", "café"), ("会議", "meeting")),
    63: (("コーヒー", "coffee"), ("カフェ", "café"), ("レストラン", "restaurant")),
    64: (("プリンター", "printer"), ("携帯", "phone"), ("開く", "open")),
    65: (("チケット", "ticket"), ("かばん", "bag"), ("携帯", "phone")),
    66: (("旅行する", "travel"), ("勉強する", "study"), ("家で働く", "work at home")),
    67: (("運転する", "drive"), ("料理する", "cook"), ("旅行する", "travel")),
    68: (("仕事中", "at work"), ("昼食中", "at lunch"), ("遅れて", "late")),
    69: (("メール", "email"), ("家", "home"), ("明日", "tomorrow")),
    70: (("メール", "email"), ("ドア", "door"), ("ファイル", "file")),
}


TRANSLATE_HINTS = {
    60: (("窓:window; 開ける:open", "ドア:door; 閉める:close", "ファイル:file; 確認する:check", "メール:email; 送る:send"), ("窓:window; 開ける:open", "ドア:door; 閉める:close", "ファイル:file; 確認する:check", "メール:email; 送る:send")),
    61: (("座る:sit", "窓:window; 開ける:open", "椅子:chair; 使う:use", "写真:photo"), ("どうぞ:go ahead", "ぜひどうぞ:please do", "使う:use", "撮る:take")),
    62: (("駅:station", "銀行:bank", "カフェ:café", "会議室:meeting room"), ("次の電車:next train; 出発する:leave", "店:shop; 開く:open", "会議:meeting; 始まる:start", "カフェ:café; 閉まる:close")),
    63: (("コーヒー:coffee; 紅茶:tea", "電車:train; バス:bus", "カフェ:café; レストラン:restaurant", "朝:morning; 夜:evening"), ("混んでいる:crowded; 場所:place", "騒がしい:noisy; 場所:place", "高い:expensive; 場所:place", "人が多い:busy; 場所:place")),
    64: (("ノートパソコン:laptop", "プリンター:printer", "携帯:phone; 充電する:charge", "ドア:door; 開く:open"), ("再起動する:restart", "確認する:check; ケーブル:cable", "充電する:charge", "開く:open; 別の方法:another way")),
    65: (("財布:wallet; 盗む:steal", "携帯:phone; 盗む:steal", "チケット:ticket; 盗む:steal", "かばん:bag; 盗む:steal"), ("かばん:bag; 取る:take", "ポケット:pocket; 取る:take", "机:desk; 取る:take", "車:car; 取る:take")),
    66: (("もっと時間:more time; 旅行する:travel", "もっとお金:more money; 引っ越す:move", "1か月の休み:free month; 海外:abroad", "より広い:bigger; 家で働く:work at home"), ("当たる:win", "1か月の休み:free month", "もっと時間:more time", "どこでも:anywhere")),
    67: (("自由な時間:free time", "元気:energy", "より静かな:quieter", "予定:schedule"), ("運転する:drive", "料理する:cook; より上手に:better", "旅行する:travel", "在宅勤務をする:work from home")),
    68: (("忙しい:busy", "疲れた:tired", "寝ている:asleep", "仕事中:at work"), ("外出中:out", "疲れた:tired", "遅れて:late", "昼食中:at lunch")),
    69: (("忙しい:busy", "疲れた:tired", "遅れて:late", "家に:at home"), ("折り返す:call back", "メールする:send an email", "後で来る:come later", "明日手伝う:help tomorrow")),
    70: (("待つ:wait", "折り返す:call back", "早く来る:come early", "メールを確認する:check the email"), ("言及する:mention", "共有する:share", "今日電話する:call today", "ドアを開ける:open the door")),
}


OPEN_MENUS = {
    60: (("窓:window", "開ける:open", "閉める:close", "ファイル:file"), ("窓:window", "開ける:open", "閉める:close", "メール:email")),
    61: (("座る:sit", "窓:window", "椅子:chair", "写真:photo"), ("どうぞ:go ahead", "使う:use", "写真:photo")),
    62: (("駅:station", "銀行:bank", "会議室:meeting room"), ("次の電車:next train", "会議:meeting", "カフェ:café")),
    63: (("コーヒー:coffee", "紅茶:tea", "バス:buses", "朝:mornings"), ("混んだ:crowded", "騒がしい:noisy", "高い:expensive", "場所:places")),
    64: (("ノートパソコン:laptop", "プリンター:printer", "携帯:phone"), ("再起動する:restart", "確認する:check", "ケーブル:cable", "充電する:charge")),
    65: (("財布:wallet", "携帯:phone", "チケット:ticket"), ("かばん:bag", "ポケット:pocket", "机:desk")),
    66: (("もっと時間:more time", "もっとお金:more money", "1か月の休み:free month"), ("当たった:won", "1か月の休み:free month", "どこでも:anywhere")),
    67: (("自由な時間:free time", "元気:energy", "より静かな:quieter"), ("運転する:drive", "料理する:cook", "旅行する:travel")),
    68: (("忙しい:busy", "疲れた:tired", "寝ている:asleep"), ("外出中:out", "遅れて:late", "昼食中:at lunch")),
    69: (("忙しい:busy", "疲れた:tired", "家に:at home"), ("折り返す:call back", "メールする:send an email", "後で来る:come later")),
    70: (("待つ:wait", "折り返す:call back", "早く来る:come early"), ("言及する:mention", "共有する:share", "今日電話する:call today")),
}


DIALOGUES = {
    60: dict(model=("Coworker", 0, 2, ("It's getting warm in here.", "ここは少し暑くなってきましたね。"), ("Of course. Is there anything else?", "もちろんです。ほかにもありますか？"), ("Sure. I'll look at it after lunch.", "分かりました。昼食後に確認します。"), ("Thanks. There's no rush.", "ありがとう。急ぎではありません。")), wild=("Coworker", 1, 2, ("The hallway is noisy today.", "今日は廊下が騒がしいですね。"), ("Sure. Is there anything else?", "もちろんです。ほかにもありますか？"), ("Not at all. I'll check it this afternoon.", "もちろんです。今日の午後に確認します。"), ("Thank you. There's no rush.", "ありがとう。急ぎではありません。"))),
    61: dict(model=("Coworker", 0, 1, ("This seat is free.", "この席は空いています。"), ("Not at all, go ahead. Do you mind if I open the window?", "全く構いません。どうぞ。私が窓を開けてもよろしいですか？"), ("Thanks. I'll open it just a little.", "ありがとう。少しだけ開けます。"), ("Perfect. Thank you.", "ちょうどいいです。ありがとう。")), wild=("Gallery staff", 3, 1, ("The exhibit continues in the next room.", "展示は隣の部屋に続きます。"), ("Not at all, please do. Do you mind if I close this door?", "全く構いません。ぜひどうぞ。このドアを閉めてもよろしいですか？"), ("Thank you. The next tour is starting.", "ありがとう。次のツアーが始まります。"), ("Of course. I'll go through now.", "もちろんです。今、先へ進みます。"))),
    62: dict(model=("Hotel receptionist", 0, 0, ("Where are you heading this afternoon?", "今日の午後はどちらへ向かいますか？"), ("It's two blocks away. Do you need the departure time too?", "2ブロック先です。出発時刻も必要ですか？"), ("It leaves at 3:20 from platform four.", "3時20分に4番ホームから出ます。"), ("Great. Thank you for your help.", "分かりました。ありがとうございます。")), wild=("Receptionist", 3, 2, ("Welcome. Are you here for the team meeting?", "ようこそ。チーム会議にいらっしゃいましたか？"), ("It's on the second floor. Do you need the start time too?", "2階です。開始時刻も必要ですか？"), ("It starts at ten, so you have time.", "10時に始まるので、まだ時間があります。"), ("Perfect. I'll go upstairs now.", "よかったです。今、上に行きます。"))),
    63: dict(model=("Friend", 0, 0, ("Shall we get a drink?", "飲み物を買いませんか？"), ("Good to know. What kind of cafés do you avoid?", "分かりました。どんなカフェを避けますか？"), ("This one is quiet, so it should be fine.", "ここは静かなので、大丈夫そうです。"), ("Great. Let's go in.", "よかった。入りましょう。")), wild=("Coworker", 1, 0, ("Should we take the train or the bus?", "電車とバス、どちらにしましょうか？"), ("Me too. What kind of places do you avoid?", "私もです。どんな場所を避けますか？"), ("This train is quiet, and there are plenty of seats.", "この電車は静かで、席もたくさんあります。"), ("Great. Let's take it.", "よかった。これに乗りましょう。"))),
    64: dict(model=("Coworker", 1, 1, ("The printer is silent when I press Print.", "印刷を押しても、プリンターが動きません。"), ("I haven't checked anything yet. What should I try first?", "まだ何も確認していません。最初に何を試せばいいですか？"), ("That worked. The cable was loose.", "直りました。ケーブルが緩んでいました。"), ("Great. Now we can print the handout.", "よかった。これで資料を印刷できますね。")), wild=("Neighbor", 3, 3, ("The side door is stuck when I pull the handle.", "取っ手を引いても、横のドアが開きません。"), ("I haven't tried another way yet. What should I try?", "まだ別の方法は試していません。何を試せばいいですか？"), ("Good idea. I'll try the other handle.", "いい考えです。別の取っ手を試します。"), ("I'll let you know if that works.", "うまくいったら知らせます。"))),
    65: dict(model=("Police officer", 0, 0, ("What happened?", "何がありましたか？"), ("I'm sorry. Where was it taken from?", "それは大変でした。どこから取られましたか？"), ("All right. I'll write down those details.", "分かりました。その情報を記録します。"), ("Thank you. That's everything I know.", "ありがとうございます。分かることは以上です。")), wild=("Station staff", 2, 1, ("What item are you reporting?", "何を届け出ますか？"), ("Where did you last have it?", "最後にどこで持っていましたか？"), ("Thank you. We'll check the cameras.", "ありがとうございます。防犯カメラを確認します。"), ("Please call me if you find it.", "見つかったら電話してください。"))),
    66: dict(model=("Friend", 0, 0, ("You work a lot. What would you change?", "よく働いていますね。何を変えたいですか？"), ("That sounds good. I've never imagined winning a big prize.", "いいですね。大きな賞金が当たることは考えたことがありません。"), ("I'd open a small café.", "小さなカフェを開きます。"), ("That sounds fun.", "楽しそうですね。")), wild=("Coworker", 2, 3, ("Imagine the office closes for a month. What would you do?", "オフィスが1か月休みだと想像してください。何をしますか？"), ("Nice. I've never imagined being able to work anywhere.", "いいですね。どこでも働ける状況は考えたことがありません。"), ("I'd work by the sea.", "私は海辺で働きます。"), ("That sounds peaceful.", "落ち着きそうですね。"))),
    67: dict(model=("Friend", 0, 0, ("You seem busy lately. What would make life easier?", "最近忙しそうですね。何があれば楽になりますか？"), ("Me too. Is there anything you wish you could do?", "私もです。できたらいいと思うことはありますか？"), ("You could start with a short lesson.", "短いレッスンから始められますよ。"), ("That's a good idea.", "いい考えです。")), wild=("Coworker", 3, 3, ("You commute every day. Is your schedule difficult?", "毎日通勤していますね。予定は大変ですか？"), ("I understand. What do you wish you could change?", "分かります。何を変えられたらいいですか？"), ("Maybe we can arrange one home day a week.", "週に1日は在宅にできるかもしれません。"), ("That would help a lot.", "それはとても助かります。"))),
    68: dict(model=("Coworker", 0, 0, ("Ken hasn't answered any messages today.", "ケンは今日、メッセージに全く返事をしていません。"), ("Maybe. Is there another explanation?", "そうかもしれません。別の説明はありますか？"), ("Right. Let's wait before we worry.", "そうですね。心配する前に待ちましょう。"), ("Agreed. We'll call later.", "そうしましょう。後で電話します。")), wild=("Friend", 2, 2, ("Leo's lights are off and he isn't answering.", "レオの部屋は消灯していて、返事もありません。"), ("That makes sense. Or is there another possibility?", "なるほど。ほかの可能性はありますか？"), ("Exactly. We don't know yet.", "そのとおりです。まだ分かりません。"), ("Let's check again later.", "後でもう一度確認しましょう。"))),
    69: dict(model=("Coworker", 0, 1, ("Did Mia explain why she missed the meeting?", "ミアは会議を欠席した理由を説明しましたか？"), ("I see. Did she say what she'd do next?", "なるほど。次に何をするか言いましたか？"), ("Good. Then we can wait for her email.", "よかった。それならメールを待てますね。"), ("Yes. I'll check later.", "はい。後で確認します。")), wild=("Friend", 1, 2, ("Did Ken say why he left early?", "ケンは早く帰った理由を言いましたか？"), ("That explains it. Did he tell you his plan?", "それで分かりました。予定をあなたに言いましたか？"), ("Fine. We'll see him later.", "分かりました。後で会えますね。"), ("Yes. He'll come after dinner.", "はい。夕食後に来ます。"))),
    70: dict(model=("Coworker", 0, 1, ("What did the receptionist tell you?", "受付の人は何と言いましたか？"), ("All right. Was there anything we shouldn't do?", "分かりました。してはいけないことはありましたか？"), ("Understood. I'll keep the file private.", "分かりました。ファイルは内密にします。"), ("Thanks. That's what she wanted.", "ありがとう。それが彼女の希望でした。")), wild=("Friend", 2, 3, ("What did the organizer tell you?", "主催者は何と言いましたか？"), ("Okay. Did she make any other request?", "分かりました。ほかにお願いはありましたか？"), ("No problem. I'll leave it closed.", "大丈夫です。閉めたままにします。"), ("Great. Now we know what to do.", "よかった。これで何をすべきか分かりました。"))),
}


LIVE_SCENES = {
    60: (("text", "other", "Tutor", "What small favor would you like to ask me? A practice request is fine.", "私にどんな小さなお願いをしたいですか？ 練習用のお願いでも構いません。"), ("input", "me", "Me", "Could you ___?", "___してもらえますか？"), ("input", "me", "Me", "Would you mind ___ing?", "___していただけますか？"), ("input", "other", "Tutor", "Tutor's answer to the request", "そのお願いに対する先生の実際の答え")),
    61: (("text", "other", "Tutor", "Do you mind if I open the window?", "私が窓を開けてもよろしいですか？"), ("input", "me", "Me", "Not at all, go ahead. / Sorry, I'd rather keep it closed.", "全く構いません。どうぞ。／すみません、閉めたままがいいです。"), ("input", "me", "Me", "Do you mind if I sit here?", "私がここに座ってもよろしいですか？"), ("input", "other", "Tutor", "Tutor's answer: Not at all, ___. / Sorry, ___.", "先生の実際の答え：全く構いません、___。／すみません、___。")),
    62: (("text", "other", "Tutor", "What place or time information do you need? A practice question is fine.", "どんな場所や時刻の情報が必要ですか？ 練習用の質問でも構いません。"), ("input", "me", "Me", "Do you know where ___ is?", "___がどこにあるか分かりますか？"), ("input", "me", "Me", "Could you tell me when ___?", "___がいつか教えてもらえますか？"), ("input", "other", "Tutor", "Tutor's answer with the place or time", "場所または時刻についての先生の実際の答え")),
    63: (("text", "other", "Tutor", "Which do you generally prefer: coffee or tea?", "コーヒーと紅茶では、ふだんどちらが好きですか？"), ("input", "me", "Me", "I generally prefer ___ to ___. / I don't have a strong preference.", "私はふだん___より___のほうが好きです。／特に強い好みはありません。"), ("input", "me", "Me", "What kinds of places do you tend to avoid?", "どんな場所を避けることが多いですか？"), ("input", "other", "Tutor", "Tutor's answer: I tend to avoid ___ places.", "先生の実際の答え：___場所を避けることが多いです。")),
    64: (("text", "other", "Tutor", "My laptop won't turn on.", "ノートパソコンの電源が入りません。"), ("input", "me", "Me", "Have you tried restarting it?", "再起動してみましたか？"), ("input", "other", "Tutor", "Tutor's answer about that fix", "その対処についての先生の実際の答え"), ("text", "me", "Me", "My printer won't print. What should I try?", "プリンターが印刷してくれません。何を試せばいいですか？"), ("input", "other", "Tutor", "Tutor's answer: one troubleshooting suggestion", "先生の実際の対処案")),
    65: (("text", "other", "Tutor", "Let's make an imaginary lost-property report. What was stolen?", "想像上の盗難届を作りましょう。何を盗まれましたか？"), ("input", "me", "Me", "My ___ was stolen. It was taken from ___.", "私の___が盗まれました。それは___から取られました。"), ("input", "me", "Me", "Have you ever lost something important?", "大切な物をなくしたことがありますか？"), ("input", "other", "Tutor", "Tutor's answer: Yes, ___. / No, I haven't.", "先生の実際の答え：はい、___。／いいえ、ありません。")),
    66: (("text", "other", "Tutor", "What would you do if you had more free time?", "もっと自由な時間があったら何をしますか？"), ("input", "me", "Me", "If I had more time, I'd ___.", "もっと時間があれば、___します。"), ("input", "me", "Me", "What would you do if you had a free month?", "1か月休みがあったら何をしますか？"), ("input", "other", "Tutor", "Tutor's answer: If I had a free month, I'd ___.", "先生の実際の答え：1か月休みがあれば、___します。")),
    67: (("text", "other", "Tutor", "What do you wish you had more of right now?", "今、もっと何があればいいと思いますか？"), ("input", "me", "Me", "I wish I had more ___. / Nothing comes to mind right now.", "もっと___があればいいのに。／今は特に思いつきません。"), ("input", "me", "Me", "What do you wish you could do?", "何ができればいいと思いますか？"), ("input", "other", "Tutor", "Tutor's answer: I wish I could ___.", "先生の実際の答え：___できたらいいのにと思います。")),
    68: (("text", "other", "Tutor", "A friend hasn't replied all day. What is your strongest guess?", "友だちが一日中返事をしていません。一番強い推測は何ですか？"), ("input", "me", "Me", "They must be ___. Or they might just be ___.", "きっと___です。それとも、ただ___なのかもしれません。"), ("input", "me", "Me", "What do you think happened?", "何があったと思いますか？"), ("input", "other", "Tutor", "Tutor's answer: They must be ___. / They might just be ___.", "先生の実際の推測：きっと___です。／ただ___なのかもしれません。")),
    69: (("text", "other", "Tutor", "Tell me one thing someone said to you recently.", "最近、誰かがあなたに言ったことを一つ教えてください。"), ("input", "me", "Me", "___ said they were ___. / No one said anything memorable recently.", "___は___だと言いました。／最近、印象に残ることは誰にも言われませんでした。"), ("input", "me", "Me", "What did someone tell you they'd do?", "誰かがすると言ったことは何ですか？"), ("input", "other", "Tutor", "Tutor's answer: ___ told me they'd ___.", "先生の実際の答え：___は___すると私に言いました。")),
    70: (("text", "other", "Tutor", "What instruction or request did someone give you recently?", "最近、誰かからどんな指示やお願いを受けましたか？"), ("input", "me", "Me", "___ told me to ___. / No one gave me an instruction recently.", "___は___するよう私に言いました。／最近は誰にも指示されませんでした。"), ("input", "me", "Me", "What did someone ask you not to do?", "誰かに何をしないよう頼まれましたか？"), ("input", "other", "Tutor", "Tutor's answer: ___ asked me not to ___.", "先生の実際の答え：___は___しないよう私に頼みました。")),
}


LIVE_HINTS = {n: {1: OPEN_MENUS[n][0], 2: OPEN_MENUS[n][1]} for n in LESSONS}
LIVE_HINTS[61] = {
    1: ("どうぞ:go ahead", "すみません:sorry", "閉めたまま:keep it closed"),
    2: OPEN_MENUS[61][0],
}
LIVE_HINTS[64] = {1: OPEN_MENUS[64][1]}
LIVE_HINTS[65] = {
    1: OPEN_MENUS[65][0] + OPEN_MENUS[65][1],
    2: OPEN_MENUS[65][0],
}


# Human-reviewed operating copy for the CORE60--70 page-by-page audit.  Open
# production names the exact frame and communicative job.  Free Talk is a real
# topic exchange rather than another controlled pattern drill: the learner
# answers a useful question, asks the tutor a natural version of it, and the
# tutor records a real short answer.  Today's pattern remains optional there.
WRITE_PROMPTS = {
    60: (("Now use “Could you ___?” to ask me for one small, useful favor.", "では、「Could you ___?」を使って、役に立つ小さなお願いを一つしてください。"), ("Now use “Would you mind ___ing?” to make one request that needs extra care.", "では、「Would you mind ___ing?」を使って、特に配慮が必要なお願いを一つしてください。")),
    61: (("Now use “Do you mind if I ___?” to ask permission for one real action.", "では、「Do you mind if I ___?」を使って、実際にしたい行動の許可を求めてください。"), ("Now use “Not at all, ___” to give permission clearly.", "では、「Not at all, ___」を使って、はっきり許可してください。")),
    62: (("Now use “Do you know where ___ is?” to ask where one useful place is.", "では、「Do you know where ___ is?」を使って、役に立つ場所を一つたずねてください。"), ("Now use “Could you tell me when ___?” to ask about one real time or event.", "では、「Could you tell me when ___?」を使って、実際の時刻や予定を一つたずねてください。")),
    63: (("Now use “I generally prefer ___ to ___” to compare two things you genuinely like.", "では、「I generally prefer ___ to ___」を使って、本当に好きなものを二つ比べてください。"), ("Now use “I tend to avoid ___” to name one kind of place you usually avoid.", "では、「I tend to avoid ___」を使って、ふだん避ける場所の種類を一つ言ってください。")),
    64: (("Now use “___ won't ___” to describe one device or object that is not working.", "では、「___ won't ___」を使って、動かない機器や物を一つ説明してください。"), ("Now use “Have you tried ___ing?” to suggest one practical fix.", "では、「Have you tried ___ing?」を使って、実用的な対処法を一つ提案してください。")),
    65: (("Now use “My ___ was stolen” to make one clear theft report.", "では、「My ___ was stolen」を使って、盗まれた持ち物について明確に伝えてください。"), ("Now use “It was taken from ___” to say where the item was taken from.", "では、「It was taken from ___」を使って、品物がどこから取られたか伝えてください。")),
    66: (("Now use “If I had ___, I'd ___” to imagine one change and its result.", "では、「If I had ___, I'd ___」を使って、変化とその結果を一つ想像してください。"), ("Now use “What would you do if ___?” to ask me about one imaginary situation.", "では、「What would you do if ___?」を使って、想像上の状況で私ならどうするか聞いてください。")),
    67: (("Now use “I wish I had ___” to name one thing you genuinely want more of.", "では、「I wish I had ___」を使って、本当にもっと欲しいものを一つ言ってください。"), ("Now use “I wish I could ___” to name one ability you would like to have.", "では、「I wish I could ___」を使って、できるようになりたいことを一つ言ってください。")),
    68: (("Now use “___ must be ___” to make one strong guess from evidence.", "では、「___ must be ___」を使って、根拠のある強い推測を一つしてください。"), ("Now use “___ might just be ___” to add one reasonable alternative.", "では、「___ might just be ___」を使って、別の可能性を一つ加えてください。")),
    69: (("Now use “___ said they were ___” to report one thing someone said.", "では、「___ said they were ___」を使って、誰かが言ったことを一つ伝えてください。"), ("Now use “___ told me they'd ___” to report one thing someone said they would do.", "では、「___ told me they'd ___」を使って、誰かがすると言ったことを一つ伝えてください。")),
    70: (("Now use “___ told me to ___” to relay one instruction you received.", "では、「___ told me to ___」を使って、受けた指示を一つ伝えてください。"), ("Now use “___ asked me not to ___” to relay one negative request.", "では、「___ asked me not to ___」を使って、しないよう頼まれたことを一つ伝えてください。")),
}


# Fill chips support only the lexical payload.  They never supply articles,
# auxiliaries, polarity, reporting structure, or the target inflection.
FILL_HINTS = {
    60: ((('開ける', 'open'), ('閉める', 'close'), ('確認する', 'check'), ('送る', 'send')), (('開ける', 'open'), ('閉める', 'close'), ('確認する', 'check'), ('送る', 'send'))),
    61: ((('座る', 'sit'), ('開ける', 'open'), ('使う', 'use'), ('撮る', 'take')), (('どうぞ', 'go ahead'), ('ぜひどうぞ', 'please do'), ('使う', 'use'), ('撮る', 'take'))),
    62: ((('駅', 'station'), ('銀行', 'bank'), ('カフェ', 'café'), ('会議室', 'meeting room')), (('次の電車', 'next train'), ('店', 'shop'), ('会議', 'meeting'), ('カフェ', 'café'))),
    63: ((('コーヒー', 'coffee'), ('電車', 'train'), ('カフェ', 'café'), ('朝', 'morning')), (('混んでいる', 'crowded'), ('騒がしい', 'noisy'), ('高い', 'expensive'), ('人が多い', 'busy'))),
    64: ((('電源が入る', 'turn on'), ('印刷する', 'print'), ('充電する', 'charge'), ('開く', 'open')), (('再起動する', 'restart'), ('確認する', 'check'), ('充電する', 'charge'), ('開く', 'open'))),
    65: ((('盗む', 'steal'), ('盗む', 'steal'), ('盗む', 'steal'), ('盗む', 'steal')), (('取る', 'take'), ('取る', 'take'), ('取る', 'take'), ('取る', 'take'))),
    66: (((('もっと時間', 'more time'), ('旅行する', 'travel')), (('もっとお金', 'more money'), ('引っ越す', 'move')), (('1か月の休み', 'free month'), ('勉強する', 'study')), (('より広い部屋', 'bigger room'), ('働く', 'work'))), (('当たる', 'win'), ('1か月の休み', 'free month'), ('もっと時間', 'more time'), ('どこでも', 'anywhere'))),
    67: ((('自由な時間', 'free time'), ('元気', 'energy'), ('静かな部屋', 'quiet room'), ('予定', 'schedule')), (('運転する', 'drive'), ('料理する', 'cook'), ('旅行する', 'travel'), ('在宅勤務をする', 'work from home'))),
    68: ((('忙しい', 'busy'), ('疲れた', 'tired'), ('寝ている', 'asleep'), ('仕事中', 'at work')), (('外出中', 'out'), ('疲れた', 'tired'), ('遅れて', 'late'), ('昼食中', 'at lunch'))),
    69: ((('忙しい', 'busy'), ('疲れた', 'tired'), ('遅れて', 'late'), ('家に', 'at home')), (('折り返す', 'call back'), ('メールする', 'send an email'), ('後で来る', 'come later'), ('明日手伝う', 'help tomorrow'))),
    70: ((('待つ', 'wait'), ('折り返す', 'call back'), ('来る', 'come'), ('確認する', 'check')), (('言及する', 'mention'), ('共有する', 'share'), ('電話する', 'call'), ('開ける', 'open'))),
}


TRANSLATE_STAGES = {number: ("supported", "supported") for number in LESSONS}


CHOICE_OMISSIONS = {
    60: set(), 61: {1}, 62: {1, 2}, 63: set(), 64: {1}, 65: {2},
    66: set(), 67: {1, 2}, 68: {2}, 69: {1}, 70: set(),
}

SPECS[61]["choices"] = ((), (
    ("相手は許可する。{t}全く構いません{/t}。どうぞ。", "", "Not at all", "Sorry", ", go ahead."),
    ("席は使われている。{t}すみません{/t}、そこには人が座っています。", "", "Sorry", "Not at all", ", someone's sitting there."),
    ("相手は許可する。{t}全く構いません{/t}。ぜひどうぞ。", "", "Not at all", "Sorry", ", please do."),
    ("今は椅子が必要だ。{t}すみません{/t}、今使っています。", "", "Sorry", "Not at all", ", I'm using it right now."),
))
SPECS[62]["choices"] = ((), ())
SPECS[64]["choices"] = ((), SPECS[64]["choices"][1])
SPECS[65]["choices"] = (SPECS[65]["choices"][0], ())
SPECS[66]["choices"] = (
    (
        ("今は時間がない。もっと時間が{t}あれば{/t}、旅行するのに。", "If I ", "had", "have", " more time, I'd travel."),
        ("今日もっと時間があれば、遠くへ行く予定です。{t}現実的な条件{/t}。", "If I ", "have", "had", " more time today, I'll travel farther."),
        ("今はお金が足りない。もっとお金が{t}あれば{/t}、引っ越すのに。", "If I ", "had", "have", " more money, I'd move."),
        ("来年もっと広い部屋があれば、在宅勤務をします。{t}現実的な条件{/t}。", "If I ", "have", "had", " a bigger room next year, I'll work at home."),
    ),
    (
        ("想像：1か月休みがあったら{t}何をしますか{/t}？", "What ", "would", "will", " you do if you had a free month?"),
        ("現実的な予定：会議が早く終わったら{t}何をしますか{/t}？", "What ", "will", "would", " you do if the meeting ends early?"),
        ("想像：どこでも働けたら{t}何をしますか{/t}？", "What ", "would", "will", " you do if you could work anywhere?"),
        ("現実的な予定：電車が遅れたら{t}何をしますか{/t}？", "What ", "will", "would", " you do if the train is late?"),
    ),
)
SPECS[67]["choices"] = ((), ())
SPECS[68]["choices"] = ((
    ("机に資料が山積みだ。彼は{t}きっと忙しい{/t}。", "He ", "must be", "might be", " busy."),
    ("返事がないだけだ。彼は{t}忙しいかもしれない{/t}。", "He ", "might be", "must be", " busy."),
    ("一晩中働いた。彼女は{t}きっと疲れている{/t}。", "She ", "must be", "might be", " tired."),
    ("少し静かなだけだ。彼女は{t}疲れているかもしれない{/t}。", "She ", "might be", "must be", " tired."),
), ())
SPECS[69]["choices"] = ((), (
    ("彼は折り返すと{t}私に言いました{/t}。", "He ", "told me", "said", " he'd call back."),
    ("彼女はメールすると{t}言いました{/t}。", "She ", "said", "told me", " she'd send an email."),
    ("彼は後で来ると{t}私に言いました{/t}。", "He ", "told me", "said", " he'd come later."),
    ("彼女は明日手伝うと{t}言いました{/t}。", "She ", "said", "told me", " she'd help tomorrow."),
))
SPECS[70]["choices"] = ((
    ("彼女は待つよう{t}私に言いました{/t}。", "She ", "told me", "said", " to wait."),
    ("彼は後で電話すると{t}言いました{/t}。", "He ", "said", "told me", " he'd call later."),
    ("彼女は早く来るよう{t}私に言いました{/t}。", "She ", "told me", "said", " to come early."),
    ("彼はメールを確認すると{t}言いました{/t}。", "He ", "said", "told me", " he'd check the email."),
), SPECS[70]["choices"][1])


REVIEWED_LIVE = {
    60: ("What's a small favor you really appreciate when someone does it for you, and why?", "誰かにしてもらうと本当にありがたい小さなことは何ですか？なぜですか？", "What small favor do you appreciate most?", "先生はどんな小さなことをしてもらうと一番ありがたいですか？"),
    61: ("What behavior bothers you most in a shared space, and why?", "共有スペースで一番気になる行動は何ですか？なぜですか？", "What bothers you most in a shared space?", "先生は共有スペースで何が一番気になりますか？"),
    62: ("When you arrive somewhere new, what information do you usually need first?", "初めての場所に着いたとき、最初にどんな情報が必要ですか？", "What information do you usually need first?", "先生は最初にどんな情報が必要ですか？"),
    63: ("What matters most when you choose a café or restaurant?", "カフェやレストランを選ぶとき、何を一番重視しますか？", "What matters most to you when you choose a place?", "先生は店を選ぶとき、何を一番重視しますか？"),
    64: ("Which device problem frustrates you most, and what do you try first?", "どんな機器の不具合が一番困りますか？最初に何を試しますか？", "Which device problem frustrates you most?", "先生はどんな機器の不具合が一番困りますか？"),
    65: ("What's one item you would be most upset to lose, and why?", "なくしたら一番困る物は何ですか？なぜですか？", "What would you be most upset to lose?", "先生は何をなくしたら一番困りますか？"),
    66: ("If you suddenly had one free month, how would you spend it?", "突然1か月休みができたら、どう過ごしますか？", "How would you spend one free month?", "先生は1か月休みがあったら、どう過ごしますか？"),
    67: ("What's one skill you'd love to learn if time and money were no problem?", "時間とお金に制限がなければ、どんな技能を身につけたいですか？", "What skill would you most like to learn?", "先生はどんな技能を一番身につけたいですか？"),
    68: ("When someone doesn't reply, what do you usually assume first?", "誰かから返事がないとき、最初に何を考えますか？", "What do you usually assume first?", "先生は最初に何を考えますか？"),
    69: ("When someone says they'll do something, how long do you wait before reminding them?", "誰かが何かすると言ったとき、どのくらい待ってから念を押しますか？", "How long do you wait before reminding someone?", "先生はどのくらい待ってから相手に念を押しますか？"),
    70: ("Do you prefer clear instructions or freedom to decide how to do a task? Why?", "明確な指示と、自分でやり方を決める自由のどちらが好きですか？なぜですか？", "Which do you prefer: clear instructions or freedom?", "先生は明確な指示と自由のどちらが好きですか？"),
}


for _number in LESSONS:
    SPECS[_number]["writes"] = WRITE_PROMPTS[_number]
    SPECS[_number]["fill_hints"] = FILL_HINTS[_number]
    LESSONS[_number]["omit_choice"] = tuple(sorted(CHOICE_OMISSIONS[_number]))
    _question, _question_ja, _ask_back, _ask_back_ja = REVIEWED_LIVE[_number]
    LESSONS[_number]["prompt"] = (
        "Let's talk about this topic. Answer my question, then ask me too.",
        "この話題について話しましょう。私の質問に答えて、そのあと私にも聞いてください。",
    )
    LIVE_SCENES[_number] = (
        ("text", "other", "Tutor", _question, _question_ja),
        ("input", "me", "Me", "Student's answer", "自分の本当の答え"),
        ("text", "me", "Me", _ask_back, _ask_back_ja),
        ("input", "other", "Tutor", "Tutor's answer", "先生の本当の短い答え"),
    )
    LIVE_HINTS[_number] = {}

# Hint chips are part of the vocabulary contract.  Declare newly introduced
# lexical base forms without promoting them to taught grammar.
for _number, _pages in FILL_HINTS.items():
    _owned = {
        entry.split("|", 1)[0].casefold()
        for value in VOCAB[_number].values()
        for entry in filter(None, value.split("; "))
    }
    _additions = []
    for _page in _pages:
        for _row in _page:
            _pairs = (_row,) if len(_row) == 2 and all(isinstance(item, str) for item in _row) else _row
            for _japanese, _english in _pairs:
                if _english.casefold() not in _owned:
                    _additions.append(f"{_english}|{_japanese}")
                    _owned.add(_english.casefold())
    if _additions:
        VOCAB[_number]["assumed"] += "; " + "; ".join(_additions)

# Translation hints likewise use lexical dictionary forms, never target
# auxiliaries, articles, or inflections.
for _number in LESSONS:
    _owned = {
        entry.split("|", 1)[0].casefold()
        for value in VOCAB[_number].values()
        for entry in filter(None, value.split("; "))
    }
    _additions = []
    for _page in TRANSLATE_HINTS[_number]:
        for _row in _page:
            for _chip in _row.split("; "):
                _japanese, _english = _chip.rsplit(":", 1)
                if _english.casefold() not in _owned:
                    _additions.append(f"{_english}|{_japanese}")
                    _owned.add(_english.casefold())
    if _additions:
        VOCAB[_number]["assumed"] += "; " + "; ".join(_additions)


ROLE_JA = {
    "Coworker": "同僚", "Gallery staff": "ギャラリーの係員",
    "Hotel receptionist": "ホテルの受付係", "Receptionist": "受付係",
    "Friend": "友人", "Neighbor": "近所の人", "Police officer": "警察官",
    "Station staff": "駅員",
}


SUPPORT_EXPRESSIONS = {
    60: (("Could you check this, if it's not too much trouble?", "ご面倒でなければ、これを確認してもらえますか？"), ("Could you send it whenever you get a chance?", "お時間のあるときに送ってもらえますか？")),
    61: (("Not at all, please do.", "全く構いません。ぜひどうぞ。"), ("Sorry, someone's sitting there.", "すみません、そこには人が座っています。")),
    62: (("Sorry to bother you. Do you know where it is?", "お邪魔してすみません。どこにあるか分かりますか？"), ("Do you know, by any chance?", "もしかして、分かりますか？")),
    63: (("In general, I prefer coffee.", "一般的には、コーヒーのほうが好きです。"), ("As a rule, I avoid crowded places.", "概して、混んだ場所は避けます。")),
    64: (("It's playing up.", "調子が悪いです。"), ("That did the trick.", "それで直りました。")),
    65: (("Apparently, it was taken on the train.", "どうやら電車で取られたそうです。"), ("It turns out it was at home.", "結局、家にあったことが分かりました。")),
    66: (("In a perfect world, I'd travel all year.", "理想を言えば、一年中旅行します。"), ("Realistically, I'd take one month off.", "現実的には、1か月休みます。")),
    67: (("If only I had more free time.", "もっと自由な時間さえあればなあ。"), ("I wish I had more time. Oh well.", "もっと時間があればいいのですが。まあ仕方ないですね。")),
    68: (("I bet he's busy.", "きっと忙しいのでしょう。"), ("He might be out. Who knows?", "外出中かもしれません。分かりませんね。")),
    69: (("Apparently, she was busy.", "どうやら彼女は忙しかったそうです。"), ("That's what she said, word for word.", "それが彼女の言った言葉そのままです。")),
    70: (("Word has it the office will move.", "うわさでは、オフィスが移転するそうです。"), ("Strictly speaking, she asked me to wait.", "厳密に言えば、彼女は待つよう私に頼みました。")),
}


SPIRAL_MARKERS = {
    60: (("POLITE-01", "contrast"), ("MODAL-01", "transfer")),
    61: (("NEGQ-01", "controlled"), ("POLITE-01", "transfer")),
    62: (("ORDER-01", "transfer"), ("REL-01", "contrast")),
    63: (("ART-01", "contrast"), ("COUNT-01", "contrast")),
    64: (("ASPECT-02", "contrast"), ("MODAL-01", "transfer")),
    65: (("REL-01", "transfer"), ("PREP-01", "checkpoint")),
    66: (("ORDER-01", "transfer"),),
    67: (("NEGQ-01", "transfer"),),
    68: (("ADJ-01", "contrast"), ("MODAL-01", "contrast")),
    69: (("REL-01", "transfer"),),
    70: (("REPORT-01", "checkpoint"), ("DO-01", "transfer")),
}


DIALOGUE_SEMANTIC_LEDGER = {
    n: {
        "model": ("partner establishes need", "learner produces pattern one", "partner responds and asks relevant follow-up", "learner produces pattern two", "partner resolves outcome", "learner closes using current or prior language"),
        "wild": ("partner establishes new context", "learner produces pattern one", "partner responds and asks relevant follow-up", "learner produces pattern two", "partner resolves outcome", "learner closes using current or prior language"),
    } for n in LESSONS
}


THREE_CHIP_EXCEPTIONS = {
    (60, 1): "The article stays bound to window; three meaningful units remain.",
    (60, 2): "Would you mind is one taught frame and the noun phrase stays intact.",
    (61, 2): "Omitted because the fixed permission response has only two honest chunks.",
    (62, 1): "The embedded subject and verb stay together to protect the exact order contrast.",
    (62, 2): "The embedded subject and verb stay together to protect the exact order contrast.",
    (63, 2): "The adjective plus plural noun is one constituent.",
    (64, 1): "The phrasal verb turn on remains intact.",
    (64, 2): "Have you tried remains one taught frame.",
    (65, 1): "The passive verb was stolen remains intact.",
    (65, 2): "The preposition is stored with taken from.",
    (66, 2): "What would you do is one question constituent.",
    (67, 1): "I wish and I had remain meaningful constituents.",
    (67, 2): "I wish and I could remain meaningful constituents.",
    (68, 1): "The modal plus be remains intact.",
    (68, 2): "The modal phrase might just be remains intact.",
    (69, 1): "The reporting clause and backshift clause remain intact.",
    (69, 2): "The reporting verb stays with its required object.",
    (70, 1): "The reporting verb stays with its required object.",
    (70, 2): "Not to remains bound to the requested action.",
}


@contextlib.contextmanager
def course_data():
    names = ("LESSONS", "SPECS", "VOCAB", "KNOWN_WORDS", "TRANSLATE_HINTS", "OPEN_MENUS", "DIALOGUES", "LIVE_SCENES", "LIVE_HINTS", "SUPPORT_EXPRESSIONS")
    previous = {name: getattr(approved, name) for name in names}
    previous_role_ja = approved.ROLE_JA
    core_previous = (core.VOCAB, core.CANONICAL_SPECS, core.DIALOGUES, core.LIVE_SCENES)
    try:
        for name in names:
            setattr(approved, name, globals()[name])
        approved.ROLE_JA = ROLE_JA
        core.VOCAB = {n: (v["new"], v["assumed"], v["receptive"]) for n, v in VOCAB.items()}
        core.CANONICAL_SPECS, core.DIALOGUES, core.LIVE_SCENES = SPECS, DIALOGUES, LIVE_SCENES
        yield
    finally:
        for name, value in previous.items():
            setattr(approved, name, value)
        approved.ROLE_JA = previous_role_ja
        core.VOCAB, core.CANONICAL_SPECS, core.DIALOGUES, core.LIVE_SCENES = core_previous


def spiral_page(number, sid, level):
    primary = {
        60: (("Could you の後ろは動詞の原形", "Could you ", "open", "opening", " the window?"), ("Would you mind の後ろは -ing 形", "Would you mind ", "checking", "check", " the file?")),
        61: (("相手は気にしない。『座ると困りますか？』", "", "Not at all", "Yes", ", go ahead."), ("相手は困る。『窓を開けると困りますか？』", "", "Yes", "Not at all", ", please keep it closed.")),
        62: (("Do you know where the station is? の内側", "Inside the embedded question: ", "subject first", "verb first", "."), ("Could you tell me when the train leaves? の内側", "Inside the embedded question: ", "subject first", "verb first", ".")),
        63: (("コーヒー全般", "I prefer ", "coffee", "the coffee", "."), ("この店のコーヒー", "I like ", "the coffee here", "coffee here", ".")),
        64: (("今も続く作業", "I've been ", "working", "finished", " since nine."), ("今の完了結果", "I've ", "finished", "been working", " the report.")),
        65: (("かばんから取られた", "It was taken ", "from my bag", "at my bag", "."), ("机の上にあった", "It was ", "on the desk", "from the desk", ".")),
        66: (("想像上の状況", "If I ", "had", "have", " more time, I'd travel."), ("現実的な明日の予定", "If it rains, I ", "will", "would", " stay in.")),
        67: (("実際には運転できない。『運転できないの？』", "No, I ", "can't", "can", ". I wish I could."), ("実際には料理できる。『料理できないの？』", "Actually, I ", "can", "can't", ".")),
        68: (("強い推測", "He ", "must be", "must to be", " busy."), ("可能性", "He ", "might be", "might to be", " out.")),
        69: (("さっき電話した人", "She's the one ", "who called", "called who", " earlier."), ("メールを送った人", "He's the one ", "who sent", "sent who", " the email.")),
        70: (("発言を報告", "She ", "said she was", "told she was", " busy."), ("人への指示を報告", "She ", "told me to", "said me to", " wait.")),
    }[number]
    secondary = {
        (60, "MODAL-01"): (("could の後ろは動詞の原形", "Could you ", "open", "opening", " the window?"), ("could の後ろは動詞の原形", "Could you ", "check", "checking", " the file?")),
        (61, "POLITE-01"): (("丁寧なお願いを質問の形で", "", "Could you", "You could", " open it?"), ("相手への配慮を質問の形で", "", "Do you mind", "You mind", " if I sit?")),
        (62, "REL-01"): (("さっき電話した人", "She's the one ", "who called", "called who", " earlier."), ("ドアを開ける物", "It's the thing ", "that opens", "opens that", " the door.")),
        (63, "COUNT-01"): (("飲み物としてのコーヒー全般", "I prefer ", "coffee", "a coffee", "."), ("注文する2杯", "I'd like ", "two coffees", "two coffee", ".")),
        (64, "MODAL-01"): (("won't の後ろは動詞の原形", "My laptop won't ", "turn on", "turns on", "."), ("won't の後ろは動詞の原形", "The door won't ", "open", "opens", ".")),
        (65, "REL-01"): (("さっき電話した人", "She's the one ", "who called", "called who", " earlier."), ("チケットを持つ物", "It's the thing ", "that holds", "holds that", " the ticket.")),
        (68, "ADJ-01"): (("本人が疲れている", "He is ", "tired", "tiring", "."), ("仕事が人を疲れさせる", "The work is ", "tiring", "tired", ".")),
        (70, "DO-01"): (("現在形の質問", "Does she ", "wait", "waits", " here?"), ("現在形の質問", "Does he ", "call", "calls", " later?")),
    }
    examples = secondary.get((number, sid), primary)
    page = core.choose_words(
        f"spiral-{sid.casefold()}", "Retrieve an earlier contrast", "前の対比を思い出そう",
        "Choose the form that matches the stated meaning.", "書かれた意味に合う形を選びましょう。", examples,
    )
    return page.replace(f'data-page-id="spiral-{sid.casefold()}"', f'data-page-id="spiral-{sid.casefold()}" data-spiral-id="{sid}" data-spiral-level="{level}"', 1)


def set_vocab(head, number):
    for category, value in VOCAB[number].items():
        head = re.sub(rf'(<meta name="podo:vocabulary:{category}" content=")[^"]*(")', rf'\g<1>{value}\2', head, count=1)
    return head


def page_id(page):
    match = re.search(r'data-page-id="([^"]+)"', page)
    return match.group(1) if match else ""


def growing_sentence_inputs(page):
    """Use wrapping value controls for full-sentence translate answers."""
    return re.sub(
        r'<input class="space-input" type="text"([^>]*)>',
        r'<textarea class="space-input"\1 rows="2"></textarea>',
        page,
    )


def customize_pages(number, data, pages):
    pages = approved.customize_pages(number, data, pages)
    result = []
    for page in pages:
        page = growing_sentence_inputs(page)
        if number == 62 and page_id(page) == "p1-teach":
            # Keep the complete embedded question legible at the 360px class
            # width without shrinking the teaching example. Split the target
            # highlight too, so its edge treatment does not create 2px of
            # horizontal overflow on the narrower example rows.
            page = page.replace(
                '<span class="ending">Do you know where the ',
                '<span class="ending">Do you know where</span><br>'
                '<span class="ending">the ',
            )
        if page_id(page) == "part3-intro":
            result.extend(spiral_page(number, sid, level) for sid, level in SPIRAL_MARKERS[number])
        result.append(page)
    return result


def build(number, data):
    source = PILOT.read_text(encoding="utf-8")
    head, foot = new_lesson.split_shell(source)
    slug = f'{number:02d}-{data["slug"]}'
    head = new_lesson.retarget(head, review_id=f"CORE-{number}", lesson_id=slug, level="B1", title=data["title"], title_ko=data["ko"], title_ja=data["ja"], version="2026-08-20")
    head = head.replace("</head>", '  <link rel="stylesheet" href="growing-inputs.css">\n</head>', 1)
    with course_data():
        head = set_vocab(head.replace('content="todo"', 'content="reviewed"'), number)
        head = core.set_proofread_status(head, "complete")
        pages = customize_pages(number, data, core.canonical_pages(number, data))
    out = TRACK / "courses" / COURSE / "lessons" / slug / "lesson.html"
    return out, new_lesson.redepth(head + "\n".join(pages) + foot, out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    expected = set(range(60, 71))
    for label, values in (("lessons", LESSONS), ("semantic specs", SPECS), ("vocabulary", VOCAB), ("dialogues", DIALOGUES), ("live scenes", LIVE_SCENES)):
        if set(values) != expected:
            raise SystemExit(f"{label} do not exactly cover CORE-60--70")
    for number, data in LESSONS.items():
        out, text = build(number, data)
        if out.exists() and not args.refresh:
            raise SystemExit(f"refusing to overwrite {out.relative_to(ROOT)}")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        out.with_name("growing-inputs.css").write_text(NARROW_GROWING_INPUT_CSS, encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)}")
    print(f"{len(LESSONS)} Core decks generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

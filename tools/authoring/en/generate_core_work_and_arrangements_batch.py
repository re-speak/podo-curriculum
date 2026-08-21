#!/usr/bin/env python3
"""Generate the explicit CORE-71--80 Work and Arrangements course batch."""

from __future__ import annotations

import argparse
import contextlib
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import generate_core_course_batch as core
import new_lesson


ROOT = new_lesson.REPO
TRACK = new_lesson.ENGLISH / "tracks/1-core-patterns"
COURSE = "core-work-and-arrangements"
PILOT = TRACK / "courses/core-first-exchanges-2/lessons/20-asking-for-help/lesson.html"
PROOFREAD_STATUS = "complete"


def rows(*items):
    return items


LESSONS = {
    71: dict(
        slug="i-should-have-called-earlier", title="I should have called earlier",
        ko="더 일찍 전화했어야 했어요", ja="もっと早く電話すればよかった",
        goal=("Say what you regret doing or not doing.", "したこと・しなかったことへの後悔を伝えましょう。"),
        p1=rows(
            ("I {t}should have{/t} called earlier.", "もっと早く電話{t}すればよかったです{/t}。", "I|should have|called|earlier."),
            ("I {t}should have{/t} checked first.", "先に確認{t}すればよかったです{/t}。", "I|should have|checked|first."),
            ("I {t}should have{/t} left sooner.", "もっと早く出発{t}すればよかったです{/t}。", "I|should have|left|sooner."),
            ("I {t}should have{/t} told you yesterday.", "昨日あなたに伝え{t}ればよかったです{/t}。", "I|should have|told you|yesterday."),
        ),
        p2=rows(
            ("I {t}shouldn't have{/t} said anything.", "何も言わ{t}なければよかったです{/t}。", "I|shouldn't have|said|anything."),
            ("I {t}shouldn't have{/t} canceled the booking.", "予約をキャンセルし{t}なければよかったです{/t}。", "I|shouldn't have|canceled|the booking."),
            ("I {t}shouldn't have{/t} waited so long.", "あんなに長く待た{t}なければよかったです{/t}。", "I|shouldn't have|waited|so long."),
            ("I {t}shouldn't have{/t} sent that message.", "あのメッセージを送ら{t}なければよかったです{/t}。", "I|shouldn't have|sent|that message."),
        ),
        rules=(("Use should have plus a past participle for the better action you did not take.", "しなかったほうの望ましい行動は、should have と過去分詞で表します。"), ("Use shouldn't have plus a past participle for an action you now regret taking.", "してしまった行動への後悔は、shouldn't have と過去分詞で表します。")),
        prompt=("Tell me about one real regret, or say that none comes to mind, then ask me too.", "実際の後悔を一つ話すか、思いつかなければそう伝えてから、私にも聞いてください。"),
    ),
    72: dict(
        slug="i-might-have-left-it-at-home", title="I might have left it at home",
        ko="집에 두고 왔을지도 몰라요", ja="家に置いてきたのかもしれません",
        goal=("Offer a possible explanation, then a confident conclusion about the past.", "過去について可能性のある説明と、確信のある結論を伝えましょう。"),
        p1=rows(
            ("I {t}might have{/t} left it at home.", "家に置いてきた{t}のかもしれません{/t}。", "I|might have left|it|at home."),
            ("She {t}might have{/t} missed the train this morning.", "彼女は今朝、電車に乗り遅れた{t}のかもしれません{/t}。", "She|might have missed|the train|this morning."),
            ("They {t}might have{/t} gone somewhere else after work.", "彼らは仕事のあと、別の場所へ行った{t}のかもしれません{/t}。", "They|might have gone|somewhere else|after work."),
            ("I {t}might have{/t} put it in my bag.", "かばんに入れた{t}のかもしれません{/t}。", "I|might have put|it|in my bag."),
        ),
        p2=rows(
            ("The traffic {t}must have been{/t} bad.", "渋滞がひどかった{t}に違いありません{/t}。", "The traffic|must have|been|bad."),
            ("The door {t}must have been{/t} locked.", "ドアに鍵がかかっていた{t}に違いありません{/t}。", "The door|must have|been|locked."),
            ("He {t}must have been{/t} tired.", "彼は疲れていた{t}に違いありません{/t}。", "He|must have|been|tired."),
            ("They {t}must have been{/t} at home.", "彼らは家にいた{t}に違いありません{/t}。", "They|must have|been|at home."),
        ),
        rules=(("Use might have plus a past participle when the explanation is only possible.", "可能性のある説明には、might have と過去分詞を使います。"), ("Use must have plus a past participle for a confident conclusion, not a past obligation.", "確信のある結論には must have と過去分詞を使い、過去の義務とは区別します。")),
        prompt=("Explain one past mystery if you have one, or say that nothing comes to mind, then ask what I think happened.", "過去の気になる出来事を一つ説明するか、思いつかなければそう伝えてから、私の推測も聞いてください。"),
    ),
    73: dict(
        slug="the-train-had-already-left", title="The train had already left",
        ko="기차는 이미 떠난 뒤였어요", ja="電車はもう出たあとでした",
        goal=("Make the order of two past events clear.", "過去の二つの出来事の順番をはっきり伝えましょう。"),
        p1=rows(
            ("The train {t}had already left{/t} when we got there.", "私たちが着いたとき、電車は{t}もう出たあとでした{/t}。", "The train|had already left|when|we got there."),
            ("The film {t}had already started{/t} when we sat down.", "私たちが席に着いたとき、映画は{t}もう始まっていました{/t}。", "The film|had already started|when|we sat down."),
            ("The shop {t}had already closed{/t} when I called.", "私が電話したとき、店は{t}もう閉まっていました{/t}。", "The shop|had already closed|when|I called."),
            ("The bus {t}had already gone{/t} when she arrived.", "彼女が着いたとき、バスは{t}もう出たあとでした{/t}。", "The bus|had already gone|when|she arrived."),
        ),
        p2=rows(
            ("{t}By the time{/t} we arrived, it {t}had closed{/t}.", "私たちが着く{t}ころには{/t}、そこは{t}閉まっていました{/t}。", "By the time|we arrived,|it|had closed."),
            ("{t}By the time{/t} I called, they {t}had left{/t}.", "私が電話した{t}ころには{/t}、彼らは{t}出発していました{/t}。", "By the time|I called,|they|had left."),
            ("{t}By the time{/t} the meeting started, she {t}had arrived{/t}.", "会議が始まる{t}ころには{/t}、彼女は{t}到着していました{/t}。", "By the time|the meeting started,|she|had arrived."),
            ("{t}By the time{/t} we got home, the rain {t}had stopped{/t}.", "帰宅した{t}ころには{/t}、雨は{t}やんでいました{/t}。", "By the time|we got home,|the rain|had stopped."),
        ),
        rules=(("Use had plus a past participle for the earlier event; use the simple past after when for the later one.", "先に起きた出来事は had と過去分詞で、when のあとの遅い出来事は単純過去で表します。"), ("Put By the time before the later event and use had plus a past participle for what was already complete.", "遅い出来事の前に By the time を置き、すでに完了していたことは had と過去分詞で表します。")),
        prompt=("Describe a time you arrived too late, or say that it has not happened, then ask about me.", "到着が遅すぎた経験を話すか、なければそう伝えてから、私にも聞いてください。"),
    ),
    74: dict(
        slug="i-was-going-to-call-but", title="I was going to call, but",
        ko="전화하려고 했는데", ja="電話するつもりでしたが",
        goal=("Explain an intention that did not happen and give the reason.", "実現しなかったつもりと、その理由を説明しましょう。"),
        p1=rows(
            ("I {t}was going to{/t} call, but I {t}ran out of time{/t}.", "電話する{t}つもりでしたが{/t}、{t}時間がなくなりました{/t}。", "I|was going to call,|but|I ran out of time."),
            ("I {t}was going to{/t} cook, but something {t}came up{/t}.", "料理する{t}つもりでしたが{/t}、急な用事が{t}できました{/t}。", "I|was going to cook,|but|something came up."),
            ("I {t}was going to{/t} book it, but it {t}slipped my mind{/t}.", "予約する{t}つもりでしたが{/t}、{t}うっかり忘れました{/t}。", "I|was going to book it,|but|it slipped my mind."),
            ("I {t}was going to{/t} go out, but I {t}felt sick{/t}.", "外出する{t}つもりでしたが{/t}、{t}気分が悪くなりました{/t}。", "I|was going to go out,|but|I felt sick."),
        ),
        p2=rows(
            ("{t}I'd planned to{/t} finish it today, but I {t}ran out of time{/t}.", "今日終える{t}予定でしたが{/t}、{t}時間がなくなりました{/t}。", "I'd planned|to finish it today,|but|I ran out of time."),
            ("{t}I'd planned to{/t} call at noon, but something {t}came up{/t}.", "正午に電話する{t}予定でしたが{/t}、急な用事が{t}できました{/t}。", "I'd planned|to call at noon,|but|something came up."),
            ("{t}I'd planned to{/t} send it yesterday, but it {t}slipped my mind{/t}.", "昨日送る{t}予定でしたが{/t}、{t}うっかり忘れました{/t}。", "I'd planned|to send it yesterday,|but|it slipped my mind."),
            ("{t}I'd planned to{/t} meet her, but I {t}felt sick{/t}.", "彼女に会う{t}予定でしたが{/t}、{t}気分が悪くなりました{/t}。", "I'd planned|to meet her,|but|I felt sick."),
        ),
        rules=(("Use was going to plus a plain verb for an intention, then use but to give the reason it did not happen.", "実現しなかったつもりは was going to と動詞の原形で表し、but のあとに理由を続けます。"), ("Use had planned to plus a plain verb for an earlier plan, then explain the change after but.", "以前に立てた予定は had planned to と動詞の原形で表し、but のあとに変わった理由を続けます。")),
        prompt=("Describe one plan that changed, or say that none changed recently, then ask me about mine.", "変わった予定を一つ話すか、最近なければそう伝えてから、私の予定も聞いてください。"),
    ),
    75: dict(
        slug="i-used-to-walk-to-school", title="I used to walk to school",
        ko="예전에는 걸어서 학교에 다녔어요", ja="以前は歩いて学校に通っていました",
        goal=("Contrast a past habit with what is true now.", "昔の習慣と今の状態を対比しましょう。"),
        p1=rows(
            ("I {t}used to{/t} walk to school.", "以前は歩いて学校に{t}通っていました{/t}。", "I|used to|walk|to school."),
            ("I {t}used to{/t} drink coffee every morning.", "以前は毎朝コーヒーを{t}飲んでいました{/t}。", "I|used to|drink coffee|every morning."),
            ("I {t}used to{/t} work downtown.", "以前は中心街で{t}働いていました{/t}。", "I|used to|work|downtown."),
            ("I {t}used to{/t} play tennis on Sundays.", "以前は日曜日にテニスを{t}していました{/t}。", "I|used to|play tennis|on Sundays."),
        ),
        p2=rows(
            ("I {t}don't walk to school{/t} anymore.", "今はもう{t}歩いて学校に通いません{/t}。", "I|don't|walk to school|anymore."),
            ("I {t}don't drink coffee{/t} anymore.", "今はもう{t}コーヒーを飲みません{/t}。", "I|don't|drink coffee|anymore."),
            ("I {t}don't work downtown{/t} anymore.", "今はもう{t}中心街では働きません{/t}。", "I|don't|work downtown|anymore."),
            ("I {t}don't play tennis{/t} anymore.", "今はもう{t}テニスをしません{/t}。", "I|don't|play tennis|anymore."),
        ),
        rules=(("Use used to plus a plain verb for a past habit or state that is no longer true.", "今は当てはまらない昔の習慣・状態には、used to と動詞の原形を使います。"), ("Use don't plus a plain verb and put anymore at the end to state the present contrast.", "今との対比は don't と動詞の原形を使い、文末に anymore を置きます。")),
        prompt=("Tell me about one real past habit, or say that nothing has changed, then ask me too.", "実際の昔の習慣を一つ話すか、変わったことがなければそう伝えてから、私にも聞いてください。"),
        omit_choice=(1,),
    ),
    76: dict(
        slug="i-had-my-phone-repaired", title="I had my phone repaired",
        ko="휴대폰을 수리 맡겼어요", ja="携帯を修理してもらいました",
        goal=("Say what service you arranged and what still needs attention.", "頼んだサービスと、まだ必要な作業を伝えましょう。"),
        p1=rows(
            ("I {t}had{/t} my phone {t}repaired{/t}.", "携帯を{t}修理して{/t}{t}もらいました{/t}。", "I|had|my phone|repaired."),
            ("I {t}had{/t} my coat {t}cleaned{/t}.", "コートを{t}クリーニングして{/t}{t}もらいました{/t}。", "I|had|my coat|cleaned."),
            ("I {t}had{/t} the battery {t}replaced{/t}.", "バッテリーを{t}交換して{/t}{t}もらいました{/t}。", "I|had|the battery|replaced."),
            ("I {t}had{/t} my watch {t}fixed{/t}.", "腕時計を{t}直して{/t}{t}もらいました{/t}。", "I|had|my watch|fixed."),
        ),
        p2=rows(
            ("I {t}need to get{/t} the screen {t}replaced{/t}.", "画面を{t}交換して{/t}{t}もらう必要があります{/t}。", "I|need to get|the screen|replaced."),
            ("I {t}need to get{/t} the zipper {t}fixed{/t}.", "ファスナーを{t}直して{/t}{t}もらう必要があります{/t}。", "I|need to get|the zipper|fixed."),
            ("I {t}need to get{/t} this coat {t}cleaned{/t}.", "このコートを{t}クリーニングして{/t}{t}もらう必要があります{/t}。", "I|need to get|this coat|cleaned."),
            ("I {t}need to get{/t} the battery {t}checked{/t}.", "バッテリーを{t}点検して{/t}{t}もらう必要があります{/t}。", "I|need to get|the battery|checked."),
        ),
        rules=(("Use had plus the thing plus a past participle for a service you arranged and completed.", "手配して完了したサービスは、had、物、過去分詞の順で表します。"), ("Use need to get plus the thing plus a past participle for a service that still needs arranging.", "これから手配する必要があるサービスは、need to get、物、過去分詞の順で表します。")),
        prompt=("Name a service you arranged or need, or say that you do not need one now, then ask me too.", "頼んだ・必要なサービスを話すか、今はなければそう伝えてから、私にも聞いてください。"),
    ),
    77: dict(
        slug="it-was-supposed-to-be-ready", title="It was supposed to be ready",
        ko="준비되어 있어야 했어요", ja="出来上がっているはずでした",
        goal=("State an unmet service expectation and ask neutrally for an update.", "満たされていないサービスの予定を伝え、中立的に状況を確認しましょう。"),
        p1=rows(
            ("It {t}was supposed to be{/t} ready today.", "今日{t}出来上がっているはずでした{/t}。", "It|was supposed to be|ready|today."),
            ("It {t}was supposed to be{/t} ready by Friday.", "金曜日までに{t}出来上がっているはずでした{/t}。", "It|was supposed to be|ready|by Friday."),
            ("The order {t}was supposed to arrive{/t} by noon today.", "注文品は今日の正午までに{t}届くはずでした{/t}。", "The order|was supposed to arrive|by noon|today."),
            ("The repair {t}was supposed to be finished{/t} by six today.", "修理は今日の6時までに{t}終わっているはずでした{/t}。", "The repair|was supposed to be finished|by six|today."),
        ),
        p2=rows(
            ("Could you {t}check what's happened to{/t} it?", "{t}どうなったか確認していただけますか{/t}？", "Could you|check|what's happened to|it?"),
            ("Could you {t}check what's happened to{/t} my order?", "{t}注文品がどうなったか確認していただけますか{/t}？", "Could you|check|what's happened to|my order?"),
            ("Could you {t}check what's happened to{/t} the repair?", "{t}修理がどうなったか確認していただけますか{/t}？", "Could you|check|what's happened to|the repair?"),
            ("Could you {t}check what's happened to{/t} the delivery?", "{t}配達がどうなったか確認していただけますか{/t}？", "Could you|check|what's happened to|the delivery?"),
        ),
        rules=(("Use was supposed to plus a plain verb for an agreed expectation that was not met.", "満たされなかった合意上の予定は、was supposed to と動詞の原形で表します。"), ("Use what's happened to for the present result, after calmly stating the expectation.", "予定を落ち着いて伝えたあと、現在の結果は what's happened to で確認します。")),
        prompt=("Describe a real delayed service, or say that you have none, then ask whether I have had one.", "実際に遅れたサービスを話すか、なければそう伝えてから、私にも経験があるか聞いてください。"),
        omit_choice=(2,),
    ),
    78: dict(
        slug="this-time-tomorrow-ill-be-flying", title="This time tomorrow I'll be flying",
        ko="내일 이 시간에는 비행 중일 거예요", ja="明日の今ごろは飛行機で移動中です",
        goal=("Place an activity in progress at two future times.", "二つの未来の時点で進行中の活動を伝えましょう。"),
        p1=rows(
            ("This time tomorrow, {t}I'll be flying{/t} home.", "明日の今ごろは、家へ向かって{t}飛行中です{/t}。", "This time tomorrow,|I'll be|flying|home."),
            ("This time next week, {t}I'll be staying{/t} in Osaka.", "来週の今ごろは、大阪に{t}滞在中です{/t}。", "This time next week,|I'll be|staying|in Osaka."),
            ("Tomorrow morning, {t}I'll be meeting{/t} a client.", "明日の朝は、顧客と{t}会っているところです{/t}。", "Tomorrow morning,|I'll be|meeting|a client."),
            ("At noon tomorrow, {t}I'll be having{/t} lunch.", "明日の正午は、昼食を{t}とっているところです{/t}。", "At noon tomorrow,|I'll be|having|lunch."),
        ),
        p2=rows(
            ("At six, {t}I'll still be traveling{/t}.", "6時には、まだ{t}移動中です{/t}。", "At six,|I'll still be|traveling."),
            ("At eight, {t}I'll still be working{/t}.", "8時には、まだ{t}仕事中です{/t}。", "At eight,|I'll still be|working."),
            ("At noon, {t}I'll still be waiting{/t}.", "正午には、まだ{t}待っているところです{/t}。", "At noon,|I'll still be|waiting."),
            ("At ten, {t}I'll still be driving{/t}.", "10時には、まだ{t}運転中です{/t}。", "At ten,|I'll still be|driving."),
        ),
        rules=(("Keep the future time anchor with will be plus the -ing form to show an activity in progress then.", "未来の時点を添え、will be と -ing 形でその時に進行中の活動を表します。"), ("Put still between will and be when the activity continues through the later future point.", "さらに遅い未来の時点まで続く活動は、will と be の間に still を置きます。")),
        prompt=("Say what you will really be doing tomorrow, or say that you have no plan, then ask me too.", "明日実際にしていることを話すか、予定がなければそう伝えてから、私にも聞いてください。"),
    ),
    79: dict(
        slug="i-should-have-it-ready-by-friday", title="I should have it ready by Friday",
        ko="금요일까지 준비할 수 있을 것 같아요", ja="金曜日までには用意できる見込みです",
        goal=("Give a realistic completion estimate and name what may change it.", "現実的な完了見込みと、それを変える可能性を伝えましょう。"),
        p1=rows(
            ("I {t}should have{/t} it ready by Friday.", "金曜日までには{t}用意できる見込みです{/t}。", "I|should have|it ready|by Friday."),
            ("I {t}should have{/t} the report ready by noon.", "正午までにはレポートを{t}用意できる見込みです{/t}。", "I|should have|the report ready|by noon."),
            ("We {t}should have{/t} the room ready by six.", "6時までには部屋を{t}用意できる見込みです{/t}。", "We|should have|the room ready|by six."),
            ("They {t}should have{/t} the order ready by Tuesday.", "火曜日までには注文品を{t}用意できる見込みです{/t}。", "They|should have|the order ready|by Tuesday."),
        ),
        p2=rows(
            ("It {t}may take{/t} another two days.", "さらに2日{t}かかるかもしれません{/t}。", "It|may take|another|two days."),
            ("It {t}may take{/t} another hour.", "さらに1時間{t}かかるかもしれません{/t}。", "It|may take|another|hour."),
            ("It {t}may take{/t} another week.", "さらに1週間{t}かかるかもしれません{/t}。", "It|may take|another|week."),
            ("It {t}may take{/t} another day.", "さらに1日{t}かかるかもしれません{/t}。", "It|may take|another|day."),
        ),
        rules=(("Use should have plus the thing plus ready for an expected state by a deadline, not advice or regret.", "期限までに見込まれる状態は、助言や後悔ではなく、should have、物、ready の順で表します。"), ("Use may plus the plain verb take to keep the extra time estimate honestly uncertain.", "追加時間が不確かなことを正直に伝えるには、may と動詞の原形 take を使います。")),
        prompt=("Give a real estimate, or say that you have no deadline now, then ask about one of my tasks.", "実際の見込みを伝えるか、今は期限がなければそう伝えてから、私の作業について聞いてください。"),
        omit_choice=(1,),
    ),
    80: dict(
        slug="let-me-know-once-its-ready", title="Let me know once it's ready",
        ko="준비되면 알려 주세요", ja="準備できたら知らせてください",
        goal=("Set an action to happen immediately after another task finishes.", "別の作業が終わったらすぐ行うことを決めましょう。"),
        p1=rows(
            ("{t}Let me know once{/t} it's ready.", "{t}準備ができたら知らせてください{/t}。", "Let me know|once|it's|ready."),
            ("{t}Let me know once{/t} the report is finished.", "{t}レポートが終わったら知らせてください{/t}。", "Let me know|once|the report|is finished."),
            ("{t}Let me know once{/t} the order arrives.", "{t}注文品が届いたら知らせてください{/t}。", "Let me know|once|the order|arrives."),
            ("{t}Let me know once{/t} you hear back.", "{t}返事が来たら知らせてください{/t}。", "Let me know|once|you|hear back."),
        ),
        p2=rows(
            ("{t}I'll start as soon as{/t} I hear back.", "{t}返事が来たらすぐ始めます{/t}。", "I'll|start|as soon as|I hear back."),
            ("{t}I'll call as soon as{/t} it arrives.", "{t}届いたらすぐ電話します{/t}。", "I'll|call|as soon as|it arrives."),
            ("{t}I'll send it as soon as{/t} it's ready.", "{t}準備できたらすぐ送ります{/t}。", "I'll|send it|as soon as|it's ready."),
            ("{t}I'll book it as soon as{/t} they reply.", "{t}返事が来たらすぐ予約します{/t}。", "I'll|book it|as soon as|they reply."),
        ),
        rules=(("Use a present form after once even when the trigger is in the future.", "未来のきっかけでも、once のあとは現在形を使います。"), ("Put will in the action clause and use a present form after as soon as for the trigger.", "will は行動の節に置き、as soon as のあとのきっかけには現在形を使います。")),
        prompt=("Name a real task that depends on a reply or finish, or say that none does, then ask me too.", "返事・完了を待つ実際の作業を話すか、なければそう伝えてから、私にも聞いてください。"),
    ),
}


def semantic_spec(meanings, writes, choices, rules, tip):
    return dict(meanings=meanings, writes=writes, choices=choices, rules=rules, tip=tip)


def choice_rows(jps, prefix, correct, distractor, suffixes):
    return tuple((jp, prefix, correct, distractor, suffix) for jp, suffix in zip(jps, suffixes, strict=True))


SPECS = {
    71: semantic_spec(
        (("Use this to look back at a better action you did not take.", "しなかったほうの望ましい行動を振り返るときに使います。"), ("Use this to name an action you took but now regret.", "してしまった行動を今は後悔していると伝えるときに使います。")),
        (("Name one thing you should have done, or say none comes to mind.", "すればよかったことを一つ話すか、思いつかないと伝えましょう。"), ("Name one thing you should not have done, or say none comes to mind.", "しなければよかったことを一つ話すか、思いつかないと伝えましょう。")),
        (
            choice_rows(("もっと早く電話{t}すればよかった{/t}。", "先に確認{t}すればよかった{/t}。", "もっと早く出発{t}すればよかった{/t}。", "昨日伝え{t}ればよかった{/t}。"), "I ", "should have", "should", (" called earlier.", " checked first.", " left sooner.", " told you yesterday.")),
            choice_rows(("何も言わ{t}なければよかった{/t}。", "予約を取り消さ{t}なければよかった{/t}。", "長く待た{t}なければよかった{/t}。", "あのメッセージを送ら{t}なければよかった{/t}。"), "I ", "shouldn't have", "should have", (" said anything.", " canceled the booking.", " waited so long.", " sent that message.")),
        ),
        (("Build the better past choice", "よりよかった過去の選択", "人 + <b>should have</b> + 過去分詞", "Action not taken", "しなかった行動", ("I <b>should have called</b> earlier.", "I <b>should have checked</b> first.")), ("Build the regretted past action", "後悔する過去の行動", "人 + <b>shouldn't have</b> + 過去分詞", "Action taken", "してしまった行動", ("I <b>shouldn't have said</b> anything.", "I <b>shouldn't have waited</b> so long."))),
        ("Should have or should've?", "should have と should've", "Use the full form for emphasis. In ordinary speech, should've is usually reduced to /ʃʊdəv/.", "強調するなら完全形を使います。普通の会話では should've は通常 /ʃʊdəv/ と短くなります。", ("Emphasis", "強調", "I should have called.", "本当に電話すればよかったです。"), ("Ordinary speech", "普通の会話", "I should've called.", "電話すればよかったです。")),
    ),
    72: semantic_spec(
        (("Use this for one possible explanation of a past event.", "過去の出来事について可能性のある説明を一つ出すときに使います。"), ("Use this for a confident conclusion based on what you know now.", "今分かっていることから確信のある結論を出すときに使います。")),
        (("Offer one possible past explanation.", "過去について可能性のある説明を一つ伝えましょう。"), ("Give one confident past conclusion.", "過去について確信のある結論を一つ伝えましょう。")),
        (
            tuple((jp, pre, "might", "must", suf) for jp, pre, suf in (("可能性はありますが、確信はありません。家に置いてきた{t}のかもしれません{/t}。", "I ", " have left it at home."), ("可能性はありますが、確信はありません。彼女は電車に乗り遅れた{t}のかもしれません{/t}。", "She ", " have missed the train."), ("可能性はありますが、確信はありません。別の場所へ行った{t}のかもしれません{/t}。", "They ", " have gone somewhere else."), ("可能性はありますが、確信はありません。かばんに入れた{t}のかもしれません{/t}。", "I ", " have put it in my bag."))),
            tuple((jp, pre, "must", "might", suf) for jp, pre, suf in (("証拠から強くそう思います。交通がひどかった{t}に違いありません{/t}。", "The traffic ", " have been bad."), ("証拠から強くそう思います。鍵がかかっていた{t}に違いありません{/t}。", "The door ", " have been locked."), ("証拠から強くそう思います。彼は疲れていた{t}に違いありません{/t}。", "He ", " have been tired."), ("証拠から強くそう思います。彼らは家にいた{t}に違いありません{/t}。", "They ", " have been at home."))),
        ),
        (("Possible past explanation", "可能性のある過去の説明", "人 + <b>might have</b> + 過去分詞", "One possibility", "一つの可能性", ("I <b>might have left</b> it at home.", "She <b>might have missed</b> the train.")), ("Confident past conclusion", "確信のある過去の結論", "人・物 + <b>must have</b> + 過去分詞", "Strong evidence", "強い根拠", ("The traffic <b>must have been</b> bad.", "The door <b>must have been</b> locked."))),
        ("Maybe or might have?", "maybe と might have", "Maybe can introduce the whole explanation. Might have builds the possibility into the verb.", "Maybe は説明全体の前に置けます。might have は可能性を動詞の中に組み込みます。", ("Sentence opener", "文全体への前置き", "Maybe I left it at home.", "もしかすると家に置いてきました。"), ("Inside the verb", "動詞の中", "I might have left it at home.", "家に置いてきたのかもしれません。")),
    ),
    73: semantic_spec(
        (("Use this when the first event was already complete before a later past event.", "あとの過去の出来事より前に、最初の出来事がすでに完了していたと伝えるときに使います。"), ("Use this to set the later past event first, then say what was already complete.", "あとの過去の出来事を先に示し、その時点ですでに完了していたことを伝えるときに使います。")),
        (("Describe two real past events whose order matters.", "順番が大切な過去の出来事を二つ話しましょう。"), ("Use By the time to make one real sequence clear.", "By the time を使い、実際の出来事の順番をはっきりさせましょう。")),
        (
            tuple((jp, pre, cor, dis, suf) for jp, pre, cor, dis, suf in (("到着より先に電車が{t}出ていた{/t}。", "The train ", "had left", "left", " when we got there."), ("着席より先に映画が{t}始まっていた{/t}。", "The film ", "had started", "started", " when we sat down."), ("電話より先に店が{t}閉まっていた{/t}。", "The shop ", "had closed", "closed", " when I called."), ("到着より先にバスが{t}出ていた{/t}。", "The bus ", "had gone", "went", " when she arrived."))),
            tuple((jp, pre, cor, dis, suf) for jp, pre, cor, dis, suf in (("着いたころには、そこは{t}閉まっていた{/t}。", "By the time we arrived, it ", "had closed", "closed", "."), ("電話したころには、彼らは{t}出発していた{/t}。", "By the time I called, they ", "had left", "left", "."), ("会議開始までに、彼女は{t}到着していた{/t}。", "By the time the meeting started, she ", "had arrived", "arrived", "."), ("帰宅したころには、雨は{t}やんでいた{/t}。", "By the time we got home, the rain ", "had stopped", "stopped", "."))),
        ),
        (("Mark the earlier event", "先の出来事を示す", "先の出来事: <b>had</b> + 過去分詞 + when + あとの出来事", "Earlier then later", "先、あと", ("The train <b>had left</b> when we arrived.", "The film <b>had started</b> when we sat down.")), ("Lead with the later deadline", "あとの時点を先に置く", "<b>By the time</b> + あとの出来事, + 先の出来事: had + 過去分詞", "View from the later point", "あとの時点から見る", ("<b>By the time</b> we arrived, it had closed.", "<b>By the time</b> I called, they had left."))),
        ("Had left or left before?", "had left と left before", "Use had left when both past events are in one timeline. Left before is a shorter alternative when the reference event is already clear.", "二つの過去の出来事を一つの時間軸で示すなら had left を使います。基準の出来事が明らかなら left before と短く言えます。", ("Full timeline", "時間軸を明示", "The train had left when we arrived.", "到着したとき、電車は出たあとでした。"), ("Reference already clear", "基準が明らか", "The train left before that.", "電車はその前に出ました。")),
    ),
    74: semantic_spec(
        (("Use this for an intention that did not happen, followed by the reason.", "実現しなかったつもりを、その理由と一緒に伝えるときに使います。"), ("Use this for a plan made earlier that did not happen, followed by the reason.", "前に立てた予定が実現しなかったことを、その理由と一緒に伝えるときに使います。")),
        (("Explain one intention that changed, or say none changed.", "変わったつもりを一つ説明するか、なかったと伝えましょう。"), ("Explain one earlier plan that changed, or say none changed.", "変わった以前の予定を一つ説明するか、なかったと伝えましょう。")),
        (
            tuple((jp, "I ", "was going to", "am going to", suf) for jp, suf in (("電話する{t}つもりでした{/t}。", " call, but I ran out of time."), ("料理する{t}つもりでした{/t}。", " cook, but something came up."), ("予約する{t}つもりでした{/t}。", " book it, but it slipped my mind."), ("外出する{t}つもりでした{/t}。", " go out, but I felt sick."))),
            tuple((jp, "I ", "had planned to", "plan to", suf) for jp, suf in (("今日終える{t}予定でした{/t}。", " finish it today, but I ran out of time."), ("正午に電話する{t}予定でした{/t}。", " call at noon, but something came up."), ("昨日送る{t}予定でした{/t}。", " send it yesterday, but it slipped my mind."), ("彼女に会う{t}予定でした{/t}。", " meet her, but I felt sick."))),
        ),
        (("Earlier intention", "以前のつもり", "人 + <b>was going to</b> + 動詞の原形, + but + 理由", "Did not happen", "実現しなかった", ("I <b>was going to call</b>, but I ran out of time.", "I <b>was going to cook</b>, but something came up.")), ("Earlier plan", "以前の予定", "人 + <b>had planned to</b> + 動詞の原形, + but + 理由", "Plan changed", "予定が変わった", ("I'd <b>planned to finish it</b>, but I ran out of time.", "I'd <b>planned to call</b>, but something came up."))),
        ("I was going to or I meant to?", "I was going to と I meant to", "I was going to states the plan. I meant to is a shorter, conversational way to admit an intention you did not carry out.", "I was going to は予定を伝えます。I meant to は実行できなかった意図を認める短く会話的な言い方です。", ("State the plan", "予定を伝える", "I was going to call.", "電話するつもりでした。"), ("Admit the missed intention", "できなかった意図を認める", "I meant to call.", "電話するつもりだったんです。")),
    ),
    75: semantic_spec(
        (("Use this for a repeated past habit or state that is no longer true.", "今は当てはまらない、昔の繰り返した習慣・状態に使います。"), ("Use this to state the present contrast directly.", "今は違うことをはっきり伝えるときに使います。")),
        (("Describe one real past habit, or say nothing has changed.", "実際の昔の習慣を一つ話すか、変化がないと伝えましょう。"), ("State what you do not do anymore, or say nothing has changed.", "今はもうしないことを話すか、変化がないと伝えましょう。")),
        ((), tuple((jp, "I ", "don't", "didn't", suffix) for jp, suffix in (("今はもう{t}歩いて学校に通いません{/t}。", " walk to school anymore."), ("今はもう{t}コーヒーを飲みません{/t}。", " drink coffee anymore."), ("今はもう{t}中心街では働きません{/t}。", " work downtown anymore."), ("今はもう{t}テニスをしません{/t}。", " play tennis anymore.")))),
        (("Past habit no longer true", "今は違う昔の習慣", "人 + <b>used to</b> + 動詞の原形", "Past contrast built in", "今との違いを含む", ("I <b>used to walk</b> to school.", "I <b>used to work</b> downtown.")), ("State the present contrast", "今の違いを伝える", "人 + <b>don't</b> + 動詞の原形 + <b>anymore</b>", "Not true now", "今はしない", ("I <b>don't</b> drink coffee <b>anymore</b>.", "I <b>don't</b> work downtown <b>anymore</b>."))),
        ("Not anymore or no longer?", "not anymore と no longer", "Not anymore is common in conversation. No longer is more formal and comes before the main verb.", "not anymore は会話で一般的です。no longer はより改まった言い方で、主な動詞の前に置きます。", ("Conversation", "会話", "I don't work there anymore.", "今はもうそこで働いていません。"), ("More formal", "より改まった言い方", "I no longer work there.", "現在はそこで働いていません。")),
    ),
    76: semantic_spec(
        (("Use this to report a service you arranged for an object.", "物について手配したサービスを報告するときに使います。"), ("Use this to name a service that still needs arranging.", "物について、これから手配する必要があるサービスを伝えるときに使います。")),
        (("Name one service you arranged, or say you have not arranged one.", "頼んだサービスを一つ話すか、頼んでいないと伝えましょう。"), ("Name one service you need, or say you do not need one now.", "必要なサービスを一つ話すか、今は必要ないと伝えましょう。")),
        (
            tuple((jp, pre, cor, dis, ".") for jp, pre, cor, dis in (("携帯を{t}修理してもらいました{/t}。", "I had my phone ", "repaired", "repair"), ("コートを{t}クリーニングしてもらいました{/t}。", "I had my coat ", "cleaned", "clean"), ("バッテリーを{t}交換してもらいました{/t}。", "I had the battery ", "replaced", "replace"), ("腕時計を{t}直してもらいました{/t}。", "I had my watch ", "fixed", "fix"))),
            tuple((jp, pre, cor, dis, ".") for jp, pre, cor, dis in (("画面を{t}交換してもらう必要があります{/t}。", "I need to get the screen ", "replaced", "replace"), ("ファスナーを{t}直してもらう必要があります{/t}。", "I need to get the zipper ", "fixed", "fix"), ("コートを{t}クリーニングしてもらう必要があります{/t}。", "I need to get this coat ", "cleaned", "clean"), ("バッテリーを{t}点検してもらう必要があります{/t}。", "I need to get the battery ", "checked", "check"))),
        ),
        (("Completed arranged service", "手配して完了したサービス", "人 + <b>had</b> + 物 + <b>過去分詞</b>", "Someone else did it", "別の人が作業した", ("I <b>had my phone repaired</b>.", "I <b>had my coat cleaned</b>.")), ("Service still needed", "まだ必要なサービス", "人 + need to <b>get</b> + 物 + <b>過去分詞</b>", "Needs arranging", "これから手配", ("I need to <b>get the screen replaced</b>.", "I need to <b>get the zipper fixed</b>."))),
        ("Repaired or fixed?", "repaired と fixed", "Repaired is neutral and specific to restoring something. Fixed is the common conversational choice.", "repaired は修理して元に戻す中立的な語です。fixed は会話でよく使う言い方です。", ("Neutral service wording", "中立的なサービス表現", "I had my phone repaired.", "携帯を修理してもらいました。"), ("Conversation", "会話", "I got my phone fixed.", "携帯を直してもらいました。")),
    ),
    77: semantic_spec(
        (("Use this to state an agreed expectation that was not met.", "満たされなかった合意上の予定を伝えるときに使います。"), ("Use this after the expectation to ask neutrally about the current result.", "予定を伝えたあと、現在どうなっているか中立的に確認するときに使います。")),
        (("State one real unmet service expectation, or say you have none.", "実際に満たされなかったサービスの予定を話すか、ないと伝えましょう。"), ("Ask neutrally what has happened to one service item.", "サービス中の物がどうなったか、中立的に確認しましょう。")),
        (
            tuple((jp, pre, "was", "is", suf) for jp, pre, suf in (("今日{t}出来上がっているはずでした{/t}。", "It ", " supposed to be ready today."), ("金曜日までに{t}出来上がっているはずでした{/t}。", "It ", " supposed to be ready by Friday."), ("正午までに{t}届くはずでした{/t}。", "The order ", " supposed to arrive by noon."), ("6時までに{t}終わっているはずでした{/t}。", "The repair ", " supposed to be finished by six."))),
            (),
        ),
        (("State the unmet expectation", "満たされなかった予定", "物 + <b>was supposed to</b> + 動詞の原形", "Agreed but not met", "合意されたが未達", ("It <b>was supposed to be</b> ready today.", "The order <b>was supposed to arrive</b> by noon.")), ("Ask for the present result", "現在の結果を確認", "Could you check + <b>what's happened to</b> + 物?", "Neutral follow-up", "中立的な確認", ("Could you check <b>what's happened to it</b>?", "Could you check <b>what's happened to my order</b>?"))),
        ("Could you check or take a look?", "Could you check と take a look", "Could you check asks for a factual update. Could you take a look asks someone to inspect the item itself.", "Could you check は事実の確認を頼みます。Could you take a look は物そのものを見てもらう頼み方です。", ("Status update", "状況確認", "Could you check what's happened to it?", "どうなったか確認していただけますか？"), ("Inspect the item", "物を見てもらう", "Could you take a look at it?", "これを見ていただけますか？")),
    ),
    78: semantic_spec(
        (("Use this to place yourself inside an activity at a stated future time.", "はっきりした未来の時点で、活動の途中にいることを伝えるときに使います。"), ("Use this when the activity will continue through a later future time.", "さらに遅い未来の時点まで活動が続くと伝えるときに使います。")),
        (("Say what you will really be doing at one future time, or say you have no plan.", "未来の一時点で実際にしていることを話すか、予定がないと伝えましょう。"), ("Say what will still be in progress later, or say nothing will be.", "あとでも続いていることを話すか、何も続いていないと伝えましょう。")),
        (
            tuple((jp, pre, "be", "am", suf) for jp, pre, suf in (("明日の今ごろは{t}飛行中です{/t}。", "This time tomorrow, I'll ", " flying home."), ("来週の今ごろは{t}滞在中です{/t}。", "This time next week, I'll ", " staying in Osaka."), ("明日の朝は{t}顧客と会っているところです{/t}。", "Tomorrow morning, I'll ", " meeting a client."), ("明日の正午は{t}昼食中です{/t}。", "At noon tomorrow, I'll ", " having lunch."))),
            tuple((jp, pre, "still be", "be still", suf) for jp, pre, suf in (("6時にはまだ{t}移動中です{/t}。", "At six, I'll ", " traveling."), ("8時にはまだ{t}仕事中です{/t}。", "At eight, I'll ", " working."), ("正午にはまだ{t}待っているところです{/t}。", "At noon, I'll ", " waiting."), ("10時にはまだ{t}運転中です{/t}。", "At ten, I'll ", " driving."))),
        ),
        (("Future activity in progress", "未来に進行中の活動", "未来の時点 + 人 + <b>will be</b> + 動詞<b>-ing</b>", "Inside the later moment", "未来の時点の途中", ("This time tomorrow, <b>I'll be flying</b> home.", "Tomorrow morning, <b>I'll be meeting</b> a client.")), ("Continuing through a later point", "さらに遅い時点まで継続", "未来の時点 + 人 + will + <b>still be</b> + 動詞-ing", "Still in progress", "まだ進行中", ("At six, <b>I'll still be traveling</b>.", "At eight, <b>I'll still be working</b>."))),
        ("I'll be meeting or I'm meeting?", "I'll be meeting と I'm meeting", "I'll be meeting places you inside the future activity. I'm meeting focuses on a firm arrangement.", "I'll be meeting は未来の活動の途中に視点を置きます。I'm meeting は確定した予定に焦点を当てます。", ("Future activity", "未来の活動の途中", "At ten, I'll be meeting a client.", "10時には顧客と会っているところです。"), ("Firm arrangement", "確定した予定", "I'm meeting a client at ten.", "10時に顧客と会う予定です。")),
    ),
    79: semantic_spec(
        (("Use this to give an expected ready state by a deadline.", "期限までに準備できる見込みを伝えるときに使います。"), ("Use this to add honest uncertainty about extra time.", "追加でかかる時間が不確かだと正直に伝えるときに使います。")),
        (("Give one real completion estimate, or say you have no current deadline.", "実際の完了見込みを一つ伝えるか、今は期限がないと伝えましょう。"), ("Name possible extra time for a real task, or say none is expected.", "実際の作業にかかりそうな追加時間を話すか、追加はなさそうだと伝えましょう。")),
        (
            (),
            tuple((jp, "It ", "may", "will", suf) for jp, suf in (("さらに2日{t}かかるかもしれません{/t}。", " take another two days."), ("さらに1時間{t}かかるかもしれません{/t}。", " take another hour."), ("さらに1週間{t}かかるかもしれません{/t}。", " take another week."), ("さらに1日{t}かかるかもしれません{/t}。", " take another day."))),
        ),
        (("Expected ready state", "準備できる見込み", "人 + <b>should have</b> + 物 + ready + by + 期限", "Realistic estimate", "現実的な見込み", ("I <b>should have it ready</b> by Friday.", "We <b>should have the room ready</b> by six.")), ("Uncertain extra time", "不確かな追加時間", "It + <b>may take</b> + another + 時間", "Could change", "変わる可能性", ("It <b>may take another two days</b>.", "It <b>may take another hour</b>."))),
        ("Should or can?", "should と can", "Should gives your realistic expectation. Can sounds more like a firm commitment you control.", "should は現実的な見込みを表します。can は自分で守れる、よりはっきりした約束に聞こえます。", ("Realistic estimate", "現実的な見込み", "I should have it ready by Friday.", "金曜日までには用意できる見込みです。"), ("Firm commitment", "はっきりした約束", "I can have it ready by Friday.", "金曜日までに用意できます。")),
    ),
    80: semantic_spec(
        (("Use this to ask for a message when a future trigger is complete.", "未来のきっかけが完了したら知らせてほしいと頼むときに使います。"), ("Use this to promise an immediate action after a future trigger.", "未来のきっかけの直後に行動すると約束するときに使います。")),
        (("Name one real trigger you want an update about.", "知らせてほしい実際のきっかけを一つ伝えましょう。"), ("Promise one real action after a trigger, or say you have no such task.", "きっかけのあとにする実際の行動を約束するか、そのような作業はないと伝えましょう。")),
        (
            tuple((jp, pre, cor, dis, suf) for jp, pre, cor, dis, suf in (("準備が{t}できたら{/t}知らせてください。", "Let me know once it ", "is", "will be", " ready."), ("レポートが{t}終わったら{/t}知らせてください。", "Let me know once the report ", "is", "will be", " finished."), ("注文品が{t}届いたら{/t}知らせてください。", "Let me know once the order ", "arrives", "will arrive", "."), ("返事が{t}来たら{/t}知らせてください。", "Let me know once you ", "hear back", "will hear back", "."))),
            tuple((jp, pre, cor, dis, suf) for jp, pre, cor, dis, suf in (("返事が来たら{t}すぐ始めます{/t}。", "I'll start as soon as I ", "hear", "will hear", " back."), ("届いたら{t}すぐ電話します{/t}。", "I'll call as soon as it ", "arrives", "will arrive", "."), ("準備できたら{t}すぐ送ります{/t}。", "I'll send it as soon as it ", "is", "will be", " ready."), ("返事が来たら{t}すぐ予約します{/t}。", "I'll book it as soon as they ", "reply", "will reply", "."))),
        ),
        (("Present form after once", "once のあとは現在形", "Let me know + <b>once</b> + 主語 + <b>現在形</b>", "Future trigger", "未来のきっかけ", ("Let me know <b>once it's ready</b>.", "Let me know <b>once the order arrives</b>.")), ("Will only in the action clause", "will は行動の節だけ", "<b>I'll + 動詞</b> + as soon as + 主語 + <b>現在形</b>", "Action after trigger", "きっかけ後の行動", ("<b>I'll start</b> as soon as I <b>hear</b> back.", "<b>I'll call</b> as soon as it <b>arrives</b>."))),
        ("As soon as or the moment?", "as soon as と the moment", "As soon as is neutral and clear. The moment adds stronger immediacy in conversation.", "as soon as は中立的で明確です。the moment は会話で、さらに強い即時性を加えます。", ("Neutral", "中立的", "I'll call as soon as it arrives.", "届いたらすぐ電話します。"), ("More immediate", "さらに即時", "I'll call the moment it arrives.", "届いた瞬間に電話します。")),
    ),
}


# Full productive/receptive ownership. CORE60--70 overlaps are reconciled before final handoff.
VOCAB = {
    71: dict(new="sooner|もっと早く; earlier|より早く; cancel|取り消す", recycled="book|予約する|CORE-41; yesterday|昨日|CORE-30", assumed="call|電話する; check|確認する; leave|出発する; tell|伝える; say|言う; wait|待つ; send|送る; message|メッセージ", receptive="regret|後悔する; my bad|私のミス; lesson learned|勉強になった; none comes to mind|思いつかない"),
    72: dict(new="traffic|交通・渋滞; locked|鍵がかかった", recycled="somewhere else|別の場所|CORE-39; bag|かばん|CORE-3; key|鍵|CORE-3; tired|疲れた|CORE-30", assumed="home|家; train|電車; door|ドア; miss|乗り遅れる; put|入れる; bad|ひどい; this morning|今朝; after work|仕事のあと", receptive="conclusion|結論; come to think of it|そういえば; that would explain it|それなら説明がつく; evidence|根拠; mystery|気になる出来事"),
    73: dict(new="by the time|〜するころには", recycled="shop|店|CORE-10; meeting|会議|CORE-30", assumed="train|電車; arrive|到着する; call|電話する; rain|雨; film|映画; bus|バス; home|家; get home|帰宅する; close|閉まる; leave|出発する; start|始まる; stop|やむ", receptive="sequence|順番; miss it|間に合わない; we just missed it|ちょうど間に合わなかった; of all days|よりによって; timeline|時間軸"),
    74: dict(new="ran out of time|時間がなくなった; slipped my mind|うっかり忘れた; something came up|急用ができた", recycled="book|予約する|CORE-41; noon|正午|CORE-38; sick|病気の|CORE-54; go out|外出する|CORE-34", assumed="call|電話する; cook|料理する; finish|終える; send|送る; meet|会う; yesterday|昨日; report|レポート; calendar|カレンダー; restaurant|レストラン", receptive="intention|つもり; I meant to|〜するつもりだった; changed plan|変わった予定"),
    75: dict(new="used to|以前は〜した; anymore|もう〜ない", recycled="walk|歩く|CORE-26; coffee|コーヒー|CORE-9; downtown|中心街|CORE-15; Sunday|日曜日|CORE-28", assumed="school|学校; work|働く; drink|飲む; play|する; tennis|テニス; every morning|毎朝", receptive="no longer|もはや〜ない; back then|当時; these days|最近は; past habit|昔の習慣"),
    76: dict(new="repair|修理する; replace|交換する; screen|画面; zipper|ファスナー; coat|コート; watch|腕時計", recycled="", assumed="phone|携帯; battery|バッテリー; clean|きれいにする; check|確認する; fix|直す; service|サービス", receptive="turn on|起動する; cracked|ひび割れた; Where can I get this repaired?|これはどこで修理してもらえますか？; while you wait|お待ちの間に"),
    77: dict(new="delivery|配達", recycled="repair|修理する|CORE-76; noon|正午|CORE-38; Friday|金曜日|CORE-28", assumed="update|進捗・最新情報; ready|準備できた; order|注文; check|確認する; arrive|到着する; finish|終える; today|今日", receptive="agreed expectation|合意上の予定; Do you have an update?|進捗はありますか？; When can I expect it?|いつ受け取れますか？; take a look|見てみる"),
    78: dict(new="traveling|移動中", recycled="client|顧客|CORE-54; noon|正午|CORE-38; drive|運転する|CORE-14; meet|会う|CORE-29", assumed="wait|待つ; work|働く; fly|飛ぶ; home|家; stay|滞在する; Osaka|大阪; lunch|昼食; tomorrow|明日; next week|来週", receptive="future point|未来の時点; all being well|順調なら; fingers crossed|うまくいきますように; firm arrangement|確定した予定"),
    79: dict(new="", recycled="noon|正午|CORE-38; Friday|金曜日|CORE-28; Tuesday|火曜日|CORE-28", assumed="ready|準備できた; report|レポート; room|部屋; order|注文; another|さらに; day|日; hour|時間; week|週; take|かかる", receptive="client|顧客; supplier|取引先; change|変更; estimate|見込み; commitment|約束; with any luck|うまくいけば; barring delays|遅れがなければ; realistic|現実的な"),
    80: dict(new="ready|準備できた; hear back|返事をもらう; reply|返事をする", recycled="book|予約する|CORE-41", assumed="report|レポート; order|注文; call|電話する; send|送る; start|始める; finish|終える; arrive|届く", receptive="file|ファイル; message|メッセージ; trigger|きっかけ; the moment|〜した瞬間; no rush|急ぎません; keep me posted|随時知らせて; immediately|すぐに"),
}


KNOWN_WORDS = {
    71: (("メッセージ", "message"), ("チェック", "check"), ("コール", "call")),
    72: (("バッグ", "bag"), ("キー", "key"), ("ドア", "door")),
    73: (("フィルム", "film"), ("バス", "bus"), ("ミーティング", "meeting")),
    74: (("レポート", "report"), ("カレンダー", "calendar"), ("レストラン", "restaurant")),
    75: (("スクール", "school"), ("コーヒー", "coffee"), ("テニス", "tennis")),
    76: (("バッテリー", "battery"), ("サービス", "service"), ("チェック", "check")),
    77: (("オーダー", "order"), ("アップデート", "update"), ("リペア", "repair")),
    78: (("クライアント", "client"), ("ランチ", "lunch"), ("ドライブ", "drive")),
    79: (("レポート", "report"), ("ルーム", "room"), ("オーダー", "order")),
    80: (("レポート", "report"), ("オーダー", "order"), ("コール", "call")),
}


TRANSLATE_HINTS = {
    71: (("電話する:call; より早く:earlier", "確認する:check", "出発する:leave; もっと早く:sooner", "伝える:tell; 昨日:yesterday"), ("言う:say", "予約する:book; 取り消す:cancel", "待つ:wait", "送る:send; メッセージ:message")),
    72: (("家:home", "電車:train; 今朝:this morning", "別の場所:somewhere else; 仕事のあと:after work", "かばん:bag"), ("交通:traffic; ひどい:bad", "ドア:door; 鍵がかかった:locked", "疲れた:tired", "家:home")),
    73: (("電車:train", "映画:film", "店:shop; 電話する:call", "バス:bus; 到着する:arrive"), ("到着する:arrive; 閉まる:close", "電話する:call; 出発する:leave", "会議:meeting; 到着する:arrive", "帰宅する:get home; 雨:rain; やむ:stop")),
    74: (("電話する:call; 時間がなくなった:ran out of time", "料理する:cook; 急用ができた:something came up", "予約する:book; うっかり忘れた:slipped my mind", "外出する:go out; 気分が悪い:sick"), ("終える:finish; 時間がなくなった:ran out of time", "電話する:call; 正午:noon; 急用ができた:something came up", "送る:send; 昨日:yesterday; うっかり忘れた:slipped my mind", "会う:meet; 気分が悪い:sick")),
    75: (("歩く:walk; 学校:school", "コーヒー:coffee; 毎朝:every morning", "働く:work; 中心街:downtown", "テニス:tennis; 日曜日:Sunday"), ("歩く:walk; 学校:school", "飲む:drink; コーヒー:coffee", "働く:work; 中心街:downtown", "する:play; テニス:tennis")),
    76: (("携帯:phone; 修理する:repair", "コート:coat; きれいにする:clean", "バッテリー:battery; 交換する:replace", "腕時計:watch; 直す:fix"), ("画面:screen; 交換する:replace", "ファスナー:zipper; 直す:fix", "コート:coat; きれいにする:clean", "バッテリー:battery; 確認する:check")),
    77: (("準備できた:ready; 今日:today", "準備できた:ready; 金曜日:Friday", "注文:order; 到着する:arrive; 正午:noon", "修理:repair; 終える:finish"), ("確認する:check", "確認する:check; 注文:order", "確認する:check; 修理:repair", "確認する:check; 配達:delivery")),
    78: (("飛ぶ:fly; 家:home", "滞在する:stay; 大阪:Osaka", "会う:meet; 顧客:client", "正午:noon; 昼食:lunch"), ("移動する:traveling", "働く:work", "待つ:wait", "運転する:drive")),
    79: (("準備できた:ready; 金曜日:Friday", "レポート:report; 準備できた:ready; 正午:noon", "部屋:room; 準備できた:ready", "注文:order; 準備できた:ready; 火曜日:Tuesday"), ("さらに:another; 日:day", "さらに:another; 時間:hour", "さらに:another; 週:week", "さらに:another; 日:day")),
    80: (("準備できた:ready", "レポート:report; 終える:finish", "注文:order; 届く:arrive", "返事をもらう:hear back"), ("始める:start; 返事をもらう:hear back", "電話する:call; 届く:arrive", "送る:send; 準備できた:ready", "予約する:book; 返事をする:reply")),
}


OPEN_MENUS = {n: (tuple(x for x in TRANSLATE_HINTS[n][0][:3]), tuple(x for x in TRANSLATE_HINTS[n][1][:3])) for n in range(71, 81)}


SUPPORT_EXPRESSIONS = {
    71: (("My bad.", "私のミスです。"), ("Lesson learned.", "勉強になりました。")),
    72: (("Come to think of it, I left in a hurry.", "そういえば、急いで出ました。"), ("That would explain it.", "それなら説明がつきます。")),
    73: (("We just missed it.", "ちょうど間に合いませんでした。"), ("Of all days!", "よりによって！")),
    74: (("It slipped my mind.", "うっかり忘れました。"), ("Something came up.", "急な用事ができました。")),
    75: (("Back then, I walked everywhere.", "当時はどこへでも歩きました。"), ("These days, I drive.", "最近は車で行きます。")),
    76: (("Where can I get this repaired?", "これはどこで修理してもらえますか？"), ("They can do it while you wait.", "待っている間に作業してもらえます。")),
    77: (("Do you have an update?", "進捗はありますか？"), ("When can I expect it?", "いつ受け取れますか？")),
    78: (("All being well, I'll arrive at six.", "順調なら6時に着きます。"), ("Fingers crossed.", "うまくいきますように。")),
    79: (("With any luck, it'll be ready Friday.", "うまくいけば金曜日に準備できます。"), ("Barring delays, we'll finish today.", "遅れがなければ今日終わります。")),
    80: (("No rush.", "急ぎません。"), ("Keep me posted.", "随時知らせてください。")),
}


DIALOGUES = {
    71: dict(model=("Friend", 0, 0, ("You sounded worried after the call. What happened?", "電話のあと心配そうでした。どうしましたか？"), ("I understand. And what do you regret saying?", "分かりました。それから、何を言ったことを後悔していますか？"), ("You can call back and explain both things now.", "今かけ直して、両方説明できますよ。"), ("You're right. I'll do that.", "そうですね。そうします。")), wild=("Teammate", 1, 3, ("The form went out before you checked it.", "確認する前にフォームを送ってしまいましたね。"), ("I saw the message too. What else do you regret?", "メッセージも見ました。ほかに何を後悔していますか？"), ("Let's correct both now and send one clear note.", "今両方直して、分かりやすい連絡を一つ送りましょう。"), ("Good idea. I'll fix them now.", "いいですね。今直します。"))),
    72: dict(model=("Friend", 0, 0, ("Your key isn't here. Where could it be?", "鍵がここにありません。どこでしょう？"), ("Maybe. The roads were completely blocked too.", "そうかもしれません。それに道路も完全にふさがっていました。"), ("That explains both the key and the late arrival.", "それで鍵と遅れて着いたことの両方に説明がつきます。"), ("Yes, I'll check at home first.", "はい、まず家を確認します。")), wild=("Coworker", 1, 1, ("Maya hasn't arrived, and her train was delayed.", "マヤがまだ着かず、電車も遅れました。"), ("That's possible. The office door didn't open this morning either.", "その可能性があります。今朝はオフィスのドアも開きませんでした。"), ("I'll call Maya while you ask reception about the door.", "私がマヤに電話するので、受付にドアを確認してください。"), ("Okay. We'll check both explanations.", "分かりました。両方の可能性を確認しましょう。"))),
    73: dict(model=("Friend", 0, 0, ("Remind me what happened at the station.", "駅で何があったか、もう一度教えてください。"), ("That's frustrating. What happened at the shop later?", "それは残念ですね。そのあと店ではどうしましたか？"), ("So the train had left and the shop had closed before you arrived.", "つまり、着く前に電車は出て、店は閉まっていたんですね。"), ("Yes. Next time I'll leave earlier.", "はい。次はもっと早く出ます。")), wild=("Colleague", 2, 2, ("What happened when you called the shop?", "店に電話したとき、どうなりましたか？"), ("And had Maya arrived before the meeting started?", "では、会議が始まる前にマヤは着いていましたか？"), ("Good. She shared the notes, so nothing was lost.", "よかったです。彼女がメモを共有したので、問題ありませんでした。"), ("Great. I'll read them now.", "よかったです。今読みます。"))),
    74: dict(model=("Coworker", 0, 2, ("I didn't hear from you yesterday. What happened?", "昨日連絡がありませんでした。どうしましたか？"), ("I understand. What about the report?", "分かりました。レポートはどうでしたか？"), ("Thanks for explaining. Let's set a new time now.", "説明ありがとう。今、新しい時間を決めましょう。"), ("Good. I'll put it in the calendar.", "はい。カレンダーに入れます。")), wild=("Friend", 2, 1, ("We still don't have a restaurant for Friday. What happened?", "金曜日のレストランがまだ決まっていません。どうしましたか？"), ("I understand. You also planned to call the restaurant at noon, right?", "分かりました。正午にレストランへ電話する予定でもありましたよね？"), ("Let's call now and book one.", "今電話して予約しましょう。"), ("Yes. I'll do it now.", "はい。今やります。"))),
    75: dict(model=("Friend", 0, 0, ("How did you get to school when you were younger?", "子どものころ、どうやって学校へ行きましたか？"), ("That's quite different. Do you still walk there?", "ずいぶん違いますね。今も歩きますか？"), ("So walking was your old routine, not your current one.", "つまり、歩くのは昔の習慣で、今の習慣ではないんですね。"), ("Exactly. These days I take the train.", "そのとおりです。最近は電車に乗ります。")), wild=("Neighbor", 2, 2, ("You know this downtown area well. Did you work here?", "この中心街に詳しいですね。ここで働いていたんですか？"), ("I see. Do you still work downtown?", "なるほど。今も中心街で働いていますか？"), ("That explains why you know every café here.", "それで、この辺のカフェを全部知っているんですね。"), ("Yes. I can show you my favorite one.", "はい。お気に入りの店を案内できます。"))),
    76: dict(model=("Friend", 0, 0, ("Your phone turns on again. Did you get it repaired?", "携帯がまた起動しましたね。修理してもらったんですか？"), ("Good. Is the cracked screen next?", "よかったです。次はひび割れた画面ですか？"), ("The shop on the corner can replace screens today.", "角の店なら今日画面を交換できますよ。"), ("Perfect. I'll go there after work.", "よかったです。仕事のあと行きます。")), wild=("Neighbor", 1, 1, ("That coat looks much cleaner now.", "そのコート、ずっときれいになりましたね。"), ("The zipper is still stuck, though.", "でもファスナーはまだ動きませんね。"), ("The cleaner next door also fixes zippers.", "隣のクリーニング店はファスナーも直しますよ。"), ("Great. I'll take it there tomorrow.", "よかったです。明日持っていきます。"))),
    77: dict(model=("Repair clerk", 0, 0, ("How can I help with your repair?", "修理について、どのようなご用件ですか？"), ("I'm sorry about the delay. What would you like me to check?", "遅れて申し訳ありません。何を確認しましょうか？"), ("I found it. The part arrived today, and it'll be ready at six.", "確認できました。部品は今日届き、6時に出来上がります。"), ("Thank you. Six works for me.", "ありがとうございます。6時で大丈夫です。")), wild=("Delivery clerk", 2, 3, ("Hello. What can I check for you?", "こんにちは。何を確認しましょうか？"), ("I see the delay. Which item needs an update?", "遅れを確認しました。どの品物の状況を確認しますか？"), ("I found it. The delivery will arrive tomorrow morning.", "確認できました。配達は明日の朝に届きます。"), ("Thanks. I'll be there then.", "ありがとう。その時間にいます。"))),
    78: dict(model=("Friend", 0, 0, ("What will you be doing this time tomorrow?", "明日の今ごろは何をしていますか？"), ("That's a long trip. Will you be home by six?", "長い移動ですね。6時までには家に着いていますか？"), ("Then I'll wait until seven before I call.", "では、電話は7時まで待ちます。"), ("Thanks. I should be home by then.", "ありがとう。そのころには家に着いているはずです。")), wild=("Coworker", 2, 1, ("What will you be doing tomorrow morning?", "明日の朝は何をしていますか？"), ("And at eight? Will the work be over?", "では8時は？ 仕事は終わっていますか？"), ("I'll move our call to nine so you can finish first.", "先に終えられるよう、電話を9時に変更します。"), ("Perfect. Nine is much better.", "よかったです。9時のほうがずっといいです。"))),
    79: dict(model=("Coworker", 0, 0, ("When do you expect the task to be ready?", "作業はいつ準備できる見込みですか？"), ("The client may ask for changes. Could that affect Friday?", "顧客から変更を求められるかもしれません。それで金曜日の見込みは変わりますか？"), ("Thanks. I'll plan for Friday but keep another two days open.", "ありがとう。金曜日を予定にしますが、さらに2日も空けておきます。"), ("That gives us a safe plan.", "それなら無理のない予定です。")), wild=("Organizer", 2, 1, ("When will the room be ready for the event?", "会場はいつイベントの準備ができますか？"), ("One supplier may be late. Could that affect six?", "取引先が一社遅れるかもしれません。それで6時の見込みは変わりますか？"), ("I'll tell the team six, with another hour as a backup.", "チームには6時と伝え、予備でさらに1時間みておきます。"), ("Good. That gives us some room.", "いいですね。それなら少し余裕ができます。"))),
    80: dict(model=("Coworker", 0, 0, ("The final file isn't ready yet. What do you need from me?", "最終ファイルはまだできていません。私に何をしてほしいですか？"), ("I will. What will you do when you hear from me?", "分かりました。私から連絡が来たら何をしますか？"), ("Okay. I'll message you as soon as the file is ready.", "分かりました。ファイルができたらすぐメッセージを送ります。"), ("Thanks. Then I can start right away.", "ありがとう。それならすぐ始められます。")), wild=("Organizer", 2, 1, ("The order hasn't arrived. What should I do?", "注文品が届いていません。どうすればいいですか？"), ("I will. What will you do when it arrives?", "分かりました。届いたら何をしますか？"), ("Good. I'll watch for the delivery and tell you immediately.", "分かりました。配達を待ち、すぐ知らせます。"), ("Thanks. Then I'll call right away.", "ありがとう。それならすぐ電話します。"))),
}


LIVE_SCENES = {
    71: (("text", "other", "Tutor", "Is there anything you wish you had done differently?", "しておけばよかったと思うことはありますか？"), ("input", "me", "Me", "I should have ___. / Nothing comes to mind right now.", "___すればよかったです。／今は特に思いつきません。"), ("text", "me", "Me", "What about you? Is there anything you should have done?", "あなたはどうですか？ しておけばよかったことはありますか？"), ("input", "other", "Tutor", "Tutor's answer: I should have ___. / Nothing comes to mind right now.", "先生の本当の答え：___すればよかったです。／今は特に思いつきません。")),
    72: (("text", "other", "Tutor", "Think of something you once couldn't find. What might have happened?", "以前、見つからなかった物を思い出してください。何が起きたのでしょうか？"), ("input", "me", "Me", "I might have ___. / I can't think of a missing item right now.", "___したのかもしれません。／今は見つからなかった物を思いつきません。"), ("text", "me", "Me", "Have you ever lost something? What do you think happened?", "何かをなくしたことはありますか？ 何が起きたと思いますか？"), ("input", "other", "Tutor", "Tutor's real answer: I might have ___. / I haven't lost anything recently.", "先生の本当の答え：___したのかもしれません。／最近は何もなくしていません。")),
    73: (("text", "other", "Tutor", "Have you ever arrived after something had already finished?", "何かがもう終わったあとに着いたことはありますか？"), ("input", "me", "Me", "Yes. ___ had already ___ when I arrived. / No, that hasn't happened to me.", "はい。着いたときには___がもう___していました。／いいえ、その経験はありません。"), ("text", "me", "Me", "What about you? What had already happened by the time you got there?", "あなたはどうですか？ 着いたころには何がもう起きていましたか？"), ("input", "other", "Tutor", "Tutor's real answer: ___ had already ___ when I arrived. / That hasn't happened to me.", "先生の本当の答え：着いたときには___がもう___していました。／その経験はありません。")),
    74: (("text", "other", "Tutor", "Has one of your plans changed recently?", "最近、予定が変わったことはありますか？"), ("input", "me", "Me", "I was going to ___, but ___. / No, none of my plans changed recently.", "___するつもりでしたが、___。／いいえ、最近変わった予定はありません。"), ("text", "me", "Me", "What about you? Was there anything you were going to do?", "あなたはどうですか？ するつもりだったことはありますか？"), ("input", "other", "Tutor", "Tutor's real answer: I was going to ___, but ___. / No, none of my plans changed recently.", "先生の本当の答え：___するつもりでしたが、___。／いいえ、最近変わった予定はありません。")),
    75: (("text", "other", "Tutor", "What's one thing you used to do but don't do anymore?", "以前はしていたけれど、今はもうしないことは何ですか？"), ("input", "me", "Me", "I used to ___. I don't ___ anymore. / Nothing has really changed.", "以前は___していました。今はもう___しません。／特に変わっていません。"), ("text", "me", "Me", "What about you? What did you use to do?", "あなたはどうですか？ 以前は何をしていましたか？"), ("input", "other", "Tutor", "Tutor's real answer: I used to ___. I don't ___ anymore. / Nothing has really changed.", "先生の本当の答え：以前は___していました。今はもう___しません。／特に変わっていません。")),
    76: (("text", "other", "Tutor", "Have you had anything repaired or cleaned recently?", "最近、何かを修理・クリーニングしてもらいましたか？"), ("input", "me", "Me", "Yes. I had my ___ ___. / No, I haven't arranged a service recently.", "はい。___を___してもらいました。／いいえ、最近サービスを頼んでいません。"), ("text", "me", "Me", "What about you? Is there anything you need to get fixed?", "あなたはどうですか？ 直してもらう必要がある物はありますか？"), ("input", "other", "Tutor", "Tutor's real answer: I need to get ___ ___. / No, I don't need a service right now.", "先生の本当の答え：___を___してもらう必要があります。／今は必要なサービスはありません。")),
    77: (("text", "other", "Tutor", "Have you ever had an order or repair that wasn't ready when promised?", "約束の時に準備できていなかった注文品や修理はありますか？"), ("input", "me", "Me", "Yes. It was supposed to be ready by ___. / No, I haven't had that problem.", "はい。___までに出来上がっているはずでした。／いいえ、その問題はありません。"), ("text", "me", "Me", "What about you? Was an order or repair ever late?", "あなたはどうですか？ 注文品や修理が遅れたことはありますか？"), ("input", "other", "Tutor", "Tutor's real answer: Yes. It was supposed to arrive by ___. / No, I haven't had that problem.", "先生の本当の答え：はい。___までに届くはずでした。／いいえ、その問題はありません。")),
    78: (("text", "other", "Tutor", "What will you be doing this time tomorrow?", "明日の今ごろは何をしていますか？"), ("input", "me", "Me", "I'll be ___. / I don't have a plan for that time yet.", "___しているところです。／その時間の予定はまだありません。"), ("text", "me", "Me", "What about you? What will you be doing this time tomorrow?", "あなたはどうですか？ 明日の今ごろは何をしていますか？"), ("input", "other", "Tutor", "Tutor's real answer: I'll be ___. / I don't have a plan for that time yet.", "先生の本当の答え：___しているところです。／その時間の予定はまだありません。")),
    79: (("text", "other", "Tutor", "Do you have a task with a real deadline now?", "今、実際に期限のある作業はありますか？"), ("input", "me", "Me", "Yes. I should have ___ ready by ___. / No, I don't have a deadline right now.", "はい。___を___までに用意できる見込みです。／いいえ、今は期限がありません。"), ("text", "me", "Me", "What about you? When should your next task be ready?", "あなたはどうですか？ 次の作業はいつ準備できる見込みですか？"), ("input", "other", "Tutor", "Tutor's real answer: I should have ___ ready by ___. / I don't have a deadline right now.", "先生の本当の答え：___を___までに用意できる見込みです。／今は期限がありません。")),
    80: (("text", "other", "Tutor", "Is one of your tasks waiting for a reply or another task to finish?", "返事や別の作業の完了を待っている作業はありますか？"), ("input", "me", "Me", "Yes. I'll ___ as soon as ___. / No, none of my tasks depend on that right now.", "はい。___します。___したらすぐに。／いいえ、今はそのような作業はありません。"), ("text", "me", "Me", "What about you? What will you do as soon as you hear back?", "あなたはどうですか？ 返事が来たらすぐ何をしますか？"), ("input", "other", "Tutor", "Tutor's real answer: I'll ___ as soon as ___. / No task depends on a reply right now.", "先生の本当の答え：___します。___したらすぐに。／今は返事を待つ作業はありません。")),
}


LIVE_HINTS = {
    71: {1: ("電話する:call", "確認する:check", "伝える:tell")}, 72: {1: ("家:home", "かばん:bag", "電車:train")},
    73: {1: ("電車:train", "映画:film", "店:shop")}, 74: {1: ("電話する:call", "料理する:cook", "急用ができる:something came up")},
    75: {1: ("歩く:walk", "コーヒー:coffee", "テニス:tennis")}, 76: {1: ("携帯:phone", "コート:coat", "修理する:repair", "きれいにする:clean")},
    77: {1: ("今日:today", "金曜日:Friday", "正午:noon")}, 78: {1: ("働く:work", "移動する:traveling", "待つ:wait")},
    79: {1: ("レポート:report", "部屋:room", "金曜日:Friday")}, 80: {1: ("始める:start", "送る:send", "返事をもらう:hear back")},
}


REVIEWED_WRITES_71_80 = {
    71: (("Use “I should have ___” to name the better action you missed.", "「I should have ___」を使って、しておけばよかった行動を伝えましょう。"), ("Use “I shouldn't have ___” to name an action you now regret.", "「I shouldn't have ___」を使って、しなければよかった行動を伝えましょう。")),
    72: (("Use “I might have ___” to offer one possible past explanation.", "「I might have ___」を使って、過去について可能性のある説明を伝えましょう。"), ("Use “___ must have ___” to give one confident past conclusion.", "「___ must have ___」を使って、過去について確信のある結論を伝えましょう。")),
    73: (("Use “___ had already ___ when ___” to put two past events in order.", "「___ had already ___ when ___」を使って、過去の二つの出来事を順番に伝えましょう。"), ("Use “By the time ___, ___ had ___” to show what was already complete.", "「By the time ___, ___ had ___」を使って、その時までに終わっていたことを伝えましょう。")),
    74: (("Use “I was going to ___, but ___” to explain an intention that changed.", "「I was going to ___, but ___」を使って、変わったつもりを説明しましょう。"), ("Use “I'd planned to ___, but ___” to explain an earlier plan that changed.", "「I'd planned to ___, but ___」を使って、変わった以前の予定を説明しましょう。")),
    75: (("Use “I used to ___” to describe one past habit that is no longer true.", "「I used to ___」を使って、今はしていない昔の習慣を伝えましょう。"), ("Use “I don't ___ anymore” to state what is different now.", "「I don't ___ anymore」を使って、今はもうしないことを伝えましょう。")),
    76: (("Use “I had ___ repaired” to name one service you arranged.", "「I had ___ repaired」を使って、頼んだサービスを一つ伝えましょう。"), ("Use “I need to get ___ fixed” to name one service you still need.", "「I need to get ___ fixed」を使って、まだ必要なサービスを伝えましょう。")),
    77: (("Use “It was supposed to ___ by ___” to state an unmet service expectation.", "「It was supposed to ___ by ___」を使って、満たされなかったサービスの予定を伝えましょう。"), ("Use “Do you know what happened to ___?” to ask neutrally about a delayed item.", "「Do you know what happened to ___?」を使って、遅れている物について中立的に尋ねましょう。")),
    78: (("Use “I'll be ___ at ___” to say what you expect to be doing at a future time.", "「I'll be ___ at ___」を使って、未来の時点でしている予定を伝えましょう。"), ("Use “I'll still be ___ at ___” to say what will remain in progress.", "「I'll still be ___ at ___」を使って、その時も続いている予定を伝えましょう。")),
    79: (("Use “I should have ___ ready by ___” to give a realistic completion estimate.", "「I should have ___ ready by ___」を使って、現実的な完了見込みを伝えましょう。"), ("Use “I may need another ___” to name possible extra time.", "「I may need another ___」を使って、追加で必要かもしれない時間を伝えましょう。")),
    80: (("Use “Please ___ as soon as ___” to request an update after one trigger.", "「Please ___ as soon as ___」を使って、きっかけのあとすぐ知らせるよう頼みましょう。"), ("Use “I'll ___ as soon as ___” to promise one action after a trigger.", "「I'll ___ as soon as ___」を使って、きっかけのあとすぐする行動を約束しましょう。")),
}


REVIEWED_LIVE_71_80 = {
    71: ("Which small mistake would bother you more: being a little late or forgetting one detail? Why?", "少し遅れることと、一つの細かいことを忘れることでは、どちらがより気になりますか？なぜですか？", "What about you—which mistake would bother you more?", "先生はどうですか？どちらの失敗がより気になりますか？"),
    72: ("When you misplace something, where do you look first?", "物をどこかに置き忘れたとき、最初にどこを探しますか？", "What about you—where do you look first?", "先生はどうですか？最初にどこを探しますか？"),
    73: ("What's something you really dislike arriving late for?", "遅刻したくないと思うことは何ですか？", "What about you—what do you never want to be late for?", "先生はどうですか？何に遅刻したくありませんか？"),
    74: ("Do you usually adapt easily when a plan changes? Why?", "予定が変わったとき、普段すぐに対応できますか？なぜですか？", "What about you—how do you handle changed plans?", "先生はどうですか？予定の変更にどう対応しますか？"),
    75: ("What habit from childhood would you like to bring back—or start now?", "子どものころの習慣で、もう一度始めたいもの、または今から始めたいものは何ですか？", "What about you—which habit would you bring back or start?", "先生はどうですか？どんな習慣をもう一度始めたいですか？"),
    76: ("When something breaks, do you prefer to repair it or replace it?", "物が壊れたら、修理するのと買い替えるのとどちらが好きですか？", "What about you—do you usually repair things?", "先生はどうですか？普段は修理しますか？"),
    77: ("How patient are you when a service or delivery is late?", "サービスや配達が遅れたとき、どのくらい待てますか？", "What about you—how do you react to a delay?", "先生はどうですか？遅れたときどうしますか？"),
    78: ("How would you most like to spend tomorrow evening?", "明日の夜はどのように過ごしたいですか？", "What about you—how would you spend tomorrow evening?", "先生はどうですか？明日の夜はどう過ごしますか？"),
    79: ("Do deadlines help you focus, or do they make you feel stressed?", "締め切りがあると集中できますか？それともストレスを感じますか？", "What about you—how do deadlines affect you?", "先生はどうですか？締め切りがあるとどう感じますか？"),
    80: ("How do you prefer to receive important updates?", "大切な連絡はどのように受け取りたいですか？", "What about you—how do you prefer to get updates?", "先生はどうですか？どの方法で連絡を受けたいですか？"),
}


ROLE_JA = {"Friend": "友人", "Teammate": "チームメンバー", "Coworker": "同僚", "Colleague": "同僚", "Neighbor": "近所の人", "Repair clerk": "修理店の店員", "Delivery clerk": "配達窓口の店員", "Organizer": "主催者"}


OMIT_LOW_VALUE_CHOICES = {71: (1, 2), 72: (1, 2), 74: (1, 2), 75: (1, 2), 77: (1, 2), 78: (1, 2), 79: (1, 2)}
for _number in range(71, 81):
    SPECS[_number]["writes"] = REVIEWED_WRITES_71_80[_number]
    _q, _q_ja, _back, _back_ja = REVIEWED_LIVE_71_80[_number]
    LESSONS[_number]["prompt"] = ("Let's talk about this topic. Answer my question, then ask me too.", "この話題について話しましょう。私の質問に答えて、そのあと私にも聞いてください。")
    LIVE_SCENES[_number] = (("text", "other", "Tutor", _q, _q_ja), ("input", "me", "Me", "Student's answer", "自分の答え"), ("text", "me", "Me", _back, _back_ja), ("input", "other", "Tutor", "Tutor's answer", "先生の答え"))
    LIVE_HINTS[_number] = {}
for _number, _parts in OMIT_LOW_VALUE_CHOICES.items():
    LESSONS[_number]["omit_choice"] = _parts
    _choices = list(SPECS[_number]["choices"])
    for _part in _parts:
        _choices[_part - 1] = ()
    SPECS[_number]["choices"] = tuple(_choices)


TRANSFER_SCENES = {
    71: "team form correction after premature sending", 72: "late colleague and locked office investigation",
    73: "workday timing update after a closed shop and meeting start", 74: "restaurant booking after a missed call",
    75: "former downtown workplace neighborhood tour", 76: "coat cleaning with a stuck zipper",
    77: "delayed parcel at a delivery desk", 78: "late work call moved around a client meeting",
    79: "event room setup estimate", 80: "late order triggers an immediate supplier call",
}


THREE_CHIP_EXCEPTIONS = {(78, 2): "The anchored future-progressive line has three honest meaning units."}


SPIRALS = {
    71: (("MODAL-01", "contrast", "Keep the modal followed by the plain verb have.", "法助動詞の直後は原形の have にしましょう。", (("should の直後は{t}原形{/t}。", "I should ", "have", "had", " called earlier."), ("shouldn't の直後は{t}原形{/t}。", "I shouldn't ", "have", "had", " waited."), ("might の直後は{t}原形{/t}。", "I might ", "have", "had", " missed it."), ("must の直後は{t}原形{/t}。", "It must ", "have", "had", " closed."))),),
    72: (("PERF-01", "contrast", "Choose a present result or one finished past time.", "今に関わる結果か、終わった過去の時かを選びましょう。", (("今も鍵が見つからない。{t}なくしたかもしれない{/t}。", "I might ", "have lost", "lost", " my keys."), ("昨日の出来事。{t}昨日なくした{/t}。", "I ", "lost", "have lost", " them yesterday."), ("今も原因を考えている。{t}置いてきたかもしれない{/t}。", "I might ", "have left", "left", " it at home."), ("先週の出来事。{t}先週置いてきた{/t}。", "I ", "left", "have left", " it there last week."))), ("MODAL-01", "transfer", "Keep have in its plain form after might and must.", "might と must のあとは原形の have を使いましょう。", (("可能性のある過去。", "It might ", "have", "had", " closed."), ("確信のある過去。", "It must ", "have", "had", " closed."), ("可能性のある過去。", "She might ", "have", "had", " left."), ("確信のある過去。", "She must ", "have", "had", " left.")))),
    73: (("PERF-01", "transfer", "Choose the form that keeps the present result or marks the earlier past.", "今の結果を保つ形か、さらに前の過去を示す形を選びましょう。", (("今も見つかっていない。", "I ", "haven't found", "hadn't found", " it."), ("到着した時点より前。", "The train ", "had left", "has left", " when we arrived."), ("今の進捗。", "We ", "have finished", "had finished", " the report."), ("会議開始より前。", "She ", "had arrived", "has arrived", " before it started."))), ("ASPECT-02", "transfer", "Choose an activity in progress or its completed result.", "進行中の活動か、完了した結果かを選びましょう。", (("電話したとき進行中。", "I was ", "cooking", "cooked", " when you called."), ("今ある完了結果。", "I've ", "finished", "been finishing", " the report."), ("着いたとき進行中。", "They were ", "waiting", "waited", " when I arrived."), ("今ある完了結果。", "I've ", "sent", "been sending", " the email.")))),
    74: (("REPORT-01", "controlled", "Choose say or tell with the correct listener pattern.", "聞き手の置き方に合う say / tell を選びましょう。", (("マヤに予定を{t}伝えた{/t}。", "I ", "told Maya", "said Maya", " I was going to call."), ("予定を{t}言った{/t}。", "I ", "said", "told", " I was going to call."), ("彼に予定を{t}伝えた{/t}。", "I ", "told him", "said him", " I'd planned to finish it."), ("予定を{t}言った{/t}。", "I ", "said", "told", " I'd planned to finish it."))),),
    75: (("ASPECT-01", "checkpoint", "Choose the old routine or the action happening now.", "昔の習慣か、今進行中の動作かを選びましょう。", (("昔の習慣。", "I ", "used to walk", "am walking", " to school."), ("今している途中。", "I ", "am walking", "used to walk", " home now."), ("昔の習慣。", "I ", "used to work", "am working", " downtown."), ("今している途中。", "I ", "am working", "used to work", " at home today."))), ("DO-01", "transfer", "Keep the main verb plain after don't.", "don't のあとは動詞を原形にしましょう。", (("今はもう働かない。", "I don't ", "work", "worked", " there anymore."), ("今はもう飲まない。", "I don't ", "drink", "drank", " coffee anymore."), ("今はもう歩かない。", "I don't ", "walk", "walked", " there anymore."), ("今はもうしない。", "I don't ", "play", "played", " tennis anymore.")))),
    77: (("PERF-01", "transfer", "Choose a present result or one finished past time.", "今につながる結果か、終わった過去の時かを選びましょう。", (("今もまだ届いていない。", "It ", "hasn't arrived", "didn't arrive", " yet."), ("昨日の配達。", "It ", "didn't arrive", "hasn't arrived", " yesterday."), ("今も修理が終わっていない。", "They ", "haven't finished", "didn't finish", " the repair yet."), ("先週の予定。", "They ", "didn't finish", "haven't finished", " it last week."))),),
    78: (("ASPECT-02", "contrast", "Choose a simple future event or an activity in progress at that time.", "単純な未来の出来事か、その時に進行中の活動かを選びましょう。", (("6時に出発する予定。", "I ", "will leave", "will be leaving", " at six."), ("6時には出発の途中。", "At six, I ", "will be leaving", "will leave", "."), ("明日働く予定。", "I ", "will work", "will be working", " tomorrow."), ("明日の今ごろは仕事中。", "This time tomorrow, I ", "will be working", "will work", "."))), ("MODAL-01", "transfer", "Keep be in its plain form after will.", "will のあとは原形の be を使いましょう。", (("未来に進行中。", "I'll ", "be", "am", " flying."), ("未来に進行中。", "She'll ", "be", "is", " working."), ("未来に進行中。", "We'll ", "be", "are", " waiting."), ("未来に進行中。", "They'll ", "be", "are", " traveling.")))),
    80: (("ASPECT-02", "checkpoint", "Choose a state that is complete or an activity still in progress.", "完了した状態か、まだ進行中の活動かを選びましょう。", (("準備が完了した状態。", "Let me know once it's ", "ready", "working", "."), ("まだ作業中。", "Let me know while you're ", "working", "ready", "."), ("完了した結果。", "Let me know once you've ", "finished", "finishing", "."), ("まだ確認中。", "Let me know while you're ", "checking", "checked", " it."))), ("PREP-01", "transfer", "Keep the preposition with the verb or noun it belongs to.", "前置詞を結びつく動詞・名詞と一緒に使いましょう。", (("顧客{t}から{/t}返事が来る。", "I hear back ", "from", "to", " the client."), ("金曜日{t}までに{/t}。", "It'll be ready ", "by", "at", " Friday."), ("返事を{t}待つ{/t}。", "I'm waiting ", "for", "at", " a reply."), ("注文品{t}について{/t}知らせる。", "Keep me posted ", "about", "to", " the order.")))),
}


DIALOGUE_SEMANTIC_LEDGER = {
    71: dict(model=("friend asks what happened", "learner names missed better action", "friend asks about regretted speech", "learner names regretted action", "friend proposes repair", "learner accepts concrete repair"), wild=("teammate identifies unchecked form", "learner names checking regret", "teammate identifies message too", "learner names sending regret", "teammate proposes one repair", "learner starts repair")),
    72: dict(model=("friend establishes missing keys", "learner offers home possibility", "friend adds blocked roads", "learner concludes traffic was bad", "friend connects both mysteries", "learner starts home check"), wild=("coworker establishes late colleague", "learner offers missed-train possibility", "coworker adds locked door", "learner concludes door was locked", "coworker divides checks", "learner confirms both checks")),
    73: dict(model=("friend asks station recap", "learner orders train and arrival", "friend asks later shop event", "learner orders shop and arrival", "friend summarizes two completed events", "learner changes departure plan"), wild=("colleague asks closed shop timing", "learner orders closure and call", "colleague asks Maya timing", "learner orders arrival and meeting", "colleague resolves notes access", "learner reads notes")),
    74: dict(model=("coworker asks missed contact", "learner gives intention and reason", "coworker asks report plan", "learner gives earlier plan and reason", "coworker proposes new time", "learner records it"), wild=("friend asks missing restaurant", "learner gives booking intention and reason", "friend asks noon call plan", "learner gives earlier call plan and interruption", "friend proposes immediate booking", "learner starts booking")),
    75: dict(model=("friend asks childhood commute", "learner gives old habit", "friend asks current contrast", "learner states no longer true", "friend summarizes contrast", "learner gives current routine"), wild=("neighbor asks downtown history", "learner gives old workplace", "neighbor asks current status", "learner states no longer true", "neighbor infers local knowledge", "learner offers tour")),
    76: dict(model=("friend confirms phone powers on", "learner reports arranged repair", "friend asks about cracked screen", "learner names screen service", "friend identifies real shop", "learner chooses visit time"), wild=("neighbor notices clean coat", "learner reports cleaning", "neighbor notices zipper", "learner names zipper service", "neighbor identifies provider", "learner chooses visit day")),
    77: dict(model=("service asks repair need", "learner states missed expectation", "service apologizes and asks item", "learner requests neutral check", "service gives concrete update", "learner accepts time"), wild=("desk asks check need", "learner states order expectation", "desk identifies delay", "learner requests delivery check", "desk gives concrete arrival", "learner accepts")),
    78: dict(model=("friend asks tomorrow activity", "learner places flight in progress", "friend checks home arrival", "learner says travel still in progress", "friend moves call", "learner confirms arrival estimate"), wild=("coworker asks morning activity", "learner places meeting in progress", "coworker asks later completion", "learner says work still in progress", "coworker moves call", "learner accepts")),
    79: dict(model=("coworker asks readiness estimate", "learner gives Friday estimate", "coworker names client-change risk", "learner gives possible additional time", "coworker builds buffer", "learner confirms safe plan"), wild=("organizer asks room estimate", "learner gives six estimate", "organizer names supplier-delay risk", "learner gives possible additional hour", "organizer communicates buffered estimate", "learner accepts buffer")),
    80: dict(model=("coworker establishes unfinished file", "learner requests readiness update", "coworker asks action after contact", "learner promises immediate start", "coworker promises readiness message", "learner resolves start timing"), wild=("organizer establishes order delay", "learner requests arrival update", "organizer asks action after arrival", "learner promises immediate call", "organizer promises immediate notice", "learner resolves call timing")),
}


def set_vocab(head, number):
    for category, value in VOCAB[number].items():
        head = re.sub(rf'(<meta name="podo:vocabulary:{category}" content=")[^"]*(")', rf'\g<1>{value}\2', head, count=1)
    return head


def hint_html(items):
    chips = []
    for item in items:
        for part in item.split("; "):
            if part and part not in chips:
                chips.append(part)
    return '<span class="hint">' + "".join(f'<span class="hint-chip">{core.esc(item)}</span>' for item in chips) + "</span>"


def known_page(number):
    cards = "".join(f'<div class="br-row"><span class="br-cn">{core.esc(jp)}</span><span class="br-eq">→</span><span class="br-ko">{core.esc(en)}</span></div>' for jp, en in KNOWN_WORDS[number])
    return core.section("words-you-know", "Words you know", "知っている単語", '<p class="section-subtitle"><span class="ko">Say the three familiar words in English.</span><span class="ja">知っている3つの単語を英語で言いましょう。</span></p><div class="bridge">' + cards + "</div>")


def support_page(number):
    lines = "".join(f'<div class="model-line"><span class="korean">{core.esc(en)}</span><span class="translation">{core.esc(ja)}</span></div>' for en, ja in SUPPORT_EXPRESSIONS[number])
    return core.section("supporting-expressions", "Useful conversation support", "会話を支える表現", '<p class="section-subtitle"><span class="ko">Read the two optional expressions.</span><span class="ja">必要なときに使える二つの表現を読みましょう。</span></p><div class="model-list">' + lines + "</div>")


def spiral_pages(number):
    pages = []
    for index, (spiral_id, level, script, script_ja, choice_data) in enumerate(SPIRALS.get(number, ())):
        pid = f"spiral-{spiral_id.casefold()}-{index}"
        page = core.choose_words(pid, "Spiral review", "スパイラル復習", script, script_ja, choice_data)
        page = page.replace(f'data-page-id="{pid}"', f'data-page-id="{pid}" data-spiral-id="{spiral_id}" data-spiral-level="{level}"', 1)
        pages.append(page)
    return pages


def translate_page(number, part, pattern):
    blocks = []
    for index, ((english, japanese, _), hints) in enumerate(zip(pattern, TRANSLATE_HINTS[number][part - 1], strict=True)):
        blocks.append('<div class="task-block"><div class="answer-box"><span class="answer-label">' + core.esc(core.strip_marks(japanese)) + '</span><span class="answer-space as-input"><input class="space-input" type="text" data-sync-id="p' + str(part) + '-translate-' + str(index) + '" data-answer="' + core.esc(core.strip_marks(english)) + '" autocomplete="off" spellcheck="false"></span>' + hint_html((hints,)) + '</div></div>')
    rendered = core.section(
        f"p{part}-translate", "Say it in English", "英語にしよう",
        '<p class="section-subtitle"><span class="ko">Read the Japanese, then say it in English.</span>'
        '<span class="ja">日本語を見て、英語で言ってみましょう。</span></p>'
        '<div class="tutor-note">Type the learner\'s complete English sentence exactly as they say it.</div>'
        + "".join(blocks),
    )
    return rendered.replace(
        f'data-page-id="p{part}-translate"',
        f'data-page-id="p{part}-translate" data-scaffolding-contract="target-v2" data-support-stage="supported"',
        1,
    )


def write_page(number, part, pattern):
    prompt_en, prompt_ja = SPECS[number]["writes"][part - 1]
    return core.section(
        f"p{part}-write", "Make it yours", "自分の文にしよう",
        f'<p class="section-subtitle"><span class="ko">{core.esc(prompt_en)}</span><span class="ja">{core.esc(prompt_ja)}</span></p>'
        '<div class="tutor-note">Let the learner answer aloud before you capture it. React first, then add only a useful correction.</div>'
        + core.feedback_compose(f"p{part}-write", hint_html(OPEN_MENUS[number][part - 1])),
    )


def live_page(number):
    rendered = []
    for index, (kind, side, speaker, english, japanese) in enumerate(LIVE_SCENES[number]):
        avatar = core.live_avatar(speaker)
        bubble = "bubble me" if side == "me" else "bubble"
        if kind == "text":
            rendered.append(f'<div class="turn {side}">{avatar}<div class="{bubble}"><span class="korean">{core.esc(english)}</span><span class="translation">{core.esc(japanese)}</span></div></div>')
        else:
            raw_hints = LIVE_HINTS[number].get(index, ()) if side == "me" else ()
            hints = hint_html(raw_hints) if raw_hints else ""
            label = english.replace("Tutor's real answer:", "Tutor's answer:")
            rendered.append(f'<div class="turn {side}">{avatar}<div class="{bubble}"><div class="answer-box tall"><span class="answer-label">{core.esc(label)}<span class="task">{core.esc(japanese)}</span></span><span class="answer-space as-input"><textarea class="free-input" data-sync-id="live-{index}" rows="2" spellcheck="false" maxlength="2000"></textarea></span>{hints}</div></div></div>')
    return core.section("p3-freetalk", "Your real answer", "自分の答え", f'<p class="section-subtitle"><span class="ko">{core.esc(LESSONS[number]["prompt"][0])}</span><span class="ja">{core.esc(LESSONS[number]["prompt"][1])}</span></p><div class="tutor-note">React naturally and follow the most interesting detail. Invite today\'s pattern only if it fits.</div><div class="dialogue">' + "".join(rendered) + "</div>")


def page_id(page):
    match = re.search(r'data-page-id="([^"]+)"', page)
    return match.group(1) if match else ""


def clarify_pattern_intro(page, number, part):
    meaning_en, meaning_ja = SPECS[number]["meanings"][part - 1]
    return page.replace(
        "First, let's practice this pattern." if part == 1 else "Next, let's practice this pattern.",
        f"{meaning_en} Please read the title aloud.",
    ).replace(
        "まず、このパターンを練習しましょう。" if part == 1 else "次に、このパターンを練習しましょう。",
        f"{meaning_ja} タイトルを声に出して読んでください。",
    )


def customize_pages(number, data, pages):
    replacements = {"words-you-know": known_page(number), "p1-translate": translate_page(number, 1, data["p1"]), "p2-translate": translate_page(number, 2, data["p2"]), "p1-write": write_page(number, 1, data["p1"]), "p2-write": write_page(number, 2, data["p2"]), "p3-freetalk": live_page(number)}
    omitted = {f"p{part}-choose" for part in data.get("omit_choice", ())}
    result = []
    for page in pages:
        pid = page_id(page)
        if pid in omitted:
            continue
        if pid == "part1-intro":
            page = clarify_pattern_intro(page, number, 1)
        elif pid == "part2-intro":
            page = clarify_pattern_intro(page, number, 2)
        if pid == "part3-intro":
            result.append(support_page(number))
            result.extend(spiral_pages(number))
        rendered = replacements.get(pid, page)
        if pid in {"p3-model", "p3-complete", "in-the-wild"}:
            variant = "wild" if pid == "in-the-wild" else "model"
            role_ja = ROLE_JA[DIALOGUES[number][variant][0]]
            rendered = rendered.replace("Please read the Me lines aloud.", "Please read your lines aloud.")
            rendered = rendered.replace("Say each complete Me line", "Say each complete line")
            rendered = rendered.replace("私は相手役をします。Me のセリフを声に出して読んでください。", f"私は{role_ja}です。自分のセリフを声に出して読んでください。")
            rendered = rendered.replace("私は相手役をします。空欄に入る言葉も含めて、自分のセリフをまるごと言ってください。", f"私は{role_ja}です。空欄に入る言葉も含めて、自分のセリフをまるごと言ってください。")
            rendered = rendered.replace("私は相手役をします。空欄に入る言葉も含めて、Me のセリフをまるごと言ってください。", f"私は{role_ja}です。空欄に入る言葉も含めて、自分のセリフをまるごと言ってください。")
        result.append(rendered)
    return result


@contextlib.contextmanager
def course_data():
    previous = (core.VOCAB, core.CANONICAL_SPECS, core.DIALOGUES, core.LIVE_SCENES)
    core.VOCAB = {n: (v["new"], v["assumed"], v["receptive"]) for n, v in VOCAB.items()}
    core.CANONICAL_SPECS, core.DIALOGUES, core.LIVE_SCENES = SPECS, DIALOGUES, LIVE_SCENES
    try:
        yield
    finally:
        core.VOCAB, core.CANONICAL_SPECS, core.DIALOGUES, core.LIVE_SCENES = previous


def build(number, data):
    source = PILOT.read_text(encoding="utf-8")
    head, foot = new_lesson.split_shell(source)
    slug = f'{number:02d}-{data["slug"]}'
    head = new_lesson.retarget(head, review_id=f"CORE-{number}", lesson_id=slug, level="B1+", title=data["title"], title_ko=data["ko"], title_ja=data["ja"], version="2026-08-20")
    with course_data():
        head = set_vocab(head.replace('content="todo"', 'content="reviewed"'), number)
        head = core.set_proofread_status(head, PROOFREAD_STATUS)
        pages = customize_pages(number, data, core.canonical_pages(number, data))
    out = TRACK / "courses" / COURSE / "lessons" / slug / "lesson.html"
    return out, new_lesson.redepth(head + "\n".join(pages) + foot, out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--lesson", type=int, action="append", choices=sorted(LESSONS))
    args = parser.parse_args()
    expected = set(range(71, 81))
    for label, values in (("lessons", LESSONS), ("semantic specs", SPECS), ("vocabulary", VOCAB), ("dialogues", DIALOGUES), ("live scenes", LIVE_SCENES)):
        if set(values) != expected:
            raise SystemExit(f"{label} do not exactly cover CORE-71--80")
    selected = set(args.lesson or LESSONS)
    for number, data in LESSONS.items():
        if number not in selected:
            continue
        out, text = build(number, data)
        if out.exists() and not args.refresh:
            raise SystemExit(f"refusing to overwrite {out.relative_to(ROOT)}")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)}")
    print(f"{len(selected)} Core decks generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

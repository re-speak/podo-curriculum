#!/usr/bin/env python3
"""Generate the explicit CORE-48--59 Experience and Ideas course batch.

The approved Core renderer owns shared markup.  This course source owns every
semantic decision that markup cannot make: examples, smallest-unit choices,
visual rules, dialogues, transfer scenes, scaffolds, and native-use tips.
"""

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
COURSE = "core-experience-and-ideas"
PILOT = TRACK / "courses/core-first-exchanges-2/lessons/20-asking-for-help/lesson.html"


def rows(*items):
    return items


LESSONS = {
    48: dict(
        slug="have-you-ever-been-to-kyoto",
        title="Have you ever been to Kyoto?",
        ko="교토에 가 본 적 있어요?",
        ja="京都に行ったことはありますか？",
        goal=("Ask about life experience and say what you have not tried yet.", "今までの経験を聞き、まだしたことがないことを話しましょう。"),
        p1=rows(
            ("{t}Have you ever{/t} been to Kyoto?", "京都に{t}行ったことはありますか{/t}？", "Have you|ever|been to|Kyoto?"),
            ("{t}Have you ever{/t} tried sushi?", "寿司を{t}食べたことはありますか{/t}？", "Have you|ever|tried|sushi?"),
            ("{t}Have you ever{/t} tried pottery?", "陶芸を{t}したことはありますか{/t}？", "Have you|ever|tried|pottery?"),
            ("{t}Have you ever{/t} stayed at a capsule hotel?", "カプセルホテルに{t}泊まったことはありますか{/t}？", "Have you|ever|stayed at|a capsule hotel?"),
        ),
        p2=rows(
            ("{t}I've never{/t} tried skiing, {t}but I'd like to{/t}.", "スキーは{t}したことがありませんが{/t}、{t}してみたいです{/t}。", "I've never|tried skiing,|but|I'd like to."),
            ("{t}I've never{/t} been to Canada, {t}but I'd like to{/t}.", "カナダには{t}行ったことがありませんが{/t}、{t}行ってみたいです{/t}。", "I've never|been to Canada,|but|I'd like to."),
            ("{t}I've never{/t} used a wheel, {t}but I'd like to{/t}.", "ろくろは{t}使ったことがありませんが{/t}、{t}使ってみたいです{/t}。", "I've never|used a wheel,|but|I'd like to."),
            ("{t}I've never{/t} stayed at a capsule hotel, {t}but I'd like to{/t}.", "カプセルホテルには{t}泊まったことがありませんが{/t}、{t}泊まってみたいです{/t}。", "I've never|stayed at a capsule hotel,|but|I'd like to."),
        ),
        # Both alternatives on Part 2 would reduce to the same never/ever
        # decision in four near-identical statements. The remaining pages
        # already retrieve the complete frame, so omit that low-value choice.
        omit_choice=(1, 2),
        rules=(
            ("Put ever before the past participle to ask about any time up to now.", "ever は過去分詞の前に置き、今までのどこかの時点での経験を聞きます。"),
            ("Put never before the past participle, then keep but I'd like to as the positive close.", "never は過去分詞の前に置き、but I'd like to を前向きな結びとして続けます。"),
        ),
        prompt=("Tell me one thing you have never tried, then ask about my experience.", "まだしたことがないことを一つ話してから、私の経験も聞いてください。"),
    ),
    49: dict(
        slug="ive-already-finished",
        title="I've already finished",
        ko="벌써 끝냈어요",
        ja="もう終わりました",
        goal=("Say what is already done and check what is still pending.", "もう終わったことを伝え、まだ確認が必要なことを聞きましょう。"),
        p1=rows(
            ("{t}I've already{/t} sent the email.", "メールは{t}もう送りました{/t}。", "I've|already|sent|the email."),
            ("{t}I've already{/t} finished the report.", "レポートは{t}もう終えました{/t}。", "I've|already|finished|the report."),
            ("{t}I've already{/t} booked the table.", "テーブルは{t}もう予約しました{/t}。", "I've|already|booked|the table."),
            ("{t}I've already{/t} paid the bill.", "請求書は{t}もう支払いました{/t}。", "I've|already|paid|the bill."),
        ),
        p2=rows(
            ("{t}Have you{/t} finished the report {t}yet{/t}?", "レポートは{t}もう{/t}終わり{t}ましたか{/t}？", "Have you|finished|the report|yet?"),
            ("{t}Have you{/t} sent the email {t}yet{/t}?", "メールは{t}もう{/t}送り{t}ましたか{/t}？", "Have you|sent|the email|yet?"),
            ("{t}Have you{/t} booked the table {t}yet{/t}?", "テーブルは{t}もう{/t}予約し{t}ましたか{/t}？", "Have you|booked|the table|yet?"),
            ("{t}Have you{/t} paid the bill {t}yet{/t}?", "請求書は{t}もう{/t}支払い{t}ましたか{/t}？", "Have you|paid|the bill|yet?"),
        ),
        omit_choice=(1,),
        rules=(
            ("Put already between have and the past participle in an affirmative update.", "肯定の進捗報告では、already を have と過去分詞の間に置きます。"),
            ("Put yet at the end of a neutral question about whether something is done.", "完了したかを普通に確認する質問では、yet を文末に置きます。"),
        ),
        prompt=("Give me one real update, then ask whether one other task is done.", "実際の進捗を一つ伝えてから、別の作業が終わったか聞いてください。"),
    ),
    50: dict(
        slug="i-went-there-last-year",
        title="I went there last year",
        ko="작년에 거기에 갔어요",
        ja="去年そこへ行きました",
        goal=("Ask about general experience, then name one finished time.", "経験をたずねてから、一度の出来事を終わった時と一緒に話しましょう。"),
        p1=rows(
            ("{t}Have you been to{/t} Kyoto?", "京都に{t}行ったことはありますか{/t}？", "Have you|been to|Kyoto?"),
            ("{t}Have you been to{/t} Canada?", "カナダに{t}行ったことはありますか{/t}？", "Have you|been to|Canada?"),
            ("{t}Have you been to{/t} this café?", "このカフェに{t}来たことはありますか{/t}？", "Have you|been to|this café?"),
            ("{t}Have you been to{/t} this museum?", "この美術館に{t}来たことはありますか{/t}？", "Have you|been to|this museum?"),
        ),
        p2=rows(
            ("{t}Yes, I went there{/t} last year.", "はい、{t}去年そこへ行きました{/t}。", "Yes,|I went|there|last year."),
            ("{t}Yes, I went there{/t} last summer.", "はい、{t}去年の夏にそこへ行きました{/t}。", "Yes,|I went|there|last summer."),
            ("{t}Yes, I went there{/t} on Friday.", "はい、{t}金曜日にそこへ行きました{/t}。", "Yes,|I went|there|on Friday."),
            ("{t}Yes, I went there{/t} two months ago.", "はい、{t}2か月前にそこへ行きました{/t}。", "Yes,|I went|there|two months ago."),
        ),
        rules=(
            ("Use have been when no finished time is named.", "終わった時を言わずに経験を聞くときは have been を使います。"),
            ("Once you name a finished time, switch to went in the simple past.", "終わった時を言ったら、単純過去の went に切り替えます。"),
        ),
        prompt=("Answer honestly; if you have not been there, say so. Then ask about one place I may know.", "正直に答え、行ったことがなければそう伝えましょう。そのあと、私が知っていそうな場所を一つ聞いてください。"),
    ),
    51: dict(
        slug="how-long-have-you-been-here",
        title="How long have you been here?",
        ko="여기에 얼마나 있었어요?",
        ja="ここにどのくらいいますか？",
        goal=("Ask how long someone has been in a place and give a duration.", "場所にどのくらいいるかをたずね、期間を答えましょう。"),
        p1=rows(
            ("{t}How long have you been in{/t} Tokyo?", "東京には{t}どのくらいいますか{/t}？", "How long|have you|been in|Tokyo?"),
            ("{t}How long have you been in{/t} Osaka?", "大阪には{t}どのくらいいますか{/t}？", "How long|have you|been in|Osaka?"),
            ("{t}How long have you been in{/t} Japan?", "日本には{t}どのくらいいますか{/t}？", "How long|have you|been in|Japan?"),
            ("{t}How long have you been in{/t} this neighborhood?", "この地域には{t}どのくらいいますか{/t}？", "How long|have you|been in|this neighborhood?"),
        ),
        p2=rows(
            ("{t}I've been here for{/t} five years.", "ここには{t}5年間います{/t}。", "I've been|here|for|five years."),
            ("{t}I've been here for{/t} three months.", "ここには{t}3か月います{/t}。", "I've been|here|for|three months."),
            ("{t}I've been here for{/t} two weeks.", "ここには{t}2週間います{/t}。", "I've been|here|for|two weeks."),
            ("{t}I've been here for{/t} a day.", "ここには{t}1日います{/t}。", "I've been|here|for|a day."),
        ),
        rules=(
            ("Keep how long at the front and use have been for a stay continuing now.", "how long を文頭に置き、今も続く滞在には have been を使います。"),
            ("Use for with a length of time and since with a starting point.", "期間の長さには for、始まった時点には since を使います。"),
        ),
        prompt=("Tell me how long you have been where you live, then ask me too.", "今住んでいる場所にどのくらいいるか答えてから、私にも聞いてください。"),
    ),
    52: dict(
        slug="ive-been-working-all-morning",
        title="I've been working all morning",
        ko="아침 내내 일하고 있어요",
        ja="午前中ずっと働いています",
        goal=("Describe an activity continuing up to now and explain its effect.", "今まで続いている活動を話し、その影響を説明しましょう。"),
        p1=rows(
            ("{t}I've been{/t} working {t}since{/t} nine.", "{t}9時から{/t}{t}ずっと働いています{/t}。", "I've been|working|since|nine."),
            ("{t}I've been{/t} studying {t}since{/t} breakfast.", "{t}朝食のあとから{/t}{t}ずっと勉強しています{/t}。", "I've been|studying|since|breakfast."),
            ("{t}I've been{/t} cleaning {t}since{/t} eight.", "{t}8時から{/t}{t}ずっと掃除しています{/t}。", "I've been|cleaning|since|eight."),
            ("{t}I've been{/t} waiting {t}since{/t} noon.", "{t}正午から{/t}{t}ずっと待っています{/t}。", "I've been|waiting|since|noon."),
        ),
        p2=rows(
            ("{t}That's why I'm{/t} exhausted.", "{t}だから疲れ切っています{/t}。", "That's why|I'm|exhausted."),
            ("{t}That's why I'm{/t} hungry.", "{t}だからおなかがすいています{/t}。", "That's why|I'm|hungry."),
            ("{t}That's why I'm{/t} tired.", "{t}だから疲れています{/t}。", "That's why|I'm|tired."),
            ("{t}That's why I'm{/t} late.", "{t}だから遅れています{/t}。", "That's why|I'm|late."),
        ),
        rules=(
            ("Build the continuing activity with have been plus the -ing form.", "今まで続く活動は have been と -ing 形で作ります。"),
            ("State the cause first, then use that's why before the effect you feel now.", "原因を先に伝え、今の結果の前に that's why を置きます。"),
        ),
        prompt=("Answer honestly; if nothing has continued for long today, say that instead.", "正直に答え、今日は長く続けていることがなければ、代わりにそう伝えましょう。"),
    ),
    53: dict(
        slug="weve-done-three-of-the-five",
        title="We've done three of the five",
        ko="다섯 개 중 세 개를 끝냈어요",
        ja="5つのうち3つ終わりました",
        goal=("Report completed work and name the next remaining task.", "終わった作業を報告し、次に残っている作業を伝えましょう。"),
        p1=rows(
            ("{t}We've finished{/t} three of the five reports.", "5本のレポートのうち3本は{t}終えました{/t}。", "We've finished|three of the five reports."),
            ("{t}We've finished{/t} two of the four forms.", "4枚のフォームのうち2枚は{t}終えました{/t}。", "We've finished|two of the four forms."),
            ("{t}We've finished{/t} four of the six rooms.", "6部屋のうち4部屋は{t}終えました{/t}。", "We've finished|four of the six rooms."),
            ("{t}We've finished{/t} two of the three boxes.", "3箱のうち2箱は{t}終えました{/t}。", "We've finished|two of the three boxes."),
        ),
        p2=rows(
            ("{t}We still need to{/t} review the budget.", "予算は{t}まだ確認する必要があります{/t}。", "We|still need to|review|the budget."),
            ("{t}We still need to{/t} send two emails.", "メールは2通{t}まだ送る必要があります{/t}。", "We|still need to|send|two emails."),
            ("{t}We still need to{/t} check two rooms.", "部屋は2つ{t}まだ確認する必要があります{/t}。", "We|still need to|check|two rooms."),
            ("{t}We still need to{/t} pack one box.", "箱は1つ{t}まだ詰める必要があります{/t}。", "We|still need to|pack|one box."),
        ),
        omit_choice=(1, 2),
        omit_reorder=(1,),
        rules=(
            ("Use have plus finished for completed work that matters to the update now.", "今の進捗に関係する完了済みの作業には have と finished を使います。"),
            ("Put still before need to when the task remains unfinished.", "作業が残っているときは、need to の前に still を置きます。"),
        ),
        prompt=("Use a real countable project if you have one; otherwise say you do not have one right now.", "数えられる実際の作業があれば使い、今なければそう伝えましょう。"),
    ),
    54: dict(
        slug="i-stayed-home-because-i-was-sick",
        title="I stayed home because I was sick",
        ko="아파서 집에 있었어요",
        ja="病気だったので家にいました",
        goal=("Explain one event from the result side and from the reason side.", "出来事を結果からも理由からも説明しましょう。"),
        p1=rows(
            ("I stayed home {t}because{/t} I was sick.", "病気だった{t}ので{/t}家にいました。", "I|stayed home|because|I was sick."),
            ("I missed the meeting {t}because{/t} my train was late.", "電車が遅れた{t}ので{/t}会議に間に合いませんでした。", "I|missed the meeting|because|my train was late."),
            ("I called a taxi {t}because{/t} it was raining.", "雨が降っていた{t}ので{/t}タクシーを呼びました。", "I|called a taxi|because|it was raining."),
            ("I moved the meeting {t}because{/t} my client was busy.", "顧客が忙しかった{t}ので{/t}会議を変更しました。", "I|moved the meeting|because|my client was busy."),
        ),
        p2=rows(
            ("I was sick, {t}so{/t} I stayed home.", "病気でした。{t}だから{/t}家にいました。", "I|was sick,|so|I stayed home."),
            ("My train was late, {t}so{/t} I called my manager.", "電車が遅れました。{t}だから{/t}上司に電話しました。", "My train|was late,|so|I called my manager."),
            ("It was raining, {t}so{/t} we met at a café.", "雨が降っていました。{t}だから{/t}カフェで会いました。", "It|was raining,|so|we met at a café."),
            ("My client was busy, {t}so{/t} we moved the meeting.", "顧客が忙しかったです。{t}だから{/t}会議を変更しました。", "My client|was busy,|so|we moved the meeting."),
        ),
        rules=(
            ("Put because before the reason: result first, reason second.", "because は理由の前に置き、結果、理由の順にします。"),
            ("Put so before the result: reason first, result second.", "so は結果の前に置き、理由、結果の順にします。"),
        ),
        prompt=("Use a real changed plan if you have one; otherwise say that none changed and ask about mine.", "実際に変わった予定があれば使い、なければ何も変わらなかったと伝えて私の予定を聞きましょう。"),
    ),
    55: dict(
        slug="shes-the-one-who-called",
        title="She's the one who called",
        ko="전화한 사람이 그분이에요",
        ja="彼女が電話をくれた人です",
        goal=("Identify a person or thing by what they did or what it does.", "人や物を、その人がしたこと・物がすることで特定しましょう。"),
        p1=rows(
            ("{t}She's the one who{/t} called earlier.", "{t}さっき電話をくれた人は彼女です{/t}。", "She's|the one|who called|earlier."),
            ("{t}He's the one who{/t} sent the email.", "{t}メールを送った人は彼です{/t}。", "He's|the one|who sent|the email."),
            ("{t}She's the one who{/t} booked the room.", "{t}部屋を予約した人は彼女です{/t}。", "She's|the one|who booked|the room."),
            ("{t}He's the one who{/t} brought the cake.", "{t}ケーキを持ってきた人は彼です{/t}。", "He's|the one|who brought|the cake."),
        ),
        p2=rows(
            ("{t}It's the thing that{/t} opens the door.", "{t}ドアを開ける物です{/t}。", "It's|the thing|that opens|the door."),
            ("{t}It's the thing that{/t} charges the phone.", "{t}携帯を充電する物です{/t}。", "It's|the thing|that charges|the phone."),
            ("{t}It's the thing that{/t} holds the tickets.", "{t}チケットを入れておく物です{/t}。", "It's|the thing|that holds|the tickets."),
            ("{t}It's the thing that{/t} plays the music.", "{t}音楽を流す物です{/t}。", "It's|the thing|that plays|the music."),
        ),
        rules=(
            ("Name the person first, then put who and the describing action after the noun.", "人を先に置き、そのあとに who と説明する動作を続けます。"),
            ("Name the thing first, then put that and what it does after the noun.", "物を先に置き、そのあとに that とその働きを続けます。"),
        ),
        prompt=("Describe one real person and one object without saying their names first.", "名前を先に言わずに、実在する人と物を一つずつ説明してください。"),
    ),
    56: dict(
        slug="i-like-it-but-its-expensive",
        title="I like it, but it's expensive",
        ko="좋긴 한데 비싸요",
        ja="気に入っていますが、高いです",
        goal=("Acknowledge a good point while adding a real limitation.", "よい点を認めながら、実際の問題点も加えましょう。"),
        p1=rows(
            ("{t}I like{/t} the place, {t}but{/t} it's expensive.", "その場所は{t}気に入っています{/t}{t}が{/t}、高いです。", "I like|the place,|but|it's expensive."),
            ("{t}I like{/t} the room, {t}but{/t} it's small.", "その部屋は{t}気に入っています{/t}{t}が{/t}、小さいです。", "I like|the room,|but|it's small."),
            ("{t}I like{/t} the café, {t}but{/t} it's crowded.", "そのカフェは{t}気に入っています{/t}{t}が{/t}、混んでいます。", "I like|the café,|but|it's crowded."),
            ("{t}I like{/t} the job, {t}but{/t} it's stressful.", "その仕事は{t}気に入っています{/t}{t}が{/t}、ストレスが多いです。", "I like|the job,|but|it's stressful."),
        ),
        p2=rows(
            ("{t}Even though{/t} it's small, it's comfortable.", "小さい{t}のに{/t}、快適です。", "Even though|it's small,|it's comfortable."),
            ("{t}Even though{/t} it's expensive, it's convenient.", "高い{t}のに{/t}、便利です。", "Even though|it's expensive,|it's convenient."),
            ("{t}Even though{/t} it's crowded, it's quiet upstairs.", "混んでいる{t}のに{/t}、2階は静かです。", "Even though|it's crowded,|it's quiet upstairs."),
            ("{t}Even though{/t} it's old, it's reliable.", "古い{t}のに{/t}、信頼できます。", "Even though|it's old,|it's reliable."),
        ),
        rules=(
            ("Use but between two equal statements when the second limits the first.", "二つの対等な文の間に but を置き、後半で前半に制限を加えます。"),
            ("Put even though before the background fact, then give the surprising main point.", "背景になる事実の前に even though を置き、そのあとに意外な要点を伝えます。"),
        ),
        prompt=("Describe one real option with a good point and a limitation, then ask mine.", "実際の選択肢についてよい点と問題点を話してから、私の意見も聞いてください。"),
    ),
    57: dict(
        slug="if-it-rains-ill-stay-in",
        title="If it rains, I'll stay in",
        ko="비가 오면 집에 있을게요",
        ja="雨が降ったら、家にいます",
        goal=("State a realistic condition and ask for another person's plan.", "現実的な条件と自分の予定を伝え、相手の予定も聞きましょう。"),
        p1=rows(
            ("{t}If{/t} it rains, {t}I'll{/t} stay in.", "{t}雨が降ったら{/t}、{t}家にいます{/t}。", "If|it rains,|I'll|stay in."),
            ("{t}If{/t} the train's late, {t}I'll{/t} take a taxi.", "{t}電車が遅れたら{/t}、{t}タクシーに乗ります{/t}。", "If|the train's late,|I'll|take a taxi."),
            ("{t}If{/t} the café's full, {t}I'll{/t} wait outside.", "{t}カフェが満席なら{/t}、{t}外で待ちます{/t}。", "If|the café's full,|I'll|wait outside."),
            ("{t}If{/t} Mina comes, {t}I'll{/t} make dinner.", "{t}ミナが来たら{/t}、{t}夕食を作ります{/t}。", "If|Mina comes,|I'll|make dinner."),
        ),
        p2=rows(
            ("{t}What will you do if{/t} the train's late?", "電車が遅れたら{t}どうしますか{/t}？", "What|will you do|if|the train's late?"),
            ("{t}What will you do if{/t} it rains?", "雨が降ったら{t}どうしますか{/t}？", "What|will you do|if|it rains?"),
            ("{t}What will you do if{/t} the café's full?", "カフェが満席なら{t}どうしますか{/t}？", "What|will you do|if|the café's full?"),
            ("{t}What will you do if{/t} Mina can't come?", "ミナが来られなかったら{t}どうしますか{/t}？", "What|will you do|if|Mina can't come?"),
        ),
        omit_choice=(2,),
        rules=(
            ("Use the present form after if, then put will in the result clause.", "if のあとは現在形にし、結果の節に will を置きます。"),
            ("Keep will in the question, but still use the present form after if.", "質問には will を残しますが、if のあとはやはり現在形にします。"),
        ),
        prompt=("Give a real plan if you have one; otherwise say you have not decided yet, then ask about mine.", "実際の予定があれば話し、まだ決めていなければそう伝えてから私の予定を聞きましょう。"),
    ),
    58: dict(
        slug="ill-call-you-when-i-get-there",
        title="I'll call you when I get there",
        ko="도착하면 전화할게요",
        ja="着いたら電話します",
        goal=("Say when an action will happen and what condition would stop it.", "行動する時を伝え、それを止める条件も話しましょう。"),
        p1=rows(
            ("{t}I'll{/t} call you {t}when{/t} I get there.", "{t}着いたら{/t}{t}電話します{/t}。", "I'll|call you|when|I get there."),
            ("{t}I'll{/t} text you {t}when{/t} I leave work.", "{t}仕事を出たら{/t}{t}メッセージします{/t}。", "I'll|text you|when|I leave work."),
            ("{t}I'll{/t} email you {t}when{/t} I finish the report.", "{t}レポートを終えたら{/t}{t}メールします{/t}。", "I'll|email you|when|I finish the report."),
            ("{t}I'll{/t} tell you {t}when{/t} I know more.", "{t}もっと分かったら{/t}{t}伝えます{/t}。", "I'll|tell you|when|I know more."),
        ),
        p2=rows(
            ("{t}Unless{/t} it rains, {t}I'll{/t} walk.", "雨が降らない{t}かぎり{/t}、{t}歩きます{/t}。", "Unless|it rains,|I'll|walk."),
            ("{t}Unless{/t} the train's late, {t}I'll{/t} be there by nine.", "電車が遅れない{t}かぎり{/t}、{t}9時までに着きます{/t}。", "Unless|the train's late,|I'll|be there by nine."),
            ("{t}Unless{/t} the meeting runs late, {t}I'll{/t} call at six.", "会議が長引かない{t}かぎり{/t}、{t}6時に電話します{/t}。", "Unless|the meeting runs late,|I'll|call at six."),
            ("{t}Unless{/t} the soil is wet, {t}I'll{/t} water the plants.", "土が湿っていない{t}かぎり{/t}、{t}植物に水をやります{/t}。", "Unless|the soil is wet,|I'll|water the plants."),
        ),
        rules=(
            ("Use the present form after when even though the main action is in the future.", "未来の話でも、when のあとは現在形を使います。"),
            ("Unless means if not; use a positive present form after it.", "unless は if not の意味で、そのあとは肯定の現在形を使います。"),
        ),
        prompt=("Use a real contact plan if you have one; otherwise say you have none, then ask about mine.", "実際の連絡予定があれば使い、なければ予定がないと伝えてから私の予定を聞きましょう。"),
    ),
    59: dict(
        slug="i-went-there-to-see-a-client",
        title="I went there to see a client",
        ko="고객을 만나러 거기에 갔어요",
        ja="顧客に会うためにそこへ行きました",
        goal=("Explain the purpose of a trip and recommend the best method.", "出かけた目的を説明し、一番よい方法を勧めましょう。"),
        p1=rows(
            ("{t}I went there to{/t} see a client.", "顧客に会うために{t}そこへ行きました{/t}。", "I went there|to|see|a client."),
            ("{t}I went there to{/t} sign the contract.", "契約書に署名するために{t}そこへ行きました{/t}。", "I went there|to|sign|the contract."),
            ("{t}I went there to{/t} use the printer.", "プリンターを使うために{t}そこへ行きました{/t}。", "I went there|to|use|the printer."),
            ("{t}I went there to{/t} pick up the tickets.", "チケットを受け取るために{t}そこへ行きました{/t}。", "I went there|to|pick up|the tickets."),
        ),
        p2=rows(
            ("{t}The best way to{/t} get there {t}is to{/t} take the bus.", "そこへ行く{t}一番よい方法は{/t}バスに乗る{t}ことです{/t}。", "The best way|to get there|is to|take the bus."),
            ("{t}The best way to{/t} save time {t}is to{/t} book online.", "時間を節約する{t}一番よい方法は{/t}オンラインで予約する{t}ことです{/t}。", "The best way|to save time|is to|book online."),
            ("{t}The best way to{/t} learn the route {t}is to{/t} walk it.", "道順を覚える{t}一番よい方法は{/t}歩いてみる{t}ことです{/t}。", "The best way|to learn the route|is to|walk it."),
            ("{t}The best way to{/t} avoid waiting {t}is to{/t} book a computer online.", "待ち時間を避ける{t}一番よい方法は{/t}パソコンをオンライン予約する{t}ことです{/t}。", "The best way|to avoid waiting|is to|book a computer online."),
        ),
        rules=(
            ("Use to plus the plain verb to answer why you went somewhere.", "出かけた目的を答えるときは、to のあとに動詞の原形を置きます。"),
            ("Keep the best way to and is to as the two anchors around the goal and method.", "目的と方法をはさむ二つの軸として、the best way to と is to を保ちます。"),
        ),
        prompt=("If you went somewhere for a reason, say why; otherwise say you did not, then ask me for one best method.", "目的があって出かけたなら理由を話し、なければ出かけていないと伝えてから、一番よい方法を私に聞きましょう。"),
    ),
}


def semantic_spec(meanings, writes, choices, rules, tip):
    return dict(meanings=meanings, writes=writes, choices=choices, rules=rules, tip=tip)


SPECS = {
    48: semantic_spec(
        (
            ("Use this to ask whether something has happened at any time in someone's life.", "今までの人生のどこかで経験したことがあるか聞くときに使います。"),
            ("Use this to name an experience you do not have while keeping the possibility open.", "まだ経験がないことを、今後してみたい気持ちと一緒に伝えるときに使います。"),
        ),
        (
            ("Ask one real Have you ever question.", "実際に聞きたい Have you ever の質問を一つ作りましょう。"),
            ("Name one thing you have never done but would like to try.", "まだしたことはないけれど、してみたいことを一つ話しましょう。"),
        ),
        (
            (),
            (
                ("スキーは{t}したことがありません{/t}。", "I've ", "never", "ever", " tried skiing, but I'd like to."),
                ("カナダには{t}行ったことがありません{/t}。", "I've ", "never", "ever", " been to Canada, but I'd like to."),
                ("ろくろは{t}使ったことがありません{/t}。", "I've ", "never", "ever", " used a wheel, but I'd like to."),
                ("カプセルホテルには{t}泊まったことがありません{/t}。", "I've ", "never", "ever", " stayed at a capsule hotel, but I'd like to."),
            ),
        ),
        (
            ("Ask about life experience", "人生の経験を聞く", "Have + 人 + <b>ever</b> + 過去分詞?", "No finished time", "終わった時を言わない", ("Have you <b>ever been</b> to Kyoto?", "Have you <b>ever tried</b> pottery?")),
            ("Keep the door open", "今後の可能性を残す", "I've + <b>never</b> + 過去分詞, + <b>but I'd like to</b>", "No experience yet", "まだ経験がない", ("I've <b>never tried it</b>, <b>but I'd like to</b>.", "I've <b>never used</b> a wheel, <b>but I'd like to</b>.")),
        ),
        ("Ever or before?", "ever と before", "Use “ever” for broad life experience. Use “before” when the earlier experience matters to the situation now.", "幅広く人生経験を聞くなら「ever」を使います。今の状況に関係する過去の経験を聞くなら「before」を使います。", ("Life experience", "幅広い人生経験", "Have you ever tried pottery?", "陶芸をしたことはありますか？"), ("Relevant previous experience", "今に関係する過去の経験", "Have you used a wheel before?", "以前、ろくろを使ったことはありますか？")),
    ),
    49: semantic_spec(
        (
            ("Use this to report a task completed sooner than someone might expect.", "予想より早く作業が終わったと伝えるときに使います。"),
            ("Use this to check neutrally whether an expected task is complete.", "終わる予定の作業が完了したか普通に確認するときに使います。"),
        ),
        (
            ("Give one true update with already.", "already を使って本当の進捗を一つ伝えましょう。"),
            ("Ask one real question with yet.", "yet を使って実際に確認したいことを一つ聞きましょう。"),
        ),
        (
            tuple((jp, "I've ", "already", "yet", suffix) for jp, suffix in (
                ("メールは{t}もう{/t}送りました。", " sent the email."),
                ("レポートは{t}もう{/t}終えました。", " finished the report."),
                ("テーブルは{t}もう{/t}予約しました。", " booked the table."),
                ("請求書は{t}もう{/t}支払いました。", " paid the bill."),
            )),
            (
                ("{t}普通に完了を確認{/t}します。", "Have you finished the report ", "yet", "already", "?"),
                ("{t}予想より早くて驚いて{/t}います。", "Have you finished the report ", "already", "yet", "?"),
                ("{t}普通に完了を確認{/t}します。", "Have you booked the table ", "yet", "already", "?"),
                ("{t}予想より早くて驚いて{/t}います。", "Have you booked the table ", "already", "yet", "?"),
            ),
        ),
        (
            ("Place already inside the verb", "already を動詞の中に置く", "I + have + <b>already</b> + 過去分詞", "Completed sooner than expected", "予想より早く完了", ("I've <b>already sent it</b>.", "I've <b>already paid</b> the bill.")),
            ("Put yet at the end", "yet は文末に", "Have + 人 + 過去分詞 + <b>yet</b>?", "Neutral completion check", "普通の完了確認", ("Have you <b>finished yet</b>?", "Have you paid the bill <b>yet</b>?")),
        ),
        ("I've finished or I'm done?", "I've finished と I'm done", "“I've finished” is a neutral progress update. “I'm done” is shorter and more conversational.", "「I've finished」は中立的な進捗報告です。「I'm done」は短く、より会話的です。", ("Neutral update", "中立的な報告", "I've finished the report.", "レポートを終えました。"), ("Conversational", "会話的", "I'm done with the report.", "レポートは終わりました。")),
    ),
    50: semantic_spec(
        (
            ("Use this to ask about an experience without naming a finished time.", "終わった時を言わずに、場所を訪れた経験を聞くときに使います。"),
            ("Use this to answer with one specific visit and a finished time.", "一度の訪問を、終わった時と一緒に答えるときに使います。"),
        ),
        (
            ("Ask whether I have been to one place.", "私が場所を訪れたことがあるか一つ聞きましょう。"),
            ("If you have visited a place, say when; otherwise write “I haven't been there.”", "場所を訪れたことがあれば時を言い、なければ「I haven't been there.」と書きましょう。"),
        ),
        (
            tuple((jp, "", "Have you been", "Did you go", suffix) for jp, suffix in (
                ("{t}今までのどこかで{/t}京都に行ったことはありますか？", " to Kyoto?"),
                ("{t}今までのどこかで{/t}カナダに行ったことはありますか？", " to Canada?"),
                ("{t}今までのどこかで{/t}このカフェに来たことはありますか？", " to this café?"),
                ("{t}今までのどこかで{/t}この美術館に来たことはありますか？", " to this museum?"),
            )),
            tuple((jp, "Yes, I ", "went", "have been", suffix) for jp, suffix in (
                ("{t}去年{/t}そこへ行きました。", " there last year."),
                ("{t}去年の夏{/t}そこへ行きました。", " there last summer."),
                ("{t}金曜日{/t}そこへ行きました。", " there on Friday."),
                ("{t}2か月前{/t}そこへ行きました。", " there two months ago."),
            )),
        ),
        (
            ("Experience with no date", "日付のない経験", "Have + 人 + <b>been to</b> + 場所?", "Any time up to now", "今までのどこか", ("Have you <b>been to</b> Kyoto?", "Have you <b>been to</b> this museum?")),
            ("Finished time means simple past", "終わった時なら単純過去", "I + <b>went there</b> + 終わった時", "One finished occasion", "一度の終わった出来事", ("I <b>went there last year</b>.", "I <b>went there on Friday</b>.")),
        ),
        ("In 2022 or back in 2022?", "in 2022 と back in 2022", "Use “in 2022” neutrally. Add “back” when you are looking back on a time that feels distant.", "中立的に年を言うなら「in 2022」を使います。遠く感じる時を振り返るなら「back」を加えます。", ("Neutral date", "中立的な年", "I went there in 2022.", "2022年にそこへ行きました。"), ("Looking back", "昔を振り返る", "I went there back in 2022.", "振り返ると、2022年にそこへ行きました。")),
    ),
    51: semantic_spec(
        (
            ("Use this to ask about a stay that began before now and is still continuing.", "前に始まり、今も続いている滞在の長さを聞くときに使います。"),
            ("Use this to give the length of that continuing stay.", "今も続いている滞在の期間を答えるときに使います。"),
        ),
        (
            ("Ask how long I have been in one place.", "私が場所にどのくらいいるか聞きましょう。"),
            ("Say how long you have been where you live now.", "今住んでいる場所にどのくらいいるか話しましょう。"),
        ),
        (
            tuple((jp, "How long have you been ", "in", "for", suffix) for jp, suffix in (
                ("{t}東京に{/t}どのくらいいますか？", " Tokyo?"),
                ("{t}大阪に{/t}どのくらいいますか？", " Osaka?"),
                ("{t}日本に{/t}どのくらいいますか？", " Japan?"),
                ("{t}この地域に{/t}どのくらいいますか？", " this neighborhood?"),
            )),
            (
                ("ここには{t}5年間{/t}います。", "I've been here ", "for", "since", " five years."),
                ("ここには{t}2021年から{/t}います。", "I've been here ", "since", "for", " 2021."),
                ("ここには{t}2週間{/t}います。", "I've been here ", "for", "since", " two weeks."),
                ("ここには{t}月曜日から{/t}います。", "I've been here ", "since", "for", " Monday."),
            ),
        ),
        (
            ("Ask about a continuing stay", "今も続く滞在を聞く", "How long + have + 人 + <b>been in</b> + 場所?", "Started before, true now", "前に始まり、今も続く", ("How long have you <b>been in</b> Tokyo?", "How long have you <b>been in</b> Japan?")),
            ("Length or starting point", "期間・開始時点", "<b>for</b> + 期間 / <b>since</b> + 開始時点", "Choose by the time phrase", "時間表現で選ぶ", ("for <b>five years</b>", "since <b>2021</b>")),
        ),
        ("Exact or approximate?", "正確・おおよそ", "Use “for five years” for an exact length. Add “about” when the number is approximate.", "正確な期間なら「for five years」を使います。おおよそなら「about」を加えます。", ("Exact length", "正確な期間", "I've been here for five years.", "ここに5年間います。"), ("Approximate length", "おおよその期間", "I've been here for about five years.", "ここに5年ほどいます。")),
    ),
    52: semantic_spec(
        (
            ("Use this when the continuing activity itself explains the situation now.", "今の状況を説明するうえで、続いている活動そのものが大事なときに使います。"),
            ("Use this after the cause to name the effect you can see or feel now.", "原因を話したあと、今見える・感じる結果を伝えるときに使います。"),
        ),
        (
            ("If something has continued today, say what and since when; otherwise say “Nothing for long today.”", "今日ずっと続けていることがあれば内容と開始時点を言い、なければ「Nothing for long today.」と伝えましょう。"),
            ("Add a true effect with That's why, or say that there is no effect to report.", "That's why で本当の結果を加えるか、伝える結果がないと言いましょう。"),
        ),
        (
            (
                ("9時から{t}ずっと働いています{/t}。", "I've ", "been working", "worked", " since nine."),
                ("朝食のあとから{t}ずっと勉強しています{/t}。", "I've ", "been studying", "studied", " since breakfast."),
                ("8時から{t}ずっと掃除しています{/t}。", "I've ", "been cleaning", "cleaned", " since eight."),
                ("正午から{t}ずっと待っています{/t}。", "I've ", "been waiting", "waited", " since noon."),
            ),
            (
                ("だから私は{t}疲れ切っています{/t}。", "That's why I'm ", "exhausted", "exhausting", "."),
                ("だから私は{t}疲れています{/t}。", "That's why I'm ", "tired", "tiring", "."),
                ("だから私は{t}退屈しています{/t}。", "That's why I'm ", "bored", "boring", "."),
                ("だから私は{t}わくわくしています{/t}。", "That's why I'm ", "excited", "exciting", "."),
            ),
        ),
        (
            ("Build the continuing activity", "続いている活動を作る", "have + <b>been</b> + 動詞<b>-ing</b> + since + 開始時点", "Activity up to now", "今まで続く活動", ("I've <b>been working</b> since nine.", "I've <b>been waiting</b> since noon.")),
            ("Connect cause to present effect", "原因を今の結果につなぐ", "原因. + <b>That's why</b> + 今の結果", "Effect now", "今の結果", ("I've been working since nine. <b>That's why</b> I'm exhausted.", "I've been waiting since noon. <b>That's why</b> I'm hungry.")),
        ),
        ("Tired or exhausted?", "tired と exhausted", "“Tired” is neutral. “Exhausted” means very tired and adds much more intensity.", "「tired」は中立的です。「exhausted」はとても疲れているという強い言い方です。", ("Neutral", "中立的", "I'm tired.", "疲れています。"), ("Much stronger", "かなり強い", "I'm exhausted.", "疲れ切っています。")),
    ),
    53: semantic_spec(
        (
            ("Use this to give a completed number as part of a progress update.", "進捗報告で、終わった数を全体の数と一緒に伝えるときに使います。"),
            ("Use this to name the task that remains after the completed work.", "終わった作業のあと、残っている作業を伝えるときに使います。"),
        ),
        (
            ("Use a real completed number if you have a countable project; otherwise say you do not have one now.", "数えられる作業があれば実際の完了数を使い、なければ今はないと伝えましょう。"),
            ("Name a real remaining task, or say that nothing remains.", "実際の残作業を一つ言うか、何も残っていないと伝えましょう。"),
        ),
        (
            tuple((jp, "We've ", "finished", "finish", suffix) for jp, suffix in (
                ("5本のレポートのうち3本は{t}終えました{/t}。", " three of the five reports."),
                ("4枚のフォームのうち2枚は{t}終えました{/t}。", " two of the four forms."),
                ("6部屋のうち4部屋は{t}終えました{/t}。", " four of the six rooms."),
                ("3箱のうち2箱は{t}終えました{/t}。", " two of the three boxes."),
            )),
            (
                ("予算は{t}まだ確認する必要があります{/t}。", "We ", "still need to review", "have already reviewed", " the budget."),
                ("メールは2通{t}まだ送る必要があります{/t}。", "We ", "still need to send", "have already sent", " two emails."),
                ("部屋は2つ{t}まだ確認する必要があります{/t}。", "We ", "still need to check", "have already checked", " two rooms."),
                ("箱は1つ{t}まだ詰める必要があります{/t}。", "We ", "still need to pack", "have already packed", " one box."),
            ),
        ),
        (
            ("Report completed work", "完了済みの作業を報告", "We + have + <b>finished</b> + 完了数 + of + 全体", "Present progress", "今の進捗", ("We've <b>finished three of the five</b>.", "We've <b>finished two of the four</b> forms.")),
            ("Keep still before need to", "still は need to の前", "We + <b>still need to</b> + 動詞", "Task remains", "作業が残っている", ("We <b>still need to</b> review the budget.", "We <b>still need to</b> pack one box.")),
        ),
        ("Need to or have to?", "need to と have to", "“Still need to” focuses on work remaining. “Still have to” can sound more like an obligation.", "「still need to」は残っている作業に焦点を当てます。「still have to」は義務の響きが強くなることがあります。", ("Remaining work", "残作業", "We still need to review the budget.", "予算はまだ確認する必要があります。"), ("Obligation", "義務を強調", "We still have to review the budget.", "予算はまだ確認しなければなりません。")),
    ),
    54: semantic_spec(
        (
            ("Use because after a result when you want to add its reason.", "結果を話したあと、その理由を加えるときに because を使います。"),
            ("Use so after a reason when you want to add its result.", "理由を話したあと、その結果を加えるときに so を使います。"),
        ),
        (
            ("Explain a real changed plan with because, or say that none changed.", "実際に変わった予定を because で説明するか、何も変わらなかったと伝えましょう。"),
            ("If you gave a cause and result, restate them with so; otherwise ask about mine.", "原因と結果を話したら so で言い直し、なければ私の予定を聞きましょう。"),
        ),
        (
            tuple((jp, prefix, "because", "so", suffix) for jp, prefix, suffix in (
                ("家にいたのは{t}病気だったから{/t}です。", "I stayed home ", " I was sick."),
                ("会議に遅れたのは{t}電車が遅れたから{/t}です。", "I missed the meeting ", " my train was late."),
                ("タクシーを呼んだのは{t}雨が降っていたから{/t}です。", "I called a taxi ", " it was raining."),
                ("会議を変更したのは{t}顧客が忙しかったから{/t}です。", "I moved the meeting ", " my client was busy."),
            )),
            tuple((jp, prefix, "so", "because", suffix) for jp, prefix, suffix in (
                ("病気でした。{t}だから{/t}家にいました。", "I was sick, ", " I stayed home."),
                ("電車が遅れました。{t}だから{/t}上司に電話しました。", "My train was late, ", " I called my manager."),
                ("雨が降っていました。{t}だから{/t}カフェで会いました。", "It was raining, ", " we met at a café."),
                ("顧客が忙しかったです。{t}だから{/t}会議を変更しました。", "My client was busy, ", " we moved the meeting."),
            )),
        ),
        (
            ("Result, then reason", "結果、そして理由", "結果 + <b>because</b> + 理由", "Explain why", "なぜかを説明", ("I stayed home <b>because I was sick</b>.", "I called a taxi <b>because it was raining</b>.")),
            ("Reason, then result", "理由、そして結果", "理由 + <b>so</b> + 結果", "Explain what happened", "何が起きたかを説明", ("I was sick, <b>so I stayed home</b>.", "It was raining, <b>so I called a taxi</b>.")),
        ),
        ("A direct reason or a softer start?", "直接の理由・やわらかい前置き", "Give the reason directly with “because.” Use “The thing is” before a sensitive explanation to soften the start.", "理由を直接言うなら「because」を使い、言いにくい説明の前には「The thing is」で始めると入り方がやわらかくなります。", ("Direct reason", "直接説明", "I left because I was sick.", "病気だったので帰りました。"), ("Softer opening", "やわらかい前置き", "The thing is, I was sick.", "実は、病気だったんです。")),
    ),
    55: semantic_spec(
        (
            ("Use this to identify a person by an action that distinguishes them.", "人を、その人を見分けられる動作で特定するときに使います。"),
            ("Use this to identify an object by what it does.", "物を、その働きで特定するときに使います。"),
        ),
        (
            ("Identify one real person with the one who.", "the one who を使って実在する人を一人特定しましょう。"),
            ("Describe one object with the thing that.", "the thing that を使って物を一つ説明しましょう。"),
        ),
        (
            tuple((jp, prefix, "who", "where", suffix) for jp, prefix, suffix in (
                ("{t}さっき電話をくれた人{/t}は彼女です。", "She's the one ", " called earlier."),
                ("{t}メールを送った人{/t}は彼です。", "He's the one ", " sent the email."),
                ("{t}部屋を予約した人{/t}は彼女です。", "She's the one ", " booked the room."),
                ("{t}ケーキを持ってきた人{/t}は彼です。", "He's the one ", " brought the cake."),
            )),
            tuple((jp, prefix, "that", "where", suffix) for jp, prefix, suffix in (
                ("{t}ドアを開ける物{/t}です。", "It's the thing ", " opens the door."),
                ("{t}携帯を充電する物{/t}です。", "It's the thing ", " charges the phone."),
                ("{t}チケットを入れておく物{/t}です。", "It's the thing ", " holds the tickets."),
                ("{t}音楽を流す物{/t}です。", "It's the thing ", " plays the music."),
            )),
        ),
        (
            ("Person first, description after", "人を先に、説明は後ろに", "the person + <b>who</b> + 動作", "Identify a person", "人を特定", ("the one <b>who called</b>", "the one <b>who sent the email</b>")),
            ("Thing first, function after", "物を先に、働きは後ろに", "the thing + <b>that</b> + 働き", "Identify an object", "物を特定", ("the thing <b>that opens the door</b>", "the thing <b>that charges the phone</b>")),
        ),
        ("The one or the person?", "the one と the person", "“The one who” is compact and conversational. “The person who” is more explicit when the listener needs clarity.", "「the one who」は短く会話的です。「the person who」は、相手に明確さが必要なときによりはっきり伝わります。", ("Conversational", "会話的", "She's the one who called.", "電話をくれたのは彼女です。"), ("More explicit", "より明確", "She's the person who called.", "電話をくれた人は彼女です。")),
    ),
    56: semantic_spec(
        (
            ("Use this to add a limitation after saying what you like.", "気に入っている点を言ったあと、問題点を加えるときに使います。"),
            ("Use this to background one fact before a surprising positive point.", "一つの事実を背景にして、意外なよい点を伝えるときに使います。"),
        ),
        (
            ("Describe one option you like and add its limitation.", "気に入っている選択肢と、その問題点を話しましょう。"),
            ("Give one true contrast with even though.", "even though を使って本当の対比を一つ話しましょう。"),
        ),
        (
            tuple((jp, prefix, "but", "because", suffix) for jp, prefix, suffix in (
                ("場所は気に入っています。{t}ただ{/t}、高いです。", "I like the place, ", " it's expensive."),
                ("部屋は気に入っています。{t}ただ{/t}、小さいです。", "I like the room, ", " it's small."),
                ("カフェは気に入っています。{t}ただ{/t}、混んでいます。", "I like the café, ", " it's crowded."),
                ("仕事は気に入っています。{t}ただ{/t}、ストレスが多いです。", "I like the job, ", " it's stressful."),
            )),
            tuple((jp, "", "Even though", "Because", suffix) for jp, suffix in (
                ("{t}小さいのに{/t}、快適です。", " it's small, it's comfortable."),
                ("{t}高いのに{/t}、便利です。", " it's expensive, it's convenient."),
                ("{t}混んでいるのに{/t}、2階は静かです。", " it's crowded, it's quiet upstairs."),
                ("{t}古いのに{/t}、信頼できます。", " it's old, it's reliable."),
            )),
        ),
        (
            ("Add an equal limitation", "対等な問題点を加える", "よい点 + <b>but</b> + 問題点", "Two equal statements", "二つの対等な文", ("I like the place, <b>but</b> it's expensive.", "I like the room, <b>but</b> it's small.")),
            ("Background the first fact", "最初の事実を背景に", "<b>Even though</b> + 背景, + 意外な要点", "Main point comes second", "要点は後ろ", ("<b>Even though</b> it's small, it's comfortable.", "<b>Even though</b> it's old, it's reliable.")),
        ),
        ("But or sentence-final though?", "but と文末の though", "Use “but” to connect the contrast directly. In relaxed speech, put “though” at the end to add the limitation afterward.", "対比を直接つなぐなら「but」を使います。くだけた会話では「though」を文末に置いて、あとから問題点を加えられます。", ("Direct connection", "直接つなぐ", "I like it, but it's expensive.", "気に入っていますが、高いです。"), ("Relaxed afterthought", "会話的な付け足し", "It's expensive, though.", "ただ、高いんですよね。")),
    ),
    57: semantic_spec(
        (
            ("Use this to state what you will do under one realistic condition.", "一つの現実的な条件で何をするか伝えるときに使います。"),
            ("Use this to ask for the other person's plan under a condition.", "条件が起きた場合の相手の予定を聞くときに使います。"),
        ),
        (
            ("Give one real if plan, or say you have not decided yet.", "if を使って実際の予定を一つ話すか、まだ決めていないと伝えましょう。"),
            ("Ask what I will do under that condition.", "その条件なら私がどうするか聞きましょう。"),
        ),
        (
            (
                ("{t}雨が降ったら{/t}、家にいます。", "If it ", "rains", "will rain", ", I'll stay in."),
                ("{t}電車が遅れたら{/t}、タクシーに乗ります。", "If the train ", "is", "will be", " late, I'll take a taxi."),
                ("{t}カフェが満席なら{/t}、外で待ちます。", "If the café ", "is", "will be", " full, I'll wait outside."),
                ("{t}ミナが来たら{/t}、夕食を作ります。", "If Mina ", "comes", "will come", ", I'll make dinner."),
            ),
            (
                ("電車が{t}遅れたら{/t}どうしますか？", "What will you do if the train ", "is", "will be", " late?"),
                ("{t}雨が降ったら{/t}どうしますか？", "What will you do if it ", "rains", "will rain", "?"),
                ("カフェが{t}満席なら{/t}どうしますか？", "What will you do if the café ", "is", "will be", " full?"),
                ("ミナが{t}来られなかったら{/t}どうしますか？", "What will you do if Mina ", "can't come", "won't be able to come", "?"),
            ),
        ),
        (
            ("Present after if, will in the result", "if のあとは現在形、結果に will", "If + 現在形, + 人 + <b>will</b> + 動詞", "Real future condition", "現実的な未来条件", ("If it <b>rains</b>, I'll stay in.", "If Mina <b>comes</b>, I'll make dinner.")),
            ("Ask with will, keep if present", "質問に will、if 節は現在形", "What + <b>will</b> + 人 + do + if + 現在形?", "Ask for the plan", "予定を聞く", ("What <b>will</b> you do if the train <b>is</b> late?", "What <b>will</b> you do if it <b>rains</b>?")),
        ),
        ("If or in case?", "if と in case", "Use “if” for the action after the condition happens. Use “in case” for preparation before it might happen.", "条件が起きたあとの行動には「if」を使います。起きるかもしれないことへの事前準備には「in case」を使います。", ("React afterward", "起きたあとに対応", "I'll take a taxi if the train is late.", "電車が遅れたらタクシーに乗ります。"), ("Prepare beforehand", "事前に備える", "I'll leave early in case the train is late.", "電車が遅れるかもしれないので早く出ます。")),
    ),
    58: semantic_spec(
        (
            ("Use this to say that one future action will follow another event.", "一つの出来事のあとに未来の行動をすると伝えるときに使います。"),
            ("Use this to state the only condition that would stop your plan.", "予定を止める唯一の条件を伝えるときに使います。"),
        ),
        (
            ("Say when you will contact someone, or say you have no contact plan.", "いつ誰かに連絡するか話すか、連絡予定がないと伝えましょう。"),
            ("Add a real unless condition if one applies; otherwise say there is no stopping condition.", "当てはまる条件があれば unless で加え、なければ止める条件はないと伝えましょう。"),
        ),
        (
            (
                ("{t}着いたら{/t}電話します。", "I'll call you when I ", "get", "will get", " there."),
                ("{t}仕事を出たら{/t}メッセージします。", "I'll text you when I ", "leave", "will leave", " work."),
                ("{t}レポートを終えたら{/t}メールします。", "I'll email you when I ", "finish", "will finish", " the report."),
                ("{t}もっと分かったら{/t}伝えます。", "I'll tell you when I ", "know", "will know", " more."),
            ),
            tuple((jp, "", "Unless", "If", suffix) for jp, suffix in (
                ("{t}雨が降らないかぎり{/t}、歩きます。", " it rains, I'll walk."),
                ("{t}電車が遅れないかぎり{/t}、9時までに着きます。", " the train's late, I'll be there by nine."),
                ("{t}会議が長引かないかぎり{/t}、6時に電話します。", " the meeting runs late, I'll call at six."),
                ("{t}土が湿っていないかぎり{/t}、植物に水をやります。", " the soil is wet, I'll water the plants."),
            )),
        ),
        (
            ("Present after when", "when のあとは現在形", "未来の文 + <b>when</b> + 現在形", "One event triggers another", "一つの出来事が次を起こす", ("I'll call you when I <b>get</b> there.", "I'll email you when I <b>finish</b>.")),
            ("Unless equals if not", "unless は if not", "<b>Unless</b> + 肯定形 = if + 否定形", "Only stopping condition", "唯一の中止条件", ("<b>Unless it rains</b>, I'll walk.", "<b>Unless the train's late</b>, I'll be there by nine.")),
        ),
        ("When or as soon as?", "when と as soon as", "“When” gives the time. “As soon as” adds that you will act immediately.", "「when」は時を伝えます。「as soon as」は、すぐ行動することまで加えます。", ("Time only", "時を伝える", "I'll call when I get there.", "着いたら電話します。"), ("Immediately", "すぐに行動", "I'll call as soon as I get there.", "着いたらすぐ電話します。")),
    ),
    59: semantic_spec(
        (
            ("Use this to explain the purpose of going somewhere.", "どこかへ行った目的を説明するときに使います。"),
            ("Use this to recommend the method that best achieves a goal.", "目的を達成する一番よい方法を勧めるときに使います。"),
        ),
        (
            ("Explain a real purpose if you went somewhere; otherwise write “I didn't go anywhere for a specific reason.”", "目的があって出かけたなら説明し、なければ「I didn't go anywhere for a specific reason.」と書きましょう。"),
            ("Recommend the best way to do one real task.", "実際の作業をする一番よい方法を一つ勧めましょう。"),
        ),
        (
            (
                ("顧客に会う{t}ために{/t}そこへ行きました。", "I went there ", "to see", "for see", " a client."),
                ("契約書に署名する{t}ために{/t}そこへ行きました。", "I went there ", "to sign", "for sign", " the contract."),
                ("プリンターを使う{t}ために{/t}そこへ行きました。", "I went there ", "to use", "for use", " the printer."),
                ("チケットを受け取る{t}ために{/t}そこへ行きました。", "I went there ", "to pick up", "for pick up", " the tickets."),
            ),
            (
                ("そこへ行く一番よい方法はバスに乗る{t}ことです{/t}。", "The best way to get there ", "is to", "is for", " take the bus."),
                ("時間を節約する一番よい方法はオンラインで予約する{t}ことです{/t}。", "The best way to save time ", "is to", "is for", " book online."),
                ("道順を覚える一番よい方法は歩いてみる{t}ことです{/t}。", "The best way to learn the route ", "is to", "is for", " walk it."),
                ("待ち時間を避ける一番よい方法はパソコンを予約する{t}ことです{/t}。", "The best way to avoid waiting ", "is to", "is for", " book a computer online."),
            ),
        ),
        (
            ("Purpose takes to plus plain verb", "目的は to と動詞の原形", "行った場所 + <b>to</b> + 動詞の原形", "Answer why", "なぜ行ったか", ("I went there <b>to see</b> a client.", "I went there <b>to use</b> the printer.")),
            ("Put the goal and method around is to", "目的と方法を is to ではさむ", "The best way to + 目的 + <b>is to</b> + 方法", "Recommend a method", "方法を勧める", ("The best way to get there <b>is to</b> take the bus.", "The best way to save time <b>is to</b> book online.")),
        ),
        ("Best or easiest?", "best と easiest", "Use “the best way” for the strongest overall choice. Use “the easiest way” when low effort is the deciding point.", "総合的に一番よいなら「the best way」を使います。手間の少なさが決め手なら「the easiest way」を使います。", ("Best overall", "総合的によい", "The best way to get there is to take the bus.", "そこへ行く一番よい方法はバスに乗ることです。"), ("Least effort", "手間が少ない", "The easiest way to book is to use the app.", "一番簡単な予約方法はアプリを使うことです。")),
    ),
}


# The ownership declaration is editorial source, not an inventory inferred
# from the finished HTML.  Recycled entries point to the first reviewed Core
# deck that taught the item; assumed items are ordinary A2 words that are not
# taught here; receptive items appear only as bounded support.
VOCAB = {
    48: dict(
        new="skiing|スキー; pottery|陶芸; wheel|ろくろ; capsule hotel|カプセルホテル",
        recycled="Canada|カナダ|CORE-4; hotel|ホテル|CORE-7",
        assumed="Kyoto|京都; sushi|寿司; try|試す; use|使う",
        receptive="not yet|まだ; a couple of times|2、3回; dates|時期; That sounds fun.|楽しそうです。",
    ),
    49: dict(
        new="bill|請求書",
        recycled="",
        assumed="email|メール; report|レポート; table|テーブル; task|作業",
        receptive="almost done|もうすぐ終わる; send|送る; finish|終える; launch|公開; just now|たった今; That's a relief.|ほっとしました。; Great. Let's go.|よかった。行きましょう。",
    ),
    50: dict(
        new="last summer|去年の夏; two months ago|2か月前",
        recycled="Canada|カナダ|CORE-4; café|カフェ|CORE-7",
        assumed="Kyoto|京都; museum|美術館; last year|去年; Friday|金曜日",
        receptive="exhibit|展示; It's been a while.|久しぶりです。; back in 2022|振り返ると2022年に; Sure. I'll tell you about it.|もちろん。話しますね。; Let's go this weekend.|今週末に行きましょう。",
    ),
    51: dict(
        new="neighborhood|地域",
        recycled="here|ここ|CORE-7",
        assumed="Tokyo|東京; Osaka|大阪; Japan|日本; five years|5年間; three months|3か月; two weeks|2週間; a day|1日",
        receptive="duration|期間; starting point|開始時点; area|地域; about five years|5年ほど; I really like it.|とても気に入っています。; I agree.|同感です。",
    ),
    52: dict(
        new="exhausted|疲れ切った",
        recycled="bored|退屈した|CORE-47; excited|わくわくした|CORE-47; tired|疲れた|CORE-30; noon|正午|CORE-38",
        assumed="work|働く; study|勉強する; clean|掃除する; wait|待つ; breakfast|朝食; hungry|空腹の; late|遅れた",
        receptive="nonstop|休みなく; I need a break.|休憩が必要です。; take a break|休憩する; all morning|午前中ずっと",
    ),
    53: dict(
        new="form|フォーム; budget|予算; pack|詰める",
        recycled="",
        assumed="report|レポート; email|メール; room|部屋; box|箱; review|確認する; check|確認する",
        receptive="send|送る; finish|終える; progress|進捗; on track|順調; behind schedule|予定より遅れて; remaining work|残作業; That'll help.|助かります。",
    ),
    54: dict(
        new="sick|病気の; manager|上司; client|顧客",
        recycled="café|カフェ|CORE-7; busy|忙しい|CORE-30",
        assumed="meeting|会議; train|電車; call|電話する; taxi|タクシー; home|家; rain|雨",
        receptive="reason|理由; result|結果; The thing is|実は; sensitive explanation|言いにくい説明; I'm glad I called.|電話してよかったです。; It worked out well.|うまくいきました。",
    ),
    55: dict(
        new="charger|充電器; wallet|財布; speaker|スピーカー; earlier|さっき",
        recycled="ticket|チケット|CORE-5; bring|持ってくる|CORE-38",
        assumed="email|メール; room|部屋; phone|携帯; door|ドア; cake|ケーキ; music|音楽; key|鍵; call|電話する; book|予約する",
        receptive="you know, the one who|ほら、〜した人; whatsisname|あの人; No problem.|どういたしまして。; Exactly.|そのとおりです。",
    ),
    56: dict(
        new="stressful|ストレスの多い; reliable|信頼できる; upstairs|2階",
        recycled="expensive|高い|CORE-19; small|小さい|CORE-43; crowded|混んでいる|CORE-44; comfortable|快適な|CORE-45; convenient|便利な|CORE-45; café|カフェ|CORE-7",
        assumed="place|場所; room|部屋; job|仕事; old|古い; quiet|静かな",
        receptive="limitation|問題点; having said that|そうは言っても; still|それでも; afterthought|付け足し; relaxed speech|くだけた会話; That's how I see it too.|私もそう思います。; I think so too.|私もそう思います。",
    ),
    57: dict(
        new="full|満席の",
        recycled="café|カフェ|CORE-7; busy|忙しい|CORE-30",
        assumed="rain|雨; train|電車; taxi|タクシー; wait|待つ; Mina|ミナ; dinner|夕食; outside|外",
        receptive="condition|条件; backup plan|予備案; just in case|念のため; either way|どちらにしても; Then let's watch a movie.|では映画を見ましょう。; we're covered|準備はできている",
    ),
    58: dict(
        new="soil|土; plant|植物; unless|〜でないかぎり",
        recycled="noon|正午|CORE-38",
        assumed="send|送る; finish|終える; call|電話する; text|メッセージする; email|メールする; report|レポート; meeting|会議; walk|歩く; water|水をやる; rain|雨; train|電車; tell|伝える",
        receptive="trigger|きっかけ; as soon as|〜するとすぐ; otherwise|そうでなければ; immediately|すぐに; Talk soon.|またあとで。; check it first|まず確認する",
    ),
    59: dict(
        new="contract|契約書; route|道順",
        recycled="ticket|チケット|CORE-5; printer|プリンター|CORE-38; best|一番よい|CORE-46; client|顧客|CORE-54",
        assumed="bus|バス; computer|パソコン; online|オンラインで; time|時間; waiting|待ち時間",
        receptive="purpose|目的; method|方法; it's worth it|その価値がある; save time|時間を節約する; efficient|効率的な; least effort|一番手間が少ない; book one now|今予約する",
    ),
}


KNOWN_WORDS = {
    48: (("京都", "Kyoto"), ("寿司", "sushi"), ("ホテル", "hotel")),
    49: (("メール", "email"), ("レポート", "report"), ("テーブル", "table")),
    50: (("京都", "Kyoto"), ("カフェ", "café"), ("ミュージアム", "museum")),
    51: (("東京", "Tokyo"), ("大阪", "Osaka"), ("ジャパン", "Japan")),
    52: (("ワーク", "work"), ("ブレックファスト", "breakfast"), ("ヌーン", "noon")),
    53: (("レポート", "report"), ("ルーム", "room"), ("メール", "email")),
    54: (("ミーティング", "meeting"), ("トレイン", "train"), ("タクシー", "taxi")),
    55: (("メール", "email"), ("フォン", "phone"), ("チケット", "ticket")),
    56: (("カフェ", "café"), ("ルーム", "room"), ("ジョブ", "job")),
    57: (("トレイン", "train"), ("タクシー", "taxi"), ("カフェ", "café")),
    58: (("メール", "email"), ("レポート", "report"), ("ミーティング", "meeting")),
    59: (("チケット", "ticket"), ("プリンター", "printer"), ("バス", "bus")),
}


# One row-specific content-word menu per closed translation. Pattern words are
# intentionally absent: the learner must retrieve those from the lesson.
TRANSLATE_HINTS = {
    48: (
        ("京都:Kyoto", "寿司:sushi", "陶芸:pottery", "カプセルホテル:capsule hotel"),
        ("スキー:skiing", "カナダ:Canada", "ろくろ:wheel", "カプセルホテル:capsule hotel"),
    ),
    49: (
        ("メール:email", "レポート:report", "テーブル:table", "請求書:bill"),
        ("レポート:report", "メール:email", "テーブル:table", "請求書:bill"),
    ),
    50: (
        ("京都:Kyoto", "カナダ:Canada", "カフェ:café", "美術館:museum"),
        ("去年:last year", "去年の夏:last summer", "金曜日:Friday", "2か月前:two months ago"),
    ),
    51: (
        ("東京:Tokyo", "大阪:Osaka", "日本:Japan", "地域:neighborhood"),
        ("5年間:five years", "3か月:three months", "2週間:two weeks", "1日:a day"),
    ),
    52: (
        ("働く:work", "朝食:breakfast", "掃除する:clean", "正午:noon"),
        ("疲れ切った:exhausted", "空腹の:hungry", "疲れた:tired", "遅れた:late"),
    ),
    53: (
        ("レポート:report", "フォーム:form", "部屋:room", "箱:box"),
        ("予算:budget", "メール:email", "部屋:room", "箱:box"),
    ),
    54: (
        ("病気の:sick", "会議:meeting; 電車:train", "タクシー:taxi; 雨:rain", "会議:meeting; 顧客:client"),
        ("病気の:sick", "電車:train; 上司:manager", "雨:rain; カフェ:café", "顧客:client; 会議:meeting"),
    ),
    55: (
        ("さっき:earlier", "メール:email", "部屋:room", "ケーキ:cake"),
        ("ドア:door", "携帯:phone", "チケット:ticket", "音楽:music"),
    ),
    56: (
        ("場所:place; 高い:expensive", "部屋:room; 小さい:small", "カフェ:café; 混んでいる:crowded", "仕事:job; ストレスの多い:stressful"),
        ("小さい:small; 快適な:comfortable", "高い:expensive; 便利な:convenient", "混んでいる:crowded; 2階:upstairs", "古い:old; 信頼できる:reliable"),
    ),
    57: (
        ("雨:rain", "電車:train; タクシー:taxi", "カフェ:café; 満席の:full", "ミナ:Mina; 夕食:dinner"),
        ("電車:train", "雨:rain", "カフェ:café", "ミナ:Mina"),
    ),
    58: (
        ("電話する:call", "メッセージする:text", "メールする:email; レポート:report", "伝える:tell"),
        ("雨:rain", "電車:train", "会議:meeting", "土:soil; 植物:plant"),
    ),
    59: (
        ("顧客:client", "契約書:contract", "プリンター:printer", "チケット:ticket"),
        ("バス:bus", "時間:time; オンラインで:online", "道順:route", "待ち時間:waiting; パソコン:computer; オンラインで:online"),
    ),
}


OPEN_MENUS = {
    48: (("京都:Kyoto", "陶芸:pottery", "カプセルホテル:capsule hotel"), ("スキー:skiing", "カナダ:Canada", "陶芸:pottery")),
    49: (("メール:email", "レポート:report", "請求書:bill"), ("メール:email", "レポート:report", "テーブル:table")),
    50: (("京都:Kyoto", "カナダ:Canada", "美術館:museum"), ("去年:last year", "金曜日:Friday", "2か月前:two months ago")),
    51: (("東京:Tokyo", "大阪:Osaka", "地域:neighborhood"), ("5年間:five years", "3か月:three months", "2週間:two weeks")),
    52: (("働く:work", "勉強する:study", "掃除する:clean"), ("疲れ切った:exhausted", "空腹の:hungry", "疲れた:tired")),
    53: (("レポート:report", "フォーム:form", "部屋:room"), ("予算:budget", "メール:email", "箱:box")),
    54: (("病気の:sick", "電車:train", "雨:rain"), ("上司:manager", "カフェ:café", "会議:meeting")),
    55: (("電話する:call", "メール:email", "部屋:room"), ("充電器:charger", "財布:wallet", "スピーカー:speaker")),
    56: (("場所:place", "部屋:room", "仕事:job"), ("快適な:comfortable", "便利な:convenient", "信頼できる:reliable")),
    57: (("雨:rain", "電車:train", "カフェ:café"), ("雨:rain", "電車:train", "ミナ:Mina")),
    58: (("電話する:call", "メッセージする:text", "メールする:email"), ("雨:rain", "会議:meeting", "土:soil")),
    59: (("顧客:client", "契約書:contract", "プリンター:printer"), ("バス:bus", "道順:route", "オンラインで:online")),
}


DIALOGUES = {
    48: dict(
        model=("Friend", 0, 0, ("I'm planning a trip to Kyoto.", "京都旅行を計画しています。"), ("Yes, a couple of times. What would you like to try there?", "はい、2、3回あります。そこで何をしてみたいですか？"), ("There's a ski area nearby.", "近くにスキー場があります。"), ("That sounds fun.", "楽しそうです。")),
        wild=("Visitor", 2, 2, ("This pottery studio looks interesting.", "この陶芸教室は面白そうですね。"), ("Yes, once. Have you used a wheel?", "はい、一度あります。ろくろを使ったことはありますか？"), ("They offer a beginner lesson.", "初心者向けのレッスンがあります。"), ("That sounds fun.", "楽しそうです。")),
    ),
    49: dict(
        model=("Coworker", 1, 1, ("Are you almost done with the report?", "レポートはもうすぐ終わりそうですか？"), ("Great. I'm checking the other tasks too.", "よかったです。ほかの作業も確認しています。"), ("Yes, just now. We're on time for the launch.", "はい、たった今送りました。公開に間に合います。"), ("That's a relief.", "ほっとしました。")),
        wild=("Organizer", 2, 3, ("How are the preparations for the charity dinner?", "チャリティー夕食会の準備はどうですか？"), ("Great. I'm checking the expenses now.", "よかったです。今、費用を確認しています。"), ("Yes, just now. Everything is ready.", "はい、たった今支払いました。これで全部準備できました。"), ("That's a relief.", "ほっとしました。")),
    ),
    50: dict(
        model=("Friend", 0, 0, ("You went to Kyoto last year, right? I'm planning a trip there.", "去年京都に行きましたよね？ 私も旅行を計画しています。"), ("Not yet. When did you go?", "まだありません。いつ行きましたか？"), ("I'd love to hear what you liked.", "気に入ったものをぜひ聞きたいです。"), ("Sure. I'll tell you about it.", "もちろん。話しますね。")),
        wild=("Neighbor", 3, 2, ("You said you visited the new museum exhibit on Friday.", "金曜日に美術館の新しい展示を見たと言っていましたね。"), ("Not yet. When did you go?", "まだありません。いつ行きましたか？"), ("Is the exhibit still open?", "その展示はまだ開いていますか？"), ("Yes. Let's go this weekend.", "はい。今週末に行きましょう。")),
    ),
    51: dict(
        model=("Neighbor", 0, 0, ("I just moved to Tokyo.", "東京に引っ越してきたばかりです。"), ("Only a week. What about you?", "まだ1週間です。あなたは？"), ("Then you know the neighborhood well.", "では、この地域をよく知っていますね。"), ("I do. I really like it.", "はい。とても気に入っています。")),
        wild=("Volunteer", 3, 2, ("I help new volunteers settle into this neighborhood.", "新しいボランティアがこの地域に慣れるのを手伝っています。"), ("I've been here since I was a kid, on and off. What about you?", "子どものころから、時々離れながらここにいます。あなたは？"), ("The people here are very friendly.", "ここの人たちはとても親切です。"), ("I agree.", "同感です。")),
    ),
    52: dict(
        model=("Coworker", 0, 0, ("You look tired. What have you been doing?", "疲れて見えます。何をしていたんですか？"), ("Since nine? You've been working nonstop.", "9時からですか？休みなく働いていたんですね。"), ("Let's stop before the next task.", "次の作業の前に止めましょう。"), ("I need a break.", "休憩が必要です。")),
        wild=("Volunteer", 2, 2, ("The community hall looks much better.", "公民館がずっときれいになりました。"), ("Since eight? You've been cleaning nonstop.", "8時からですか？休みなく掃除していたんですね。"), ("We're done for today.", "今日は終わりです。"), ("I need a break.", "休憩が必要です。")),
    ),
    53: dict(
        model=("Teammate", 0, 0, ("How many of the reports have we finished?", "レポートは何本終わりましたか？"), ("Good. What still needs attention?", "いいですね。まだ何をする必要がありますか？"), ("I'll help with that this afternoon.", "午後にそれを手伝います。"), ("Thanks. That'll help.", "ありがとう。助かります。")),
        wild=("Roommate", 2, 3, ("How many rooms have we finished?", "部屋はいくつ終わりましたか？"), ("Good. What still remains?", "いいですね。まだ何が残っていますか？"), ("I'll take the last box.", "最後の箱は私がやります。"), ("Thanks. That'll help.", "ありがとう。助かります。")),
    ),
    54: dict(
        model=("Coworker", 1, 1, ("I heard you missed the meeting. That's why I'm asking—what happened?", "会議に間に合わなかったと聞きました。だから聞いていますが、何があったんですか？"), ("I see. Did you tell your manager?", "なるほど。上司には伝えましたか？"), ("Good. They know what happened now.", "よかったです。これで事情が伝わりました。"), ("I'm glad I called.", "電話してよかったです。")),
        wild=("Friend", 2, 2, ("The picnic moved indoors. How did you get here in the rain?", "ピクニックは屋内になりましたね。この雨の中どうやって来たんですか？"), ("That makes sense. Where did everyone meet?", "なるほど。みんなはどこで会いましたか？"), ("A café was a good backup.", "カフェはよい予備案でしたね。"), ("It worked out well.", "うまくいきました。")),
    ),
    55: dict(
        model=("Coworker", 0, 0, ("Which person is Maya?", "どの人がマヤさんですか？"), ("Got it. And how can I identify the key?", "分かりました。では、鍵はどう見分けられますか？"), ("Thanks. Now I know both.", "ありがとう。これで両方分かりました。"), ("No problem.", "どういたしまして。")),
        wild=("Friend", 3, 3, ("I met several people at the party, but I don't remember Leo. Which person is he?", "パーティーで何人かに会いましたが、レオを覚えていません。どの人ですか？"), ("Thanks. And what was the speaker for?", "ありがとう。では、スピーカーは何に使ったんですか？"), ("Right—that's where the music came from.", "そうですね。そこから音楽が流れていたんですね。"), ("Exactly.", "そのとおりです。")),
    ),
    56: dict(
        model=("Friend", 1, 0, ("What do you think of the apartment?", "そのアパートはどう思いますか？"), ("True. Is there anything you like about it?", "そうですね。気に入っている点はありますか？"), ("That sounds like a fair trade-off.", "それなら納得できる一長一短ですね。"), ("That's how I see it too.", "私もそう思います。")),
        wild=("Neighbor", 0, 1, ("What do you think of the local gym?", "近所のジムはどう思いますか？"), ("Is there anything good about it despite the price?", "高くても、何かよいところはありますか？"), ("Then it may be worth considering.", "それなら検討する価値があるかもしれません。"), ("I think so too.", "私もそう思います。")),
    ),
    57: dict(
        model=("Friend", 0, 1, ("What will you do tomorrow if it rains?", "明日雨が降ったら、何をしますか？"), ("Good backup. I haven't decided what I'll do.", "よい予備案ですね。私はまだどうするか決めていません。"), ("I'll stay in too, then.", "では、私も家にいます。"), ("Then let's watch a movie.", "では映画を見ましょう。")),
        wild=("Friend", 3, 3, ("What's the plan for game night if Mina comes?", "ミナが来たら、ゲームの夜はどうする予定ですか？"), ("Great. I haven't made a backup plan if she can't.", "いいですね。彼女が来られない場合の予備案はまだ決めていません。"), ("Then I'll bring dinner instead.", "では、代わりに私が夕食を持っていきます。"), ("Perfect. Either way, we're covered.", "完璧です。どちらにしても準備はできています。")),
    ),
    58: dict(
        model=("Friend", 0, 0, ("Let me know when you arrive.", "着いたら知らせてください。"), ("Thanks. Are you planning to walk?", "ありがとう。歩く予定ですか？"), ("Good. I'll watch for your call.", "分かりました。電話を待っています。"), ("Great. Talk soon.", "分かりました。またあとで。")),
        wild=("Neighbor", 3, 3, ("Let me know how my plants look this evening.", "今晩、植物の様子を知らせてください。"), ("Thanks. Will you water them?", "ありがとう。水をやってもらえますか？"), ("Check the soil first. If it's wet, don't water them; otherwise, water them.", "まず土を確認してください。湿っていたら水をやらず、そうでなければやってください。"), ("I'll check it first.", "まず確認します。")),
    ),
    59: dict(
        model=("Coworker", 0, 0, ("Why did you go across town?", "なぜ街の反対側まで行ったんですか？"), ("There's a direct bus. What's the best way to get there?", "直通バスがあります。そこへ行く一番よい方法は何ですか？"), ("That makes sense. The bus stops right outside the building.", "なるほど。バスは建物のすぐ外に止まります。"), ("Exactly.", "そのとおりです。")),
        wild=("Friend", 2, 3, ("Why did you go to the library?", "なぜ図書館に行ったんですか？"), ("They have computers too. How can you avoid waiting?", "パソコンもあります。どうすれば待たずに使えますか？"), ("Exactly. Then a computer will be ready for you.", "そのとおりです。そうすればパソコンを用意できます。"), ("Perfect. I'll book one now.", "よかったです。今予約します。")),
    ),
}


LIVE_SCENES = {
    48: (("text", "other", "Tutor", "What's something you've never tried but would like to?", "まだしたことはないけれど、してみたいことは何ですか？"), ("input", "me", "Me", "I've never ___, but I'd like to. / Nothing comes to mind right now.", "まだ___をしたことはありませんが、してみたいです。／今は特に思いつきません。"), ("input", "me", "Me", "Have you ever ___?", "___をしたことはありますか？"), ("input", "other", "Tutor", "Tutor's answer: Yes, I have. / No, I haven't.", "先生の答え：はい、あります。／いいえ、ありません。")),
    49: (("text", "other", "Tutor", "Have you finished anything today?", "今日は何か終えましたか？"), ("input", "me", "Me", "Yes. I've already ___. / No, I haven't finished anything yet.", "はい。私はもう___を終えました。／いいえ、まだ何も終えていません。"), ("input", "me", "Me", "Have you finished ___ yet?", "もう___を終えましたか？"), ("input", "other", "Tutor", "Tutor's answer: Yes. I've already ___. / No, I haven't finished it yet.", "先生の答え：はい。もう___を終えました。／いいえ、まだ終えていません。")),
    50: (("text", "other", "Tutor", "Have you been to Kyoto?", "京都に行ったことはありますか？"), ("input", "me", "Me", "Yes, I went there ___. / No, I haven't been there.", "はい、___に行きました。／いいえ、行ったことはありません。"), ("input", "me", "Me", "Have you been to ___?", "___に行ったことはありますか？"), ("input", "other", "Tutor", "Tutor's answer: Yes, I went there ___. / No, I haven't been there.", "先生の答え：はい、___に行きました。／いいえ、行ったことはありません。")),
    51: (("text", "other", "Tutor", "How long have you been in your current town, city, or area?", "今の町・街・地域にどのくらい住んでいますか？"), ("input", "me", "Me", "I've been here for / since ___. / I don't live in a city, but I've been in this area for / since ___.", "ここに___の間／___から住んでいます。／街には住んでいませんが、この地域に___の間／___から住んでいます。"), ("input", "me", "Me", "How long have you been in your current town, city, or area?", "今の町・街・地域にどのくらい住んでいますか？"), ("input", "other", "Tutor", "Tutor's answer: I've been here for / since ___. / I live outside a city, and I've been in this area for / since ___.", "先生の答え：ここに___の間／___から住んでいます。／街の外に住んでいて、この地域に___の間／___から住んでいます。")),
    52: (("text", "other", "Tutor", "Have you been doing anything for a while today?", "今日は何かをしばらく続けていましたか？"), ("input", "me", "Me", "Yes. I've been ___ since ___. That's why I'm ___. / No, nothing for long today.", "はい。___から___をしていて、だから今___です。／いいえ、今日は長く続けたことはありません。"), ("input", "me", "Me", "What have you been doing today?", "今日は何をしていましたか？"), ("input", "other", "Tutor", "Tutor's answer: I've been ___ since ___. That's why I'm ___.", "先生の答え：___から___をしていて、だから今___です。")),
    53: (("text", "other", "Tutor", "Are you working on anything with a clear total right now?", "今、全体の数がはっきりした作業をしていますか？"), ("input", "me", "Me", "Yes. We've finished ___ of ___. We still need to ___. / No, I don't have a project like that right now.", "はい。___個中___個を終えて、まだ___する必要があります。／いいえ、今はそのような作業はありません。"), ("input", "me", "Me", "How many of the ___ have you finished?", "___はいくつ終わりましたか？"), ("input", "other", "Tutor", "Tutor's answer: I've finished ___ of the ___.", "先生の答え：___個中___個を終えました。")),
    54: (("text", "other", "Tutor", "Has one of your plans changed recently? Why?", "最近、予定が一つ変わりましたか？ なぜですか？"), ("input", "me", "Me", "Yes. I ___ because ___. / No, none of my plans changed.", "はい。___なので___しました。／いいえ、予定は変わりませんでした。"), ("input", "me", "Me", "Did any of your plans change? Why?", "何か予定が変わりましたか？ なぜですか？"), ("input", "other", "Tutor", "Tutor's answer: Yes. I ___ because ___. / No, none of my plans changed.", "先生の答え：はい。___なので___しました。／いいえ、予定は変わりませんでした。")),
    55: (("text", "other", "Tutor", "Who was the last person who called or messaged you?", "最後に電話かメッセージをくれた人は誰ですか？"), ("input", "me", "Me", "___ is the one who ___. / No one has called or messaged me recently.", "___は___した人です。／最近は誰からも電話やメッセージが来ていません。"), ("input", "me", "Me", "What's the thing that ___?", "___する物は何ですか？"), ("input", "other", "Tutor", "Tutor's answer: It's the thing that ___.", "先生の答え：それは___する物です。")),
    56: (("text", "other", "Tutor", "Is there a place you like even though it has a problem?", "問題点があっても気に入っている場所はありますか？"), ("input", "me", "Me", "Yes. I like ___, but ___. Even though ___, ___. / Not really.", "はい。___は好きですが、___です。___なのに、___です。／特にありません。"), ("input", "me", "Me", "Do you like a place even though it's ___?", "___でも気に入っている場所はありますか？"), ("input", "other", "Tutor", "Tutor's answer: Yes. Even though it's ___, ___. / Not really.", "先生の答え：はい。___でも、___です。／特にありません。")),
    57: (("text", "other", "Tutor", "What will you do if it rains tomorrow?", "明日雨が降ったら、何をしますか？"), ("input", "me", "Me", "If it rains, I'll ___. / I haven't decided yet.", "雨が降ったら___します。／まだ決めていません。"), ("input", "me", "Me", "What will you do if it rains?", "雨が降ったら何をしますか？"), ("input", "other", "Tutor", "Tutor's answer: If it rains, I'll ___. / I haven't decided yet.", "先生の答え：雨が降ったら___します。／まだ決めていません。")),
    58: (("text", "other", "Tutor", "Will you contact anyone later today? When?", "今日このあと誰かに連絡しますか？ いつですか？"), ("input", "me", "Me", "Yes. I'll ___ when ___. Unless ___, I'll ___. / No, I don't plan to contact anyone today.", "はい。___したら___します。___でないかぎり___します。／いいえ、今日は誰にも連絡する予定はありません。"), ("input", "me", "Me", "When will you contact someone?", "いつ誰かに連絡しますか？"), ("input", "other", "Tutor", "Tutor's answer: I'll ___ when ___.", "先生の答え：___したら___します。")),
    59: (("text", "other", "Tutor", "Did you go anywhere for a specific reason recently?", "最近、何か目的があって出かけましたか？"), ("input", "me", "Me", "Yes. I went there to ___. / No, I didn't go anywhere for a specific reason.", "はい。___するためにそこへ行きました。／いいえ、特別な目的で出かけてはいません。"), ("input", "me", "Me", "What's the best way to ___?", "___する一番よい方法は何ですか？"), ("input", "other", "Tutor", "Tutor's answer: The best way to ___ is to ___.", "先生の答え：___する一番よい方法は___することです。")),
}


LIVE_HINTS = {
    48: {1: ("スキー:skiing", "陶芸:pottery", "カプセルホテル:capsule hotel"), 2: ("スキー:skiing", "陶芸:pottery", "寿司:sushi")},
    49: {1: ("メール:email", "レポート:report", "請求書:bill"), 2: ("メール:email", "レポート:report", "請求書:bill")},
    50: {1: ("去年:last year", "金曜日:Friday", "2か月前:two months ago"), 2: ("京都:Kyoto", "カナダ:Canada", "美術館:museum")},
    51: {1: ("5年間:five years", "3か月:three months", "2週間:two weeks"), 2: ("5年間:five years", "3か月:three months", "2週間:two weeks")},
    52: {1: ("働く:work", "勉強する:study", "掃除する:clean"), 2: ("働く:work", "勉強する:study", "掃除する:clean")},
    53: {1: ("レポート:report", "フォーム:form", "部屋:room"), 2: ("レポート:report", "フォーム:form", "部屋:room")},
    54: {1: ("病気の:sick", "電車:train", "雨:rain"), 2: ("会議:meeting", "電車:train", "雨:rain")},
    55: {1: ("電話する:call", "メール:email", "予約する:book"), 2: ("ドア:door", "携帯:phone", "音楽:music")},
    56: {1: ("カフェ:café", "部屋:room", "高い:expensive", "小さい:small", "便利な:convenient", "快適な:comfortable"), 2: ("高い:expensive", "小さい:small", "混んでいる:crowded")},
    57: {1: ("雨:rain", "電車:train", "カフェ:café"), 2: ("雨:rain", "電車:train", "カフェ:café")},
    58: {1: ("電話する:call", "メッセージする:text", "メールする:email"), 2: ("電話する:call", "メッセージする:text", "メールする:email")},
    59: {1: ("顧客:client", "契約書:contract", "プリンター:printer"), 2: ("バス:bus", "道順:route", "オンラインで:online")},
}


# Human-reviewed operating copy for the CORE48-59 page-by-page audit.  The
# write prompt names the exact communicative job and the free-talk question is
# a genuine topic conversation: today's pattern may occur naturally, but is
# never required.  The learner's ask-back is visible and the tutor gives a real
# answer rather than modelling another pattern response.
REVIEWED_WRITES_48_59 = {
    48: (("Use “Have you ever ___?” to ask one experience question you genuinely want answered.", "「Have you ever ___?」を使って、本当に答えを知りたい経験の質問を一つしましょう。"), ("Use “I've never ___, but I'd like to” to name one new experience you would like to try.", "「I've never ___, but I'd like to」を使って、まだ経験はないけれど挑戦したいことを一つ話しましょう。")),
    49: (("Use “I've already ___” to give one true update about something you finished.", "「I've already ___」を使って、本当に終えたことを一つ報告しましょう。"), ("Use “Have you ___ yet?” to ask whether one real task is complete.", "「Have you ___ yet?」を使って、実際の作業が一つ終わったか尋ねましょう。")),
    50: (("Use “Have you been to ___?” to ask whether I have visited one place.", "「Have you been to ___?」を使って、私がある場所を訪れたことがあるか尋ねましょう。"), ("Use “I went there ___” to say when you visited a place; if you have not, say “I haven't been there.”", "「I went there ___」を使って訪れた時を話し、行ったことがなければ「I haven't been there.」と言いましょう。")),
    51: (("Use “How long have you been in ___?” to ask how long I have lived in one place.", "「How long have you been in ___?」を使って、私がある場所にどのくらい住んでいるか尋ねましょう。"), ("Use “I've been here for ___” to say how long you have lived where you are now.", "「I've been here for ___」を使って、今の場所にどのくらい住んでいるか話しましょう。")),
    52: (("Use “I've been ___ since ___” to say what has continued today and when it started.", "「I've been ___ since ___」を使って、今日続けていることと開始時点を話しましょう。"), ("Use “That's why I'm ___” to add one true effect, or say there is no effect to report.", "「That's why I'm ___」を使って本当の結果を一つ加え、なければ伝える結果はないと言いましょう。")),
    53: (("Use “We've finished ___ of ___” to report real progress on one countable task.", "「We've finished ___ of ___」を使って、数えられる作業の本当の進捗を報告しましょう。"), ("Use “We still need to ___” to name one remaining task.", "「We still need to ___」を使って、まだ残っている作業を一つ伝えましょう。")),
    54: (("Use “___ because ___” to explain one real changed plan and its reason.", "「___ because ___」を使って、実際に変わった予定と理由を説明しましょう。"), ("Use “___, so ___” to tell the same event with the reason first and result second.", "「___, so ___」を使って、同じ出来事を理由、結果の順で話しましょう。")),
    55: (("Use “___ is the one who ___” to identify one real person by something they did.", "「___ is the one who ___」を使って、実在する人をその人がしたことで特定しましょう。"), ("Use “It's the thing that ___” to describe one object without naming it first.", "「It's the thing that ___」を使って、名前を先に言わずに物を一つ説明しましょう。")),
    56: (("Use “I like ___, but ___” to give one real good point and limitation.", "「I like ___, but ___」を使って、本当によい点と問題点を一つずつ話しましょう。"), ("Use “Even though ___, ___” to give one surprising positive point despite a limitation.", "「Even though ___, ___」を使って、問題点があっても意外によい点を一つ話しましょう。")),
    57: (("Use “If ___, I'll ___” to give one realistic condition and plan.", "「If ___, I'll ___」を使って、現実的な条件と予定を一つ話しましょう。"), ("Use “What will you do if ___?” to ask about one real backup plan.", "「What will you do if ___?」を使って、本当の予備案を一つ尋ねましょう。")),
    58: (("Use “I'll ___ when ___” to say when you will contact someone.", "「I'll ___ when ___」を使って、いつ誰かに連絡するか話しましょう。"), ("Use “Unless ___, I'll ___” to name the condition that could change your plan.", "「Unless ___, I'll ___」を使って、予定が変わる条件を一つ伝えましょう。")),
    59: (("Use “I went there to ___” to explain the real purpose of one trip.", "「I went there to ___」を使って、出かけた本当の目的を一つ説明しましょう。"), ("Use “The best way to ___ is to ___” to recommend one practical method.", "「The best way to ___ is to ___」を使って、実用的な方法を一つ勧めましょう。")),
}


REVIEWED_LIVE_48_59 = {
    48: ("What's something new you'd like to try this year, and why?", "今年、新しく挑戦したいことは何ですか？なぜですか？", "What about you—what would you like to try?", "先生はどうですか？何に挑戦したいですか？"),
    49: ("What's one small task you like finishing early, and why?", "早めに終えると気分がよい小さな作業は何ですか？なぜですか？", "What about you—which task do you like finishing early?", "先生はどうですか？どの作業を早めに終えたいですか？"),
    50: ("Which place would you happily visit again, and why?", "もう一度喜んで行きたい場所はどこですか？なぜですか？", "What about you—which place would you visit again?", "先生はどうですか？どこをもう一度訪れたいですか？"),
    51: ("What makes a place feel like home to you?", "どんなことがあると、その場所を自分の家のように感じますか？", "What about you—what makes a place feel like home?", "先生はどうですか？どんな場所なら家のように感じますか？"),
    52: ("What kind of activity makes time pass quickly for you?", "どんなことをしていると、時間が早く過ぎますか？", "What about you—what makes time pass quickly?", "先生はどうですか？何をしていると時間が早く過ぎますか？"),
    53: ("Do you prefer projects with a clear finish line or open-ended work? Why?", "終わりが明確な作業と、終わりが決まっていない作業のどちらが好きですか？なぜですか？", "What about you—which kind of project do you prefer?", "先生はどうですか？どちらの作業が好きですか？"),
    54: ("When a plan changes unexpectedly, do you usually feel stressed or flexible?", "予定が突然変わったら、ストレスを感じますか？それとも柔軟に対応できますか？", "What about you—how do you react when plans change?", "先生はどうですか？予定が変わったらどう反応しますか？"),
    55: ("Are you better at remembering people by their names, faces, or what they did?", "人を覚えるとき、名前・顔・その人がしたことのどれが一番覚えやすいですか？", "What about you—how do you remember people?", "先生はどうですか？人をどう覚えますか？"),
    56: ("Which matters most when you choose a place: comfort, price, or convenience?", "場所を選ぶとき、快適さ・価格・便利さのどれを最も重視しますか？", "What about you—which matters most?", "先生はどうですか？どれを最も重視しますか？"),
    57: ("Do you enjoy making backup plans, or do you prefer to decide in the moment?", "予備案を作るのが好きですか？それとも、その場で決めたいですか？", "What about you—do you usually make backup plans?", "先生はどうですか？普段、予備案を作りますか？"),
    58: ("Do you prefer people to call, text, or email you when plans change?", "予定が変わったとき、電話・メッセージ・メールのどれで連絡してほしいですか？", "What about you—how do you prefer to be contacted?", "先生はどうですか？どの方法で連絡してほしいですか？"),
    59: ("When you need to learn how to do something, who or what do you ask first?", "何かのやり方を知りたいとき、最初に誰や何に聞きますか？", "What about you—who or what do you ask first?", "先生はどうですか？最初に誰や何に聞きますか？"),
}


# Choice pages are useful only when the learner must make a real meaning or
# form decision. These reviewed rows deliberately vary the correct alternative;
# fixed-frame pages with no honest contrast are omitted in LESSONS instead.
REVIEWED_CHOICES_48_59 = {
    50: (
        (
            ("{t}今までの経験{/t}を聞きます。", "", "Have you been", "Did you go", " to Kyoto?"),
            ("{t}去年の旅行{/t}を聞きます。", "", "Did you go", "Have you been", " to Canada last year?"),
            ("{t}今までの経験{/t}を聞きます。", "", "Have you been", "Did you go", " to this café?"),
            ("{t}金曜日の訪問{/t}を聞きます。", "", "Did you go", "Have you been", " to this museum on Friday?"),
        ),
        (
            ("{t}去年{/t}そこへ行きました。", "Yes, I ", "went", "have been", " there last year."),
            ("{t}今までに{/t}そこへ行ったことがあります。", "Yes, I ", "have been", "went", " there before."),
            ("{t}金曜日{/t}そこへ行きました。", "Yes, I ", "went", "have been", " there on Friday."),
            ("{t}これまでに2回{/t}そこへ行ったことがあります。", "Yes, I ", "have been", "went", " there twice so far."),
        ),
    ),
    51: (
        (
            ("{t}東京に{/t}どのくらいいますか？", "How long have you been ", "in", "for", " Tokyo?"),
            ("ここには{t}5年間{/t}いますか？", "Have you been here ", "for", "in", " five years?"),
            ("{t}日本に{/t}どのくらいいますか？", "How long have you been ", "in", "for", " Japan?"),
            ("ここには{t}2週間{/t}いますか？", "Have you been here ", "for", "in", " two weeks?"),
        ),
        SPECS[51]["choices"][1],
    ),
    54: (
        (
            ("家にいたのは{t}病気だったから{/t}です。", "I stayed home ", "because", "so", " I was sick."),
            ("電車が遅れました。{t}だから{/t}上司に電話しました。", "My train was late, ", "so", "because", " I called my manager."),
            ("タクシーを呼んだのは{t}雨だったから{/t}です。", "I called a taxi ", "because", "so", " it was raining."),
            ("顧客が忙しかったです。{t}だから{/t}会議を変更しました。", "My client was busy, ", "so", "because", " we moved the meeting."),
        ),
        (
            ("病気でした。{t}だから{/t}家にいました。", "I was sick, ", "so", "because", " I stayed home."),
            ("上司に電話したのは{t}電車が遅れたから{/t}です。", "I called my manager ", "because", "so", " my train was late."),
            ("雨でした。{t}だから{/t}カフェで会いました。", "It was raining, ", "so", "because", " we met at a café."),
            ("会議を変更したのは{t}顧客が忙しかったから{/t}です。", "We moved the meeting ", "because", "so", " my client was busy."),
        ),
    ),
    55: (
        (
            ("{t}電話をくれた人{/t}は彼女です。", "She's the one ", "who", "where", " called earlier."),
            ("{t}初めて会ったカフェ{/t}はここです。", "This is the café ", "where", "who", " we first met."),
            ("{t}部屋を予約した人{/t}は彼女です。", "She's the one ", "who", "where", " booked the room."),
            ("{t}会議をした部屋{/t}はあそこです。", "That's the room ", "where", "who", " we held the meeting."),
        ),
        (
            ("ドアを開ける{t}物{/t}です。", "It's the thing ", "that", "where", " opens the door."),
            ("携帯を充電した{t}場所{/t}です。", "It's the place ", "where", "that", " I charged my phone."),
            ("チケットを入れる{t}物{/t}です。", "It's the thing ", "that", "where", " holds the tickets."),
            ("音楽を聞いた{t}場所{/t}です。", "It's the place ", "where", "that", " we heard the music."),
        ),
    ),
    56: (
        (
            ("場所は好きです。{t}ただ{/t}、高いです。", "I like the place, ", "but", "because", " it's expensive."),
            ("部屋が静か{t}なので{/t}、気に入っています。", "I like the room ", "because", "but", " it's quiet."),
            ("カフェは好きです。{t}ただ{/t}、混んでいます。", "I like the café, ", "but", "because", " it's crowded."),
            ("勤務時間が柔軟{t}なので{/t}、仕事が好きです。", "I like the job ", "because", "but", " the hours are flexible."),
        ),
        (
            ("{t}小さいのに{/t}、快適です。", "", "Even though", "Because", " it's small, it's comfortable."),
            ("{t}静かなので{/t}、快適です。", "", "Because", "Even though", " it's quiet, it's comfortable."),
            ("{t}混んでいるのに{/t}、2階は静かです。", "", "Even though", "Because", " it's crowded, it's quiet upstairs."),
            ("{t}信頼できるので{/t}、よく使います。", "", "Because", "Even though", " it's reliable, I use it often."),
        ),
    ),
    58: (
        SPECS[58]["choices"][0],
        (
            ("{t}雨が降らないかぎり{/t}、歩きます。", "", "Unless", "If", " it rains, I'll walk."),
            ("{t}電車が遅れたら{/t}、タクシーに乗ります。", "", "If", "Unless", " the train's late, I'll take a taxi."),
            ("{t}会議が長引かないかぎり{/t}、6時に電話します。", "", "Unless", "If", " the meeting runs late, I'll call at six."),
            ("{t}土が乾いていたら{/t}、水をやります。", "", "If", "Unless", " the soil is dry, I'll water the plants."),
        ),
    ),
}


ROLE_JA = {
    "Friend": "友人", "Visitor": "参加者", "Coworker": "同僚", "Organizer": "主催者",
    "Neighbor": "近所の人", "Volunteer": "ボランティア", "Teammate": "チームメンバー",
    "Roommate": "同居人",
}


for _number in range(48, 60):
    SPECS[_number]["writes"] = REVIEWED_WRITES_48_59[_number]
    _question, _question_ja, _ask_back, _ask_back_ja = REVIEWED_LIVE_48_59[_number]
    LESSONS[_number]["prompt"] = (
        "Let's talk about this topic. Answer my question, then ask me too.",
        "この話題について話しましょう。私の質問に答えて、そのあと私にも聞いてください。",
    )
    LIVE_SCENES[_number] = (
        ("text", "other", "Tutor", _question, _question_ja),
        ("input", "me", "Me", "Student's answer", "自分の答え"),
        ("text", "me", "Me", _ask_back, _ask_back_ja),
        ("input", "other", "Tutor", "Tutor's answer", "先生の答え"),
    )
    LIVE_HINTS[_number] = {}
for _number, _choices in REVIEWED_CHOICES_48_59.items():
    SPECS[_number]["choices"] = _choices

# No honest two-way decision exists on these fixed-frame choice pages.
LESSONS[59]["omit_choice"] = (2,)

# Articles remain learner decisions; lexical hint chips never supply them.
_core51_hints = list(TRANSLATE_HINTS[51])
_core51_p2 = list(_core51_hints[1])
_core51_p2[3] = "1日:day"
_core51_hints[1] = tuple(_core51_p2)
TRANSLATE_HINTS[51] = tuple(_core51_hints)
VOCAB[51]["assumed"] = VOCAB[51]["assumed"].replace("a day|1日", "day|1日")


TRANSFER_SCENES = {
    48: "pottery studio orientation",
    49: "charity dinner preparation",
    50: "neighborhood museum exhibit",
    51: "community garden orientation",
    52: "community hall cleanup",
    53: "spring cleaning at home",
    54: "picnic moved indoors because of rain",
    55: "party memory and object identification",
    56: "local gym evaluation",
    57: "home game-night backup plan",
    58: "houseplant care",
    59: "library computer and printer visit",
}


BRIEF_PRODUCTION_MODELS = {
    48: ("I've never tried it, but I'd like to.",),
    49: ("I've already sent it.", "Have you finished yet?"),
    53: ("We've finished three of the five.",),
}


# Required brief support is receptive: the learner reads useful conversational
# language here but is never required to produce it as a lesson target.
SUPPORT_EXPRESSIONS = {
    48: (("Have you tried skiing? Not yet, but I'd like to.", "スキーをしたことはありますか？ まだですが、してみたいです。"),),
    50: (("I've been there, but it's been a while.", "行ったことはありますが、しばらく前です。"),),
    53: (("We're on track.", "順調です。"), ("We're behind schedule.", "予定より遅れています。")),
    55: (("You know, the one who called earlier.", "ほら、さっき電話をくれた人です。"), ("Whatsisname brought the cake.", "ほら、あの人がケーキを持ってきました。")),
    56: (("Having said that, it's still convenient.", "そうは言っても、それでも便利です。"),),
    57: (("I'll take an umbrella, just in case.", "念のため傘を持っていきます。"),),
    59: (("The trip takes longer, but it's worth it.", "移動時間は長くなりますが、その価値があります。"),),
}


SUPPORT_OWNERSHIP = {
    48: ("not yet",),
    50: ("it's been a while",),
    53: ("on track", "behind schedule"),
    55: ("you know, the one who", "whatsisname"),
    56: ("having said that", "still"),
    57: ("just in case",),
    59: ("it's worth it",),
}


# Three-chip builds are permitted only when a taught multiword frame or a full
# clause would become a dishonest mechanical split. CORE-53 part 1 is omitted
# because the quantifier noun phrase has only two meaningful units.
THREE_CHIP_EXCEPTIONS = {
    (50, 1): "Keep the taught been to frame intact.",
    (52, 2): "Keep the taught That's why frame intact.",
    (53, 1): "Omit: the quantifier noun phrase has only two meaningful units.",
    (56, 2): "Keep each contrast clause intact around Even though.",
}


SPIRAL_MARKERS = {
    50: ("NEGQ-01", "recognition"),
    54: ("ASPECT-02", "controlled"),
    59: ("REL-01", "checkpoint"),
}


# This ledger makes adjacency and resolution reviewable without inferring
# intent from the rendered HTML. Each tuple names the purpose of all six turns.
DIALOGUE_SEMANTIC_LEDGER = {
    48: dict(model=("friend names Kyoto plan", "learner asks Kyoto experience", "friend answers and asks desired activity", "learner names skiing gap", "friend offers nearby ski option", "learner accepts"), wild=("visitor notices pottery studio", "learner asks pottery experience", "visitor answers and asks wheel experience", "learner names wheel gap", "visitor offers beginner lesson", "learner accepts")),
    49: dict(model=("coworker asks report status", "learner reports report complete", "coworker checks other tasks", "learner asks email status", "coworker resolves email status", "learner expresses relief"), wild=("organizer asks dinner preparation status", "learner reports table booked", "organizer checks expenses", "learner asks bill status", "organizer resolves bill and readiness", "learner expresses relief")),
    50: dict(model=("friend establishes learner Kyoto visit", "learner asks friend's Kyoto experience", "friend says no and asks visit time", "learner supplies last year", "friend asks to hear what learner liked", "learner agrees"), wild=("neighbor establishes learner museum visit", "learner asks neighbor's museum experience", "neighbor says no and asks visit time", "learner supplies Friday", "neighbor asks whether exhibit remains open", "learner confirms and proposes visit")),
    51: dict(model=("neighbor says they just moved", "learner asks time in Tokyo", "neighbor answers and asks learner", "learner gives duration", "neighbor infers local knowledge", "learner confirms"), wild=("volunteer frames neighborhood orientation", "learner asks time in neighborhood", "volunteer answers and asks learner", "learner gives duration", "volunteer comments on people", "learner agrees")),
    52: dict(model=("coworker notices tiredness", "learner names ongoing work", "coworker confirms duration", "learner states current effect", "coworker proposes stopping", "learner agrees"), wild=("volunteer notices improved hall", "learner names ongoing cleaning", "volunteer confirms duration", "learner states current effect", "volunteer ends work", "learner agrees")),
    53: dict(model=("teammate asks completed report count", "learner gives count", "teammate asks remaining work", "learner names budget review", "teammate offers help", "learner accepts"), wild=("roommate asks completed room count", "learner gives count", "roommate asks remaining work", "learner names final box", "roommate takes box", "learner accepts")),
    54: dict(model=("coworker asks why meeting was missed", "learner gives train reason", "coworker checks manager contact", "learner gives reason-result version", "coworker confirms resolution", "learner expresses relief"), wild=("friend asks rain travel explanation", "learner gives taxi reason", "friend asks meeting place", "learner gives cafe result", "friend validates backup", "learner confirms")),
    55: dict(model=("coworker asks Maya identity", "learner identifies by call", "coworker asks key identity", "learner identifies by function", "coworker confirms both", "learner closes"), wild=("friend recalls party and asks Leo identity", "learner identifies Leo by cake action", "friend asks speaker function", "learner identifies by function", "friend resolves music source", "learner confirms")),
    56: dict(model=("friend asks apartment opinion", "learner gives limitation", "friend asks good point", "learner gives contrast", "friend accepts trade-off", "learner agrees"), wild=("neighbor asks gym opinion", "learner gives price limitation", "neighbor asks good point despite price", "learner gives convenience contrast", "neighbor says it merits consideration", "learner agrees")),
    57: dict(model=("friend asks rain contingency", "learner gives rain backup", "friend admits no decision", "learner asks friend's rain plan", "friend adopts learner plan", "learner proposes shared activity"), wild=("friend asks Mina contingency", "learner gives condition plan", "friend admits no backup", "learner asks no-Mina plan", "friend offers dinner", "learner confirms coverage")),
    58: dict(model=("friend requests arrival contact", "learner promises call on arrival", "friend checks walking plan", "learner gives rain exception", "friend confirms waiting", "learner closes"), wild=("neighbor requests plant update", "learner promises update", "neighbor asks watering plan", "learner gives soil exception", "neighbor clarifies check-then-act", "learner confirms")),
    59: dict(model=("coworker asks trip purpose", "learner names client purpose", "coworker establishes direct bus and asks route", "learner recommends bus", "coworker confirms stop location", "learner confirms"), wild=("friend asks library purpose", "learner names printer purpose", "friend asks how to avoid waiting", "learner recommends online booking", "friend confirms readiness", "learner books")),
}


def set_vocab(head, number):
    for category, value in VOCAB[number].items():
        head = re.sub(
            rf'(<meta name="podo:vocabulary:{category}" content=")[^"]*(")',
            rf'\g<1>{value}\2',
            head,
            count=1,
        )
    return head


def hint_html(items):
    chips = []
    for item in items:
        chips.extend(part for part in item.split("; ") if part)
    return '<span class="hint">' + "".join(
        f'<span class="hint-chip">{core.esc(item)}</span>' for item in chips
    ) + "</span>"


def known_page(number):
    cards = "".join(
        f'<div class="br-row"><span class="br-cn">{core.esc(japanese)}</span>'
        f'<span class="br-eq">→</span><span class="br-ko">{core.esc(english)}</span></div>'
        for japanese, english in KNOWN_WORDS[number]
    )
    return core.section(
        "words-you-know",
        "Words you know",
        "知っている単語",
        '<p class="section-subtitle"><span class="ko">Say the three familiar words in English.</span>'
        '<span class="ja">知っている3つの単語を英語で言いましょう。</span></p>'
        f'<div class="bridge">{cards}</div>',
    )


def support_page(number):
    lines = "".join(
        '<div class="model-line">'
        f'<span class="korean">{core.esc(english)}</span>'
        f'<span class="translation">{core.esc(japanese)}</span>'
        '</div>'
        for english, japanese in SUPPORT_EXPRESSIONS[number]
    )
    return core.section(
        "supporting-expressions",
        "Useful conversation support",
        "会話を支える表現",
        '<p class="section-subtitle"><span class="ko">Read an optional phrase only when it fits.</span>'
        '<span class="ja">必要な場面だけで使える補助表現を読みましょう。</span></p>'
        f'<div class="model-list">{lines}</div>',
    )


def spiral_page(number):
    spiral_id, level = SPIRAL_MARKERS[number]
    if number == 50:
        page = core.choose_words(
            "spiral-negq-01",
            "Recognize the negative question",
            "否定疑問を聞き分けよう",
            "Use the stated fact to choose the short answer.",
            "書かれた事実に合う短い答えを選びましょう。",
            (
                ("京都に行ったことがない。『京都に行ったことはないんですか？』", "Haven't you been to Kyoto? No, I ", "haven't", "have", "."),
                ("実は京都に行ったことがある。『京都に行ったことはないんですか？』", "Haven't you been to Kyoto? Actually, I ", "have", "haven't", "."),
                ("カナダに行ったことがない。『カナダに行ったことはないんですか？』", "Haven't you been to Canada? No, I ", "haven't", "have", "."),
                ("実はその美術館に行ったことがある。『その美術館に行ったことはないんですか？』", "Haven't you been to that museum? Actually, I ", "have", "haven't", "."),
            ),
        )
    elif number == 54:
        page = core.choose_words(
            "spiral-aspect-02",
            "Ongoing activity or present result?",
            "継続中の活動？ 今の完了結果？",
            "Choose the form that matches the time meaning.",
            "時間の意味に合う形を選びましょう。",
            (
                ("9時から{t}ずっと働いている{/t}。", "I've been ", "working", "finished", " since nine."),
                ("レポートを{t}もう終えた{/t}。", "I've ", "finished", "been writing", " the report."),
                ("8時から{t}ずっと掃除している{/t}。", "I've been ", "cleaning", "cleaned", " since eight."),
                ("メールを{t}もう送った{/t}。", "I've ", "sent", "been writing", " the email."),
            ),
        )
    else:
        page = core.reorder(
            "spiral-rel-01",
            (
                ("She's the person who called earlier.", "さっき電話をくれた人は彼女です。", "She's|the person|who called|earlier."),
                ("It's the thing that opens the door.", "ドアを開ける物です。", "It's|the thing|that opens|the door."),
                ("He's the one who sent the email.", "メールを送った人は彼です。", "He's|the one|who sent|the email."),
                ("It's the charger that charges the phone.", "携帯を充電する充電器です。", "It's the charger|that|charges|the phone."),
            ),
        ).replace("Build the sentence", "Retrieve the relative clause", 1).replace("文を組み立てよう", "関係節を思い出そう", 1)
    return page.replace(
        f'data-page-id="spiral-{spiral_id.casefold()}"',
        f'data-page-id="spiral-{spiral_id.casefold()}" data-spiral-id="{spiral_id}" data-spiral-level="{level}"',
        1,
    )


def translate_page(number, part, pattern):
    blocks = []
    for index, ((english, japanese, _), hints) in enumerate(
        zip(pattern, TRANSLATE_HINTS[number][part - 1], strict=True)
    ):
        blocks.append(
            '<div class="task-block"><div class="answer-box">'
            f'<span class="answer-label">{core.esc(core.strip_marks(japanese))}</span>'
            '<span class="answer-space as-input">'
            f'<input class="space-input" type="text" data-sync-id="p{part}-translate-{index}" '
            f'data-answer="{core.esc(core.strip_marks(english))}" autocomplete="off" spellcheck="false">'
            '</span>' + hint_html((hints,)) + '</div></div>'
        )
    page = core.section(
        f"p{part}-translate",
        "Say it in English",
        "英語にしよう",
        '<p class="section-subtitle"><span class="ko">Read the Japanese, then say it in English.</span>'
        '<span class="ja">日本語を見て、英語で言ってみましょう。</span></p>'
        '<div class="tutor-note">Type the learner\'s complete English sentence exactly as they say it.</div>'
        + "".join(blocks),
    )
    return page.replace(
        f'data-page-id="p{part}-translate"',
        f'data-page-id="p{part}-translate" data-scaffolding-contract="target-v2" data-support-stage="supported"',
        1,
    )


def write_page(number, part, pattern):
    prompt_en, prompt_ja = SPECS[number]["writes"][part - 1]
    return core.section(
        f"p{part}-write",
        "Make it yours",
        "自分の文にしよう",
        f'<p class="section-subtitle"><span class="ko">{core.esc(prompt_en)}</span>'
        f'<span class="ja">{core.esc(prompt_ja)}</span></p>'
        '<div class="tutor-note">Let the learner answer aloud before you capture it. React first, then add only a useful correction.</div>'
        + core.feedback_compose(f"p{part}-write", hint_html(OPEN_MENUS[number][part - 1])),
    )


def live_page(number):
    rendered = []
    for index, (kind, side, speaker, english, japanese) in enumerate(LIVE_SCENES[number]):
        avatar = core.live_avatar(speaker)
        bubble = "bubble me" if side == "me" else "bubble"
        if kind == "text":
            rendered.append(
                f'<div class="turn {side}">{avatar}<div class="{bubble}">'
                f'<span class="korean">{core.esc(english)}</span>'
                f'<span class="translation">{core.esc(japanese)}</span></div></div>'
            )
        else:
            raw_hints = LIVE_HINTS[number].get(index, ()) if side == "me" else ()
            hints = hint_html(raw_hints) if raw_hints else ""
            rendered.append(
                f'<div class="turn {side}">{avatar}<div class="{bubble}"><div class="answer-box tall">'
                f'<span class="answer-label">{core.esc(english)}<span class="task">{core.esc(japanese)}</span></span>'
                '<span class="answer-space as-input">'
                f'<textarea class="free-input" data-sync-id="live-{index}" rows="2" spellcheck="false" maxlength="2000"></textarea>'
                f'</span>{hints}</div></div></div>'
            )
    return core.section(
        "p3-freetalk",
        "Your real answer",
        "自分の答え",
        f'<p class="section-subtitle"><span class="ko">{core.esc(LESSONS[number]["prompt"][0])}</span>'
        f'<span class="ja">{core.esc(LESSONS[number]["prompt"][1])}</span></p>'
        '<div class="tutor-note">React naturally and follow the most interesting detail. Use today\'s pattern only if it fits.</div>'
        '<div class="dialogue">' + "".join(rendered) + "</div>",
    )


def page_id(page):
    match = re.search(r'data-page-id="([^"]+)"', page)
    return match.group(1) if match else ""


def customize_pages(number, data, pages):
    replacements = {
        "words-you-know": known_page(number),
        "p1-translate": translate_page(number, 1, data["p1"]),
        "p2-translate": translate_page(number, 2, data["p2"]),
        "p1-write": write_page(number, 1, data["p1"]),
        "p2-write": write_page(number, 2, data["p2"]),
        "p3-freetalk": live_page(number),
    }
    omitted = {f"p{part}-choose" for part in data.get("omit_choice", ())}
    result = []
    for page in pages:
        pid = page_id(page)
        if pid in omitted:
            continue
        if pid == "part3-intro" and number in SUPPORT_EXPRESSIONS:
            result.append(support_page(number))
        if pid == "part3-intro" and number in SPIRAL_MARKERS:
            result.append(spiral_page(number))
        rendered = replacements.get(pid, page)
        if pid in {"p3-model", "p3-complete", "in-the-wild"}:
            variant = "wild" if pid == "in-the-wild" else "model"
            role = DIALOGUES[number][variant][0]
            role_ja = ROLE_JA[role]
            rendered = rendered.replace("Please read the Me lines aloud.", "Please read your lines aloud.")
            rendered = rendered.replace("Say each complete Me line", "Say each complete line")
            rendered = rendered.replace(
                "私は相手役をします。Me のセリフを声に出して読んでください。",
                f"私は{role_ja}です。自分のセリフを声に出して読んでください。",
            )
            rendered = rendered.replace(
                "私は相手役をします。空欄に入る言葉も含めて、自分のセリフをまるごと言ってください。",
                f"私は{role_ja}です。空欄に入る言葉も含めて、自分のセリフをまるごと言ってください。",
            )
            rendered = rendered.replace(
                "私は相手役をします。空欄に入る言葉も含めて、Me のセリフをまるごと言ってください。",
                f"私は{role_ja}です。空欄に入る言葉も含めて、自分のセリフをまるごと言ってください。",
            )
        result.append(rendered)
    return result


@contextlib.contextmanager
def course_data():
    previous = (core.VOCAB, core.CANONICAL_SPECS, core.DIALOGUES, core.LIVE_SCENES)
    renderer_vocab = {
        number: (values["new"], values["assumed"], values["receptive"])
        for number, values in VOCAB.items()
    }
    core.VOCAB, core.CANONICAL_SPECS, core.DIALOGUES, core.LIVE_SCENES = (
        renderer_vocab,
        SPECS,
        DIALOGUES,
        LIVE_SCENES,
    )
    try:
        yield
    finally:
        core.VOCAB, core.CANONICAL_SPECS, core.DIALOGUES, core.LIVE_SCENES = previous


def build(number, data):
    source = PILOT.read_text(encoding="utf-8")
    head, foot = new_lesson.split_shell(source)
    slug = f'{number:02d}-{data["slug"]}'
    level = "A2 → B1" if number <= 53 else "B1"
    head = new_lesson.retarget(
        head,
        review_id=f"CORE-{number}",
        lesson_id=slug,
        level=level,
        title=data["title"],
        title_ko=data["ko"],
        title_ja=data["ja"],
        version="2026-08-20",
    )
    with course_data():
        head = set_vocab(head.replace('content="todo"', 'content="reviewed"'), number)
        head = core.set_proofread_status(head, "complete")
        pages = customize_pages(number, data, core.canonical_pages(number, data))
    out = TRACK / "courses" / COURSE / "lessons" / slug / "lesson.html"
    return out, new_lesson.redepth(head + "\n".join(pages) + foot, out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--lesson", type=int, action="append", choices=sorted(LESSONS))
    args = parser.parse_args()
    expected = set(range(48, 60))
    for label, values in (
        ("lessons", LESSONS),
        ("semantic specs", SPECS),
        ("vocabulary", VOCAB),
        ("dialogues", DIALOGUES),
        ("live scenes", LIVE_SCENES),
    ):
        if set(values) != expected:
            raise SystemExit(f"{label} do not exactly cover CORE-48--59")
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

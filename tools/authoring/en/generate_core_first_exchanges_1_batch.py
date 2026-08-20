#!/usr/bin/env python3
"""Generate the explicit Core 1-11 authoring batch from the approved Core shell.

This is intentionally a course-specific content source.  It reuses the approved
Core renderer, but every semantic choice, dialogue, transfer and native-use tip
for Core 1-11 is owned below rather than inferred from a model sentence.
"""

from __future__ import annotations

import argparse
import contextlib
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import generate_core_course_batch as core
import new_lesson


ROOT = new_lesson.REPO
TRACK = new_lesson.ENGLISH / "tracks/1-core-patterns"
COURSE = "core-first-exchanges-1"
PILOT = TRACK / "courses/core-first-exchanges-2/lessons/20-asking-for-help/lesson.html"


def rows(*items):
    return items


LESSONS = {
    1: dict(
        slug="hi-im-mina", title="Hi, I'm Mina", ko="안녕하세요, 미나예요", ja="こんにちは、ミナです",
        goal=("Introduce yourself in two common ways.", "よく使う二つの言い方で自己紹介しましょう。"),
        p1=rows(
            ("{t}Hi, I'm{/t} Mina.", "{t}こんにちは、{/t}ミナです。", "Hi,|I'm|Mina."),
            ("{t}Hi, I'm{/t} Ken.", "{t}こんにちは、{/t}ケンです。", "Hi,|I'm|Ken."),
            ("{t}Hi, I'm{/t} Yuki.", "{t}こんにちは、{/t}ユキです。", "Hi,|I'm|Yuki."),
            ("{t}Hi, I'm{/t} Emi.", "{t}こんにちは、{/t}エミです。", "Hi,|I'm|Emi."),
        ),
        p2=rows(
            ("{t}My name is{/t} Mina.", "{t}私の名前は{/t}ミナです。", "My name is|Mina."),
            ("{t}My name is{/t} Ken.", "{t}私の名前は{/t}ケンです。", "My name is|Ken."),
            ("{t}My name is{/t} Yuki.", "{t}私の名前は{/t}ユキです。", "My name is|Yuki."),
            ("{t}My name is{/t} Emi.", "{t}私の名前は{/t}エミです。", "My name is|Emi."),
        ),
        omit_choice=(1, 2),
        omit_reorder=(2,),
        rules=(("Keep I with am; in conversation, use the contraction I'm.", "I と am を一緒にし、会話では短縮形 I'm を使います。"), ("Keep My name is together, then add your name.", "My name is をひとまとまりにして、そのあとに名前を続けます。")),
        prompt=("Do you prefer using your first name or family name when you meet someone new? Why?", "初対面の人には、名字と名前のどちらで呼ばれたいですか？理由も教えてください。"),
    ),
    2: dict(
        slug="im-a-designer", title="I'm a designer", ko="저는 디자이너예요", ja="私はデザイナーです",
        goal=("Say your job with a or an.", "a または an を使って仕事を言いましょう。"),
        p1=rows(
            ("I'm {t}a{/t} designer.", "私は{t}デザイナー{/t}です。", "I'm|a designer."),
            ("I'm {t}a{/t} nurse.", "私は{t}看護師{/t}です。", "I'm|a nurse."),
            ("I'm {t}a{/t} teacher.", "私は{t}教師{/t}です。", "I'm|a teacher."),
            ("I'm {t}a{/t} chef.", "私は{t}料理人{/t}です。", "I'm|a chef."),
        ),
        p2=rows(
            ("I'm {t}an{/t} engineer.", "私は{t}エンジニア{/t}です。", "I'm|an engineer."),
            ("I'm {t}an{/t} artist.", "私は{t}アーティスト{/t}です。", "I'm|an artist."),
            ("I'm {t}an{/t} editor.", "私は{t}編集者{/t}です。", "I'm|an editor."),
            ("I'm {t}an{/t} office worker.", "私は{t}会社員{/t}です。", "I'm|an office worker."),
        ),
        omit_choice=(1,),
        omit_reorder=(1, 2),
        rules=(("Use a before a job that begins with a consonant sound.", "子音の音で始まる仕事の前には a を使います。"), ("Use an before a job that begins with a vowel sound.", "母音の音で始まる仕事の前には an を使います。")),
        prompt=("What job would be fun to try for one day? Why?", "一日だけ体験するなら、どんな仕事が楽しそうですか？理由も教えてください。"),
    ),
    3: dict(
        slug="i-live-in-tokyo", title="I live in Tokyo", ko="저는 도쿄에 살아요", ja="私は東京に住んでいます",
        goal=("Say where you're from and where you live now.", "出身地と今住んでいる場所を言いましょう。"),
        p1=rows(
            ("{t}I'm from{/t} Osaka.", "{t}出身は{/t}大阪です。", "I'm|from|Osaka."),
            ("{t}I'm from{/t} Tokyo.", "{t}出身は{/t}東京です。", "I'm|from|Tokyo."),
            ("{t}I'm from{/t} Kyoto.", "{t}出身は{/t}京都です。", "I'm|from|Kyoto."),
            ("{t}I'm from{/t} Fukuoka.", "{t}出身は{/t}福岡です。", "I'm|from|Fukuoka."),
        ),
        p2=rows(
            ("{t}I live in{/t} Tokyo now.", "今は東京に{t}住んでいます{/t}。", "I|live in|Tokyo|now."),
            ("{t}I live in{/t} Osaka now.", "今は大阪に{t}住んでいます{/t}。", "I|live in|Osaka|now."),
            ("{t}I live in{/t} Kyoto now.", "今は京都に{t}住んでいます{/t}。", "I|live in|Kyoto|now."),
            ("{t}I live in{/t} Nagoya now.", "今は名古屋に{t}住んでいます{/t}。", "I|live in|Nagoya|now."),
        ),
        omit_choice=(1,),
        rules=(("Keep I'm from together, then add the place you come from.", "I'm from をひとまとまりにして、そのあとに出身地を続けます。"), ("English order is I, then live in, then the place, with now at the end.", "英語では I、live in、場所の順にして、now を最後に置きます。")),
        prompt=("If you could live in another city or country for a year, where would you choose? Why?", "別の町や国に一年住めるなら、どこを選びますか？理由も教えてください。"),
    ),
    4: dict(
        slug="this-is-my-friend-leo", title="This is my friend, Leo", ko="제 친구 레오예요", ja="こちらは友だちのレオです",
        goal=("Introduce another person and add one fact about them.", "人を紹介して、その人について一つ情報を加えましょう。"),
        p1=rows(
            ("{t}This is my{/t} friend, Leo.", "{t}こちらは私の{/t}友だち、レオです。", "This is my|friend,|Leo."),
            ("{t}This is my{/t} friend, Anna.", "{t}こちらは私の{/t}友だち、アナです。", "This is my|friend,|Anna."),
            ("{t}This is my{/t} coworker, Ken.", "{t}こちらは私の{/t}同僚、ケンです。", "This is my|coworker,|Ken."),
            ("{t}This is my{/t} sister, Emi.", "{t}こちらは私の{/t}姉、エミです。", "This is my|sister,|Emi."),
        ),
        p2=rows(
            ("{t}He's{/t} {t}from{/t} Canada.", "{t}彼は{/t}カナダ{t}出身です{/t}。", "He's|from|Canada."),
            ("{t}She's{/t} {t}from{/t} Australia.", "{t}彼女は{/t}オーストラリア{t}出身です{/t}。", "She's|from|Australia."),
            ("{t}He's{/t} {t}from{/t} Japan.", "{t}彼は{/t}日本{t}出身です{/t}。", "He's|from|Japan."),
            ("{t}She's{/t} {t}from{/t} Korea.", "{t}彼女は{/t}韓国{t}出身です{/t}。", "She's|from|Korea."),
        ),
        omit_choice=(1,),
        rules=(("Use This is my, then say the relationship and the person's name.", "This is my のあとに関係と名前を続けます。"), ("After the name is known, use he's or she's instead of repeating it.", "名前を紹介したあとは、名前を繰り返さず he's または she's を使います。")),
        prompt=("Who is someone you'd like me to meet? What are they like?", "私に会わせたい人は誰ですか？どんな人ですか？"),
    ),
    5: dict(
        slug="is-this-your-bag", title="Is this your bag?", ko="이거 가방 맞아요?", ja="これはあなたのかばんですか？",
        goal=("Work out who an object belongs to.", "物が誰のものか確かめましょう。"),
        p1=rows(
            ("{t}Is this your{/t} bag?", "{t}これはあなたのかばんですか{/t}？", "Is this|your bag?"),
            ("{t}Is this your{/t} phone?", "{t}これはあなたの携帯ですか{/t}？", "Is this|your phone?"),
            ("{t}Is this your{/t} ticket?", "{t}これはあなたのチケットですか{/t}？", "Is this|your ticket?"),
            ("{t}Is this your{/t} key?", "{t}これはあなたの鍵ですか{/t}？", "Is this|your key?"),
        ),
        omit_reorder=(1,),
        p2=rows(
            ("Yes, {t}that one's mine{/t}.", "はい、{t}それは私のです{/t}。", "Yes,|that one's|mine."),
            ("Yes, {t}this one's mine{/t}.", "はい、{t}これは私のです{/t}。", "Yes,|this one's|mine."),
            ("No, {t}that one's yours{/t}.", "いいえ、{t}それはあなたのです{/t}。", "No,|that one's|yours."),
            ("No, {t}this one's yours{/t}.", "いいえ、{t}これはあなたのです{/t}。", "No,|this one's|yours."),
        ),
        rules=(("Move is before this to turn the statement into a question.", "文を質問にするときは is を this の前に移動します。"), ("Use mine without a noun when the object is already clear.", "どの物か分かっているときは、名詞を繰り返さず mine を使います。")),
        prompt=("What's one thing you often lose or forget? Where do you usually find it?", "よくなくしたり忘れたりする物は何ですか？たいていどこで見つかりますか？"),
    ),
    6: dict(
        slug="are-you-a-student", title="Are you a student?", ko="학생이에요?", ja="学生ですか？",
        goal=("Ask what someone is and answer briefly.", "相手の仕事などをたずね、短く答えましょう。"),
        p1=rows(
            ("{t}Are you{/t} a student?", "{t}学生ですか{/t}？", "Are you|a student?"),
            ("{t}Are you{/t} a teacher?", "{t}教師ですか{/t}？", "Are you|a teacher?"),
            ("{t}Are you{/t} a designer?", "{t}デザイナーですか{/t}？", "Are you|a designer?"),
            ("{t}Are you{/t} an engineer?", "{t}エンジニアですか{/t}？", "Are you|an engineer?"),
        ),
        omit_reorder=(1,),
        p2=rows(
            ("{t}Yes, I am.{/t} I'm a student.", "{t}はい、そうです。{/t}学生です。", "Yes,|I am.|I'm a student."),
            ("{t}No, I'm not.{/t} I'm a nurse.", "{t}いいえ、違います。{/t}看護師です。", "No,|I'm not.|I'm a nurse."),
            ("{t}Yes, I am.{/t} I'm an engineer.", "{t}はい、そうです。{/t}エンジニアです。", "Yes,|I am.|I'm an engineer."),
            ("{t}No, I'm not.{/t} I'm a designer.", "{t}いいえ、違います。{/t}デザイナーです。", "No,|I'm not.|I'm a designer."),
        ),
        rules=(("Move are before you to ask the question; keep the job with a or an.", "質問では are を you の前に移動し、仕事には a または an をつけます。"), ("Repeat be in a short answer: Yes, I am or No, I'm not.", "短い答えでも be を繰り返し、Yes, I am または No, I'm not と言います。")),
        prompt=("What job did you want when you were a child? Has that changed?", "子どものころ、どんな仕事に就きたかったですか？今は変わりましたか？"),
    ),
    7: dict(
        slug="theres-a-cafe-near-here", title="There's a café near here", ko="근처에 카페가 있어요", ja="この近くにカフェがあります",
        goal=("Say that a place exists nearby and where it is.", "近くにある場所と、その位置を言いましょう。"),
        p1=rows(
            ("{t}There's a{/t} café near here.", "この近くに{t}カフェがあります{/t}。", "There's|a café|near here."),
            ("{t}There's a{/t} bank near here.", "この近くに{t}銀行があります{/t}。", "There's|a bank|near here."),
            ("{t}There's a{/t} station near here.", "この近くに{t}駅があります{/t}。", "There's|a station|near here."),
            ("{t}There's a{/t} hotel near here.", "この近くに{t}ホテルがあります{/t}。", "There's|a hotel|near here."),
        ),
        p2=rows(
            ("{t}It's next to{/t} the bank.", "{t}銀行の隣です{/t}。", "It's|next to|the bank."),
            ("{t}It's next to{/t} the station.", "{t}駅の隣です{/t}。", "It's|next to|the station."),
            ("{t}It's next to{/t} the hotel.", "{t}ホテルの隣です{/t}。", "It's|next to|the hotel."),
            ("{t}It's next to{/t} the café.", "{t}カフェの隣です{/t}。", "It's|next to|the café."),
        ),
        omit_choice=(1,),
        rules=(("Use There's a as one chunk to introduce one nearby place.", "近くに場所が一つあると伝えるときは There's a をひとまとまりで使います。"), ("Keep next to with the place; it means immediately beside it.", "next to は場所と一緒に使い、すぐ隣という意味です。")),
        prompt=("What's one place you wish you had near your home? Why?", "家の近くにあったらいいと思う場所は何ですか？理由も教えてください。"),
    ),
    8: dict(
        slug="its-cold-today", title="It's cold today", ko="오늘은 추워요", ja="今日は寒いです",
        goal=("Ask and say what today's weather is like.", "今日の天気についてたずね、答えましょう。"),
        p1=rows(
            ("{t}Is it{/t} cold today?", "今日は{t}寒いですか{/t}？", "Is it|cold|today?"),
            ("{t}Is it{/t} hot today?", "今日は{t}暑いですか{/t}？", "Is it|hot|today?"),
            ("{t}Is it{/t} sunny today?", "今日は{t}晴れていますか{/t}？", "Is it|sunny|today?"),
            ("{t}Is it{/t} rainy today?", "今日は{t}雨ですか{/t}？", "Is it|rainy|today?"),
        ),
        p2=rows(
            ("{t}Yes, it is.{/t} It's very cold.", "{t}はい、そうです。{/t}とても寒いです。", "Yes,|it is.|It's very|cold."),
            ("{t}No, it isn't.{/t} It's not hot.", "{t}いいえ、違います。{/t}暑くありません。", "No,|it isn't.|It's not|hot."),
            ("{t}Yes, it is.{/t} It's very sunny.", "{t}はい、そうです。{/t}とてもよく晴れています。", "Yes,|it is.|It's very|sunny."),
            ("{t}No, it isn't.{/t} It's not rainy.", "{t}いいえ、違います。{/t}雨ではありません。", "No,|it isn't.|It's not|rainy."),
        ),
        omit_reorder=(2,),
        rules=(("Weather questions still need it: put is before it.", "天気の質問にも it が必要で、is を it の前に置きます。"), ("Answer with it is after yes and it isn't after no.", "yes のあとは it is、no のあとは it isn't で答えます。")),
        prompt=("What kind of weather gives you energy? What do you like to do then?", "どんな天気だと元気が出ますか？そんな日は何をするのが好きですか？"),
    ),
    9: dict(
        slug="two-coffees-please", title="Two coffees, please", ko="커피 두 잔 주세요", ja="コーヒーを二つお願いします",
        goal=("Order a counted item and correct the quantity if needed.", "数をつけて注文し、必要なら個数を直しましょう。"),
        p1=rows(
            ("Two coffee{t}s{/t}, please.", "コーヒーを{t}二つ{/t}お願いします。", "Two|coffees,|please."),
            ("Two ticket{t}s{/t}, please.", "チケットを{t}二枚{/t}お願いします。", "Two|tickets,|please."),
            ("Three bag{t}s{/t}, please.", "かばんを{t}三つ{/t}お願いします。", "Three|bags,|please."),
            ("Four water{t}s{/t}, please.", "水を{t}四つ{/t}お願いします。", "Four|waters,|please."),
        ),
        p2=rows(
            ("{t}Actually,{/t} {t}just one{/t} coffee, thanks.", "{t}やっぱり、{/t}コーヒーは{t}一つだけ{/t}お願いします。", "Actually,|just one|coffee,|thanks."),
            ("{t}Actually,{/t} {t}just one{/t} ticket, thanks.", "{t}やっぱり、{/t}チケットは{t}一枚だけ{/t}お願いします。", "Actually,|just one|ticket,|thanks."),
            ("{t}Actually,{/t} {t}just one{/t} bag, thanks.", "{t}やっぱり、{/t}かばんは{t}一つだけ{/t}お願いします。", "Actually,|just one|bag,|thanks."),
            ("{t}Actually,{/t} {t}just one{/t} water, thanks.", "{t}やっぱり、{/t}水は{t}一つだけ{/t}お願いします。", "Actually,|just one|water,|thanks."),
        ),
        omit_choice=(1,),
        rules=(("After two or more, add -s to the item even though the number is already clear.", "二つ以上なら、数が分かっていても品物に -s をつけます。"), ("After one, use the singular item with no -s.", "one のあとは -s のない単数形を使います。")),
        prompt=("What do you usually order at a café? Do you ever change your order?", "カフェではいつも何を注文しますか？注文を変えることはありますか？"),
    ),
    10: dict(
        slug="the-cafe-on-the-corner", title="The café on the corner", ko="모퉁이에 있는 그 카페", ja="角にあるそのカフェ",
        goal=("Mention something new, then refer back to it.", "新しいものを話題に出してから、同じものをもう一度指しましょう。"),
        p1=rows(
            ("{t}There's a{/t} café on the corner.", "角に{t}カフェがあります{/t}。", "There's|a café|on the corner."),
            ("{t}There's a{/t} bank on this street.", "この通りに{t}銀行があります{/t}。", "There's|a bank|on this street."),
            ("{t}There's a{/t} restaurant near the station.", "駅の近くに{t}レストランがあります{/t}。", "There's|a restaurant|near the station."),
            ("{t}There's a{/t} shop next to the bank.", "銀行の隣に{t}店があります{/t}。", "There's|a shop|next to the bank."),
        ),
        p2=rows(
            ("{t}The{/t} café is open until six.", "{t}その{/t}カフェは6時まで開いています。", "The café|is open|until six."),
            ("{t}The{/t} bank is open until five.", "{t}その{/t}銀行は5時まで開いています。", "The bank|is open|until five."),
            ("{t}The{/t} restaurant is open until midnight.", "{t}その{/t}レストランは深夜0時まで開いています。", "The restaurant|is open|until midnight."),
            ("{t}The{/t} shop is open until eight.", "{t}その{/t}店は8時まで開いています。", "The shop|is open|until eight."),
        ),
        omit_choice=(1,),
        rules=(("Use a when you introduce one place for the first time.", "場所を初めて話題に出すときは a を使います。"), ("Use the when both people now know which place you mean.", "どの場所か二人とも分かっているときは the を使います。")),
        prompt=("Is there a café, restaurant, or shop near you that you recommend? What makes it special?", "近くにおすすめのカフェ、レストラン、店はありますか？どんなところが特別ですか？"),
    ),
    11: dict(
        slug="wheres-the-station", title="Where's the station?", ko="역이 어디예요?", ja="駅はどこですか？",
        goal=("Ask where a place is and describe its location.", "場所をたずねて、その位置を説明しましょう。"),
        p1=rows(
            ("{t}Where's the{/t} station?", "{t}駅はどこですか{/t}？", "Where's|the station?"),
            ("{t}Where's the{/t} bank?", "{t}銀行はどこですか{/t}？", "Where's|the bank?"),
            ("{t}Where's the{/t} hotel?", "{t}ホテルはどこですか{/t}？", "Where's|the hotel?"),
            ("{t}Where's the{/t} café?", "{t}カフェはどこですか{/t}？", "Where's|the café?"),
        ),
        omit_reorder=(1,),
        p2=rows(
            ("{t}It's behind{/t} the post office.", "{t}郵便局の後ろです{/t}。", "It's|behind|the post office."),
            ("{t}It's behind{/t} the bank.", "{t}銀行の後ろです{/t}。", "It's|behind|the bank."),
            ("{t}It's behind{/t} the hotel.", "{t}ホテルの後ろです{/t}。", "It's|behind|the hotel."),
            ("{t}It's behind{/t} the café.", "{t}カフェの後ろです{/t}。", "It's|behind|the café."),
        ),
        rules=(("Keep Where's together, then add the specific place with the.", "Where's をひとまとまりにして、the をつけた場所を続けます。"), ("Keep the place phrase together: behind the post office.", "場所の表現は behind the post office のようにひとまとまりで覚えます。")),
        prompt=("What's one place in your area that's hard to find? How would you explain where it is?", "近所で見つけにくい場所はどこですか？場所をどう説明しますか？"),
    ),
}


VOCAB = {
    1: dict(new="name|名前; Nice to meet you.|はじめまして。", recycled="", assumed="hi|こんにちは; hello|こんにちは; Mina|ミナ; Ken|ケン; Yuki|ユキ; Emi|エミ", receptive="What's your name?|お名前は？; first name|名前; family name|名字; easy to remember|覚えやすい"),
    2: dict(new="designer|デザイナー; engineer|エンジニア; nurse|看護師; artist|アーティスト; teacher|教師; chef|料理人; editor|編集者; office worker|会社員", recycled="", assumed="job|仕事", receptive="What do you do?|お仕事は？; design|デザイン分野; work in|～の分野で働く"),
    3: dict(new="live|住む; from|出身の; now|今", recycled="", assumed="Tokyo|東京; Osaka|大阪; Kyoto|京都; Nagoya|名古屋; Fukuoka|福岡", receptive="Where are you from?|出身はどこですか？; originally|もともと; city|町; country|国; for a year|一年"),
    4: dict(new="friend|友だち; coworker|同僚; sister|姉・妹; Canada|カナダ; Australia|オーストラリア; Korea|韓国; Nice to meet you too.|こちらこそ、はじめまして。", recycled="name|名前|CORE-1; from|出身の|CORE-3; Nice to meet you.|はじめまして。|CORE-1", assumed="Japan|日本; Leo|レオ; Anna|アナ; Ken|ケン; Emi|エミ", receptive="Nice to see you.|また会えてうれしいです。; kind|親切な; funny|面白い"),
    5: dict(new="mine|私のもの; yours|あなたのもの; key|鍵; bag|かばん; ticket|チケット", recycled="", assumed="phone|携帯; pen|ペン; Thank you.|ありがとうございます。", receptive="Sorry, my mistake.|すみません、間違えました。; I think|～だと思います; umbrella|傘"),
    6: dict(new="student|学生", recycled="designer|デザイナー|CORE-2; engineer|エンジニア|CORE-2; nurse|看護師|CORE-2; teacher|教師|CORE-2; Nice to meet you too.|こちらこそ、はじめまして。|CORE-4", assumed="job|仕事", receptive="Actually|実は; doctor|医師; changed|変わった"),
    7: dict(new="near|近く; here|ここ; next to|隣に; bank|銀行; café|カフェ; station|駅; hotel|ホテル; That's right.|その通りです。", recycled="", assumed="place|場所", receptive="Is there ... around here?|この近くに…はありますか？; supermarket|スーパー; park|公園; gym|ジム"),
    8: dict(new="cold|寒い; hot|暑い; sunny|晴れた; rainy|雨の; Not really.|あまり。", recycled="", assumed="today|今日; very|とても", receptive="How's the weather?|天気はどうですか？; really|本当に; go outside|外に出る"),
    9: dict(new="actually|やっぱり; just|ただ・だけ; please|お願いします; thanks|ありがとう; coffee|コーヒー; water|水; That's all, thanks.|以上です、ありがとうございます。", recycled="ticket|チケット|CORE-5; bag|かばん|CORE-5", assumed="one|1; two|2; three|3; four|4", receptive="Anything else?|ほかには？; tea|お茶; a snack|軽食; change my order|注文を変える"),
    10: dict(new="corner|角; open|開いている; until|まで; restaurant|レストラン; shop|店; street|通り; midnight|深夜0時; the same one|同じもの", recycled="café|カフェ|CORE-7; bank|銀行|CORE-7; station|駅|CORE-7; near|近く|CORE-7; next to|隣に|CORE-7", assumed="six|6; five|5; eight|8", receptive="you know the one|例の場所; that|その; service|サービス"),
    11: dict(new="behind|後ろに; post office|郵便局; It's about five minutes.|5分くらいです。", recycled="station|駅|CORE-7; bank|銀行|CORE-7; hotel|ホテル|CORE-7; café|カフェ|CORE-7; next to|隣に|CORE-7; restaurant|レストラン|CORE-10", assumed="place|場所", receptive="How do I get there?|どう行けばいいですか？; park|公園"),
}


KNOWN_WORDS = {
    1: (("ハロー", "hello"), ("ネーム", "name"), ("ハイ", "hi")),
    2: (("デザイナー", "designer"), ("エンジニア", "engineer"), ("アーティスト", "artist")),
    3: (("東京", "Tokyo"), ("大阪", "Osaka"), ("京都", "Kyoto")),
    4: (("カナダ", "Canada"), ("オーストラリア", "Australia"), ("日本", "Japan")),
    5: (("バッグ", "bag"), ("チケット", "ticket"), ("ペン", "pen")),
    6: (("デザイナー", "designer"), ("エンジニア", "engineer"), ("ナース", "nurse")),
    7: (("カフェ", "café"), ("ホテル", "hotel"), ("ステーション", "station")),
    8: (("ホット", "hot"), ("レイニー", "rainy"), ("トゥデイ", "today")),
    9: (("コーヒー", "coffee"), ("チケット", "ticket"), ("バッグ", "bag")),
    10: (("カフェ", "café"), ("レストラン", "restaurant"), ("バンク", "bank")),
    11: (("ステーション", "station"), ("ホテル", "hotel"), ("カフェ", "café")),
}


# Each tuple is a row-specific vocabulary menu.  These are editorial choices:
# pattern words are never hinted, and every non-target content word needed for
# a closed translation appears on its own row.
TRANSLATE_HINTS = {
    1: (("ミナ:Mina", "ケン:Ken", "ユキ:Yuki", "エミ:Emi"), ("ミナ:Mina", "ケン:Ken", "ユキ:Yuki", "エミ:Emi")),
    2: (("デザイナー:designer", "看護師:nurse", "教師:teacher", "料理人:chef"), ("エンジニア:engineer", "アーティスト:artist", "編集者:editor", "会社員:office worker")),
    3: (("大阪:Osaka", "東京:Tokyo", "京都:Kyoto", "福岡:Fukuoka"), ("東京:Tokyo", "大阪:Osaka", "京都:Kyoto", "名古屋:Nagoya")),
    4: (("友だち:friend; レオ:Leo", "友だち:friend; アナ:Anna", "同僚:coworker; ケン:Ken", "姉:sister; エミ:Emi"), ("カナダ:Canada", "オーストラリア:Australia", "日本:Japan", "韓国:Korea")),
    5: (("かばん:bag", "携帯:phone", "チケット:ticket", "鍵:key"), ("", "", "", "")),
    6: (("学生:student", "教師:teacher", "デザイナー:designer", "エンジニア:engineer"), ("学生:student", "看護師:nurse", "エンジニア:engineer", "デザイナー:designer")),
    7: (("カフェ:café", "銀行:bank", "駅:station", "ホテル:hotel"), ("銀行:bank", "駅:station", "ホテル:hotel", "カフェ:café")),
    8: (("寒い:cold", "暑い:hot", "晴れた:sunny", "雨の:rainy"), ("寒い:cold", "暑い:hot", "晴れた:sunny", "雨の:rainy")),
    9: (("コーヒー:coffee", "チケット:ticket", "かばん:bag", "水:water"), ("コーヒー:coffee", "チケット:ticket", "かばん:bag", "水:water")),
    10: (("カフェ:café; 角:corner", "銀行:bank; 通り:street", "レストラン:restaurant; 駅:station", "店:shop; 銀行:bank"), ("カフェ:café; 6時:six", "銀行:bank; 5時:five", "レストラン:restaurant; 深夜0時:midnight", "店:shop; 8時:eight")),
    11: (("駅:station", "銀行:bank", "ホテル:hotel", "カフェ:café"), ("郵便局:post office", "銀行:bank", "ホテル:hotel", "カフェ:café")),
}


# Supported translations keep lexical help while the learner produces today's
# pattern. CORE-5 Part 2 is the first deliberate checkpoint: mine/yours are the
# target contrast itself, so showing them as hints would give away the answer.
TRANSLATE_STAGES = {
    number: ("supported", "supported") for number in LESSONS
}
TRANSLATE_STAGES[5] = ("supported", "checkpoint")


OPEN_MENUS = {
    1: (("ミナ:Mina", "ケン:Ken", "ユキ:Yuki"), ("ミナ:Mina", "ケン:Ken", "ユキ:Yuki")),
    2: (("デザイナー:designer", "看護師:nurse", "教師:teacher"), ("エンジニア:engineer", "アーティスト:artist", "編集者:editor")),
    3: (("大阪:Osaka", "東京:Tokyo", "京都:Kyoto"), ("東京:Tokyo", "大阪:Osaka", "名古屋:Nagoya")),
    4: (("友だち:friend", "同僚:coworker", "姉・妹:sister"), ("カナダ:Canada", "オーストラリア:Australia", "日本:Japan")),
    5: (("かばん:bag", "携帯:phone", "鍵:key"), ("私のもの:mine", "あなたのもの:yours")),
    6: (("学生:student", "教師:teacher", "エンジニア:engineer"), ("看護師:nurse", "教師:teacher", "デザイナー:designer")),
    7: (("カフェ:café", "銀行:bank", "ホテル:hotel"), ("銀行:bank", "駅:station", "ホテル:hotel")),
    8: (("寒い:cold", "暑い:hot", "晴れた:sunny"), ("寒い:cold", "暑い:hot", "晴れた:sunny")),
    9: (("コーヒー:coffee", "チケット:ticket", "水:water"), ("コーヒー:coffee", "チケット:ticket", "かばん:bag")),
    10: (("カフェ:café", "銀行:bank", "レストラン:restaurant"), ("6時:six", "5時:five", "深夜0時:midnight")),
    11: (("駅:station", "銀行:bank", "ホテル:hotel"), ("郵便局:post office", "銀行:bank", "ホテル:hotel")),
}


def semantic_spec(meanings, writes, choices, rules, tip):
    return dict(meanings=meanings, writes=writes, choices=choices, rules=rules, tip=tip)


SPECS = {
    1: semantic_spec(
        (("Use this friendly opener when you say your name.", "親しみのある言い方で名前を伝えるときに使います。"), ("Use this clear form when you state your name.", "名前をはっきり伝えるときに使います。")),
        (("Now use “Hi, I'm ___.” to introduce yourself.", "では、「Hi, I'm ___.」を使って自己紹介してください。"), ("Now use “My name is ___.” to introduce yourself.", "では、「My name is ___.」を使って自己紹介してください。")),
        ((), ()),
        (("Contract I am in conversation", "会話では I am を短くする", "I am → <b>I'm</b>", "Spoken contraction", "会話の短縮形", ("Hi, <b>I am</b> Mina. → Hi, <b>I'm</b> Mina.", "<b>I am</b> Ken. → <b>I'm</b> Ken.")), ("Keep My name is together", "My name is をひとまとまりに", "<b>My name is</b> + 名前", "Clear introduction", "名前をはっきり伝える", ("<b>My name is</b> Mina.", "<b>My name is</b> Yuki."))),
        ("Hi or Hello?", "Hi と Hello", "Both are natural. Hi is friendly and casual; Hello is a little more neutral.", "どちらも自然です。Hi は親しみのあるカジュアルな言い方で、Hello は少し中立的です。", ("Friendly and casual", "親しみのある場面", "Hi, I'm Mina.", "こんにちは、ミナです。"), ("Neutral", "幅広い場面", "Hello, I'm Mina.", "こんにちは、ミナです。")),
    ),
    2: semantic_spec(
        (("Use a before a job that starts with a consonant sound.", "子音の音で始まる仕事を言うときは a を使います。"), ("Use an before a job that starts with a vowel sound.", "母音の音で始まる仕事を言うときは an を使います。")),
        (("Now use “I'm a ___.” to name a job that starts with a consonant sound.", "では、「I'm a ___.」を使って、子音の音で始まる仕事を一つ言ってください。"), ("Now use “I'm a/an ___.” to tell me your real job.", "では、「I'm a/an ___.」を使って、自分の本当の仕事を教えてください。")),
        (
            tuple((jp, "I'm ", "a", "an", suffix) for jp, suffix in (("私は{t}デザイナー{/t}です。", " designer."), ("私は{t}看護師{/t}です。", " nurse."), ("私は{t}教師{/t}です。", " teacher."), ("私は{t}料理人{/t}です。", " chef."))),
            (
                ("私は{t}デザイナー{/t}です。", "I'm ", "a", "an", " designer."),
                ("私は{t}エンジニア{/t}です。", "I'm ", "an", "a", " engineer."),
                ("私は{t}教師{/t}です。", "I'm ", "a", "an", " teacher."),
                ("私は{t}アーティスト{/t}です。", "I'm ", "an", "a", " artist."),
            ),
        ),
        (("Use a before a consonant sound", "子音の音の前には a", "I'm + <b>a</b> + 子音の音で始まる仕事", "Consonant sound", "子音の音", ("I'm <b>a</b> designer.", "I'm <b>a</b> nurse.")), ("Use an before a vowel sound", "母音の音の前には an", "I'm + <b>an</b> + 母音の音で始まる仕事", "Vowel sound", "母音の音", ("I'm <b>an</b> engineer.", "I'm <b>an</b> artist."))),
        ("A job or a field?", "仕事名と分野", "Name a specific job with “I'm a designer.” Name the broader field with “I work in design.”", "具体的な仕事名は「I'm a designer.」、広い分野は「I work in design.」で伝えます。", ("Specific job", "具体的な仕事名", "I'm a designer.", "デザイナーです。"), ("Broader field", "広い分野", "I work in design.", "デザインの分野で働いています。")),
    ),
}


def _simple_spec(number, meanings, writes, choices, rule_details, tip):
    """Add an explicitly supplied specification; no pedagogical field is inferred."""
    SPECS[number] = semantic_spec(meanings, writes, choices, rule_details, tip)


_simple_spec(3,
    (("Use this to name the place you come from.", "出身地を伝えるときに使います。"), ("Use this to say where you live at the present time.", "今住んでいる場所を伝えるときに使います。")),
    (("Now use “I'm from ___.” to say where you're really from.", "では、「I'm from ___.」を使って、本当の出身地を言ってください。"), ("Now use “I live in ___ now.” to say where you really live.", "では、「I live in ___ now.」を使って、今本当に住んでいる場所を言ってください。")),
    (tuple((jp, "I'm ", "from", "in", suffix) for jp, suffix in (("{t}出身は{/t}大阪です。", " Osaka."), ("{t}出身は{/t}東京です。", " Tokyo."), ("{t}出身は{/t}京都です。", " Kyoto."), ("{t}出身は{/t}福岡です。", " Fukuoka."))), (
        ("{t}大阪出身です{/t}。", "", "I'm from", "I live in", " Osaka."),
        ("今は{t}東京に住んでいます{/t}。", "", "I live in", "I'm from", " Tokyo now."),
        ("{t}京都出身です{/t}。", "", "I'm from", "I live in", " Kyoto."),
        ("今は{t}名古屋に住んでいます{/t}。", "", "I live in", "I'm from", " Nagoya now."),
    )),
    (("Keep from with the origin", "出身地の前に from", "I'm + <b>from</b> + 出身地", "Origin", "出身地", ("I'm <b>from</b> Osaka.", "I'm <b>from</b> Kyoto.")), ("Put the verb before the place", "動詞を場所の前に", "I + <b>live in</b> + 場所 + now", "Current home", "今住んでいる場所", ("I <b>live in</b> Tokyo now.", "I <b>live in</b> Nagoya now."))),
    ("From or originally from?", "from と originally from", "Use “from” for a simple origin. Add “originally” when you want to stress where your story began.", "出身地を簡単に言うなら「from」を使います。最初にいた場所を強調するなら「originally」を加えます。", ("Simple origin", "出身地を簡単に", "I'm from Osaka.", "大阪出身です。"), ("Emphasize the starting point", "最初の場所を強調", "I'm originally from Osaka.", "もともとは大阪出身です。")),
)

_simple_spec(4,
    (("Use this to present another person by name.", "人を名前と一緒に紹介するときに使います。"), ("Use he or she to add a fact after the introduction.", "紹介したあと、he または she でその人の情報を加えるときに使います。")),
    (("Now use “This is my ___, ___.” to introduce someone you know.", "では、「This is my ___, ___.」を使って、知っている人を紹介してください。"), ("Now use “He's/She's from ___.” to add one true fact about that person.", "では、「He's/She's from ___.」を使って、その人の本当の出身地を加えてください。")),
    (tuple((jp, "This is ", "my", "your", suffix) for jp, suffix in (("こちらは{t}私の{/t}友だち、レオです。", " friend, Leo."), ("こちらは{t}私の{/t}友だち、アナです。", " friend, Anna."), ("こちらは{t}私の{/t}同僚、ケンです。", " coworker, Ken."), ("こちらは{t}私の{/t}姉、エミです。", " sister, Emi."))), (("{t}彼は{/t}カナダ出身です。", "", "He's", "She's", " from Canada."), ("{t}彼女は{/t}オーストラリア出身です。", "", "She's", "He's", " from Australia."), ("{t}彼は{/t}日本出身です。", "", "He's", "She's", " from Japan."), ("{t}彼女は{/t}韓国出身です。", "", "She's", "He's", " from Korea."))),
    (("Present the person with This is my", "This is my で人を紹介", "<b>This is my</b> + 関係 + 名前", "Introduce a person", "人を紹介する", ("<b>This is my friend</b>, Leo.", "<b>This is my coworker</b>, Ken.")), ("Replace the known name", "紹介した名前を代名詞に", "男性: <b>He's</b> / 女性: <b>She's</b> + from + 場所", "Add one fact", "情報を一つ加える", ("<b>He's</b> from Canada.", "<b>She's</b> from Australia."))),
    ("Meet or see?", "meet と see", "Say “Nice to meet you” the first time. Say “Nice to see you” when you meet the person again.", "初対面では「Nice to meet you」と言います。再会したときは「Nice to see you」と言います。", ("First meeting", "初対面", "Nice to meet you.", "はじめまして。"), ("Meeting again", "再会", "Nice to see you.", "また会えてうれしいです。")),
)

_simple_spec(5,
    (("Use this to check whether an object belongs to the other person.", "物が相手のものか確かめるときに使います。"), ("Use mine when you answer without repeating the object.", "物の名前を繰り返さず、自分のものだと答えるときに mine を使います。")),
    (("Now use “Is this your ___?” to ask about one real object near you.", "では、「Is this your ___?」を使って、近くの物について聞いてください。"), ("Now use “That one's mine/yours.” to say who one object belongs to.", "では、「That one's mine/yours.」を使って、物が誰のものか言ってください。")),
    ((("{t}これはあなたのかばんですか{/t}？", "", "Is this", "This is", " your bag?"), ("{t}これはあなたの携帯です。{/t}", "", "This is", "Is this", " your phone."), ("{t}これはあなたのチケットですか{/t}？", "", "Is this", "This is", " your ticket?"), ("{t}これはあなたの鍵です。{/t}", "", "This is", "Is this", " your key.")), (("はい、{t}それは私のです{/t}。", "Yes, that one's ", "mine", "my", "."), ("はい、{t}これは私のです{/t}。", "Yes, this one's ", "mine", "my", "."), ("いいえ、{t}それはあなたのです{/t}。", "No, that one's ", "yours", "your", "."), ("いいえ、{t}これはあなたのです{/t}。", "No, this one's ", "yours", "your", "."))),
    (("Move is to the front", "is を文の先頭へ", "This is your bag. → <b>Is this</b> your bag?", "Be question", "be の質問", ("<b>Is this</b> your bag?", "<b>Is this</b> your phone?")), ("Use mine without a noun", "名詞なしで mine", "that one + is + <b>mine</b>", "Object already known", "物が分かっている", ("That one's <b>mine</b>.", "This one's <b>mine</b>."))),
    ("Direct or softer?", "直接言う・やわらかく言う", "“That's mine” is direct. Add “I think” when you are not completely sure.", "「That's mine」は直接的です。確信がないときは「I think」を加えてやわらかく言います。", ("Certain", "確信がある", "That's mine.", "それは私のです。"), ("Not completely sure", "確信がない", "I think that's mine.", "それは私のだと思います。")),
)

_simple_spec(6,
    (("Use this to ask whether a job or role is true for someone.", "仕事や立場が相手に当てはまるか聞くときに使います。"), ("Use Yes, I am or No, I'm not, then add the correct job.", "Yes, I am または No, I'm not で答え、そのあとに正しい仕事を加えます。")),
    (("Now use “Are you a/an ___?” to ask me one real job question.", "では、「Are you a/an ___?」を使って、私の仕事について一つ質問してください。"), ("Answer “Are you a student?” with “Yes, I am” or “No, I'm not,” then add your real job.", "「Are you a student?」に「Yes, I am」か「No, I'm not」で答え、本当の仕事を加えてください。")),
    ((
        ("{t}学生ですか{/t}？", "", "Are you", "Is she", " a student?"),
        ("彼女は{t}教師ですか{/t}？", "", "Is she", "Are you", " a teacher?"),
        ("{t}デザイナーですか{/t}？", "", "Are you", "Is he", " a designer?"),
        ("彼は{t}エンジニアですか{/t}？", "", "Is he", "Are you", " an engineer?"),
    ), (
        ("{t}はい、そうです。{/t}学生です。", "Yes, I ", "am", "do", ". I'm a student."),
        ("{t}いいえ、違います。{/t}看護師です。", "No, I'm ", "not", "don't", ". I'm a nurse."),
        ("{t}はい、そうです。{/t}エンジニアです。", "Yes, I ", "am", "do", ". I'm an engineer."),
        ("{t}いいえ、違います。{/t}デザイナーです。", "No, I'm ", "not", "don't", ". I'm a designer."),
    )),
    (("Move are before you", "are を you の前に", "<b>Are you</b> + a / an + 仕事?", "Ask about a role", "仕事・立場を聞く", ("<b>Are you</b> a student?", "<b>Are you</b> an engineer?")), ("Repeat be in the answer", "答えでも be を使う", "No, + I <b>am not</b>. / Yes, + I <b>am</b>.", "Complete short answer", "短い答え", ("No, <b>I'm not</b>.", "Yes, <b>I am</b>."))),
    ("No, I'm not or Actually, no?", "No, I'm not と Actually, no", "Both are natural. “Actually, no” gently corrects an assumption before you add the right information.", "どちらも自然です。「Actually, no」は、思い込みをやわらかく訂正してから正しい情報を加える言い方です。", ("Direct answer", "直接答える", "No, I'm not.", "いいえ、違います。"), ("Gentle correction", "やわらかく訂正", "Actually, no. I'm a nurse.", "実は違います。看護師です。")),
)

_simple_spec(7,
    (("Use this to introduce one place that exists nearby.", "近くに場所が一つあると伝えるときに使います。"), ("Use this to say that the place is immediately beside another place.", "その場所が別の場所のすぐ隣にあると伝えるときに使います。")),
    (("Now use “There's a ___ near here.” to name one useful place near you.", "では、「There's a ___ near here.」を使って、近くの便利な場所を一つ言ってください。"), ("Now use “It's next to ___.” to say where that place is.", "では、「It's next to ___.」を使って、その場所がどこにあるか言ってください。")),
    (tuple((jp, "", "There's", "It's", suffix) for jp, suffix in (("この近くに{t}カフェがあります{/t}。", " a café near here."), ("この近くに{t}銀行があります{/t}。", " a bank near here."), ("この近くに{t}駅があります{/t}。", " a station near here."), ("この近くに{t}ホテルがあります{/t}。", " a hotel near here."))), (
        ("この近くに{t}カフェがあります{/t}。", "", "There's a", "It's next to", " café near here."),
        ("駅の{t}隣です{/t}。", "", "It's next to", "There's a", " the station."),
        ("この近くに{t}ホテルがあります{/t}。", "", "There's a", "It's next to", " hotel near here."),
        ("銀行の{t}隣です{/t}。", "", "It's next to", "There's a", " the bank."),
    )),
    (("Introduce an existing place", "ある場所を話題に出す", "<b>There's a</b> + 場所 + near here", "One nearby place", "近くの場所", ("<b>There's a</b> café near here.", "<b>There's a</b> bank near here.")), ("Keep next to with the place", "next to と場所を一緒に", "It's + <b>next to</b> + the + 場所", "Immediately beside", "すぐ隣", ("It's <b>next to</b> the bank.", "It's <b>next to</b> the station."))),
    ("Near here or around here?", "near here と around here", "Both mean nearby. “Around here” is especially common in questions about the local area.", "どちらも近くという意味です。「around here」は、この辺りについて聞く質問で特によく使います。", ("Statement", "伝える", "There's a café near here.", "この近くにカフェがあります。"), ("Local question", "この辺りで聞く", "Is there a café around here?", "この辺りにカフェはありますか？")),
)

_simple_spec(8,
    (("Use this to ask whether one weather description is true today.", "今日の天気について、一つの説明が当てはまるか聞くときに使います。"), ("Answer with Yes, it is or No, it isn't.", "Yes, it is または No, it isn't で答えます。")),
    (("Now use “Is it ___ today?” to ask me one real weather question.", "では、「Is it ___ today?」を使って、今日の天気について一つ質問してください。"), ("Answer “Is it cold today?” with a true short answer, then add one weather detail.", "「Is it cold today?」に本当の短い答えを言い、天気の情報を一つ加えてください。")),
    ((
        ("今日は{t}寒いですか{/t}？", "", "Is it", "It's", " cold today?"),
        ("今日は{t}暑いです。{/t}", "", "It's", "Is it", " hot today."),
        ("今日は{t}晴れていますか{/t}？", "", "Is it", "It's", " sunny today?"),
        ("今日は{t}雨です。{/t}", "", "It's", "Is it", " rainy today."),
    ), (
        ("今日は寒いですか？{t}はい、そうです。{/t}", "Is it cold today? Yes, it ", "is", "isn't", "."),
        ("今日は暑いですか？{t}いいえ、違います。{/t}", "Is it hot today? No, it ", "isn't", "is", "."),
        ("今日は晴れていますか？{t}はい、そうです。{/t}", "Is it sunny today? Yes, it ", "is", "isn't", "."),
        ("今日は雨ですか？{t}いいえ、違います。{/t}", "Is it rainy today? No, it ", "isn't", "is", "."),
    )),
    (("Weather questions need it", "天気の質問にも it", "<b>Is it</b> + 天気の言葉 + today?", "Weather question", "天気を聞く", ("<b>Is it</b> cold today?", "<b>Is it</b> sunny today?")), ("Match the short answer", "短い答えを合わせる", "Yes, <b>it is</b>. / No, <b>it isn't</b>.", "Weather answer", "天気に答える", ("Yes, <b>it is</b>.", "No, <b>it isn't</b>."))),
    ("Very cold or really cold?", "very cold と really cold", "Both are natural. “Really cold” often sounds more conversational and expressive.", "どちらも自然です。「really cold」のほうが会話的で、実感を込めやすい言い方です。", ("Neutral emphasis", "中立的な強調", "It's very cold.", "とても寒いです。"), ("Conversational emphasis", "会話的な強調", "It's really cold.", "本当に寒いです。")),
)

_simple_spec(9,
    (("Use a number and plural item to order more than one.", "二つ以上を注文するときに、数と複数形を使います。"), ("Use this to correct the order to one item.", "注文を一つに訂正するときに使います。")),
    (("Now use “[number] ___, please.” to order the quantity you want.", "では、「[number] ___, please.」を使って、ほしい数を注文してください。"), ("Now use “Actually, just one ___, thanks.” to change the quantity to one.", "では、「Actually, just one ___, thanks.」を使って、数を一つに直してください。")),
    (tuple((jp, prefix, correct, distractor, suffix) for jp, prefix, correct, distractor, suffix in (("{t}コーヒーを二つ{/t}お願いします。", "Two ", "coffees", "coffee", ", please."), ("{t}チケットを二枚{/t}お願いします。", "Two ", "tickets", "ticket", ", please."), ("{t}かばんを三つ{/t}お願いします。", "Three ", "bags", "bag", ", please."), ("{t}水を四つ{/t}お願いします。", "Four ", "waters", "water", ", please."))), tuple((jp, prefix, correct, distractor, suffix) for jp, prefix, correct, distractor, suffix in (("{t}やっぱり、コーヒーは一つだけ{/t}お願いします。", "Actually, just one ", "coffee", "coffees", ", thanks."), ("{t}やっぱり、チケットは一枚だけ{/t}お願いします。", "Actually, just one ", "ticket", "tickets", ", thanks."), ("{t}やっぱり、かばんは一つだけ{/t}お願いします。", "Actually, just one ", "bag", "bags", ", thanks."), ("{t}やっぱり、水は一つだけ{/t}お願いします。", "Actually, just one ", "water", "waters", ", thanks.")))),
    (("Mark more than one twice", "数と -s の両方で示す", "2以上の数 + 品物<b>-s</b> + please", "Plural order", "複数の注文", ("Two coffee<b>s</b>, please.", "Three bag<b>s</b>, please.")), ("One takes the singular", "one の後ろは単数形", "just one + 品物（<b>-s なし</b>）", "Correct to one", "一つに訂正", ("just one <b>coffee</b>", "just one <b>ticket</b>"))),
    ("Which word gets the stress?", "どの語を強く言う？", "Stress “one” to correct the quantity. Stress “coffee” to correct the item.", "個数を直すなら「one」を強く言います。品物を直すなら「coffee」を強く言います。", ("Correct the quantity", "個数を訂正", "Actually, just ONE coffee, thanks.", "やっぱり、コーヒーは一つだけお願いします。"), ("Correct the item", "品物を訂正", "Actually, just one COFFEE, thanks.", "やっぱり、一つだけ、コーヒーをお願いします。")),
)

_simple_spec(10,
    (("Use a to introduce one place for the first time.", "場所を初めて話題に出すときに a を使います。"), ("Use the to refer back to the same place.", "同じ場所をもう一度指すときに the を使います。")),
    (("Now use “There's a ___.” to introduce one new place.", "では、「There's a ___.」を使って、新しい場所を一つ話題に出してください。"), ("Now use “The ___ is ___.” to add one fact about that same place.", "では、「The ___ is ___.」を使って、その同じ場所について一つ情報を加えてください。")),
    (tuple((jp, "There's ", "a", "the", suffix) for jp, suffix in (("{t}初めて話題に出します{/t}。角にカフェがあります。", " café on the corner."), ("{t}初めて話題に出します{/t}。この通りに銀行があります。", " bank on this street."), ("{t}初めて話題に出します{/t}。駅の近くにレストランがあります。", " restaurant near the station."), ("{t}初めて話題に出します{/t}。銀行の隣に店があります。", " shop next to the bank."))), (
        ("角に{t}カフェがあります{/t}。", "There's ", "a", "the", " café on the corner."),
        ("角にカフェがあります。{t}そのカフェは{/t}6時まで開いています。", "There's a café on the corner. ", "The", "A", " café is open until six."),
        ("駅の近くに{t}レストランがあります{/t}。", "There's ", "a", "the", " restaurant near the station."),
        ("駅の近くにレストランがあります。{t}そのレストランは{/t}深夜0時まで開いています。", "There's a restaurant near the station. ", "The", "A", " restaurant is open until midnight."),
    )),
    (("Introduce with a", "最初は a", "There's + <b>a</b> + 新しい場所", "First mention", "初めて話題に出す", ("There's <b>a</b> café on the corner.", "There's <b>a</b> restaurant near the station.")), ("Refer back with the", "次は the", "<b>The</b> + 同じ場所 + 情報", "Later mention", "同じ場所をもう一度指す", ("<b>The</b> café is open until six.", "<b>The</b> restaurant is open until midnight."))),
    ("The café or that café?", "the café と that café", "Use “the café” for the shared place. Use “that café” when you point it out or contrast it with another one.", "共有している場所なら「the café」を使います。指し示したり別の店と比べたりするときは「that café」を使います。", ("Shared reference", "話題を共有している", "The café is open until six.", "そのカフェは6時まで開いています。"), ("Pointing or contrast", "指す・比べる", "That café is open until six.", "あのカフェは6時まで開いています。")),
)

_simple_spec(11,
    (("Use this to ask for the location of one specific place.", "特定の場所の位置をたずねるときに使います。"), ("Use this to locate the place behind a clear landmark.", "分かりやすい目印の後ろにあると説明するときに使います。")),
    (("Now use “Where's the ___?” to ask where one real place is.", "では、「Where's the ___?」を使って、実際の場所を一つ聞いてください。"), ("Now use “It's behind/next to ___.” to describe one real location.", "では、「It's behind/next to ___.」を使って、実際の場所の位置を説明してください。")),
    ((
        ("{t}駅はどこですか{/t}？", "", "Where's", "What's", " the station?"),
        ("{t}お名前は何ですか{/t}？", "", "What's", "Where's", " your name?"),
        ("{t}ホテルはどこですか{/t}？", "", "Where's", "What's", " the hotel?"),
        ("{t}カフェはどこですか{/t}？", "", "Where's", "What's", " the café?"),
    ), (
        ("郵便局の{t}後ろです{/t}。", "It's ", "behind", "next to", " the post office."),
        ("駅の{t}隣です{/t}。", "It's ", "next to", "behind", " the station."),
        ("ホテルの{t}後ろです{/t}。", "It's ", "behind", "next to", " the hotel."),
        ("カフェの{t}隣です{/t}。", "It's ", "next to", "behind", " the café."),
    )),
    (("Ask with Where's the", "Where's the で場所を聞く", "<b>Where's the</b> + 場所?", "Specific place", "特定の場所", ("<b>Where's the</b> station?", "<b>Where's the</b> hotel?")), ("Store the full place phrase", "場所の表現をまとめて覚える", "It's + <b>behind the</b> + 目印", "Behind a landmark", "目印の後ろ", ("It's <b>behind the</b> post office.", "It's <b>behind the</b> bank."))),
    ("Contracted or full?", "短縮形・短縮しない形", "“Where's” is usual in relaxed speech. The full “Where is” sounds more deliberate and can emphasize the question; it is not more polite by itself.", "普段の会話では「Where's」が一般的です。短縮しない「Where is」はより意識的に響き、質問を強調できますが、それ自体がより丁寧なわけではありません。", ("Ordinary question", "ふつうの質問", "Where's the station?", "駅はどこですか？"), ("Deliberate emphasis", "質問を強調", "Where IS the station?", "では、駅はいったいどこですか？")),
)


# Exact six-turn exchanges.  Model and completion are rendered from the same
# tuple, so partner turns and turn order cannot drift.
DIALOGUES = {
    1: dict(model=("Classmate", 0, 0, ("Hi. What's your name?", "こんにちは。お名前は？"), ("Sorry, did you say Nina?", "すみません、ニナさんですか？"), ("Mina. Got it. Nice to meet you.", "ミナさんですね。分かりました。はじめまして。"), ("Nice to meet you.", "はじめまして。")), wild=("Neighbor", 1, 1, ("Hi. What's your name?", "こんにちは。お名前は？"), ("Sorry, could you say that again?", "すみません、もう一度言ってもらえますか？"), ("Ken. Got it. Nice to meet you.", "ケンさんですね。分かりました。はじめまして。"), ("Nice to meet you.", "はじめまして。"))),
    2: dict(model=("Classmate", 0, 1, ("What do you do?", "お仕事は何ですか？"), ("What else do you do?", "ほかにどんな仕事をしていますか？"), ("A designer and an artist. So what's your main job?", "デザイナーでアーティストなんですね。主な仕事は何ですか？"), ("I'm a designer.", "デザイナーです。")), wild=("Guest", 2, 2, ("What do you do?", "お仕事は何ですか？"), ("What else do you do?", "ほかにどんな仕事をしていますか？"), ("A teacher and an editor. So what's your main job?", "教師で編集者なんですね。主な仕事は何ですか？"), ("I'm a teacher.", "教師です。"))),
    3: dict(model=("Classmate", 0, 0, ("Where are you from?", "出身はどこですか？"), ("Osaka. Where do you live now?", "大阪なんですね。今はどこに住んでいますか？"), ("Tokyo. Could you say where you live once more?", "東京ですね。今住んでいる場所をもう一度言ってもらえますか？"), ("I live in Tokyo now.", "今は東京に住んでいます。")), wild=("Neighbor", 1, 1, ("Where are you from?", "出身はどこですか？"), ("Tokyo. Where do you live now?", "東京なんですね。今はどこに住んでいますか？"), ("Osaka. Could you say where you live once more?", "大阪ですね。今住んでいる場所をもう一度言ってもらえますか？"), ("I live in Osaka now.", "今は大阪に住んでいます。"))),
    4: dict(model=("Classmate", 0, 0, ("Who's this?", "こちらはどなたですか？"), ("Nice to meet you, Leo. Where's he from?", "はじめまして、レオさん。出身はどこですか？"), ("Canada. Nice to meet you.", "カナダなんですね。はじめまして。"), ("Nice to meet you too.", "こちらこそ、はじめまして。")), wild=("Host", 1, 1, ("Who's this?", "こちらはどなたですか？"), ("Nice to meet you, Anna. Where's she from?", "はじめまして、アナさん。出身はどこですか？"), ("Australia. Nice to meet you.", "オーストラリアなんですね。はじめまして。"), ("Nice to meet you too.", "こちらこそ、はじめまして。"))),
    5: dict(model=("Coworker", 0, 0, ("I found this bag near your desk.", "机の近くでこのかばんを見つけました。"), ("Yes. Is that phone yours too?", "はい。あの携帯もあなたのですか？"), ("Great. We found both owners.", "よかった。両方の持ち主が分かりました。"), ("Thank you.", "ありがとうございます。")), wild=("Guest", 2, 2, ("I found this ticket by the chair.", "椅子のそばでこのチケットを見つけました。"), ("No, that one's yours. Is that key yours?", "いいえ、それはあなたのです。あの鍵はあなたのですか？"), ("Right—the key is mine.", "そうですね。鍵は私のです。"), ("Thank you.", "ありがとうございます。"))),
    6: dict(model=("Classmate", 0, 0, ("Ask me about my job.", "私の仕事について聞いてください。"), ("No, I'm not. I'm a nurse. Are you a student?", "いいえ、違います。看護師です。あなたは学生ですか？"), ("A student. Nice to meet you.", "学生なんですね。はじめまして。"), ("Nice to meet you too.", "こちらこそ、はじめまして。")), wild=("Guest", 1, 2, ("Ask me about my job.", "私の仕事について聞いてください。"), ("Yes, I am. Are you an engineer?", "はい、そうです。あなたはエンジニアですか？"), ("An engineer. Nice to meet you.", "エンジニアなんですね。はじめまして。"), ("Nice to meet you too.", "こちらこそ、はじめまして。"))),
    7: dict(model=("Local", 0, 0, ("Is there a café around here?", "この辺りにカフェはありますか？"), ("Great. Where exactly?", "よかった。正確にはどこですか？"), ("So it's next to the bank?", "つまり、銀行の隣ですか？"), ("That's right.", "その通りです。")), wild=("Traveler", 1, 1, ("Is there a bank near here?", "この近くに銀行はありますか？"), ("Good. Where is it?", "よかった。どこですか？"), ("So it's next to the station?", "つまり、駅の隣ですか？"), ("That's right.", "その通りです。"))),
    8: dict(model=("Friend", 0, 0, ("Ask me about today's weather.", "今日の天気について聞いてください。"), ("Yes, it is. Is it cold where you are?", "はい、寒いです。あなたのいる場所も寒いですか？"), ("Very cold there too. Do you like cold weather?", "そちらもとても寒いんですね。寒い天気は好きですか？"), ("Not really.", "あまり好きではありません。")), wild=("Friend", 1, 1, ("Ask me about today's weather.", "今日の天気について聞いてください。"), ("Yes, it is. Is it hot where you are?", "はい、暑いです。あなたのいる場所も暑いですか？"), ("So it isn't hot there. Do you like hot weather?", "そちらは暑くないんですね。暑い天気は好きですか？"), ("Not really.", "あまり好きではありません。"))),
    9: dict(model=("Server", 0, 0, ("What can I get you?", "何になさいますか？"), ("Two coffees. Is that right?", "コーヒーを二つですね？"), ("One coffee. Anything else?", "コーヒーを一つですね。ほかには？"), ("That's all, thanks.", "以上です、ありがとうございます。")), wild=("Clerk", 1, 1, ("How many tickets do you need?", "チケットは何枚必要ですか？"), ("Two tickets?", "二枚ですか？"), ("One ticket. Anything else?", "一枚ですね。ほかには？"), ("That's all, thanks.", "以上です、ありがとうございます。"))),
    10: dict(model=("Friend", 0, 0, ("Is there anywhere to get coffee?", "コーヒーを飲める所はありますか？"), ("Good. What time is it open until?", "いいですね。何時まで開いていますか？"), ("Until six. The café on the corner?", "6時までですね。角のカフェですか？"), ("Yes, the same one.", "はい、同じカフェです。")), wild=("Traveler", 1, 1, ("Is there a bank on this street?", "この通りに銀行はありますか？"), ("Great. What time is it open until?", "よかった。何時まで開いていますか？"), ("Until five. The bank on this street?", "5時までですね。この通りの銀行ですか？"), ("Yes, the same one.", "はい、同じ銀行です。"))),
    11: dict(model=("Travel partner", 0, 1, ("Let's find the station and the hotel.", "駅とホテルを探しましょう。"), ("The station's behind the post office. What about the hotel?", "駅は郵便局の後ろです。ホテルはどこですか？"), ("Thanks. Is that far?", "ありがとうございます。そこは遠いですか？"), ("It's about five minutes.", "5分くらいです。")), wild=("Travel partner", 1, 2, ("Let's find the bank and the café.", "銀行とカフェを探しましょう。"), ("The bank's behind the post office. What about the café?", "銀行は郵便局の後ろです。カフェはどこですか？"), ("Thanks. Is that far?", "ありがとうございます。そこは遠いですか？"), ("It's about five minutes.", "5分くらいです。"))),
}


LIVE_SCENES = {
    1: (("input", "me", "Me", "Your answer. Use today's pattern only if it fits naturally.", "自分の答え。今日のパターンは自然に使えるときだけ使う"), ("text", "me", "Me", "How about you?", "先生はどうですか？"), ("input", "other", "Tutor", "Tutor's answer: Give a real, brief answer.", "先生の本当の短い答え")),
    2: (("input", "me", "Me", "Your answer. Use today's pattern only if it fits naturally.", "自分の答え。今日のパターンは自然に使えるときだけ使う"), ("text", "me", "Me", "How about you?", "先生はどうですか？"), ("input", "other", "Tutor", "Tutor's answer: Give a real, brief answer.", "先生の本当の短い答え")),
    3: (("input", "me", "Me", "Your answer. Use today's pattern only if it fits naturally.", "自分の答え。今日のパターンは自然に使えるときだけ使う"), ("text", "me", "Me", "How about you?", "先生はどうですか？"), ("input", "other", "Tutor", "Tutor's answer: Give a real, brief answer.", "先生の本当の短い答え")),
    4: (("input", "me", "Me", "Your answer. Use today's pattern only if it fits naturally.", "自分の答え。今日のパターンは自然に使えるときだけ使う"), ("text", "me", "Me", "How about you?", "先生はどうですか？"), ("input", "other", "Tutor", "Tutor's answer: Give a real, brief answer.", "先生の本当の短い答え")),
    5: (("input", "me", "Me", "Your answer. Use today's pattern only if it fits naturally.", "自分の答え。今日のパターンは自然に使えるときだけ使う"), ("text", "me", "Me", "How about you?", "先生はどうですか？"), ("input", "other", "Tutor", "Tutor's answer: Give a real, brief answer.", "先生の本当の短い答え")),
    6: (("input", "me", "Me", "Your answer. Use today's pattern only if it fits naturally.", "自分の答え。今日のパターンは自然に使えるときだけ使う"), ("text", "me", "Me", "How about you?", "先生はどうですか？"), ("input", "other", "Tutor", "Tutor's answer: Give a real, brief answer.", "先生の本当の短い答え")),
    7: (("input", "me", "Me", "Your answer. Use today's pattern only if it fits naturally.", "自分の答え。今日のパターンは自然に使えるときだけ使う"), ("text", "me", "Me", "How about you?", "先生はどうですか？"), ("input", "other", "Tutor", "Tutor's answer: Give a real, brief answer.", "先生の本当の短い答え")),
    8: (("input", "me", "Me", "Your answer. Use today's pattern only if it fits naturally.", "自分の答え。今日のパターンは自然に使えるときだけ使う"), ("text", "me", "Me", "How about you?", "先生はどうですか？"), ("input", "other", "Tutor", "Tutor's answer: Give a real, brief answer.", "先生の本当の短い答え")),
    9: (("input", "me", "Me", "Your answer. Use today's pattern only if it fits naturally.", "自分の答え。今日のパターンは自然に使えるときだけ使う"), ("text", "me", "Me", "How about you?", "先生はどうですか？"), ("input", "other", "Tutor", "Tutor's answer: Give a real, brief answer.", "先生の本当の短い答え")),
    10: (("input", "me", "Me", "Your answer. Use today's pattern only if it fits naturally.", "自分の答え。今日のパターンは自然に使えるときだけ使う"), ("text", "me", "Me", "How about you?", "先生はどうですか？"), ("input", "other", "Tutor", "Tutor's answer: Give a real, brief answer.", "先生の本当の短い答え")),
    11: (("input", "me", "Me", "Your answer. Use today's pattern only if it fits naturally.", "自分の答え。今日のパターンは自然に使えるときだけ使う"), ("text", "me", "Me", "How about you?", "先生はどうですか？"), ("input", "other", "Tutor", "Tutor's answer: Give a real, brief answer.", "先生の本当の短い答え")),
}


# Event index -> explicit menu for learner-editable live fields. Tutor fields
# deliberately have no learner menu.
LIVE_HINTS = {
    1: {0: ("名字:family name", "名前:first name", "覚えやすい:easy to remember")},
    2: {0: ("料理人:chef", "教師:teacher", "デザイナー:designer")},
    3: {0: ("町:city", "国:country", "一年:for a year")},
    4: {0: ("友だち:friend", "同僚:coworker", "親切な:kind", "面白い:funny")},
    5: {0: ("携帯:phone", "鍵:key", "傘:umbrella", "かばん:bag")},
    6: {0: ("教師:teacher", "医師:doctor", "デザイナー:designer", "変わった:changed")},
    7: {0: ("スーパー:supermarket", "公園:park", "カフェ:café", "ジム:gym")},
    8: {0: ("晴れた:sunny", "雨の:rainy", "寒い:cold", "外に出る:go outside")},
    9: {0: ("コーヒー:coffee", "お茶:tea", "軽食:a snack", "注文を変える:change my order")},
    10: {0: ("カフェ:café", "レストラン:restaurant", "店:shop", "サービス:service")},
    11: {0: ("駅:station", "レストラン:restaurant", "公園:park", "隣に:next to")},
}


# Every final learner line is explicitly owned by today's pattern work or by a
# named bounded support expression; none is generated filler. Tests compare the
# rendered sixth turn and its owner to this source.
SUPPORT_LINE_OWNERS = {
    1: "CORE-1 supporting expression",
    4: "CORE-4 supporting expression",
    5: "CORE-5 bounded survival chunk",
    6: "CORE-4 supporting expression",
    7: "CORE-7 bounded survival chunk",
    8: "CORE-8 supporting expression",
    9: "CORE-9 supporting expression",
    10: "CORE-10 supporting expression",
    11: "CORE-11 supporting expression",
}


FINAL_LINE_OWNERSHIP = {
    number: {
        variant: (
            data[variant][6][0],
            SUPPORT_LINE_OWNERS.get(number, f"CORE-{number} current pattern"),
        )
        for variant in ("model", "wild")
    }
    for number, data in DIALOGUES.items()
}


def set_vocab(head, number):
    """Write all four ownership categories without changing the old generator."""
    import re

    for category, value in VOCAB[number].items():
        head = re.sub(
            rf'(<meta name="podo:vocabulary:{category}" content=")[^"]*(")',
            rf'\g<1>{value}\2', head, count=1,
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
        "words-you-know", "Words you know", "知っている単語",
        '<p class="section-subtitle"><span class="ko">Say the three familiar words in English.</span>'
        '<span class="ja">知っている3つの単語を英語で言いましょう。</span></p>'
        f'<div class="bridge">{cards}</div>',
    )


def intro_page(number, part, pattern):
    model = core.strip_marks(pattern[0][0])
    meaning_en, meaning_ja = SPECS[number]["meanings"][part - 1]
    return (
        f'    <div class="transition-page" data-page-id="part{part}-intro" data-act="Pattern {part}">'
        f'<span class="transition-kicker">PART {part}</span>'
        f'<h2 class="transition-title">{core.esc(model)}</h2>'
        f'<p class="section-subtitle"><span class="ko">{core.esc(meaning_en)} Please read the title aloud.</span>'
        f'<span class="ja">{core.esc(meaning_ja)}タイトルを声に出して読んでください。</span></p>'
        '<div class="tutor-note">Have the learner read the title once, then move on.</div></div>\n'
    )


def translate_page(number, part, pattern):
    stage = TRANSLATE_STAGES[number][part - 1]
    blocks = []
    for index, ((english, japanese, _), hints) in enumerate(
        zip(pattern, TRANSLATE_HINTS[number][part - 1], strict=True)
    ):
        lexical_help = hint_html((hints,)) if hints else ""
        blocks.append(
            '<div class="task-block"><div class="answer-box">'
            f'<span class="answer-label">{core.esc(core.strip_marks(japanese))}</span>'
            '<span class="answer-space as-input">'
            f'<input class="space-input" type="text" data-sync-id="p{part}-translate-{index}" '
            f'data-answer="{core.esc(core.strip_marks(english))}" autocomplete="off" spellcheck="false">'
            '</span>' + lexical_help + '</div></div>'
        )
    if stage == "supported" and not any(TRANSLATE_HINTS[number][part - 1]):
        raise ValueError(f"CORE-{number} Part {part} supported translation needs lexical help")
    if stage == "checkpoint" and any(TRANSLATE_HINTS[number][part - 1]):
        raise ValueError(f"CORE-{number} Part {part} checkpoint translation cannot expose hints")
    return core.section(
        f"p{part}-translate", "Say it in English", "英語にしよう",
        '<p class="section-subtitle"><span class="ko">Read the Japanese, then say it in English.</span>'
        '<span class="ja">日本語を見て、英語で言ってみましょう。</span></p>'
        '<div class="tutor-note">Type the learner\'s complete English sentence exactly as they say it.</div>'
        + "".join(blocks),
        attributes=f'data-scaffolding-contract="target-v2" data-support-stage="{stage}"',
    )


def write_page(number, part, pattern):
    prompt_en, prompt_ja = SPECS[number]["writes"][part - 1]
    return core.section(
        f"p{part}-write", "Make it yours", "自分の文にしよう",
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
            hints = hint_html(LIVE_HINTS[number].get(index, ())) if side == "me" else ""
            rendered.append(
                f'<div class="turn {side}">{avatar}<div class="{bubble}">'
                '<div class="answer-box tall">'
                f'<span class="answer-label">{core.esc(english)}<span class="task">{core.esc(japanese)}</span></span>'
                '<span class="answer-space as-input">'
                f'<textarea class="free-input" data-sync-id="live-{index}" rows="2" spellcheck="false" maxlength="2000"></textarea>'
                f'</span>{hints}</div></div></div>'
            )
    return core.section(
        "p3-freetalk", "Let's talk", "話してみよう",
        f'<p class="section-subtitle"><span class="ko">{core.esc(LESSONS[number]["prompt"][0])}</span>'
        f'<span class="ja">{core.esc(LESSONS[number]["prompt"][1])}</span></p>'
        '<div class="tutor-note">Ask the question above and react naturally. When the learner asks back, give a real, brief answer.</div>'
        '<div class="dialogue">' + "".join(rendered) + "</div>",
    )


def page_id(page):
    import re
    match = re.search(r'data-page-id="([^"]+)"', page)
    return match.group(1) if match else ""


def customize_pages(number, data, pages):
    replacements = {
        "words-you-know": known_page(number),
        "part1-intro": intro_page(number, 1, data["p1"]),
        "part2-intro": intro_page(number, 2, data["p2"]),
        "p1-translate": translate_page(number, 1, data["p1"]),
        "p2-translate": translate_page(number, 2, data["p2"]),
        "p1-write": write_page(number, 1, data["p1"]),
        "p2-write": write_page(number, 2, data["p2"]),
        "p3-freetalk": live_page(number),
    }
    result = []
    for page in pages:
        pid = page_id(page)
        omitted_choices = {f"p{part}-choose" for part in data.get("omit_choice", ())}
        if pid in omitted_choices:
            continue
        result.append(replacements.get(pid, page))
    return result


@contextlib.contextmanager
def course_data():
    """Temporarily provide this narrow batch to the approved renderer."""
    previous = (core.VOCAB, core.CANONICAL_SPECS, core.DIALOGUES, core.LIVE_SCENES)
    renderer_vocab = {
        number: (values["new"], values["assumed"], values["receptive"])
        for number, values in VOCAB.items()
    }
    core.VOCAB, core.CANONICAL_SPECS, core.DIALOGUES, core.LIVE_SCENES = (
        renderer_vocab, SPECS, DIALOGUES, LIVE_SCENES
    )
    try:
        yield
    finally:
        core.VOCAB, core.CANONICAL_SPECS, core.DIALOGUES, core.LIVE_SCENES = previous


def build(number, data):
    source = PILOT.read_text(encoding="utf-8")
    head, foot = new_lesson.split_shell(source)
    slug = f'{number:02d}-{data["slug"]}'
    level = "Pre-A1" if number <= 6 else "A1"
    head = new_lesson.retarget(
        head,
        review_id=f"CORE-{number}", lesson_id=slug, level=level,
        title=data["title"], title_ko=data["ko"], title_ja=data["ja"],
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
    args = parser.parse_args()
    missing_specs = set(LESSONS) - set(SPECS)
    if missing_specs:
        raise SystemExit(f"missing explicit semantic specs: {sorted(missing_specs)}")
    for number, data in LESSONS.items():
        out, text = build(number, data)
        if out.exists() and not args.refresh:
            raise SystemExit(f"refusing to overwrite {out.relative_to(ROOT)}")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)}")
    print(f"{len(LESSONS)} Core decks generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

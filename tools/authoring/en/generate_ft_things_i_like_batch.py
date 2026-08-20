#!/usr/bin/env python3
"""Generate the explicit FT 21-33 Things I Like accessible/full pairs.

This narrow source owns only the 26 matched decks in talk-things-i-like.  Every
article row is authored as one stable claim in two language loads, and every
question page owns one conversational job plus answer-dependent follow-ups.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import generate_ft_me_lately_batch as base
import new_lesson


ROOT = new_lesson.REPO
TRACK = new_lesson.ENGLISH / "tracks/3-freetalking"
COURSE = "talk-things-i-like"
CANONICAL = {
    variant: TRACK / f"courses/talk-between-two-countries-{variant}/lessons/01-this-surprised-me/lesson.html"
    for variant in ("accessible", "full")
}
prompt = base.prompt
esc = base.esc


def topic(*, slug, title, ko, ja, goal, outcomes, article_title, articles, prompts):
    return {
        "slug": slug,
        "title": title,
        "ko": ko,
        "ja": ja,
        "goal": goal,
        "outcomes": outcomes,
        "article_title": article_title,
        "articles": articles,
        "prompts": prompts,
    }


TOPICS = {
    21: topic(
        slug="a-film-you-never-get-tired-of",
        title="A film you never get tired of",
        ko="몇 번을 봐도 질리지 않는 영화",
        ja="何度見ても飽きない映画",
        goal=("Let's talk about a film you can watch again and again.", "何度でも見たくなる映画について話しましょう。"),
        outcomes=(("Name the film and your history with it", "映画と自分との関わりを話す"), ("Explain what keeps changing", "見るたびに変わる点を説明する"), ("Choose one scene to share", "見せたい場面を一つ選ぶ")),
        article_title=("Why some films reward another viewing", "何度見ても楽しめる映画"),
        articles=[
            ("Some films are fun once, while others invite us back many times.", "Some films satisfy us once, whereas others keep inviting us back for another viewing.", "一度で満足する映画もあれば、何度も見たくなる映画もあります。"),
            ("Knowing the ending can make a familiar film feel comfortable.", "Already knowing the ending can make a familiar film unexpectedly comforting.", "結末を知っているからこそ、なじみのある映画に安心できることがあります。"),
            ("We can relax and notice details when we no longer have to follow the plot.", "Once we no longer need to track the plot, we can notice quieter visual and emotional details.", "筋を追わなくてよくなると、細かな映像や感情に気づけます。"),
            ("A line may mean something different after our own life changes.", "The meaning of a line can shift after our own experience or circumstances change.", "自分の経験や状況が変わると、同じ台詞の意味も変わることがあります。"),
            ("Watching with another person can reveal parts we had stopped seeing.", "Watching with someone else can reveal moments we had begun to take for granted.", "ほかの人と見ると、自分が見過ごしていた場面に気づけます。"),
            ("A favorite film does not have to be perfect to matter to us.", "A film can matter deeply to us without being technically perfect.", "大切な映画は、作品として完璧である必要はありません。"),
            ("Sometimes a film stays important because it belongs to a particular memory.", "Sometimes a film endures because it is attached to a particular person, place, or period.", "ある人や場所、時期の思い出と結びついているから、大切であり続ける映画もあります。"),
            ("Other people may miss the exact thing that makes it special to us.", "Other viewers may completely miss the quality that gives the film its personal value.", "ほかの人には、自分にとって特別な点がまったく伝わらないこともあります。"),
            ("Rewatching can become a small ritual during stressful or unsettled times.", "A rewatch can become a reassuring ritual during stressful or unsettled periods.", "見返すことが、ストレスが多い時や落ち着かない時の小さな習慣になることがあります。"),
            ("The scene we choose for someone else shows what we value in the whole film.", "The first scene we share with someone often reveals what we value in the film as a whole.", "人に最初に見せたい場面には、その映画で何を大切にしているかが表れます。"),
        ],
        prompts=[
            prompt("A familiar film", "何度も見たい映画", "What film could you happily watch more than twice?", "何度でも見たい映画は何ですか？", ["What mood would make you choose it?", "Who would you recommend it to?"]),
            prompt("One scene", "一つの場面", "Which scene from that film comes to mind first?", "その映画で最初に思い浮かぶ場面はどれですか？", ["What happens in that scene?", "Why has that moment stayed with you?"]),
            prompt("How many times", "見た回数", "How many times would you need to see it before you knew it well?", "その映画をよく知っていると言えるまで、何回くらい見る必要がありますか？", ["Which details would take time to notice?", "At what point might it stop feeling fresh?"]),
            prompt("What you notice now", "見方の変化", "What might you notice on a second viewing that you missed the first time?", "二回目に見ると、最初は見逃したどんなことに気づきそうですか？", ["What could change the way you see the story?", "Which character might become more interesting?"]),
            prompt("Who you watched with", "一緒に見る人", "Who would be the most interesting person to watch it with?", "誰と一緒に見ると、いちばん面白くなりそうですか？", ["How might that person react?", "What might they notice that you missed?"]),
            prompt("What others miss", "伝わりにくい魅力", "What might a new viewer misunderstand about this film?", "初めて見る人は、この映画のどこを誤解しそうですか？", ["Which criticism would you understand?", "What would you explain before recommending it?"]),
            prompt("Why you return", "また見る理由", "What makes you want to watch it again?", "また見たいと思わせるものは何ですか？", ["Does your reason change with your mood?", "When would you choose a different film?"]),
            prompt("Show me first", "最初に見せる場面", "If you could show me one scene, which would you choose?", "私に一つの場面を見せるなら、どれを選びますか？", ["What should I pay attention to?", "What would that scene not explain about the film?"]),
        ],
    ),
    22: topic(
        slug="something-in-english-you-genuinely-enjoyed",
        title="Something in English you genuinely enjoyed",
        ko="진심으로 즐겼던 영어 콘텐츠",
        ja="心から楽しめた英語のもの",
        goal=("Let's trace one enjoyable experience in English and what it led to.", "英語で楽しめた一つの体験と、その後につながったことを話しましょう。"),
        outcomes=(("Describe the first enjoyable thing", "最初に楽しめたものを説明する"), ("Explain what you understood", "理解できたことを話す"), ("Recommend a next starting point", "次の入り口をすすめる")),
        article_title=("Enjoyment before perfect understanding", "完全に分からなくても楽しめること"),
        articles=[
            ("Many people first connect with English through entertainment, not study.", "Many people first form a personal connection with English through entertainment rather than formal study.", "英語との最初の個人的なつながりは、勉強より娯楽から生まれることがよくあります。"),
            ("A song, film, or game can feel exciting even when much of the language is unclear.", "A song, film, or game can be absorbing even when much of its language remains unclear.", "言葉の多くが分からなくても、歌や映画、ゲームに夢中になることがあります。"),
            ("Enjoyment gives us a reason to return to the same words.", "Enjoyment creates a reason to revisit the same language without treating repetition as work.", "楽しさがあると、同じ英語に繰り返し触れる理由ができます。"),
            ("Repeated scenes or lyrics slowly make unfamiliar expressions easier to recognize.", "Repeated scenes, lyrics, or instructions gradually make unfamiliar expressions recognizable.", "場面や歌詞、指示を繰り返すうちに、知らない表現も少しずつ分かるようになります。"),
            ("Understanding one small part can feel like a real breakthrough.", "Understanding one small part independently can feel like a genuine breakthrough.", "自分で一部分を理解できると、本当の突破口のように感じられます。"),
            ("That moment can change English from a school subject into something personal.", "That moment can transform English from an academic subject into a source of personal interest.", "その瞬間、英語が学校の科目から自分の興味へ変わることがあります。"),
            ("People often explore more after finding one creator, genre, or community they like.", "People often explore much more once they find a creator, genre, or community that feels like theirs.", "好きな作り手やジャンル、仲間を一つ見つけると、さらに広く探すことがあります。"),
            ("Subtitles and translations can support enjoyment without replacing the English.", "Subtitles and translations can support comprehension without replacing direct engagement with the English.", "字幕や翻訳は、英語そのものに触れる体験を失わずに理解を助けられます。"),
            ("The best starting point is different for each person's interests.", "A useful gateway depends more on a person's interests than on a universal list of easy material.", "よい入り口は、誰にでも同じ簡単な教材より、その人の興味によって変わります。"),
            ("A personal recommendation works best when it explains why the experience is enjoyable.", "A thoughtful recommendation explains not only what to try, but why the experience may be rewarding.", "よいおすすめは、何を試すかだけでなく、なぜ楽しめそうかも伝えます。"),
        ],
        prompts=[
            prompt("The first enjoyable thing", "最初に楽しめたもの", "What was the first thing in English you actually enjoyed — song, film, game, anything?", "歌や映画、ゲームなど何でもよいので、英語で初めて本当に楽しめたものは何でしたか？", ["What do you remember about it?", "What made it feel different from studying?"]),
            prompt("The kind of thing", "どんなもの？", "Was it something you watched, listened to, read, or played?", "それは見たもの、聴いたもの、読んだもの、遊んだもののどれでしたか？", ["How did you find it?", "Did anyone share the experience with you?"]),
            prompt("Your age then", "そのときの年齢", "How old were you when you found it?", "それを見つけたとき、何歳くらいでしたか？", ["What else were you interested in then?", "How did English fit into your life at that time?"]),
            prompt("How much you understood", "理解できた量", "How much of the English did you understand?", "その英語をどのくらい理解できましたか？", ["Which part was clear first?", "What helped with the difficult parts?"]),
            prompt("What came next", "その次", "What did you do after you enjoyed it?", "それを楽しんだあと、何をしましたか？", ["Did you look for anything similar?", "Which action kept your interest going?"]),
            prompt("What brought you here", "今につながったもの", "How did that experience lead to the English you use now?", "その体験は、今使っている英語にどうつながりましたか？", ["Which part of the connection is strongest?", "What might have happened without it?"]),
            prompt("A good starting point", "よい入り口", "What helps someone enjoy English before they understand everything?", "すべて理解する前でも英語を楽しむには、何が役立ちますか？", ["How much support is useful?", "What can make the experience feel like work?"]),
            prompt("Your recommendation", "自分のおすすめ", "What would you recommend to someone starting English now?", "今英語を始める人に、何をすすめますか？", ["Why would that be a good gateway?", "Who might prefer a different starting point?"]),
        ],
    ),
    23: topic(
        slug="music-for-different-parts-of-your-day",
        title="Music for different parts of your day",
        ko="하루의 장면마다 듣는 음악",
        ja="一日の場面ごとに聴く音楽",
        goal=("Let's build the soundtrack to different parts of your day.", "一日のさまざまな場面に合う音楽について話しましょう。"),
        outcomes=(("Describe when you listen", "聴く場面を説明する"), ("Connect music and mood", "音楽と気分を結びつける"), ("Compare past and present taste", "昔と今の好みを比べる")),
        article_title=("Music changes with the moment", "場面によって変わる音楽"),
        articles=[
            ("The same song can play different roles at breakfast, at work, and on the way home.", "The same song can serve a completely different purpose at breakfast, during work, and on the journey home.", "同じ曲でも、朝食中、仕事中、帰り道ではまったく違う役割を持ちます。"),
            ("Morning music can help us wake up or protect a quiet start.", "Morning music can provide energy or preserve the calm of a slow start.", "朝の音楽は、目を覚ましたり、静かな始まりを守ったりできます。"),
            ("During a commute, familiar music can make repeated travel feel shorter and easier.", "During a commute, familiar music can make a repetitive journey seem shorter and more manageable.", "通勤中になじみのある音楽を聴くと、いつもの移動が短く、少し楽に感じられます。"),
            ("Some work needs silence, while other work becomes easier with a steady sound.", "Some tasks require silence, whereas others benefit from a steady musical background.", "静けさが必要な作業もあれば、一定の音楽があるほうが進みやすい作業もあります。"),
            ("Lyrics can compete with reading or writing because both need language attention.", "Lyrics can interfere with reading or writing because both compete for the same language attention.", "歌詞は、同じ言語への注意を使うため、読む作業や書く作業を邪魔することがあります。"),
            ("Our choice often changes with mood before we consciously notice the mood.", "Our musical choice often shifts with our mood before we consciously identify how we feel.", "自分の気分に気づく前に、選ぶ音楽が変わることがあります。"),
            ("A song from years ago can bring back how we felt then for a moment.", "A song from years ago can briefly bring back how we felt at that time.", "何年も前の曲を聴くと、当時の気持ちが一瞬よみがえることがあります。"),
            ("Shared spaces shape what we play and how much of our taste we reveal.", "Shared spaces shape both what we play and how much of our taste we reveal.", "共有する場所では、何を流すか、好みをどこまで見せるかが変わります。"),
            ("Shuffle can create funny moments by playing a private favorite in the wrong setting.", "Shuffle can expose an amusing mismatch between a private favorite and a public setting.", "シャッフル再生では、個人的に好きな曲が場違いな場所で流れる面白さがあります。"),
            ("A day's music becomes a soundtrack even when we never planned one.", "The music attached to ordinary moments becomes a personal soundtrack without deliberate planning.", "普通の場面に結びついた音楽が、意識しなくても自分のサウンドトラックになります。"),
        ],
        prompts=[
            prompt("Music on the way", "移動中の音楽", "What do you like to listen to while travelling somewhere?", "どこかへ移動するとき、何を聴くのが好きですか？", ["How does it change the journey?", "When do you prefer silence?"]),
            prompt("The last thing you played", "最後に再生したもの", "What was the last piece of music you played?", "最後に再生した音楽は何でしたか？", ["Where were you at the time?", "Why did that music fit the moment?"]),
            prompt("Music and mood", "音楽と気分", "How does your choice of music change with your mood?", "気分によって、選ぶ音楽はどう変わりますか？", ["Which mood changes your choice most?", "Can music change the mood back?"]),
            prompt("A morning song", "朝の一曲", "What kind of song works best in the morning?", "朝にはどんな曲がいちばん合いますか？", ["What would be too much that early?", "Does your answer change on weekends?"]),
            prompt("Music you cannot work to", "作業に合わない音楽", "What kind of music can you not work or study to?", "仕事や勉強中に聴けないのは、どんな音楽ですか？", ["What distracts you about it?", "Which tasks need a different sound?"]),
            prompt("Five years ago", "5年前の好み", "What did you love listening to five years ago?", "5年前は何を聴くのが好きでしたか？", ["What has changed in your taste?", "Which old favorite still works?"]),
            prompt("A risky shuffle", "シャッフルの危険", "What song would surprise people if it suddenly played from your phone?", "スマホから突然流れたら、周りの人が驚きそうな曲は何ですか？", ["Which setting would make it funniest or most awkward?", "What would the song reveal about your taste?"]),
            prompt("Your day's soundtrack", "一日のサウンドトラック", "Which three parts of your day need different music?", "一日のどの三つの場面に、それぞれ違う音楽が必要ですか？", ["How would each part sound?", "Which part matters most to get right?"]),
        ],
    ),
    24: topic(
        slug="your-go-to-karaoke-song",
        title="Your go-to karaoke song",
        ko="노래방에서 꼭 부르는 노래",
        ja="カラオケの定番曲",
        goal=("Let's talk about the songs that work—or fail—at karaoke.", "カラオケでうまくいく曲、うまくいかない曲について話しましょう。"),
        outcomes=(("Name your reliable song", "定番曲を挙げる"), ("Explain the room and the choice", "場の雰囲気と選択を説明する"), ("Recommend a song for someone else", "ほかの人に一曲すすめる")),
        article_title=("A song for the room", "その場に合う一曲"),
        articles=[
            ("A good karaoke choice is not always the song we like most.", "The strongest karaoke choice is not necessarily the song we admire most privately.", "カラオケでいちばんよい選曲は、自分がいちばん好きな曲とは限りません。"),
            ("The singer needs a melody and range that feel manageable.", "The singer needs a melody and vocal range that feel manageable.", "歌う人には、無理のないメロディーや音域が必要です。"),
            ("The room also matters because some songs invite everyone in.", "The room matters too, because certain songs invite other people to join the moment.", "みんなが一緒に楽しめる曲もあるため、その場の雰囲気も大切です。"),
            ("A familiar opening helps people recognize the song quickly.", "A recognizable opening lets everyone identify the song immediately.", "なじみのあるイントロなら、みんながすぐに何の曲か分かります。"),
            ("A long quiet song may be beautiful but difficult in a lively group.", "A long, restrained song may be beautiful yet poorly suited to a lively group.", "長く静かな曲は美しくても、にぎやかなグループには合わないことがあります。"),
            ("A backup song can rescue us when the first choice goes badly.", "A dependable backup song can rescue the mood after an ambitious first choice goes badly.", "難しい最初の曲がうまくいかなかったとき、頼れる予備の曲が場を救います。"),
            ("People often learn their go-to song from friends, family, or repeated nights out.", "People often inherit a go-to song through friends, family, or repeated social occasions.", "定番曲は、友人や家族、何度もの集まりを通して身につくことがあります。"),
            ("Some songs are avoided because the lyrics or memories feel too personal.", "Some songs remain off-limits because their lyrics or associations feel too personal to share.", "歌詞や思い出が個人的すぎて、人前では避ける曲もあります。"),
            ("Choosing for someone else means thinking about their voice and confidence.", "Recommending a song for someone else requires attention to their voice, taste, and confidence.", "ほかの人にすすめるときは、その人の声や好み、自信を考える必要があります。"),
            ("The best karaoke memory often comes from the group, not perfect singing.", "The best karaoke memories usually come from a shared moment rather than flawless singing.", "最高のカラオケの思い出は、完璧な歌より、みんなで共有した瞬間から生まれることが多いです。"),
        ],
        prompts=[
            prompt("Your first song", "最初の一曲", "What song would you choose first at karaoke?", "カラオケで最初にどの曲を選びますか？", ["What makes it a reliable choice?", "Would you sing it alone or with a group?"]),
            prompt("Your ideal karaoke", "理想のカラオケ", "What kind of karaoke night would you enjoy most?", "どんなカラオケなら、いちばん楽しめそうですか？", ["Who would be there?", "What would make the room feel comfortable?"]),
            prompt("Why that song", "その曲を選ぶ理由", "Why does that song work for you?", "なぜその曲は自分に合いますか？", ["Which part feels easiest?", "What makes it enjoyable to sing?"]),
            prompt("How you learned it", "覚えたきっかけ", "Who or what taught you that song?", "その曲は誰から、または何から覚えましたか？", ["What do you remember about learning it?", "Has the song changed meaning for you?"]),
            prompt("Your backup", "予備の曲", "What would your backup song be if your first choice felt wrong?", "最初の曲が合わないとき、予備の曲に何を選びますか？", ["What kind of room would suit it?", "How would it differ from your first choice?"]),
            prompt("Never at karaoke", "絶対に歌わない曲", "What would you never sing at karaoke?", "カラオケで絶対に歌わない曲は何ですか？", ["What makes it a bad choice for you?", "Who could sing it well instead?"]),
            prompt("A song for the group", "みんなのための曲", "What makes a song good for a whole group?", "みんなで楽しめる曲には、何が必要ですか？", ["Does everyone need to know it?", "When can a quiet song still work?"]),
            prompt("A song for me", "私へのおすすめ", "Ask me what I enjoy singing, then recommend one karaoke song.", "私が歌って楽しめるものを聞いてから、カラオケの曲を一つすすめてください。", ["Why does that song fit what I told you?", "What should my backup be?"]),
        ],
    ),
    25: topic(
        slug="your-go-to-late-night-food",
        title="Your go-to late-night food",
        ko="밤늦게 찾게 되는 음식",
        ja="夜遅くについ選ぶ食べ物",
        goal=("Let's talk about what you choose when hunger arrives late.", "夜遅くにお腹がすいたときの選択について話しましょう。"),
        outcomes=(("Describe the usual order", "いつもの注文を説明する"), ("Explain the situation around it", "その場面を説明する"), ("Introduce a Japanese favorite", "日本のおすすめを紹介する")),
        article_title=("Why late-night food feels different", "夜食が特別に感じる理由"),
        articles=[
            ("Late-night hunger often arrives after a long day or a missed meal.", "Late-night hunger often reflects a long day, an irregular schedule, or a meal that never quite happened.", "夜遅い空腹は、長い一日や不規則な予定、食べ損ねた食事のあとによく起こります。"),
            ("At that hour, convenience can matter more than a perfect meal.", "At that hour, speed and convenience often outweigh the idea of a balanced meal.", "その時間には、完璧な食事より速さや便利さが大切になりがちです。"),
            ("A craving may point us toward salty, warm, or familiar food.", "A strong craving may pull us toward food that is salty, warm, rich, or deeply familiar.", "無性に何かを食べたい気持ちで、塩辛いもの、温かいもの、なじみのあるものを選ぶことがあります。"),
            ("Delivery makes the choice easy, but waiting can make us order too much.", "Delivery removes effort from the choice, although the wait can encourage us to order more than we need.", "宅配は手間を減らしますが、待つ間に必要以上に注文することもあります。"),
            ("Eating alone and sharing food can create very different late-night memories.", "A solitary snack and a shared late-night meal can carry completely different emotional meanings.", "一人の夜食と、誰かと食べる夜食では、思い出の意味が大きく変わります。"),
            ("The food that feels great at night may feel heavy the next morning.", "Food that feels satisfying at midnight may feel uncomfortably heavy the following morning.", "夜中に満足した食べ物が、翌朝には重く感じられることがあります。"),
            ("People develop a regular order because it removes one more decision from a tiring day.", "A regular order reduces decision-making at the point when our energy is already low.", "疲れて判断する力が残っていないとき、いつもの注文が決断を一つ減らしてくれます。"),
            ("Local late-night food often reflects what is open and easy to share.", "Local late-night favorites often reflect opening hours, delivery culture, and what is easy to share.", "その土地の定番の夜食には、営業時間や宅配文化、分けやすさが表れます。"),
            ("Visitors may not understand why an ordinary dish feels perfect at that time.", "A visitor may miss why an ordinary dish feels exactly right in that particular late-night setting.", "旅行者には、普通の料理がなぜその夜の時間にぴったりなのか伝わらないことがあります。"),
            ("The story around the food can matter as much as the taste.", "The people, place, and reason for being awake can matter as much as the food itself.", "起きていた理由や、一緒にいた人、場所も、食べ物そのものと同じくらい大切です。"),
        ],
        prompts=[
            prompt("The 11 p.m. order", "夜11時の注文", "It's 11pm and you're hungry. What do you order?", "夜11時にお腹がすきました。何を注文しますか？", ["What makes that your first choice?", "Where would you order it from?"]),
            prompt("A late-night situation", "夜食がほしくなる時", "What kind of night makes late-night food especially appealing?", "どんな夜だと、夜食が特にほしくなりますか？", ["What keeps you awake on a night like that?", "How does your mood affect what you want to eat?"]),
            prompt("Your likely choice", "選びそうなもの", "If you ate late at night, what would you be most likely to choose?", "夜遅くに食べるなら、いちばん選びそうなものは何ですか？", ["How would it compare with your daytime choice?", "What might make you choose something else?"]),
            prompt("What decides it", "食べるかどうか", "What usually decides whether you eat after 10 p.m.?", "夜10時以降に食べるかどうかは、普段何で決まりますか？", ["Does hunger or routine matter more?", "What would make a late meal worth it?"]),
            prompt("Who with", "一緒に食べる人", "If you shared a late-night meal, who would it be with?", "誰かと夜食を食べるなら、誰を選びますか？", ["How might that person change the order?", "What would be different if you ate alone?"]),
            prompt("The morning after", "翌朝", "What late-night food might you regret in the morning?", "翌朝に後悔しそうな夜食は何ですか？", ["What might feel wrong the next day?", "Why could it still be tempting at night?"]),
            prompt("Japan's best late-night food", "日本の最高の夜食", "What is the best late-night food in Japan?", "日本でいちばんの夜食は何ですか？", ["Where should someone try it?", "What makes it especially good late at night?"]),
            prompt("What I might miss", "私に伝わりにくいこと", "What would I not understand about that food at first?", "その食べ物について、私が最初は理解できなさそうなことは何ですか？", ["Which detail would change my mind?", "What should I order with it?"]),
        ],
    ),
    26: topic(
        slug="a-food-combination-you-just-dont-understand",
        title="A food combination you just don't understand",
        ko="도무지 이해할 수 없는 음식 조합",
        ja="どうしても理解できない食べ合わせ",
        goal=("Let's explore where your taste says yes, no, or maybe.", "食べ合わせについて、自分の「あり・なし・場合による」を話しましょう。"),
        outcomes=(("Take an immediate side", "すぐに立場を選ぶ"), ("Explain a real taste experience", "実際の味の体験を説明する"), ("Set the point where you would try it", "試してもよい条件を決める")),
        article_title=("When two foods meet", "二つの食べ物が出会うとき"),
        articles=[
            ("A food pairing can feel normal in one place and strange in another.", "A food pairing can feel completely ordinary in one culture and deeply strange in another.", "ある文化では普通の食べ合わせが、別の文化ではとても奇妙に感じられます。"),
            ("Sweet and salty tastes often work together because each makes the other clearer.", "Sweet and salty flavors often work together because contrast makes both more noticeable.", "甘さと塩気は、対比によって互いをはっきりさせるため、よく合います。"),
            ("Texture can matter as much as flavor when two foods are combined.", "Texture can be just as decisive as flavor when two foods are brought together.", "二つの食べ物を合わせるとき、食感も味と同じくらい重要です。"),
            ("A combination may sound worse than it tastes because the name creates an image first.", "A combination can sound worse than it tastes because its description creates resistance before the first bite.", "名前から先にイメージができるため、実際の味より悪く聞こえる組み合わせもあります。"),
            ("Trying one careful version is different from judging every version.", "Trying one well-made version provides better evidence than judging the whole idea from a poor example.", "丁寧に作られた一つを試すことは、すべてを決めつけることとは違います。"),
            ("An acquired taste may become enjoyable only after several tries.", "An acquired taste may become enjoyable only after familiarity replaces the initial surprise.", "慣れて好きになる味は、最初の驚きが薄れてから楽しめるようになります。"),
            ("People defend familiar combinations because they carry memories as well as flavor.", "People often defend familiar combinations because they carry memory and identity as well as flavor.", "なじみのある組み合わせには、味だけでなく思い出や自分らしさも含まれています。"),
            ("Refusing a food can be about smell, texture, or an ingredient—not closed-mindedness.", "Refusal may come from smell, texture, or a specific ingredient rather than simple closed-mindedness.", "食べ物を断る理由は、偏見ではなく、匂いや食感、特定の材料かもしれません。"),
            ("The person offering the food and the setting can change our willingness to try it.", "Trust in the person offering the food and the setting can change our willingness to experiment.", "すすめる人への信頼や場面によって、試す気持ちは変わります。"),
            ("A fair conversation leaves room for both curiosity and a firm no.", "A fair food conversation makes room for genuine curiosity as well as a firm personal limit.", "公平な食べ物の会話では、好奇心にも、はっきり断ることにも余地があります。"),
        ],
        prompts=[
            prompt("Pineapple on pizza", "パイナップルのピザ", "Pineapple on pizza — yes or no?", "パイナップルのピザは、ありですか、なしですか？", ["Would you eat one slice right now?", "Would your answer change if someone else ordered it?"]),
            prompt("What pineapple adds", "パイナップルの役割", "What do you think pineapple adds to a pizza?", "パイナップルはピザに何を加えると思いますか？", ["How might the sweetness work or clash?", "Would texture matter more than flavor?"]),
            prompt("Why your side", "その立場の理由", "What matters most in your answer: taste, texture, or the idea itself?", "答えを決めるうえで、味、食感、組み合わせのイメージのどれがいちばん大切ですか？", ["Which detail is hardest to accept?", "What detail might work better than expected?"]),
            prompt("Your own combination", "自分の組み合わせ", "Invent an unusual food combination that might actually work.", "意外でも、実際には合いそうな食べ合わせを考えてください。", ["What would make the flavors work together?", "Who might enjoy it most?"]),
            prompt("Hard to understand", "理解しにくい組み合わせ", "Which popular food pairing is hardest for you to understand?", "人気はあるけれど、自分にはいちばん理解しにくい食べ合わせは何ですか？", ["What exactly feels wrong about it?", "What could make a better version of it?"]),
            prompt("A changed mind", "変わるかもしれない好み", "What food combination could you imagine changing your mind about?", "どんな食べ合わせなら、考えが変わるかもしれませんか？", ["What would persuade you to try it again?", "Whose version would you trust?"]),
            prompt("A firm no", "絶対に無理", "What food combination would you refuse to try?", "どんな食べ合わせなら、試すのを断りますか？", ["Is the limit about one ingredient?", "Could any setting change your answer?"]),
            prompt("One fair chance", "一度だけ試すなら", "Which strange combination would you give one fair chance?", "変わった食べ合わせを一つだけ公平に試すなら、何にしますか？", ["Who would you trust to make it?", "What would count as a successful first bite?"]),
        ],
    ),
    27: topic(
        slug="a-restaurant-you-want-to-keep-to-yourself",
        title="A restaurant you want to keep to yourself",
        ko="나만 알고 싶은 식당",
        ja="人に教えたくないお気に入りの店",
        goal=("Let's introduce a favorite restaurant without losing what makes it special.", "特別さを守りながら、お気に入りの店について話しましょう。"),
        outcomes=(("Describe the place and order", "店と注文を説明する"), ("Tell how you found it", "見つけた経緯を話す"), ("Explain what popularity might change", "人気で変わりそうなことを説明する")),
        article_title=("The problem with a hidden gem", "隠れた名店を教える難しさ"),
        articles=[
            ("A favorite restaurant can feel personal even though it is a public place.", "A favorite restaurant can feel strangely personal despite being open to everyone.", "誰でも入れる店でも、お気に入りのレストランは個人的な場所のように感じられます。"),
            ("We may value the staff, pace, and atmosphere as much as the food.", "The staff, pace, and atmosphere may matter just as much as the menu itself.", "料理だけでなく、店員、時間の流れ、雰囲気も大切かもしれません。"),
            ("A regular order creates comfort because we know exactly what will arrive.", "A regular order creates comfort through the certainty of knowing exactly what will arrive.", "いつもの注文には、何が来るか分かる安心感があります。"),
            ("Finding a place by chance makes it feel like a discovery we earned.", "Finding a place by chance can make it feel like a discovery we personally earned.", "偶然見つけた店は、自分で発見した特別な場所のように感じられます。"),
            ("Taking one trusted person there can deepen the connection.", "Sharing the place with one trusted person can deepen our own connection to it.", "信頼する人を一人連れて行くと、その店とのつながりが深まることがあります。"),
            ("Word-of-mouth helps a good business survive.", "Word-of-mouth can help an excellent independent business remain financially sustainable.", "口コミは、よい個人店が続いていく助けになります。"),
            ("Too much attention can also bring lines, noise, and a different atmosphere.", "Too much attention can also bring queues, noise, hurried service, and a changed atmosphere.", "注目されすぎると、行列や騒音、急いだ接客で雰囲気が変わることもあります。"),
            ("Keeping a place secret protects our experience but does not support the owner.", "Keeping a place secret may protect our experience while doing nothing to support the owner.", "店を秘密にすれば自分の体験は守れますが、店主の助けにはなりません。"),
            ("A hidden gem is often special because it fits one person's needs, not everyone's.", "A hidden gem often feels special because it fits one person's habits rather than universal standards.", "隠れた名店は、誰にでも最高だからではなく、ある人の習慣に合うから特別なことがあります。"),
            ("The best recommendation tells the right person why the place suits them.", "The most thoughtful recommendation matches the place to the right person and explains why.", "いちばんよいおすすめは、その店に合う人を考え、理由を伝えることです。"),
        ],
        prompts=[
            prompt("A place you protect", "教えたくない店", "What restaurant—real or imagined—would you want to keep to yourself?", "実在する店でも想像の店でも、秘密にしておきたいレストランはどんな店ですか？", ["What makes it feel special?", "Who would you trust enough to tell?"]),
            prompt("The kind of place", "どんな店？", "What is the restaurant like?", "そのレストランはどんな店ですか？", ["What kind of food does it serve?", "What makes the atmosphere feel special?"]),
            prompt("Where it is", "場所", "Where would people find it?", "その店はどこにありそうですか？", ["What is the area like?", "How easy would it be to find?"]),
            prompt("Your order", "選びたい注文", "What would you order there?", "そこで何を注文したいですか？", ["Why would that be your first choice?", "What else might be worth trying?"]),
            prompt("How it is found", "見つける方法", "How might someone discover it?", "その店は、どのように見つけられそうですか？", ["What would make someone return?", "Would they expect it to be good at first?"]),
            prompt("Who you would take", "連れて行きたい人", "Who would you take there first?", "最初に誰を連れて行きたいですか？", ["How might they react?", "Would sharing it change the place for you?"]),
            prompt("If it became popular", "人気になったら", "What would change if the restaurant became popular?", "そのレストランが人気になったら、何が変わると思いますか？", ["Which change would bother you most?", "What might improve for the owner?"]),
            prompt("Worth keeping quiet", "秘密にする価値", "What makes a restaurant worth keeping quiet?", "どんなレストランなら、人に教えずにおきたくなりますか？", ["Where is the line between sharing and protecting it?", "What would make you recommend it widely?"]),
        ],
    ),
    28: topic(
        slug="a-book-you-chose-for-someone-else",
        title="A book you chose for someone else",
        ko="누군가를 위해 고른 책",
        ja="誰かのために選んだ本",
        goal=("Let's tell the story behind a book chosen for another person.", "誰かのために選んだ本にある物語を話しましょう。"),
        outcomes=(("Describe the book and recipient", "本と贈る相手を説明する"), ("Explain why it fit", "合うと思った理由を話す"), ("Choose a book for the tutor", "講師に一冊選ぶ")),
        article_title=("Choosing a book for someone", "誰かのために本を選ぶこと"),
        articles=[
            ("Giving a book away means making a guess about another person's interests.", "Giving a book away requires a careful guess about another person's interests, time, and attention.", "本を贈ることは、相手の興味を想像して選ぶことです。"),
            ("A book we love is not automatically the right book for someone else.", "A book that mattered deeply to us is not automatically appropriate for someone else.", "自分にとって大切な本が、必ずしも相手に合うとは限りません。"),
            ("The best choice often connects with a conversation we have already had.", "The most thoughtful choice often grows out of a conversation or concern the two people have shared.", "よい選択は、二人が以前に話したことや共有した関心から生まれることが多いです。"),
            ("A short note can explain why the giver thought of that person.", "A brief personal note can explain the connection without telling the recipient how to read the book.", "短いメモなら、読み方を押しつけずに、なぜその人を思い出したか伝えられます。"),
            ("The recipient may feel pressure if the giver keeps asking whether they finished it.", "Repeatedly asking whether the recipient finished the book can turn a gift into an obligation.", "読み終えたか何度も聞くと、贈り物が義務のようになることがあります。"),
            ("Some people enjoy receiving a recommendation more than owning another object.", "For some people, the recommendation itself is more valuable than receiving another physical object.", "人によっては、本という物より、おすすめそのもののほうがうれしい場合があります。"),
            ("A book can continue a conversation long after it is given.", "A well-chosen book can continue a conversation long after the moment of giving.", "よく選ばれた本は、贈ったあとも長く会話を続けてくれます。"),
            ("Not knowing whether it was read can be part of giving without conditions.", "Accepting that we may never know whether it was read is part of giving without conditions.", "読まれたか分からないことを受け入れるのも、条件をつけずに贈ることの一部です。"),
            ("The book that helped us may help another person for a completely different reason.", "A book that helped us may reach another person through an entirely different idea or moment.", "自分を助けた本が、別の人にはまったく違う理由で届くことがあります。"),
            ("Choosing for someone reveals how we see them as well as what we like.", "Choosing a book for someone reveals our view of that person as much as our own taste.", "誰かのために本を選ぶと、自分の好みだけでなく、その人をどう見ているかも表れます。"),
        ],
        prompts=[
            prompt("A book to give away", "人に贈る本", "What book would you choose for someone else, and who would receive it?", "誰かに本を贈るなら、どの本を誰に選びますか？", ["What makes the match interesting?", "Would you add a note?"]),
            prompt("A book chosen for you", "自分のために選ばれた本", "What book has someone chosen for you, or what would you love them to choose?", "誰かが自分のために選んだ本、または選んでほしい本は何ですか？", ["What would that choice say about you?", "Who knows your reading taste best?"]),
            prompt("The book", "その本", "What is the book you chose about?", "選んだ本は、どんな内容ですか？", ["What makes it memorable?", "Which part might interest the other person most?"]),
            prompt("A good choice", "よい選択だった証拠", "How would you know the book was a good choice for them?", "その本が相手に合っていたと、どうすれば分かりますか？", ["What response would you hope for?", "Would it matter if they never finished it?"]),
            prompt("Why that book", "その本を選んだ理由", "Why does that book seem right for them?", "なぜその本が相手に合うと思いますか？", ["Which part makes you think of them?", "What other book could also fit?"]),
            prompt("Knowing the book", "本をどこまで知る？", "How well do you need to know a book before giving it to someone?", "人に本を贈る前に、その本をどのくらい知っている必要がありますか？", ["Would you give a book you had not read?", "What would make you trust someone else's recommendation?"]),
            prompt("Choosing well", "よい選び方", "What makes a book a good gift?", "どんな本がよい贈り物になりますか？", ["How much should the giver explain?", "When is a recommendation better than a gift?"]),
            prompt("A book for me", "私に選ぶ一冊", "Ask me what I enjoy reading, then choose a book for me.", "私がどんな本を読むのが好きか聞いてから、私に一冊選んでください。", ["Why does it fit what I told you?", "What would you ask after I read it?"]),
        ],
    ),
    29: topic(
        slug="a-hobby-other-people-underestimate",
        title="A hobby other people underestimate",
        ko="사람들이 얕보는 취미",
        ja="人に価値を分かってもらいにくい趣味",
        goal=("Let's show what outsiders miss about a hobby.", "趣味について、外からは見えない魅力を伝えましょう。"),
        outcomes=(("Name a misunderstood hobby", "誤解される趣味を挙げる"), ("Describe its best moment", "最高の瞬間を説明する"), ("Invite someone in honestly", "正直に人を誘う")),
        article_title=("The work hidden inside a hobby", "趣味の中に隠れた工夫"),
        articles=[
            ("People can underestimate a hobby when they only see the result.", "An outsider can underestimate a hobby when they see only the final result.", "結果だけを見る人は、その趣味の価値を低く見てしまうことがあります。"),
            ("The person doing it notices choices and small improvements that others miss.", "The participant notices decisions, technique, and gradual improvement that outsiders overlook.", "実際にする人は、ほかの人が見逃す選択や技術、小さな上達に気づいています。"),
            ("Learning the details changes what counts as a good result.", "Learning the details completely changes what the person recognizes as quality.", "細部を学ぶと、何をよい結果と考えるかが変わります。"),
            ("Quiet hobbies can offer concentration without producing an exciting story.", "Quiet hobbies can provide deep concentration even when they produce no dramatic story to tell.", "静かな趣味は、派手な話にならなくても深い集中を与えてくれます。"),
            ("Repeated practice can be satisfying precisely because progress is slow.", "Repeated practice can become satisfying precisely because improvement is gradual and earned.", "上達がゆっくりで、自分の努力で得るものだからこそ、反復練習が楽しくなることがあります。"),
            ("The cost and time may make no sense until someone understands the reward.", "The time and expense may seem unreasonable until someone understands the kind of reward involved.", "どんな満足が得られるか分からないと、時間や費用が理解されにくいことがあります。"),
            ("A community gives people language for details that are hard to explain outside it.", "A community provides shared language for distinctions that are difficult to explain to outsiders.", "仲間がいると、外の人には説明しにくい違いを共有する言葉ができます。"),
            ("Trying the hobby once may not reveal the moment that regular participants love.", "A single attempt may never reach the moment that makes the hobby rewarding for regular participants.", "一度試すだけでは、続ける人が好きな瞬間まで届かないかもしれません。"),
            ("An honest invitation includes both the pleasure and the frustrating parts.", "An honest invitation explains both the pleasure and the frustrating parts instead of hiding them.", "正直に誘うなら、楽しさだけでなく、もどかしい部分も隠さず伝えます。"),
            ("Helping someone notice one detail can change how they see the whole activity.", "Teaching someone to notice one meaningful detail can transform their view of the entire activity.", "大切な細部を一つ見つける手助けをすると、その活動全体の見方が変わることがあります。"),
        ],
        prompts=[
            prompt("A misunderstood hobby", "誤解される趣味", "What hobby do people underestimate?", "人に価値を分かってもらいにくい趣味は何ですか？", ["Why might it look boring from the outside?", "What do its fans understand?"]),
            prompt("What people do", "その趣味ですること", "What do people actually do in that hobby?", "その趣味では、実際にどんなことをしますか？", ["Which part takes the most attention?", "What might a beginner try first?"]),
            prompt("What outsiders miss", "外から見えないもの", "What do outsiders miss about the hobby?", "その趣味について、外の人は何を見落としていますか？", ["Which detail takes time to notice?", "What looks easier than it really is?"]),
            prompt("How it begins", "始め方", "What is the best way for a beginner to start?", "初心者が始めるなら、どんな方法がいちばんよいですか？", ["What might make someone continue after the first try?", "Who could help a beginner understand it?"]),
            prompt("Time for it", "必要な時間", "How much time does the hobby need before it becomes rewarding?", "その趣味が面白くなるまで、どのくらい時間が必要ですか？", ["How could someone make room for it?", "When would the time begin to feel well spent?"]),
            prompt("The best moment", "最高の瞬間", "What seems like the best moment in the hobby?", "その趣味で、いちばんよさそうな瞬間は何ですか？", ["How often might that moment happen?", "What has to go right first?"]),
            prompt("What is underestimated", "低く見られている点", "Why might people underestimate the hobby?", "なぜ人はその趣味を低く評価するかもしれませんか？", ["Which image might need correcting?", "Could any criticism be fair?"]),
            prompt("Convince me to try", "私を誘うなら", "What would convince me to try it once?", "私が一度試してみたくなるように、何を伝えますか？", ["What should my first experience be?", "What difficulty should you warn me about?"]),
        ],
    ),
    30: topic(
        slug="something-in-your-room-you-would-never-throw-away",
        title="Something in your room you would never throw away",
        ko="방에서 절대 버리지 않을 물건",
        ja="部屋にある絶対に捨てないもの",
        goal=("Let's tell the story of an object you would keep.", "手元に残したい物の物語を話しましょう。"),
        outcomes=(("Choose and describe the object", "物を選んで説明する"), ("Tell how it gained value", "価値が生まれた経緯を話す"), ("Imagine its future", "その物の未来を考える")),
        article_title=("Why ordinary objects become irreplaceable", "普通の物がかけがえなくなる理由"),
        articles=[
            ("An ordinary object can become valuable because of the story attached to it.", "An ordinary object can become irreplaceable because of the personal history attached to it.", "普通の物でも、そこに結びついた物語によって、価値のあるものになります。"),
            ("Its market price may have little connection to its sentimental value.", "Its market price may have almost no relationship to its sentimental value.", "市場での値段と、その物への思い入れは、ほとんど関係がないかもしれません。"),
            ("A gift can preserve a relationship even when the giver is far away.", "A gift can preserve a sense of connection even when the giver is far away.", "贈り物は、贈った人が遠くにいても、つながりを残してくれます。"),
            ("Marks and damage can become part of the memory instead of reducing the value.", "Marks, repairs, and damage can become evidence of a shared history rather than defects.", "傷や修理の跡が、欠点ではなく、共に過ごした歴史になることがあります。"),
            ("Keeping everything makes it harder to see which objects truly matter.", "Keeping everything can make it harder to recognize which objects carry genuine meaning.", "何でも取っておくと、本当に大切な物が見えにくくなります。"),
            ("A keepsake earns its space by helping us remember something specific.", "A keepsake earns its place by preserving a specific person, event, or version of ourselves.", "思い出の品は、特定の人や出来事、昔の自分を残すことで、置いておく価値を持ちます。"),
            ("Other people may not understand why the object matters.", "The object's meaning may be completely invisible to anyone outside the story.", "その物の意味は、物語を知らない人にはまったく見えないことがあります。"),
            ("Throwing something away can feel like choosing which memories remain visible.", "Discarding an object can feel like deciding which parts of our past remain physically visible.", "物を捨てることは、過去のどの部分を目に見える形で残すか決めるように感じられます。"),
            ("A photograph can preserve the appearance, but not always the physical feeling.", "A photograph can preserve appearance, but it cannot always replace texture, weight, or physical presence.", "写真は見た目を残せますが、手触りや重さ、その物がある感覚までは置き換えられません。"),
            ("The objects we still keep in ten years may tell a different story about us.", "The objects that survive another decade may tell a different story about who we became.", "10年後にも残っている物は、自分がどんな人になったかという別の物語を伝えるかもしれません。"),
        ],
        prompts=[
            prompt("The object", "その物", "What object would you never throw away?", "絶対に捨てたくない物は何ですか？", ["What makes it irreplaceable?", "What would you notice first if it disappeared?"]),
            prompt("Your oldest object", "いちばん古い持ち物", "Which object you own has been with you the longest?", "持っている物の中で、いちばん長く手元にあるものは何ですか？", ["How often do you use or notice it?", "What shows its age?"]),
            prompt("How you got it", "手に入れた経緯", "How did you get the object?", "その物をどうやって手に入れましたか？", ["What was happening in your life then?", "What makes the way you got it memorable?"]),
            prompt("How long", "持っている期間", "How long have you had it?", "どのくらい長く持っていますか？", ["How has it changed over that time?", "What part has stayed the same?"]),
            prompt("Who understands", "大切さが分かる人", "Who would best understand why the object matters to you?", "その物が自分にとって大切な理由を、いちばん理解してくれそうなのは誰ですか？", ["How would that person explain its value?", "What would be hardest to explain to a stranger?"]),
            prompt("Possible regret", "捨てたら後悔する物", "What kind of object are you most likely to regret throwing away?", "どんな物を捨てると、いちばん後悔しそうですか？", ["What memory could make it hard to replace?", "How do you decide when to let something go?"]),
            prompt("Ten years from now", "10年後", "Which object will you still have in ten years?", "10年後にも持っていそうな物は何ですか？", ["What might happen to it by then?", "Who might care about it after you?"]),
            prompt("The story to share", "伝えたい物語", "Tell me the story of the object you would show me first.", "私に最初に見せたい物の物語を話してください。", ["Which detail should I notice?", "What would a photograph fail to capture?"]),
        ],
    ),
    31: topic(
        slug="what-you-actually-wear",
        title="What you actually wear",
        ko="실제로 자주 입는 옷",
        ja="実際によく着る服",
        goal=("Let's compare the clothes you own with the clothes you actually wear.", "持っている服と、実際に着る服を比べましょう。"),
        outcomes=(("Describe the real wardrobe", "実際の手持ちの服を説明する"), ("Explain a change in taste", "好みの変化を話す"), ("Choose beyond the usual limits", "普段の制限なしで選ぶ")),
        article_title=("The small wardrobe inside the big one", "たくさんの服の中の小さな定番"),
        articles=[
            ("Most people wear a small part of their wardrobe much more than the rest.", "Most people rely on a surprisingly small part of their wardrobe while much of it remains untouched.", "多くの人は、手持ちの服の一部ばかり着て、ほかはほとんど使いません。"),
            ("Comfort, weather, and daily routines often decide more than fashion.", "Comfort, climate, work, and daily routines often shape our choices more strongly than fashion does.", "流行よりも、着心地、天気、日課が服を決めることがよくあります。"),
            ("A go-to outfit saves time because the pieces already work together.", "A go-to outfit reduces decision-making because its pieces are already known to work together.", "定番の服装は、組み合わせが合うと分かっているので、考える時間を減らします。"),
            ("Some clothes belong to an imagined life rather than the life we actually live.", "Some clothes belong to an imagined version of our life rather than our actual routine.", "実際の生活ではなく、想像している生活のために持っている服もあります。"),
            ("We may keep an unworn item because it was expensive or once suited us.", "We may keep an unworn item because of its price, memory, or connection to an earlier identity.", "値段や思い出、昔の自分とのつながりから、着ない服を残すことがあります。"),
            ("Color can make a wardrobe easy to combine or feel repetitive.", "A limited color range can make a wardrobe coherent while also making it feel repetitive.", "色を絞ると組み合わせやすくなりますが、同じようにも感じられます。"),
            ("Our clothes change when our body, work, priorities, or confidence changes.", "Our wardrobe evolves as our body, work, priorities, and confidence change.", "体、仕事、優先順位、自信が変わると、服も変わります。"),
            ("Someone who dresses well may simply understand what suits their real life.", "A well-dressed person may be someone who understands what genuinely suits their life, not someone who owns more.", "おしゃれな人は、たくさん持っている人ではなく、自分の生活に合うものを分かっている人かもしれません。"),
            ("An unlimited budget would remove price, but not taste or practical needs.", "An unlimited budget would remove financial limits without removing taste, comfort, or practical needs.", "予算が無制限でも、好み、着心地、実用性は残ります。"),
            ("What we repeatedly wear is often a more honest picture of us than what we buy.", "What we repeatedly wear may reveal our real priorities more honestly than what we purchase.", "何を買うかより、何を繰り返し着るかのほうが、本当の優先順位を表すことがあります。"),
        ],
        prompts=[
            prompt("Your main colour", "多い色", "What colour is most of your wardrobe?", "手持ちの服でいちばん多い色は何ですか？", ["Why does that colour work for you?", "Which colour do you avoid?"]),
            prompt("What you wore today", "今日の服", "What made you choose what you're wearing today?", "今日の服を選んだ理由は何ですか？", ["Which part was practical?", "What would you change for a different plan?"]),
            prompt("What you wear most", "いちばん着るもの", "What do you actually wear most often?", "実際にいちばんよく着るものは何ですか？", ["What makes it reliable?", "How many versions of it do you own?"]),
            prompt("How it changed", "変わった好み", "How has what you wear changed in the past few years?", "ここ数年で、着る服はどう変わりましたか？", ["What caused the biggest change?", "Which old habit remains?"]),
            prompt("Owned but unworn", "持っているけれど着ない服", "Which item in your wardrobe gets worn least?", "手持ちの服の中で、いちばん着ていないものは何ですか？", ["Why did you buy or keep it?", "What would make you wear it again?"]),
            prompt("Never wear", "絶対に着ないもの", "What would you never wear?", "絶対に着ないものは何ですか？", ["Is the problem style, comfort, or situation?", "Could anyone wear it well, or is the item itself the problem?"]),
            prompt("Style you enjoy", "好きな着こなし", "Whose style do you enjoy looking at?", "誰の服の着こなしを見るのが好きですか？", ["What do they understand about clothes?", "Which part of their style would not work for you?"]),
            prompt("No budget limit", "予算がなければ", "What would you buy if your clothing budget had no limit?", "服の予算に上限がなければ、何を買いますか？", ["Would you buy more or buy differently?", "Which practical limit would still remain?"]),
        ],
    ),
    32: topic(
        slug="the-oldest-thing-you-still-use",
        title="The oldest thing you still use",
        ko="아직도 쓰는 가장 오래된 물건",
        ja="今も使っているいちばん古いもの",
        goal=("Let's tell the life story of something that still works.", "今も使える古い物の歩みを話しましょう。"),
        outcomes=(("Identify and date the object", "物と年代を説明する"), ("Explain why it lasted", "長く使えた理由を話す"), ("Decide what deserves keeping", "残す価値のある物を考える")),
        article_title=("What makes an object last", "物が長く使える理由"),
        articles=[
            ("An old object survives because someone keeps choosing to use it.", "An old object survives not only through durability, but because someone repeatedly chooses to use it.", "古い物が残るのは、丈夫だからだけでなく、誰かが繰り返し使うことを選ぶからです。"),
            ("Durable materials and simple construction can make repair easier.", "Durable materials and straightforward construction can make maintenance and repair possible.", "丈夫な材料と単純な作りは、手入れや修理をしやすくします。"),
            ("Familiarity also matters because we already know exactly how the object behaves.", "Familiarity matters because we understand the object's habits, limits, and small imperfections.", "使い慣れた物は、その特徴や限界、小さな欠点まで分かっています。"),
            ("Replacing it may require learning a new system for very little benefit.", "Replacing it may impose the cost of learning a new system for only a minor practical gain.", "買い替えると、わずかな利点のために新しい使い方を覚える必要があるかもしれません。"),
            ("An old tool may be less efficient but more dependable in a familiar task.", "An older tool may be less efficient on paper yet more dependable for a familiar task.", "古い道具は数字上は効率が低くても、慣れた作業では頼りになることがあります。"),
            ("Repairs create a record of how the object and its owner adapted.", "Repairs form a visible record of how the object and its owner have adapted over time.", "修理の跡は、物と持ち主が時間とともにどう対応してきたかを残します。"),
            ("Keeping everything old is different from keeping what still serves a purpose.", "Keeping every old object is different from deliberately keeping one that still serves a purpose.", "古い物を何でも残すことと、今も役立つ物を意識して残すことは違います。"),
            ("Some items are built to last, while others are difficult or expensive to repair.", "Some products are built to last, whereas others make repair difficult or uneconomical.", "長持ちするように作られた物もあれば、修理が難しい物や高くつく物もあります。"),
            ("The oldest useful thing in a home can reveal changing technology and habits.", "The oldest useful object in a home can reveal how technology and daily habits have changed around it.", "家で今も使ういちばん古い物から、技術や日々の習慣の変化が見えます。"),
            ("What we refuse to replace shows which qualities new products have not improved.", "What we refuse to replace can reveal which qualities newer products have failed to improve.", "買い替えたくない物は、新しい製品でも改善できていない大切な性質を教えてくれます。"),
        ],
        prompts=[
            prompt("Your oldest useful thing", "いちばん古い実用品", "What's the oldest thing you still use?", "今も使っているいちばん古い物は何ですか？", ["Where do you keep it?", "What does it look like now?"]),
            prompt("Used recently", "最近使った古い物", "Which old item did you use most recently?", "最近使った古い物は何ですか？", ["What made it useful?", "How often does it still earn a place in your day?"]),
            prompt("How old", "古さ", "How old is the object?", "その物はどのくらい古いですか？", ["How certain are you about its age?", "What else has changed since you got it?"]),
            prompt("How you got it", "手に入れた方法", "How did you get it?", "それをどうやって手に入れましたか？", ["Was it new at the time?", "Who chose it?"]),
            prompt("Why you kept it", "残した理由", "Why have you kept using it?", "なぜそれを使い続けていますか？", ["Which quality matters most?", "Has it ever needed repair?"]),
            prompt("Keeper or thrower", "残す人？捨てる人？", "Are you generally a keeper or a thrower?", "普段、物を残すほうですか、捨てるほうですか？", ["What is easiest for you to discard?", "Which category is hardest?"]),
            prompt("Repair or replace", "修理か買い替えか", "When do you repair something instead of replacing it?", "どんなとき、買い替えずに修理しますか？", ["What makes a repair worth the effort?", "When is replacement the better choice?"]),
            prompt("Never get rid of", "手放さない物", "What will you never get rid of?", "絶対に手放さない物は何ですか？", ["Is its value practical or personal?", "Who might use it after you?"]),
        ],
    ),
    33: topic(
        slug="a-food-you-only-eat-to-be-polite",
        title="A food you only eat to be polite",
        ko="예의상 먹는 음식",
        ja="礼儀のためだけに食べるもの",
        goal=("Let's talk about food, honesty, and politeness at the table.", "食卓での好み、正直さ、礼儀について話しましょう。"),
        outcomes=(("Describe the food and setting", "食べ物と場面を説明する"), ("Explain the polite response", "礼儀としての反応を説明する"), ("Choose what to say honestly", "正直に何と言うか選ぶ")),
        article_title=("Kindness when the food is not for you", "好みでない料理への思いやり"),
        articles=[
            ("Food offered by another person can carry effort, welcome, and pride.", "Food offered by another person can carry effort, hospitality, family history, and pride.", "人から出された料理には、手間、歓迎の気持ち、誇りが込められていることがあります。"),
            ("That meaning can make an honest dislike difficult to express.", "That social meaning can make a simple statement of dislike feel unexpectedly harsh.", "その意味があるため、嫌いだと正直に言うだけでも強く聞こえることがあります。"),
            ("Eating a small amount may show courtesy without pretending to love the food.", "Trying a small amount can show courtesy without requiring us to pretend that we love the dish.", "少し食べることで、大好きなふりをせずに礼儀を示せます。"),
            ("A warm comment about the effort or another dish can still be sincere.", "A warm, specific comment about the effort or another part of the meal can remain completely sincere.", "手間や別の料理について具体的に温かく伝えることは、十分に誠実です。"),
            ("Diet, allergies, and strong physical reactions require clearer boundaries.", "Dietary needs, allergies, and strong physical reactions require clear boundaries rather than politeness through eating.", "食事上の制限、アレルギー、強い身体反応がある場合は、食べて礼儀を示すより明確に断る必要があります。"),
            ("The relationship and the setting change how directly we can speak.", "Our relationship with the host and the formality of the setting shape how directly we can respond.", "相手との関係や場の改まり方によって、どのくらい直接言えるかが変わります。"),
            ("Hosts often prefer useful information to praise or enthusiasm that is obviously false.", "Thoughtful hosts often prefer useful information to praise or enthusiasm that is clearly insincere.", "思いやりのあるもてなし手は、明らかに本心ではない褒め言葉や反応より、役立つ情報を好むことがあります。"),
            ("A food that is loved by everyone else can make our own reaction feel strange.", "A food that everyone else adores can make us question or hide our own reaction.", "ほかの人がみんな大好きな料理だと、自分の反応を疑ったり隠したりすることがあります。"),
            ("Taste can change, but repeated polite eating does not guarantee that it will.", "Taste can evolve, although repeatedly eating something out of duty does not guarantee affection.", "好みは変わることがありますが、義務で何度も食べても好きになるとは限りません。"),
            ("Good table manners protect both the relationship and a person's real limits.", "Good table manners make room for both the relationship and a person's genuine limits.", "よい食卓の礼儀は、人間関係も、その人の本当の限界も守ります。"),
        ],
        prompts=[
            prompt("Eating to be polite", "礼儀のために食べるもの", "Is there something you eat to be polite?", "礼儀のために食べるものはありますか？", ["Which food comes closest?", "What would make it hard to refuse?"]),
            prompt("An awkward table", "困る食卓", "In what situation might food you do not want end up on your plate?", "食べたくないものが皿にのるとしたら、どんな場面ですか？", ["Who would have served it?", "Why would refusing feel awkward?"]),
            prompt("The food", "その食べ物", "What food would you only eat out of politeness?", "礼儀のためだけなら食べるものは何ですか？", ["Which taste or texture would be difficult?", "Could you enjoy any part of it?"]),
            prompt("Where it happens", "食べる場面", "Where would you be most likely to have to eat it?", "それを食べる可能性がいちばん高いのは、どんな場面ですか？", ["How formal would the situation be?", "Would your response change somewhere else?"]),
            prompt("Would anyone notice?", "気づかれる？", "Would people notice that you did not like it?", "好きではないことに、周りの人は気づくと思いますか？", ["What might reveal your reaction?", "How could another person respond?"]),
            prompt("What you would say", "やさしく伝える", "How would you tell someone kindly that you did not like the food?", "その料理が好きではなかったことを、やさしくどう伝えますか？", ["Which words would soften it?", "When might you need to be more direct?"]),
            prompt("Everyone else loves it", "みんなが好きなもの", "What food does everyone else seem to love that you do not get?", "ほかの人はみんな好きそうなのに、自分にはよさが分からない食べ物は何ですか？", ["What do people praise about it?", "Have you ever tried a better version?"]),
            prompt("Honesty or feelings", "正直さか気持ちか", "Which matters more at dinner: honesty or protecting the host's feelings?", "食事の場では、正直さと相手の気持ちを守ることのどちらが大切ですか？", ["When should honesty win?", "What would you want a guest to tell you?"]),
        ],
    ),
}


# The English variants intentionally differ in both language load and, in some
# rows, a bounded semantic detail.  Japanese support therefore resolves per
# variant before rendering; it is never read directly from one shared tuple
# slot.  Rows not listed here have genuinely identical support in both variants.
ARTICLE_JA_OVERRIDES = {
    "accessible": {
        (21, 3): "筋を追わなくてよくなると、くつろいで細かな点に気づけます。",
        (21, 7): "ある思い出と結びついているから、大切であり続ける映画もあります。",
        (21, 10): "人に見せたい場面には、その映画で何を大切にしているかが表れます。",
        (22, 1): "英語に最初に親しむきっかけは、勉強より娯楽から生まれることがよくあります。",
        (22, 2): "言葉の多くが分からなくても、歌や映画、ゲームにわくわくすることがあります。",
        (22, 4): "場面や歌詞を繰り返すうちに、知らない表現も少しずつ分かるようになります。",
        (22, 5): "一部分を理解できると、本当の突破口のように感じられます。",
        (22, 8): "字幕や翻訳は、英語そのものを失わずに楽しむ助けになります。",
        (22, 9): "よい入り口は、その人の興味によって変わります。",
        (22, 10): "よいおすすめは、なぜ楽しめそうかを伝えます。",
        (23, 1): "同じ曲でも、朝食中、仕事中、帰り道では違う役割を持ちます。",
        (23, 5): "歌詞も読み書きも言葉への集中を必要とするため、歌詞が読み書きの妨げになることがあります。",
        (23, 10): "一日の音楽は、計画していなくてもサウンドトラックになります。",
        (24, 6): "最初の曲がうまくいかなかったとき、予備の曲が助けになります。",
        (24, 9): "ほかの人にすすめるときは、その人の声や自信を考える必要があります。",
        (25, 1): "夜遅い空腹は、長い一日や食べ損ねた食事のあとによく起こります。",
        (25, 2): "その時間には、理想的な食事より手軽さが大切になることがあります。",
        (25, 5): "一人で食べる夜食と、誰かと分けて食べる夜食では、まったく違う思い出が生まれます。",
        (25, 8): "その土地の定番の夜食には、開いている店や分けやすさが表れます。",
        (25, 9): "旅行者には、なぜ普通の料理がその時間にはぴったりなのか分からないことがあります。",
        (25, 10): "食べ物の周りにある物語も、味と同じくらい大切になることがあります。",
        (26, 1): "ある場所では普通の食べ合わせが、別の場所では奇妙に感じられることがあります。",
        (26, 6): "慣れて好きになる味は、何度か試したあとで楽しめるようになることがあります。",
        (26, 7): "なじみのある組み合わせには、味だけでなく思い出も含まれています。",
        (26, 9): "すすめる人や場面によって、試す気持ちは変わります。",
        (27, 6): "口コミは、よい店が続いていく助けになります。",
        (27, 7): "注目されすぎると、行列や騒音で雰囲気が変わることもあります。",
        (27, 9): "隠れた名店は、誰にでも最高だからではなく、ある人に合うから特別なことがあります。",
        (28, 3): "よい選択は、二人が以前に話したことから生まれることが多いです。",
        (28, 4): "短いメモなら、なぜその人を思い出したか伝えられます。",
        (28, 5): "贈った人から読み終えたか何度も聞かれると、受け取った人はプレッシャーを感じることがあります。",
        (28, 7): "本は、贈ったあとも長く会話を続けてくれます。",
        (29, 2): "実際にする人は、ほかの人が見逃す選択や小さな上達に気づいています。",
        (29, 4): "静かな趣味は、面白い話にならなくても集中を与えてくれます。",
        (29, 5): "上達がゆっくりだからこそ、反復練習が楽しくなることがあります。",
        (29, 7): "仲間がいると、外の人には説明しにくい細部を話す言葉ができます。",
        (30, 4): "傷や損傷が、価値を下げるのではなく思い出の一部になることがあります。",
        (30, 6): "思い出の品は、何か具体的なことを思い出させるから、置いておく価値があります。",
        (30, 7): "ほかの人には、なぜその物が大切なのか分からないことがあります。",
        (30, 8): "物を捨てることは、どの思い出を目に見える形で残すか選ぶように感じられます。",
        (30, 9): "写真は見た目を残せますが、実物の感触までは残せないことがあります。",
        (30, 10): "10年後にも残っている物は、自分について別の物語を伝えるかもしれません。",
        (31, 5): "高かったり、昔は自分に似合ったりしたから、着ない服を残すことがあります。",
        (31, 6): "色によって、手持ちの服が組み合わせやすくなったり、同じように感じられたりします。",
        (31, 8): "おしゃれな人は、自分の生活に合うものを分かっているのかもしれません。",
        (31, 9): "予算が無制限でも、好みや実用性は残ります。",
        (31, 10): "何を買うかより、何を繰り返し着るかのほうが、本当の自分を表すことがあります。",
        (32, 1): "古い物が残るのは、誰かが繰り返し使うことを選ぶからです。",
        (32, 2): "丈夫な材料と単純な作りは、修理をしやすくします。",
        (32, 3): "使い慣れた物は、どう動くかがよく分かっているので大切です。",
        (32, 5): "古い道具は効率が低くても、慣れた作業では頼りになることがあります。",
        (32, 6): "修理の跡は、物と持ち主がどう対応したかという記録になります。",
        (32, 7): "古い物を何でも残すことと、今も役立つ物を残すことは違います。",
        (33, 4): "手間や別の料理について温かく伝えることは、十分に誠実です。",
        (33, 2): "その意味があるため、嫌いだと正直に伝えにくくなることがあります。",
        (33, 5): "食事上の制限、アレルギー、強い身体反応がある場合は、より明確に断る必要があります。",
        (33, 6): "相手との関係や場面によって、どのくらい直接言えるかが変わります。",
        (33, 7): "もてなす人は、明らかに本心ではない褒め言葉や反応より、役立つ情報を好むことがあります。",
        (33, 8): "ほかの人がみんな大好きな料理だと、自分の反応が変に感じられることがあります。",
        (33, 9): "好みは変わることがありますが、礼儀のために何度も食べても、変わるとは限りません。",
    },
    "full": {
        (21, 3): "筋を追う必要がなくなると、映像や感情表現のさりげない細部に気づけます。",
        (21, 5): "ほかの人と見ると、見慣れて気に留めなくなっていた場面に改めて気づけます。",
        (21, 9): "見返すことが、ストレスが多い時や落ち着かない時に安心できる小さな習慣になることがあります。",
        (22, 3): "楽しさがあれば、反復を作業と感じることなく、同じ英語に何度も触れられます。",
        (23, 2): "朝の音楽は、元気を与えたり、ゆっくりした始まりの静けさを守ったりできます。",
        (23, 5): "歌詞も読み書きも言葉への集中を必要とするため、歌詞が読み書きの妨げになることがあります。",
        (23, 9): "シャッフル再生では、個人的に好きな曲と公の場とのずれが面白く表れることがあります。",
        (24, 8): "歌詞やその曲との結びつきが人前で共有するには個人的すぎて、避ける曲もあります。",
        (25, 2): "その時間には、バランスのよい食事より、速さや手軽さを優先しがちです。",
        (25, 3): "無性に何かを食べたいときは、塩辛いもの、温かいもの、こってりしたものや、強くなじみを感じるものに手が伸びることがあります。",
        (25, 5): "一人で食べる軽食と誰かと囲む夜食では、込められる気持ちや意味がまったく違うことがあります。",
        (25, 9): "旅行者には、なぜ普通の料理が、夜遅くのその場面にこそぴったりなのか分からないことがあります。",
        (26, 4): "説明を聞いただけで、ひと口目の前に抵抗感が生まれ、実際の味より悪く聞こえる組み合わせもあります。",
        (26, 5): "上手に作られた一つを試すほうが、よくない一例から全体を判断するより、よい根拠になります。",
        (28, 1): "本を贈るときは、相手の興味だけでなく、その本を読む時間や集中力まで慎重に考える必要があります。",
        (28, 9): "自分を助けた本が、別の人にはまったく違う考えや瞬間を通して届くことがあります。",
        (30, 1): "普通の物でも、そこに結びついた個人的な歴史によって、かけがえのないものになります。",
        (31, 2): "流行よりも、着心地、気候、仕事、日課のほうが服の選択に強く影響することがよくあります。",
        (33, 1): "人から出された料理には、手間、もてなしの気持ち、家族の歴史、誇りが込められていることがあります。",
        (33, 7): "思いやりのあるホストは、明らかに本心ではない褒め言葉や反応より、役立つ情報を好むことがあります。",
    },
}


ARTICLE_JA = {
    topic_no: {
        variant: tuple(
            ARTICLE_JA_OVERRIDES[variant].get((topic_no, row), article[2])
            for row, article in enumerate(topic["articles"], 1)
        )
        for variant in ("accessible", "full")
    }
    for topic_no, topic in TOPICS.items()
}


CLAIM_ORDER = {
    number: tuple(f"{number}-{index:02d}" for index in range(1, 11))
    for number in TOPICS
}


VOCABULARY = {
    21: {"new": "rewatch|見返す", "recycled": "", "assumed": "film|映画; scene|場面; ending|結末; memory|思い出; detail|細部", "receptive": "comforting|心が落ち着く; ritual|習慣的な行為"},
    22: {"new": "breakthrough|突破口", "recycled": "", "assumed": "English|英語; song|曲; film|映画; game|ゲーム; subtitles|字幕; translation|翻訳", "receptive": "absorbing|夢中にさせる; formal study|正式な学習; gateway|入り口"},
    23: {"new": "soundtrack|場面に合う音楽", "recycled": "", "assumed": "music|音楽; song|曲; commute|通勤; mood|気分; lyrics|歌詞; shuffle|シャッフル再生", "receptive": "interfere|妨げる; repetitive|繰り返しの"},
    24: {"new": "backup song|予備の曲", "recycled": "", "assumed": "karaoke|カラオケ; song|曲; group|グループ; singer|歌う人; lyrics|歌詞", "receptive": "off-limits|避けるべき; flawless|完璧な; vocal range|音域"},
    25: {"new": "craving|無性に食べたい気持ち", "recycled": "restaurant|レストラン|CORE-10", "assumed": "food|食べ物; order|注文する; delivery|宅配; morning|朝; Japan|日本", "receptive": "solitary|一人きりの; irregular|不規則な"},
    26: {"new": "food pairing|食べ合わせ; acquired taste|慣れると好きになる味", "recycled": "", "assumed": "pizza|ピザ; pineapple|パイナップル; taste|味; texture|食感; ingredient|材料", "receptive": "resistance|抵抗感; closed-mindedness|偏見"},
    27: {"new": "hidden gem|隠れた名店; word-of-mouth|口コミ", "recycled": "restaurant|レストラン|CORE-10", "assumed": "staff|店員; menu|メニュー; atmosphere|雰囲気; owner|店主; order|注文", "receptive": "financially sustainable|経営を続けられる; universal standards|一般的な基準"},
    28: {"new": "", "recycled": "recommendation|おすすめ|FT-11", "assumed": "book|本; gift|贈り物; note|メモ; conversation|会話; recipient|受け取る人", "receptive": "obligation|義務; appropriate|ふさわしい; give away|人に贈る"},
    29: {"new": "underestimate|低く評価する", "recycled": "", "assumed": "hobby|趣味; result|結果; practice|練習; time|時間; cost|費用; community|仲間", "receptive": "outsider|外部の人; gradual|少しずつの"},
    30: {"new": "sentimental value|思い入れ; keepsake|思い出の品", "recycled": "", "assumed": "room|部屋; object|物; gift|贈り物; memory|思い出; photograph|写真", "receptive": "irreplaceable|かけがえのない; discard|捨てる"},
    31: {"new": "wardrobe|手持ちの服; go-to outfit|定番の服装", "recycled": "", "assumed": "clothes|服; colour|色; weather|天気; comfort|着心地; budget|予算; style|スタイル", "receptive": "coherent|まとまりのある; untouched|使われていない"},
    32: {"new": "durable|丈夫な; built to last|長持ちするように作られた", "recycled": "", "assumed": "old|古い; use|使う; repair|修理; replace|買い替える; object|物; tool|道具", "receptive": "maintenance|手入れ; uneconomical|費用に見合わない"},
    33: {"new": "courtesy|礼儀", "recycled": "", "assumed": "food|食べ物; dinner|食事会; host|もてなす人; taste|好み; allergy|アレルギー; effort|手間", "receptive": "hospitality|もてなし; dietary needs|食事上の制限"},
}


GLOSSES = {
    21: {"accessible": {9: ("Rewatching", "rewatch", "見返す")}, "full": {2: ("comforting", "comforting", "心が落ち着く")}},
    22: {"accessible": {5: ("breakthrough", "breakthrough", "突破口")}, "full": {9: ("gateway", "gateway", "入り口")}},
    23: {"accessible": {10: ("soundtrack", "soundtrack", "場面に合う音楽")}, "full": {5: ("interfere", "interfere", "妨げる")}},
    24: {"accessible": {6: ("backup song", "backup song", "予備の曲")}, "full": {2: ("vocal range", "vocal range", "音域")}},
    25: {"accessible": {3: ("craving", "craving", "無性に食べたい気持ち")}, "full": {5: ("solitary", "solitary", "一人きりの")}},
    26: {"accessible": {1: ("food pairing", "food pairing", "食べ合わせ"), 6: ("acquired taste", "acquired taste", "慣れると好きになる味")}, "full": {4: ("resistance", "resistance", "抵抗感")}},
    27: {"accessible": {6: ("Word-of-mouth", "word-of-mouth", "口コミ"), 9: ("hidden gem", "hidden gem", "隠れた名店")}, "full": {6: ("financially sustainable", "financially sustainable", "経営を続けられる")}},
    28: {"accessible": {1: ("Giving a book away", "give away", "人に贈る")}, "full": {5: ("obligation", "obligation", "義務")}},
    29: {"accessible": {1: ("underestimate", "underestimate", "低く評価する")}, "full": {1: ("outsider", "outsider", "外部の人")}},
    30: {"accessible": {2: ("sentimental value", "sentimental value", "思い入れ"), 6: ("keepsake", "keepsake", "思い出の品")}, "full": {1: ("irreplaceable", "irreplaceable", "かけがえのない")}},
    31: {"accessible": {1: ("wardrobe", "wardrobe", "手持ちの服"), 3: ("go-to outfit", "go-to outfit", "定番の服装")}, "full": {6: ("coherent", "coherent", "まとまりのある")}},
    32: {"accessible": {2: ("Durable", "durable", "丈夫な"), 8: ("built to last", "built to last", "長持ちするように作られた")}, "full": {2: ("maintenance", "maintenance", "手入れ")}},
    33: {"accessible": {3: ("courtesy", "courtesy", "礼儀")}, "full": {1: ("hospitality", "hospitality", "もてなし")}},
}


def set_complete(head: str) -> str:
    name = "podo:proofread-status"
    if f'name="{name}"' in head:
        return base.set_meta(head, name, "complete")
    return re.sub(
        r'(<meta name="podo:content-version" content="[^"]+">)',
        rf'\1\n  <meta name="{name}" content="complete">',
        head,
        count=1,
    )


def article_page(topic_no: int, topic_data: dict, variant: str) -> str:
    rows = []
    column = 0 if variant == "accessible" else 1
    for index, (article, claim_id) in enumerate(
        zip(topic_data["articles"], CLAIM_ORDER[topic_no], strict=True), start=1
    ):
        en = article[column]
        ja = ARTICLE_JA[topic_no][variant][index - 1]
        en_markup, words = base.marked_text(en, GLOSSES[topic_no][variant].get(index))
        rows.append(
            f'        <div class="sent" role="button" tabindex="0" data-sync-option="s{index}" data-claim-id="{claim_id}"><span class="s-line"><span class="s-ko">{en_markup}</span><span class="s-mark" aria-hidden="true"></span></span><span class="s-open"><span class="s-ja">{esc(ja)}</span>{words}</span></div>'
        )
    title, title_ja = topic_data["article_title"]
    body = '''      <p class="section-subtitle"><span class="ko">Did you have any questions about the article?</span><span class="ja">記事について何か質問はありましたか？</span></p>
      <div class="tutor-note">Answer the learner's questions, then move on. If there are none—or the learner did not complete the pre-study—skip the article; do not spend class time reading it.</div>
      <div class="sents" data-sync-id="article-open" data-sync-kind="selection" data-sync-state="open">
''' + "\n".join(rows) + '''
      </div>'''
    return base.page("article", title, title_ja, body)


def build(topic_no: int, variant: str) -> str:
    topic_data = TOPICS[topic_no]
    canonical = CANONICAL[variant].read_text(encoding="utf-8")
    head, foot = new_lesson.split_shell(canonical)
    slug = f'{topic_no:02d}-{topic_data["slug"]}'
    level = "B1 accessible" if variant == "accessible" else "B2-C1 full"
    head = new_lesson.retarget(
        head,
        review_id=f"FT-{topic_no}",
        lesson_id=slug,
        level=level,
        title=topic_data["title"],
        title_ko=topic_data["ko"],
        title_ja=topic_data["ja"],
        version="2026-08-21",
    )
    head = set_complete(head)
    head = base.set_meta(head, "podo:vocabulary-status", "reviewed")
    for category in ("new", "recycled", "assumed", "receptive"):
        head = base.set_meta(head, f"podo:vocabulary:{category}", VOCABULARY[topic_no][category])

    goal_en, goal_ja = topic_data["goal"]
    pages = [
        base.ft_contract.goal_page(
            title=topic_data["title"], title_ja=topic_data["ja"],
            topic_en=goal_en, topic_ja=goal_ja,
            data_act="Things I like", kicker="THINGS I LIKE",
        ),
        article_page(topic_no, topic_data, variant),
        base.extract_page(canonical, "lesson-style"),
        '''    <div class="transition-page" data-page-id="talk-intro" data-act="Let's talk"><span class="transition-kicker">8 QUESTION POOL</span><h2 class="transition-title">Let's talk <span class="title-ja">(話そう)</span></h2><p class="section-subtitle"><span class="ko">We don't need to answer every question. Let's follow the most interesting parts of your answers.</span><span class="ja">全部の質問に答える必要はありません。答えの中でいちばん面白いところを広げていきましょう。</span></p><div class="tutor-note">Treat these pages as a pool, not a sequence. React or share briefly before choosing the next prompt, skip freely, and move to feedback with 2–3 minutes left.</div></div>\n''',
    ]
    prompt_ids = (("warm-1", "WARM-UP 1"), ("warm-2", "WARM-UP 2")) + tuple(
        (f"q{i}", f"QUESTION {i}") for i in range(1, 7)
    )
    pages.extend(
        base.question_page(page_id, number, item, variant)
        for (page_id, number), item in zip(prompt_ids, topic_data["prompts"], strict=True)
    )
    pages.append(base.extract_page(canonical, "feedback"))
    output = TRACK / "courses" / f"{COURSE}-{variant}" / "lessons" / slug / "lesson.html"
    return new_lesson.redepth(head + "\n".join(pages) + foot, output)


def output_path(topic_no: int, variant: str) -> pathlib.Path:
    topic_data = TOPICS[topic_no]
    slug = f'{topic_no:02d}-{topic_data["slug"]}'
    return TRACK / "courses" / f"{COURSE}-{variant}" / "lessons" / slug / "lesson.html"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true", help="regenerate only this narrow batch")
    args = parser.parse_args()
    written = 0
    for topic_no in TOPICS:
        for variant in ("accessible", "full"):
            output = output_path(topic_no, variant)
            if output.exists() and not args.refresh:
                raise SystemExit(f"refusing to overwrite {output.relative_to(ROOT)}")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(build(topic_no, variant), encoding="utf-8")
            print(f"wrote {output.relative_to(ROOT)}")
            written += 1
    print(f"{written} Freetalking decks generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

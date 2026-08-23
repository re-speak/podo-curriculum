"""Reviewed standalone conversation prompts for Freetalking FT10-33.

The first prompt in each topic is owned by the authoritative Freetalking TOC.
This module replaces prompts 2-8 after that opening so every page can start a
conversation on its own. Accessible and full keep the same talking job; full
follow-ups deepen the idea without relying on academic wording.
"""

from __future__ import annotations


def reviewed(
    accessible: str,
    japanese: str,
    accessible_followups: tuple[str, str],
    full_followups: tuple[str, str],
    *,
    full: str | None = None,
) -> dict[str, object]:
    return {
        "accessible": accessible,
        "full": full or accessible,
        "ja": japanese,
        "accessible_followups": list(accessible_followups),
        "full_followups": list(full_followups),
    }


REWRITES = {
    10: [
        reviewed("What's taking up most of your free time these days?", "最近、自由時間の多くを何に使っていますか？", ("Did you choose to spend that time on it?", "What would you like more time for?"), ("Did you choose to give it that much time?", "What would you make more time for?")),
        reviewed("What's something you became interested in after trying it once?", "一度試したあと、興味を持つようになったものは何ですか？", ("What made the first try enjoyable?", "Do you usually try new things once or more than once?"), ("Which part caught your attention first?", "Do you usually try new things once or more than once?")),
        reviewed("Which new hobby would be easiest to fit into your week?", "新しい趣味の中で、あなたの一週間にいちばん取り入れやすいものは何ですか？", ("When could you do it?", "Which is easiest to fit into a week: exercise, reading, or a class?"), ("Which part of your week has room for it?", "Which is easiest to fit into a week: exercise, reading, or a class?")),
        reviewed("Who do you enjoy talking to about new interests?", "新しく興味を持ったことについて、誰と話すのが楽しいですか？", ("What makes that person easy to talk to?", "Do online groups make new interests easier to share?"), ("What kind of response do they usually give?", "Do online groups make new interests easier to share?")),
        reviewed("Do you prefer sharing new interests or keeping them private?", "新しい興味は人に話すほうですか、それとも自分だけにしておくほうですか？", ("What makes you mention an interest?", "When do you keep one to yourself?"), ("How much do other people's reactions matter?", "When does sharing make an interest more enjoyable?")),
        reviewed("What would you happily spend less time on for a new hobby?", "新しい趣味のためなら、何に使う時間を喜んで減らせますか？", ("Why would that be easy to reduce?", "What time would you protect?"), ("What would make the trade worth it?", "Which part of your routine would you refuse to give up?")),
        reviewed("What interest could grow into a bigger part of your life?", "これから生活の中でもっと大きな存在になりそうな興味は何ですか？", ("What would progress look like?", "Is an interest easier to keep alone or with other people?"), ("How could it change the way you spend your time?", "Is an interest easier to keep alone or with other people?")),
    ],
    11: [
        reviewed("How many episodes do you give a show before you quit?", "作品を見るのをやめる前に、何話くらいまで見ますか？", ("What helps you decide?", "Have you ever stopped after one episode?"), ("What has to happen before you commit to a series?", "What can make you leave after one episode?")),
        reviewed("What can keep you watching even when a story is slow?", "物語の進みが遅くても、見続けたくなるのはどんな要素ですか？", ("Is a character or the mood more important?", "What makes a slow story feel worth it?"), ("Which character or detail can carry a slow episode?", "When does slow become boring?")),
        reviewed("Which recommendation do you trust more: a friend or an app?", "作品のおすすめは、友人とアプリのどちらをより信頼しますか？", ("What does that source know about your taste?", "When has it given you a bad choice?"), ("What kind of recommendation feels personal?", "What does an app often misunderstand about your mood?")),
        reviewed("What makes you stop watching a show halfway?", "作品を途中で見るのをやめるのは、どんな理由からですか？", ("Which problem loses your interest fastest?", "What could make the show worth trying again?"), ("What can ruin a good series?", "What could make you try it again?")),
        reviewed("When is watching one more episode a bad idea?", "もう一話見るのがよくないのは、どんなときですか？", ("What do you need to do the next day?", "How late is too late?"), ("Which next-day responsibility would make you stop?", "What happens when you ignore that limit?")),
        reviewed("What makes an ending satisfying?", "どんな結末なら満足できますか？", ("Do you want every question answered?", "Can a sad ending still be good?"), ("Which loose ends need an answer?", "When can an open ending work better?")),
        reviewed("Do you enjoy a show more when you watch it alone or with someone else?", "作品は一人で見るほうが楽しめますか、それとも誰かと一緒に見るほうが楽しめますか？", ("What changes when another person is there?", "Which kind of show is better to share?"), ("When does company improve the experience?", "Which kind of show would you rather watch alone?")),
    ],
    12: [
        reviewed("What kind of compliment can feel awkward instead of nice?", "うれしいより、気まずく感じる褒め言葉はどんなものですか？", ("What makes it uncomfortable?", "Which is more awkward: praise from a stranger or praise in public?"), ("Does the speaker, timing, or wording matter most?", "Which is more awkward: praise from a stranger or praise in public?")),
        reviewed("Does praise matter more from someone close to you or from an expert?", "褒め言葉は、親しい人と専門家のどちらから言われるほうが心に響きますか？", ("Why does that person's praise matter?", "When might praise from a stranger still feel good?"), ("Why does that person's praise matter?", "When might praise from a stranger still feel good?")),
        reviewed("What makes a compliment feel believable?", "どんな褒め言葉なら信じられますか？", ("Does timing matter?", "What makes praise sound false?"), ("Which details show that the person truly noticed?", "Why can good praise still be hard to accept?")),
        reviewed("What's your natural reaction when someone praises you?", "褒められたとき、自然にどんな反応をしますか？", ("What do you say first?", "What do you feel but not say?"), ("Does your reaction change with the person?", "What response feels warm without rejecting the praise?")),
        reviewed("Which stays with you longer: a compliment or criticism?", "褒め言葉と批判では、どちらが長く心に残りますか？", ("Why do those words stay?", "Do they change what you do next?"), ("Why can one comment outweigh many others?", "How do you stop an unfair comment from taking over?")),
        reviewed("What do you notice that makes you want to compliment someone?", "人のどんなところに気づくと、褒めたくなりますか？", ("Do you notice effort or results first?", "What makes you say it aloud?"), ("Which quiet effort deserves more recognition?", "What makes a compliment useful rather than polite?")),
        reviewed("What everyday compliment should people give more often?", "日常で、もっと多く伝えるとよい褒め言葉は何ですか？", ("Who would enjoy hearing it?", "Which feels better: 'Good job' or praise about one specific thing?"), ("What could that compliment help someone notice?", "Which feels better: 'Good job' or praise about one specific thing?")),
    ],
    13: [
        reviewed("What would make this weekend feel well spent?", "今週末を有意義だったと感じるには、何があればよいですか？", ("Do you need rest, activity, or both?", "What would you like to avoid?"), ("What would leave you feeling refreshed?", "What would make the weekend feel wasted?")),
        reviewed("Do you like weekends planned or open?", "週末は予定を決めたいですか、それとも空けておきたいですか？", ("What is worth planning?", "How much time do you leave open?"), ("Which plans benefit from structure?", "When does an open day feel better?")),
        reviewed("Which sounds better this weekend: time alone or time with someone?", "今週末は、一人の時間と誰かと過ごす時間のどちらがよさそうですか？", ("What makes that choice appealing now?", "What balance would feel right?"), ("What kind of company would fit your mood?", "How much time alone would you still want?")),
        reviewed("What's one simple thing you would enjoy this weekend?", "今週末に楽しめそうな、簡単なことを一つ挙げるとしたら何ですか？", ("When would you do it?", "What would make it better?"), ("Why does that sound good right now?", "Who, if anyone, would you invite?")),
        reviewed("What usually makes you change a weekend plan?", "週末の予定を変えるのは、ふつうどんな理由からですか？", ("Which plans are easiest to change?", "When do you decide?"), ("Which change is easy to accept?", "When does a change improve the weekend?")),
        reviewed("What part of a weekend is worth planning ahead?", "週末のどんなことは、前もって決める価値がありますか？", ("What information helps most?", "What can wait until the day?"), ("Which decision becomes harder at the last minute?", "What is better left spontaneous?")),
        reviewed("If a plan gets canceled, what's your best backup?", "予定が中止になったら、いちばんよい代わりの過ごし方は何ですか？", ("Would you enjoy the extra free time?", "Would anyone else need to know?"), ("Could the backup be better than the original plan?", "How quickly would you decide what to do?")),
    ],
    14: [
        reviewed("Imagine finishing something important. What would change first?", "大切なことを終えたと想像してください。最初に何が変わりますか？", ("Which change would matter most?", "Would you celebrate or start the next goal?"), ("Which part of daily life would change?", "Would you celebrate or start the next goal?")),
        reviewed("What makes a goal worth your time?", "どんな目標なら、時間をかける価値がありますか？", ("What kind of change can it bring?", "What might you leave until later?"), ("How do you know the goal is truly yours?", "What would you refuse to give up for it?")),
        reviewed("Which gets in the way more: time, money, or doubt?", "目標の邪魔になりやすいのは、時間、お金、自信のなさのどれですか？", ("Why does it get in the way?", "Which part can a person control?"), ("How does that problem usually appear?", "What small step could help?")),
        reviewed("When is dropping a goal a smart decision?", "目標をやめることが賢い判断になるのは、どんなときですか？", ("What warning sign should someone notice?", "Is stopping always the same as failing?"), ("How do you know it is time to stop trying?", "Is stopping always the same as failing?")),
        reviewed("How can sharing a goal make success feel different?", "目標を誰かに話すと、達成したときの気持ちはどう変わりますか？", ("Who, if anyone, would understand the effort?", "Would you share it with one person or keep it private?"), ("Who, if anyone, would understand the effort?", "Would you share it with one person or keep it private?")),
        reviewed("What kind of goal is okay to change as life changes?", "生活が変わったとき、どんな目標なら変えてもよいと思いますか？", ("What part should stay important?", "Is it okay to make a goal smaller when life gets busy?"), ("What should stay important?", "Is it okay to make a goal smaller when life gets busy?")),
        reviewed("What's one useful first step toward a difficult goal?", "難しい目標に向かう、役に立つ最初の一歩は何ですか？", ("When could someone do it?", "What would make it easier?"), ("Why is that step small enough to start?", "What would show that it worked?")),
    ],
    15: [
        reviewed("What small purchase is hardest to resist?", "どんな小さな買い物がいちばん我慢しにくいですか？", ("What catches your attention?", "What makes walking away easier?"), ("What makes it especially tempting?", "What feeling are you hoping to get?")),
        reviewed("Which do you spend more on: convenience, comfort, or fun?", "便利さ、快適さ、楽しさの中で、どれにいちばんお金を使いますか？", ("What is a typical example?", "Has that changed recently?"), ("Why do you spend more on that?", "Which one would you most like to spend less on?")),
        reviewed("When does spending extra feel worth it?", "少し多くお金を使ってもよいと思うのは、どんなときですか？", ("Which benefit lasts longest?", "When would it feel like too much?"), ("What lasting benefit makes it worth the price?", "When is paying more no longer worth it?")),
        reviewed("What usually makes you decide not to buy something?", "物を買わないと決めるのは、ふつうどんな理由からですか？", ("Which reason matters most?", "When might you buy it anyway?"), ("Which warning sign makes you pause?", "How long do you wait before deciding?")),
        reviewed("What kind of spending looks wasteful to you but useful to someone else?", "自分には無駄に見えても、ほかの人には役立ちそうな出費は何ですか？", ("Why might they value it?", "Which is easier to understand: spending on hobbies or convenience?"), ("When could it be useful?", "Which is easier to understand: spending on hobbies or convenience?")),
        reviewed("What life change can completely change a budget?", "どんな生活の変化で、予算は大きく変わりますか？", ("Which cost would change first?", "What would become less important?"), ("Which new responsibility would matter most?", "How quickly would spending habits need to change?")),
        reviewed("If money became tight, what small pleasure would be hard to give up?", "お金に余裕がなくなったら、どんな小さな楽しみを手放しにくいですか？", ("Why does it matter to you?", "Could you find a cheaper version?"), ("What does that pleasure add to daily life?", "What limit would make you finally cut it?")),
    ],
    16: [
        reviewed("Which is harder: starting something new or being bad at it?", "新しいことを始めることと、うまくできないことでは、どちらが難しいですか？", ("What makes that part uncomfortable?", "What could make it easier?"), ("Where does the discomfort come from?", "When can it become enjoyable?")),
        reviewed("What gives people the final push to try something new?", "新しいことを試す最後のきっかけになるのは何ですか？", ("Does another person's help matter?", "Can waiting make it harder?"), ("How much does encouragement matter?", "When does curiosity become stronger than fear?")),
        reviewed("What's something that is often easier than people expect?", "人が思っているより簡単なことは何ですか？", ("Why does it look difficult at first?", "What helps a beginner?"), ("Which part creates the wrong impression?", "What still takes real practice?")),
        reviewed("What makes a first try worth repeating?", "初めて試したことを、もう一度やりたいと思うのはどんなときですか？", ("What would you change the second time?", "Does company make a difference?"), ("Which small success makes a second try likely?", "What would you do differently next time?")),
        reviewed("Which first-time experiences make the best stories?", "どんな初体験が、いちばん面白い話になりますか？", ("Which detail makes them memorable?", "Can an awkward start improve the story?"), ("Why are mistakes often the best part later?", "What makes a story worth retelling?")),
        reviewed("What helps you enjoy being a beginner?", "初心者であることを楽しむには、何が役立ちますか？", ("What kind of progress feels good?", "Who makes learning more fun?"), ("How can you lower the pressure to be good?", "Which sign of progress keeps you curious?")),
        reviewed("What would be fun to try with no pressure to be good at it?", "上手にできなくてもよいなら、何を試すと楽しそうですか？", ("What makes it appealing?", "Would you try it alone or with someone?"), ("What would make the timing right?", "What might surprise you about the experience?")),
    ],
    17: [
        reviewed("What effort do people often make without getting credit?", "人はどんな努力をしても、なかなか評価されないことがありますか？", ("Why is that work easy to miss?", "Who benefits from it?"), ("What makes the effort almost invisible?", "How could people recognize it better?")),
        reviewed("What kind of progress is easy to miss?", "どんな進歩は見落としやすいですか？", ("What small sign shows it?", "When does it become clear?"), ("Why do people notice results before progress?", "How could someone record that change?")),
        reviewed("How can you tell when someone has been working hard quietly?", "人が人知れず頑張っていたことは、どうすれば分かりますか？", ("What small sign would show it?", "Would asking about it help?"), ("What small changes can show the effort?", "How should someone respond when they notice?")),
        reviewed("How do you celebrate a small win?", "小さな成功を、どのように祝いますか？", ("Do you tell anyone?", "What simple reward feels good?"), ("When is private satisfaction enough?", "How can celebrating help the next step?")),
        reviewed("When is keeping a small win private better than sharing it?", "小さな成功を人に話さず、自分だけにしておくほうがよいのはどんなときですか？", ("Why might sharing feel uncomfortable?", "Who would still understand it?"), ("Can sharing change the meaning of the win?", "When does telling someone make it more valuable?")),
        reviewed("Which helps more: praise from someone else or noticing your own progress?", "ほかの人に褒められることと、自分の進歩に気づくことでは、どちらがより役立ちますか？", ("Why does that one help?", "When does the other one matter?"), ("Which kind of motivation lasts longer?", "How can outside praise become less important?")),
        reviewed("What small sign can show that a month went well?", "一か月がうまくいったと分かる、小さなサインは何ですか？", ("Which result matters most?", "Did you have more good days or bad days this month?"), ("Why is that sign meaningful?", "Did you have more good days or bad days this month?")),
    ],
    18: [
        reviewed("Which matters more in a song: lyrics, voice, or beat?", "曲では、歌詞、声、リズムのどれがいちばん大切ですか？", ("What is one example?", "What can make you choose differently?"), ("Which element creates the first impression?", "Which one keeps the song interesting?")),
        reviewed("When do you get tired of a song you love?", "好きな曲に飽きるのは、どんなときですか？", ("How often is too often?", "What makes you return later?"), ("Does overplaying change the song or your mood?", "How long does a song need to feel fresh again?")),
        reviewed("What kind of memory can a song bring back instantly?", "曲を聴くと、どんな思い出がすぐによみがえりますか？", ("Which detail returns first?", "How does the memory change the song?"), ("Why does music hold that memory so strongly?", "Can the feeling change over time?")),
        reviewed("What activity is better with music?", "音楽があるともっとよくなる活動は何ですか？", ("What kind of music fits it?", "When would silence be better?"), ("How does the music change your pace or mood?", "Which task needs silence instead?")),
        reviewed("What can make a favorite song hard to hear?", "好きな曲でも、聴くのがつらくなるのはどんな理由からですか？", ("Can a memory change the song?", "Would time make it easier?"), ("Can a song belong too strongly to one period?", "What might help someone enjoy it again?")),
        reviewed("What song would you send someone who needed energy?", "元気が必要な人に、どんな曲を送りますか？", ("What part gives it energy?", "When you need energy, do you choose a fast song or a familiar one?"), ("Would the lyrics or sound matter more?", "When you need energy, do you choose a fast song or a familiar one?")),
        reviewed("Which song belongs on a playlist about your year?", "今年を表すプレイリストに、どんな曲を入れますか？", ("What part of the year does it match?", "Would your year need a happy song or a calm one?"), ("What story would the song tell?", "Would your year need a happy song or a calm one?")),
    ],
    19: [
        reviewed("What do you usually do instead of the task you're avoiding?", "やるべきことを避けているとき、代わりに何をしますか？", ("Why is that activity tempting?", "Does it help you feel better?"), ("What feeling are you trying to avoid?", "When does the distraction create more stress?")),
        reviewed("Which gets harder after a delay: starting or finishing?", "先延ばしにすると、始めることと終わらせることのどちらが難しくなりますか？", ("Why does that part get harder?", "What can make it easier again?"), ("How does the delay change the task in your mind?", "What breaks that pattern?")),
        reviewed("Which task is easiest to put off: boring, difficult, or unclear?", "退屈な仕事、難しい仕事、はっきりしない仕事の中で、いちばん先延ばしにしやすいのはどれですか？", ("Why does that type cause delay?", "What would make it clearer or easier?"), ("Which emotion comes with that kind of task?", "What first step reduces the resistance?")),
        reviewed("What problems can a small unfinished task cause?", "小さな用事を終わらせないままにすると、どんな問題が起こりますか？", ("Who else might be affected?", "Can a tiny task create a lot of stress?"), ("Why can a tiny task stay on your mind?", "Can a tiny task create a lot of stress?")),
        reviewed("What can make you start an annoying task right away?", "面倒な用事でも、すぐに始められるのはどんなときですか？", ("Does a deadline help?", "Would doing only five minutes work?"), ("Which outside pressure is actually useful?", "How can you make the first step smaller?")),
        reviewed("How do you reward yourself after finishing something annoying?", "面倒なことを終えたあと、どのように自分にご褒美をあげますか？", ("What reward fits a small task?", "Do you plan it before starting?"), ("Does the reward improve motivation or only relief?", "When is finishing itself enough?")),
        reviewed("What's one trick that makes a delayed task easier to restart?", "先延ばしにしたことを再開しやすくするコツは何ですか？", ("What could you prepare first?", "Who could help?"), ("How could you make the task feel easier?", "How much would you try to finish on the first day back?")),
    ],
    20: [
        reviewed("What are the three things you usually take when you go out?", "出かけるとき、ふつう持っていく三つの物は何ですか？", ("Which one do you use first?", "Which one could you leave behind?"), ("Which item earns its place every day?", "What changes on a longer day out?")),
        reviewed("Which bulky everyday item is still worth carrying?", "かさばっても持ち歩く価値がある日用品は何ですか？", ("When is it most useful?", "Would you carry an umbrella, a water bottle, or something else?"), ("When is it most useful?", "Would you carry an umbrella, a water bottle, or something else?")),
        reviewed("What do you reach for most when you're away from home?", "外出中に、いちばんよく手に取る物は何ですか？", ("What do you use it for?", "What would happen without it?"), ("Which part of your day depends on it?", "Could another item replace it?")),
        reviewed("What emergency item do people carry but rarely use?", "人が持ち歩いていても、めったに使わない非常用の物は何ですか？", ("What problem is it for?", "Is it worth carrying?"), ("How serious would the problem need to be?", "When does being prepared become too much?")),
        reviewed("What do people forget most often when they leave home?", "家を出るとき、人は何をいちばん忘れやすいですか？", ("When do they usually notice?", "What is the easiest backup?"), ("Why is that item easy to forget?", "How does forgetting it change the day?")),
        reviewed("Which things did phones replace in people's pockets?", "スマートフォンは、人が持ち歩いていたどんな物の代わりになりましたか？", ("Which old item do you miss?", "What might phones replace next?"), ("Which replacement made daily life easier?", "What was lost when the old item disappeared?")),
        reviewed("What can you guess about someone from what's in their bag?", "バッグの中身から、その人について何が分かると思いますか？", ("Which item tells you the most?", "What could make you guess wrong?"), ("Which item tells you the most?", "What could make you guess wrong?")),
    ],
    21: [
        reviewed("Which film scene can you picture clearly even now?", "今でもはっきり思い浮かべられる映画の場面はどれですか？", ("What happens in it?", "Why did it stay with you?"), ("Which visual or line makes it memorable?", "Has its meaning changed for you?")),
        reviewed("Which is more fun: watching a favorite again or trying a new film?", "好きな映画をもう一度見ることと、新しい映画を見ることでは、どちらが楽しいですか？", ("Why does that choice win?", "When would you choose the other one?"), ("What do you gain from that choice?", "What mood could reverse your answer?")),
        reviewed("What detail do people often miss the first time they watch a film?", "映画を初めて見るとき、人はどんな細部を見落としやすいですか？", ("Why is it easy to miss?", "Do you notice acting, music, or background details first?"), ("Does knowing the ending help?", "Do you notice acting, music, or background details first?")),
        reviewed("Who would make an interesting person to watch a film with?", "誰と映画を見ると、面白くなりそうですか？", ("What might they notice?", "Would you rather watch with someone who has the same taste or different taste?"), ("Would you choose someone with similar taste or different taste?", "Which scene would you watch their reaction to?")),
        reviewed("What makes a popular film hard for some people to enjoy?", "人気の映画でも、人によって楽しみにくいのはどんな理由からですか？", ("Which criticism could be fair?", "Can too much hype make a film harder to enjoy?"), ("What were they expecting?", "Can too much hype make a film harder to enjoy?")),
        reviewed("How can watching a film again change your opinion of it?", "映画をもう一度見ると、その映画への意見はどう変わりますか？", ("What might you notice the second time?", "Can a film seem better or worse as you get older?"), ("What might you notice the second time?", "Can a film seem better or worse as you get older?")),
        reviewed("Which Japanese film would you show someone first?", "日本映画を初めて見る人に、最初にどの作品を見せますか？", ("Why is it a good introduction?", "Would comedy, drama, or animation be the easiest introduction?"), ("Why is it a good introduction?", "Would comedy, drama, or animation be the easiest introduction?")),
    ],
    22: [
        reviewed("Which lets you enjoy English most easily: music, shows, books, or games?", "音楽、番組、本、ゲームの中で、英語をいちばん楽しみやすいのはどれですか？", ("What makes that format easier?", "When do you use it?"), ("Which kind of attention does it require?", "What would make another format easier?")),
        reviewed("Which helps an English line stay in your memory: sound, meaning, or repetition?", "英語の一言を覚えやすくするのは、音、意味、繰り返しのどれですか？", ("Does understanding every word matter?", "Can a line stay with you even when you do not fully understand it?"), ("Can sound make a line memorable before its meaning is clear?", "When does repetition become annoying?")),
        reviewed("How much of a story do you need to understand before you can enjoy it?", "物語を楽しむには、どのくらい理解する必要がありますか？", ("Can pictures or music fill the gaps?", "When does missing English become frustrating?"), ("Which clues carry the meaning without words?", "What kind of missing detail matters most?")),
        reviewed("Do subtitles help you enjoy English, or distract you from it?", "字幕は英語を楽しむ助けになりますか、それとも気が散りますか？", ("Which language do you prefer?", "When do you turn them off?"), ("What do subtitles help you notice?", "What can they stop you from hearing?")),
        reviewed("When you hear a new English expression, do you look it up or keep watching?", "新しい英語表現を聞いたとき、調べますか、それともそのまま見続けますか？", ("What makes you stop and check?", "When is guessing enough?"), ("When does looking it up improve the experience?", "When does it break the flow?")),
        reviewed("What makes English practice stop feeling like study?", "英語の練習が勉強のように感じなくなるのは、どんなときですか？", ("What keeps it fun?", "How much challenge is enough?"), ("When does repetition become enjoyable?", "What can make fun content feel like homework?")),
        reviewed("What would you recommend to someone who wants fun English?", "楽しく英語に触れたい人に、何をおすすめしますか？", ("Why is it a good starting point?", "Would you recommend music, a show, or a game first?"), ("How much English do they need to understand?", "Would you recommend music, a show, or a game first?")),
    ],
    23: [
        reviewed("What was the last piece of music you played?", "最後に聴いた音楽は何ですか？", ("Why did you choose it?", "What were you doing then?"), ("Did you choose it or let an app choose?", "How well did it fit the moment?")),
        reviewed("Which fits a bad mood better: music that matches it or music that changes it?", "気分が悪いとき、その気分に合う音楽と気分を変える音楽のどちらがよいですか？", ("Why does that help?", "When would you choose the other kind?"), ("What does matching the mood allow you to feel?", "When can changing the mood work better?")),
        reviewed("What kind of song works best in the morning?", "朝にはどんな曲がいちばん合いますか？", ("How should it make you feel?", "Would the same song work at night?"), ("Which sound sets the right pace?", "What would feel too intense early in the day?")),
        reviewed("What kind of music makes it harder to concentrate?", "どんな音楽だと集中しにくくなりますか？", ("Do lyrics cause the problem?", "Which task needs silence?"), ("Which musical detail steals your attention?", "Can familiar music become easier to ignore?")),
        reviewed("Which old song takes you back to a specific time?", "どの昔の曲を聴くと、ある時期を思い出しますか？", ("What comes back first?", "Do old songs bring back people or places more strongly?"), ("What connects it to that time?", "Do old songs bring back people or places more strongly?")),
        reviewed("What song would surprise people if it played from your phone?", "あなたのスマートフォンから流れたら、人が驚きそうな曲は何ですか？", ("Why would they not expect it?", "Do people usually guess your music taste correctly?"), ("Why would it surprise them?", "Do people usually guess your music taste correctly?")),
        reviewed("Which moment needs music most: morning, travel, or late night?", "朝、移動中、夜遅くの中で、音楽がいちばん必要なのはいつですか？", ("What does music add at that time?", "Which of the other two could be quiet?"), ("What does music add at that time?", "Which of the other two could be quiet?")),
    ],
    24: [
        reviewed("What kind of karaoke night would you enjoy most?", "どんなカラオケの夜がいちばん楽しそうですか？", ("How many people would be there?", "What would make the mood comfortable?"), ("Would the group be serious singers or casual ones?", "What could ruin the atmosphere?")),
        reviewed("What makes a karaoke song easier than it sounds?", "聞いた感じより歌いやすいカラオケ曲には、どんな特徴がありますか？", ("Is an easy chorus or a comfortable key more important?", "Would a slow song or a fast song be easier?"), ("Is an easy chorus or a comfortable key more important?", "Would a slow song or a fast song be easier?")),
        reviewed("What's the easiest way to learn a karaoke song?", "カラオケの曲を覚えるいちばん簡単な方法は何ですか？", ("Do you start with the words or the melody?", "How many times do you need to hear it?"), ("Does singing along or listening first work better?", "Which mistake is hardest to notice?")),
        reviewed("What's a good backup song when your first choice feels wrong?", "最初に選んだ曲が合わないとき、どんな曲がよい予備になりますか？", ("Why is it reliable?", "Would you choose a slow song or a group song as a backup?"), ("What makes a backup song safe?", "Would you choose a slow song or a group song as a backup?")),
        reviewed("What would you never sing at karaoke?", "カラオケで絶対に歌わない曲は何ですか？", ("What makes it a bad fit?", "Would the right group change your mind?"), ("Is the limit about the song or the situation?", "Could a private room change the answer?")),
        reviewed("What makes a song good for a whole group?", "どんな曲なら、グループ全員で楽しめますか？", ("Should everyone know the words?", "Who should start it?"), ("How important is a familiar chorus?", "When can a group song exclude someone?")),
        reviewed("Ask me what I enjoy singing, then recommend one karaoke song.", "私に歌うのが好きな曲を聞いてから、カラオケ曲を一つおすすめしてください。", ("Why does it fit my answer?", "What should my backup be?"), ("Which detail in my answer guided you?", "What warning would you give me before I try it?")),
    ],
    25: [
        reviewed("What kind of night makes late-night food especially appealing?", "どんな夜だと、夜食が特に魅力的に感じますか？", ("What keeps you awake?", "How does your mood affect the food?"), ("Which need matters most then: comfort, speed, or hunger?", "What makes the meal memorable?")),
        reviewed("Which is better late at night: a hot meal or a quick snack?", "夜遅くには、温かい食事と手軽な軽食のどちらがよいですか？", ("Why does that fit the time?", "When would you choose the other one?"), ("How does the next morning affect your choice?", "Which situation reverses your answer?")),
        reviewed("What decides whether you eat after 10 p.m.?", "夜10時を過ぎて食べるかどうかは、何で決まりますか？", ("Does hunger or routine matter more?", "When is food worth it?"), ("How much does the next day's schedule matter?", "Which feeling can be mistaken for hunger?")),
        reviewed("Who makes a late-night meal more fun to share?", "夜食を一緒に食べると楽しくなるのは、どんな人ですか？", ("What would you order together?", "How would eating alone feel different?"), ("What kind of conversation fits that meal?", "Could company change what you order?")),
        reviewed("What late-night food might you regret in the morning?", "朝になって後悔しそうな夜食は何ですか？", ("What might feel wrong the next day?", "Why is it still tempting?"), ("Which part creates the regret: amount, spice, or timing?", "When might it still be worth it?")),
        reviewed("What is the best late-night food in Japan?", "日本でいちばんよい夜食は何ですか？", ("Where should someone try it?", "Why is it good late at night?"), ("Why is it better at night?", "Would a visitor understand why people like it?")),
        reviewed("What late-night food looks ordinary but makes perfect sense at that hour?", "普通に見えても、夜遅くにはぴったりな食べ物は何ですか？", ("What changes at that time?", "What should someone order with it?"), ("Which detail would a visitor miss?", "Would it feel as good during the day?")),
    ],
    26: [
        reviewed("Which would you rather try: sweet-and-salty popcorn or meat with fruit?", "甘じょっぱいポップコーンと果物を使った肉料理なら、どちらを試したいですか？", ("What sounds good about it?", "What could make the other one work?"), ("What sounds good about it?", "What could make the other one work?")),
        reviewed("Which matters most in a strange food combination: taste, texture, or the idea?", "変わった食べ合わせでは、味、食感、組み合わせのイメージのどれがいちばん大切ですか？", ("Which part is hardest to accept?", "What could work better than expected?"), ("How much can the name influence the first bite?", "Which part can a skilled cook fix?")),
        reviewed("Which sounds better to try: chocolate with chili, fries with ice cream, or something else?", "試すなら、チョコレートと唐辛子、フライドポテトとアイスクリーム、それとも別の組み合わせのどれがよさそうですか？", ("What might make the flavors work?", "Would you try one bite?"), ("Which contrast makes it sound interesting?", "How would you serve it?")),
        reviewed("Which popular food pairing is hardest for you to understand?", "人気があっても、いちばん理解しにくい食べ合わせは何ですか？", ("What feels wrong about it?", "Could a better version work?"), ("Is the problem flavor, texture, or the idea?", "What do fans probably enjoy?")),
        reviewed("What food combination could you imagine changing your mind about?", "考えが変わるかもしれない食べ合わせは何ですか？", ("What would persuade you to try it?", "Whose version would you trust?"), ("What would make you willing to try it again?", "Could one good meal change your mind?")),
        reviewed("What food combination would you refuse to try?", "絶対に試したくない食べ合わせは何ですか？", ("Is one ingredient the problem?", "Could any setting change your answer?"), ("Where does curiosity stop for you?", "Is the limit about safety or simply how it feels?")),
        reviewed("Who would you trust to choose one strange bite for you?", "変わった食べ物を一口だけ選んでもらうなら、誰を信頼しますか？", ("Why would you trust their taste?", "What rule would you give them?"), ("Would you want a safe surprise or a real challenge?", "Would liking one bite be enough?")),
    ],
    27: [
        reviewed("What makes a small restaurant feel special?", "小さなレストランが特別に感じられるのは、どんなところですか？", ("Is the food or atmosphere more important?", "What makes people return?"), ("Which detail cannot be copied easily?", "How much does the owner matter?")),
        reviewed("Where do the best hidden restaurants usually appear?", "よい穴場のレストランは、どんな場所にあることが多いですか？", ("Why are they easy to miss?", "How would you find one?"), ("What makes the location part of the experience?", "Would a central location change the feeling?")),
        reviewed("What's one dish that can make a restaurant worth returning to?", "その一品のためにまた行きたくなる料理は何ですか？", ("What makes it reliable?", "Would you ever order something else?"), ("Which detail keeps it memorable?", "Can one great dish carry an average menu?")),
        reviewed("Which recommendation do you trust most: a friend, reviews, or walking past?", "友人、口コミ、店の前を通った印象の中で、どれをいちばん信頼しますか？", ("Why does that source feel reliable?", "When has it been wrong?"), ("What information does that source give you?", "Which source is easiest to fake?")),
        reviewed("Who is the best person to take to a tiny favorite restaurant?", "お気に入りの小さなレストランに連れて行くなら、どんな人がいちばんよいですか？", ("What would they enjoy?", "Would sharing it change the place for you?"), ("What kind of guest would understand the place?", "Who might accidentally spoil the experience?")),
        reviewed("What changes when a small restaurant becomes popular?", "小さなレストランが人気になると、何が変わりますか？", ("Which change would bother regulars?", "What might improve for the owner?"), ("Can the place grow without losing its character?", "Which disadvantage would be fair to accept?")),
        reviewed("When does keeping a great restaurant secret become unfair to the owner?", "すてきなレストランを秘密にすることが、店主に不公平になるのはどんなときですか？", ("What help might the restaurant need?", "Would you tell one friend or post online?"), ("When does secrecy stop helping the owner?", "Would you tell one friend or post online?")),
    ],
    28: [
        reviewed("Would you give someone a book you love or choose one from their wish list?", "自分の好きな本を贈りますか、それとも相手の欲しい本のリストから選びますか？", ("Why would you choose that way?", "When might the other choice be better?"), ("Why would you choose that way?", "When might the other choice be better?")),
        reviewed("What should you know about someone before choosing a book for them?", "その人のために本を選ぶ前に、相手について何を知っておくとよいですか？", ("Does their free time matter?", "Which interest helps most?"), ("How much does their reading mood matter?", "What should the giver avoid guessing?")),
        reviewed("How can you tell that a book matches someone?", "本がその人に合っているかは、どうすれば分かりますか？", ("What reaction would you hope for?", "Would finishing the book matter?"), ("Which response would show a real connection?", "Can a good match still go unfinished?")),
        reviewed("Would you give someone a book you haven't read?", "自分が読んでいない本を、人に贈りますか？", ("What would make you trust it?", "What would you say about the choice?"), ("Whose recommendation would be enough?", "What responsibility does the giver have?")),
        reviewed("When is recommending a book better than buying it as a gift?", "本を贈るより、おすすめするだけのほうがよいのはどんなときですか？", ("What pressure can a gift create?", "When is buying it more thoughtful?"), ("How can a gift make someone feel they have to read it?", "What choice does a recommendation leave open?")),
        reviewed("What note would you write inside a gift book?", "本を贈るとき、中にどんなメッセージを書きますか？", ("Would you explain why you chose it?", "How personal would the note be?"), ("What should the note avoid promising?", "Could the note matter more than the book?")),
        reviewed("Ask me what I enjoy reading, then choose a book for me.", "私に好きな読書について聞いてから、本を一冊選んでください。", ("Why does it fit my answer?", "What might surprise me?"), ("Which part of my answer guided the choice?", "What would you ask after I read it?")),
    ],
    29: [
        reviewed("Which hobby looks easy but takes real skill?", "簡単そうに見えて、実は技術が必要な趣味は何ですか？", ("Which skill is hidden?", "Which looks easier than it is: cooking, photography, or gaming?"), ("Why do outsiders miss the difficulty?", "Which looks easier than it is: cooking, photography, or gaming?")),
        reviewed("What part of a quiet hobby can be exciting?", "静かな趣味でも、どんなところがわくわくしますか？", ("What does a fan notice?", "Can a quiet hobby still feel competitive?"), ("Which small decision creates excitement?", "Can a quiet hobby still feel competitive?")),
        reviewed("What can a beginner do in the first hour of a new hobby?", "新しい趣味を始めた最初の一時間に、初心者は何ができますか？", ("What would feel successful?", "Who or what could help?"), ("Which early result would encourage them?", "What should they not worry about yet?")),
        reviewed("How long should someone try a hobby before deciding it's not for them?", "趣味が自分に合わないと決める前に、どのくらい試すべきですか？", ("What needs time to become fun?", "When is stopping reasonable?"), ("Which difficulty is only temporary?", "What sign shows a real mismatch?")),
        reviewed("What moment makes a hobby feel rewarding?", "趣味をやっていてよかったと感じるのは、どんな瞬間ですか？", ("How often does it happen?", "What has to go right first?"), ("Is progress or enjoyment more important then?", "Can a frustrating hobby still be rewarding?")),
        reviewed("Why do people judge hobbies from the outside?", "なぜ人は、趣味を外から見ただけで判断するのでしょうか？", ("Which image can be misleading?", "Could any criticism be fair?"), ("What is impossible to see without trying it?", "How can fans explain it without overselling?")),
        reviewed("Which hobby would you try once if it were completely free?", "すべて無料なら、一度試してみたい趣味は何ですか？", ("What makes it interesting?", "What difficulty would you expect?"), ("Would free equipment be enough to start?", "What might make you continue after one try?")),
    ],
    30: [
        reviewed("What ordinary object can become valuable because of a story?", "物語があることで価値が生まれる、普通の物は何ですか？", ("What kind of story changes it?", "Can a cheap object become valuable because of a memory?"), ("Why can the story matter more than the object?", "Can a cheap object become valuable because of a memory?")),
        reviewed("Which loss would be harder: an everyday tool or a childhood photo?", "日用品と子どものころの写真では、どちらをなくすほうがつらいですか？", ("Why is that one harder to replace?", "Could money solve either loss?"), ("Why is that one harder to replace?", "Could money solve either loss?")),
        reviewed("When can a useful gift become sentimental?", "実用的な贈り物が思い出の品になるのは、どんなときですか？", ("Does the giver or the memory matter more?", "Would a watch, bag, or kitchen tool be a good example?"), ("Does the giver or the memory matter more?", "Would a watch, bag, or kitchen tool be a good example?")),
        reviewed("Who understands a sentimental object better: the giver or the owner?", "思い出のある物をよりよく理解するのは、贈った人と持ち主のどちらですか？", ("What does each person know?", "Could their stories differ?"), ("Whose story would you want to hear first?", "How can the object connect two memories?")),
        reviewed("What kind of object are people most likely to regret throwing away?", "人が捨てたあとで後悔しやすいのは、どんな物ですか？", ("What memory makes it hard to replace?", "How can someone decide before throwing it out?"), ("Why does the value become clear too late?", "Would a photograph preserve enough?")),
        reviewed("What object today might still matter in ten years?", "今ある物の中で、十年後も大切そうなものは何ですか？", ("What could happen to it by then?", "Would its value be practical or personal?"), ("How might its meaning change?", "Who else could care about it?")),
        reviewed("If your room became a small museum, what would you put in it?", "自分の部屋を小さな博物館にするなら、何を展示しますか？", ("What story would the label tell?", "Which detail should visitors notice?"), ("What would it show about your life?", "What would a photograph fail to capture?")),
    ],
    31: [
        reviewed("What made you choose what you're wearing today?", "今日の服を選んだ理由は何ですか？", ("Which part was practical?", "What would you change for another plan?"), ("Did comfort, weather, or appearance matter most?", "What does the choice say about your day?")),
        reviewed("What do you actually wear most often?", "実際にいちばんよく着るものは何ですか？", ("What makes it reliable?", "How many versions do you own?"), ("What makes it your usual choice?", "When would you choose something else?")),
        reviewed("Which has changed how you dress most: work, weather, or comfort?", "仕事、天気、着心地の中で、服装をいちばん変えたのはどれですか？", ("What changed first?", "Which old habit remains?"), ("How did daily life drive the change?", "Would you dress differently somewhere else?")),
        reviewed("Why do people keep clothes they rarely wear?", "人はなぜ、ほとんど着ない服を持ち続けるのでしょうか？", ("Which reason is most common?", "When should they finally let the clothes go?"), ("Which reason is most common?", "When should they finally let the clothes go?")),
        reviewed("What would you never wear?", "絶対に着ないものは何ですか？", ("Is the problem style, comfort, or situation?", "Could anyone wear it well?"), ("Which limit is strongest for you?", "Could the right event change your answer?")),
        reviewed("What kind of personal style do you enjoy looking at?", "どんなファッションを見るのが好きですか？", ("What makes that style interesting?", "Would you rather look at a simple style or a colorful one?"), ("What makes that style interesting?", "Do you admire the clothes or the confidence?")),
        reviewed("What would you buy if your clothing budget had no limit?", "服に使えるお金に制限がなければ、何を買いますか？", ("Would you buy more or buy differently?", "Which practical limit would remain?"), ("Would quality or variety matter more?", "What would you still refuse to buy?")),
    ],
    32: [
        reviewed("What old item works better than its newer version?", "新しい物よりよく使える古い物は何ですか？", ("What does it do better?", "Why do people still replace it?"), ("Which design choice makes it better?", "What advantage does the newer version have?")),
        reviewed("How can you guess an object's age just by looking at it?", "物を見ただけで、その古さはどう分かりますか？", ("Which mark shows its age?", "Can old things still look new?"), ("Does wear make the object better or worse?", "Which materials age well?")),
        reviewed("What old object becomes more beautiful after years of use?", "何年も使うことで、より美しくなる古い物は何ですか？", ("What changes over time?", "Would you prefer it new?"), ("Which signs of age add character?", "When does wear stop being attractive?")),
        reviewed("Why do some things last while others break quickly?", "長く使える物と、すぐ壊れる物があるのはなぜですか？", ("Does care or quality matter more?", "Which part usually fails first?"), ("How much does repairable design matter?", "Can a cheap object still be built to last?")),
        reviewed("Do you usually keep things or get rid of them quickly?", "物を取っておくほうですか、それともすぐに手放すほうですか？", ("What is easiest to get rid of?", "Which kind is hardest?"), ("What rule guides your decision?", "When has your habit caused a problem?")),
        reviewed("When do you repair something instead of replacing it?", "物を買い替えず、修理するのはどんなときですか？", ("What makes the effort worth it?", "When is replacement better?"), ("Which matters more: the cost or your feelings about the item?", "What should companies make easier to repair?")),
        reviewed("Which objects made today could still be useful in ten years?", "今作られている物の中で、十年後も役立ちそうなのは何ですか？", ("What would help them last?", "Which could last longer: a tool, furniture, or clothing?"), ("What would help them last?", "Which could last longer: a tool, furniture, or clothing?")),
    ],
    33: [
        reviewed("Which is harder to refuse: a homemade dish from a friend or an expensive dish at a restaurant?", "友人の手料理とレストランの高価な料理では、どちらが断りにくいですか？", ("Why does that one create pressure?", "When would refusal be easier?"), ("Why does that one create pressure?", "When would refusal be easier?")),
        reviewed("What taste or texture is hardest to hide your reaction to?", "反応を隠すのがいちばん難しい味や食感は何ですか？", ("What does your face do?", "Could a better version change your mind?"), ("Why does the reaction happen so quickly?", "How could a host notice without words?")),
        reviewed("Where is it hardest to say no to food: at someone's home, at work, or at a restaurant?", "食べ物を断りにくいのは、誰かの家、職場、レストランのどこですか？", ("What makes that place difficult?", "What could someone say politely?"), ("What kind of pressure appears there?", "When is refusing still reasonable?")),
        reviewed("How can a host tell that a guest doesn't like a dish?", "客が料理を好きではないと、ホストはどうすれば分かりますか？", ("Which small reaction gives it away?", "How should the host respond?"), ("What might the host misunderstand?", "How can they make refusal feel safe?")),
        reviewed("How would you kindly say that you didn't like a dish?", "料理が好みではなかったと、どのように優しく伝えますか？", ("Which words would soften it?", "When should you be more direct?"), ("How can you be honest without judging the cooking?", "What useful detail could you add?")),
        reviewed("Why do some popular foods divide opinion?", "人気があっても好き嫌いが分かれる食べ物があるのはなぜですか？", ("Is taste, texture, or expectation usually the reason?", "Which food is a good example?"), ("Is taste, texture, or expectation usually the reason?", "Which food is a good example?")),
        reviewed("Which matters more at dinner: honesty or protecting the host's feelings?", "食事の場では、正直さとホストの気持ちを守ることのどちらが大切ですか？", ("When should honesty win?", "What would you want a guest to tell you?"), ("What harm can polite dishonesty cause?", "When does being polite become dishonest?")),
    ],
}


OPENINGS = {
    10: reviewed("What's something new you might enjoy trying?", "新しく試してみたいと思うことは何ですか？", ("What makes it look enjoyable?", "Would you try it alone or with someone?"), ("What first caught your interest?", "What would make you want to try it?")),
    12: reviewed("Which feels better: praise for your effort or praise for the result?", "努力を褒められることと、結果を褒められることでは、どちらがうれしいですか？", ("Why does that kind feel better?", "When would you prefer the other kind?"), ("What does that kind of praise help you notice?", "When can the other kind matter more?")),
    14: reviewed("What's one thing you'd like to finish this year?", "今年中に終わらせたいことを一つ挙げるとしたら何ですか？", ("Why does it matter to you?", "What could make it difficult?"), ("What would completing it change?", "What might you need to put aside?")),
    17: reviewed("On a difficult day, what small thing feels like a win?", "大変な日に、どんな小さなことができると成功したと感じますか？", ("Why can that be difficult?", "How would it change the rest of the day?"), ("What effort would another person probably miss?", "What should count as enough on a hard day?")),
    21: reviewed("What kind of film is easiest to watch again?", "どんな映画なら、もう一度見やすいですか？", ("What makes that kind easy to rewatch?", "Would you choose comedy, action, or something else?"), ("What makes that kind easy to rewatch?", "Would you choose comedy, action, or something else?")),
    22: reviewed("What's one thing in English you enjoy—music, a show, a game, or something else?", "音楽、番組、ゲームなど、英語で楽しんでいるものを一つ挙げるとしたら何ですか？", ("What makes it fun for you?", "How much of the English do you understand?"), ("What keeps you coming back to it?", "What can you enjoy even when some English is unclear?")),
    24: reviewed("What kind of song is a safe first choice at karaoke?", "カラオケの最初の一曲には、どんな曲が無難ですか？", ("What makes that kind reliable?", "Would you choose a slow song or an upbeat one?"), ("What makes that kind reliable?", "Would you choose a slow song or an upbeat one?")),
    27: reviewed("Would you tell everyone about a great small restaurant, or keep it quiet?", "すてきな小さなレストランを見つけたら、みんなに教えますか、それとも秘密にしますか？", ("Why would you make that choice?", "Who would you tell first?"), ("What would you want to protect about the place?", "When would sharing it help the restaurant?")),
    28: reviewed("Who would you enjoy choosing a book for?", "誰のためなら、楽しく本を選べそうですか？", ("What kind of book might suit them?", "Is a book easier to choose for a close friend or a coworker?"), ("What do you know about their taste?", "Is a book easier to choose for a close friend or a coworker?")),
    29: reviewed("What's a hobby that is more interesting than it looks?", "見た目より面白い趣味は何ですか？", ("Why might it look boring at first?", "Which looks least interesting from outside: gardening, collecting, or puzzles?"), ("Which hidden skill makes it interesting?", "Which looks least interesting from outside: gardening, collecting, or puzzles?")),
    30: reviewed("What kind of object is hardest to throw away?", "どんな物がいちばん捨てにくいですか？", ("What memory or use gives that kind of object value?", "Would a photo, letter, or useful old tool be hardest?"), ("What memory or use gives that kind of object value?", "Would a photo, letter, or useful old tool be hardest?")),
}


EARLY_REWRITES = {
    2: [
        reviewed("What do people often get wrong about Japan?", "人は日本について、どんなことをよく誤解していますか？", ("Where does that idea come from?", "What do movies get most wrong: work, school, or daily life?"), ("Why does the idea sound believable?", "What do movies get most wrong: work, school, or daily life?")),
        reviewed("Which image of Japan seems partly true but too simple?", "日本について、一部は本当でも単純すぎるイメージは何ですか？", ("Which part is true?", "Which gives a less accurate picture: movies or social media?"), ("Which part of the image is accurate?", "Which gives a less accurate picture: movies or social media?")),
        reviewed("What's one thing about daily life in Japan that movies often miss?", "日本の日常生活で、映画が見落としがちなことは何ですか？", ("Why is it rarely shown?", "Do movies show work, school, or home life least accurately?"), ("Which ordinary detail would correct the picture?", "Do movies show work, school, or home life least accurately?")),
        reviewed("Which part of Japan is most different from its image abroad?", "日本のどんなところが、海外でのイメージと最も違いますか？", ("What image do people have?", "Where can a visitor see ordinary life: a neighborhood, a station, or a school?"), ("Which experience would challenge the image fastest?", "Where can a visitor see ordinary life most clearly?")),
        reviewed("What 'good' idea about Japanese people can still be unfair?", "日本人について、「よい」イメージに見えても、不公平になりうる考えは何ですか？", ("Why can it create pressure?", "Can praise put pressure on a whole group?"), ("What does it expect people to be like?", "Can praise put pressure on a whole group?")),
        reviewed("What simple idea about another country do you question?", "ほかの国について、単純すぎると思うイメージは何ですか？", ("Why are you unsure about it?", "Do you trust movies or local people more?"), ("Where did you hear the idea?", "Do you trust movies or local people more?")),
        reviewed("What can make someone change their mind about a country?", "国についての考えを変えるきっかけは何ですか？", ("Can one personal story help?", "Would you trust a traveler or someone who lives there?"), ("Which experience is hardest to ignore?", "Would you trust a traveler or someone who lives there?")),
        reviewed("What's a better question visitors can ask about life in Japan?", "日本での生活について、旅行者はどんな質問をするとよいですか？", ("Who should they ask?", "Would you ask about food, work, or family life first?"), ("How might answers differ across Japan?", "Would you ask about food, work, or family life first?")),
    ],
    3: [
        reviewed("What Japanese food would you most want me to try?", "私にいちばん食べてほしい日本の料理は何ですか？", ("Why did it come to mind first?", "Would you start a visitor with ramen, curry, or something else?"), ("What makes the dish memorable?", "Would you start a visitor with ramen, curry, or something else?")),
        reviewed("Which Japanese food might look difficult but taste easy?", "難しそうに見えても、食べると親しみやすい日本料理は何ですか？", ("What makes it look difficult?", "Which is harder for a visitor: a new taste or a new texture?"), ("What taste might surprise them?", "Which is harder for a visitor: a new taste or a new texture?")),
        reviewed("What Japanese dish would you recommend to someone who dislikes raw fish?", "生魚が苦手な人に、どんな日本料理をおすすめしますか？", ("Why is it a good alternative?", "Which feels safest for a visitor: noodles, grilled food, or rice dishes?"), ("What still makes it feel Japanese?", "Which feels safest for a visitor: noodles, grilled food, or rice dishes?")),
        reviewed("How would you describe the taste and texture of a favorite Japanese dish?", "好きな日本料理の味と食感を、どのように説明しますか？", ("Which ingredient stands out?", "Which is easier to describe: taste or texture?"), ("Which detail is hardest to explain?", "Which is easier to describe: taste or texture?")),
        reviewed("Where does Japanese food taste best?", "日本料理は、どこで食べるといちばんおいしいですか？", ("Does the season matter?", "Would you choose a home, a small restaurant, or a market?"), ("Does the season matter?", "Would you choose a home, a small restaurant, or a market?")),
        reviewed("Which Japanese food is best for sharing?", "みんなで分けて食べるのにいちばんよい日本料理は何ですか？", ("Who would you share it with?", "Which is easiest to share: hot pot, sushi, or snacks?"), ("How does sharing change the meal?", "Which is easiest to share: hot pot, sushi, or snacks?")),
        reviewed("What should a first-time visitor know before trying Japanese food?", "初めて日本料理を食べる人は、何を知っておくとよいですか？", ("Which mistake is common?", "Would you explain the taste, texture, or table manners first?"), ("What warning would actually help?", "Would you explain the taste, texture, or table manners first?")),
        reviewed("How much can a traditional dish change before it becomes something else?", "伝統料理は、どこまで変わると別の料理になりますか？", ("Which part must stay the same?", "What change would you welcome?"), ("Is the name, method, or taste most important?", "Who gets to decide what counts?")),
    ],
    4: [
        reviewed("Do you pick your bowl up when you eat?", "食べるとき、お椀を手に持ちますか？", ("What do you usually do with the bowl?", "Does the answer change with the kind of bowl?"), ("What makes that feel natural to you?", "How might the answer change in another country?")),
        reviewed("At someone else's table, what small rule is easiest to miss?", "ほかの人の食卓で、見落としやすい小さなルールは何ですか？", ("How could a guest notice it?", "What do you do when you don't know a table rule?"), ("Why do hosts rarely explain it?", "What do you do when you don't know a table rule?")),
        reviewed("What table habit is normal in your home but unusual elsewhere?", "自分の家では普通でも、ほかでは珍しい食卓の習慣は何ですか？", ("Who taught the habit?", "At someone else's home, do you follow their rules or yours?"), ("What does the habit mean at home?", "At someone else's home, do you follow their rules or yours?")),
        reviewed("Who should start eating first at a formal meal?", "改まった食事では、誰が最初に食べ始めるべきですか？", ("What happens if someone starts early?", "Is the rule changing?"), ("What does waiting communicate?", "When is the rule unnecessary?")),
        reviewed("What table behavior feels rude even when no harm is meant?", "悪気がなくても、食卓で失礼に感じる行動は何ですか？", ("Why does it bother people?", "Would you correct a visitor?"), ("What might people think the person meant?", "What could make the moment less awkward?")),
        reviewed("Which table custom from another country would you like to try?", "ほかの国の食卓の習慣で、試してみたいものは何ですか？", ("What looks enjoyable?", "Would you rather try a new table rule or a new food?"), ("How would it change the meal?", "Would you rather try a new table rule or a new food?")),
        reviewed("Who taught you a table rule you still follow?", "今も守っている食事のルールを、誰に教わりましたか？", ("Which rule mattered most to them?", "Do you follow more rules at home or in a restaurant?"), ("Why did that lesson stay with you?", "Do you follow more rules at home or in a restaurant?")),
        reviewed("Which old table manner should disappear?", "昔からの食事マナーで、なくなってもよいものは何ですか？", ("Why is it no longer useful?", "Are table manners becoming more relaxed?"), ("Why did the rule exist?", "Are table manners becoming more relaxed?")),
    ],
    5: [
        reviewed("If I visited Japan for one day, where would you take me besides the famous places?", "私が一日だけ日本を訪れたら、有名な場所以外のどこへ連れて行きますか？", ("What would we do there?", "Would you plan food, nature, or shopping first?"), ("What side of Japan would the place show?", "Would you plan food, nature, or shopping first?")),
        reviewed("What makes a local place better than a famous tourist spot?", "地元の場所が有名な観光地よりよいのは、どんなところですか？", ("What can a visitor notice there?", "What might be less convenient?"), ("Which ordinary detail makes it meaningful?", "When is the famous place still worth choosing?")),
        reviewed("Where would you take a visitor who likes quiet places?", "静かな場所が好きな旅行者を、どこへ連れて行きますか？", ("What could they do there?", "Would they enjoy a park, a café, or a temple most?"), ("What would make the place memorable?", "Would they enjoy a park, a café, or a temple most?")),
        reviewed("What place shows everyday life in your area?", "あなたの地域の日常生活が見える場所はどこですか？", ("What would a visitor see there?", "Where is daily life easiest to see: a station, a market, or a park?"), ("Which routine would be easiest to see?", "Where is daily life easiest to see: a station, a market, or a park?")),
        reviewed("When is the best time to see a familiar place?", "身近な場所を見るのにいちばんよい時間はいつですか？", ("What changes at that time?", "Do you prefer familiar places in the morning or at night?"), ("How do the people, sounds, or light change?", "Do you prefer familiar places in the morning or at night?")),
        reviewed("Which local place would you show a food lover?", "食べ物が好きな人に、地元のどこを案内しますか？", ("What should they try?", "Would a food lover prefer a market or a restaurant?"), ("What does the place show about local food?", "Would a food lover prefer a market or a restaurant?")),
        reviewed("What do guidebooks often fail to explain about local places?", "ガイドブックは、地元の場所について何を説明できていないことが多いですか？", ("Why is that hard to explain?", "Do guidebooks miss local routines or local stories more often?"), ("Why is that hard to explain?", "Do guidebooks miss local routines or local stories more often?")),
        reviewed("What kind of place would you want me to show you in my country?", "私の国では、どんな場所を案内してほしいですか？", ("What would you hope to experience?", "Would you rather see daily life or a famous place?"), ("Would you prefer daily life or a special place?", "Would you rather explore one area or move around?")),
    ],
    6: [
        reviewed("Which English word would you like to understand better?", "もっとよく理解したい英単語は何ですか？", ("Where have you seen or heard it?", "Do new words stick better from songs, shows, or conversations?"), ("Which use of the word confuses you?", "Do new words stick better from songs, shows, or conversations?")),
        reviewed("Which is harder to translate: a joke, a feeling, or a polite phrase?", "冗談、気持ち、丁寧な表現の中で、いちばん訳しにくいのはどれですか？", ("Why is that one difficult?", "Which is easier to translate: facts or feelings?"), ("Which part depends on the situation?", "Which is easier to translate: facts or feelings?")),
        reviewed("What's one English word that sounds strange in Japanese?", "日本語にすると不思議に聞こえる英単語は何ですか？", ("What is the usual translation?", "Do English words sound stranger in ads or everyday conversation?"), ("What changes in Japanese?", "Do English words sound stranger in ads or everyday conversation?")),
        reviewed("Which Japanese word needs a full English sentence to explain?", "英語では一文使わないと説明しにくい日本語は何ですか？", ("When do people use it?", "Which is harder to explain in English: a food name or a feeling?"), ("When does the word feel natural?", "Which is harder to explain in English: a food name or a feeling?")),
        reviewed("When does a dictionary translation sound wrong?", "辞書の訳が不自然に聞こえるのは、どんなときですか？", ("Can the word still be correct?", "What context changes it?"), ("Does tone or relationship matter more?", "How would you repair the translation?")),
        reviewed("Which word or phrase changes meaning most depending on who you're talking to?", "話す相手によって意味が大きく変わる言葉や表現は何ですか？", ("How does it change with a stranger?", "Do you speak differently to a friend and a boss?"), ("When does it sound natural?", "Do you speak differently to a friend and a boss?")),
        reviewed("What kind of translation mistake can make a serious scene funny?", "どんな翻訳ミスで、真面目な場面が面白くなってしまいますか？", ("What meaning was probably intended?", "Have subtitles ever made you laugh?"), ("Can a word-for-word translation cause it?", "Have subtitles ever made you laugh?")),
        reviewed("Which matters more in translation: exact meaning or the same feeling?", "翻訳では、正確な意味と同じ感覚のどちらが大切ですか？", ("When does your choice matter most?", "When would the other one win?"), ("What should a translator never lose?", "How could they keep both?")),
    ],
    8: [
        reviewed("What do you actually do on New Year's Day?", "元日は実際に何をしますか？", ("Which part comes to mind first?", "Would you rather rest at home or go out on New Year's Day?"), ("Which part feels most different from a normal day?", "Would you rather rest at home or go out on New Year's Day?")),
        reviewed("Which part of New Year's Day do you look forward to most?", "元日のどの時間をいちばん楽しみにしていますか？", ("What makes it special?", "Would the day feel incomplete without it?"), ("Which feeling or person makes it important?", "Has that favorite part changed over time?")),
        reviewed("What kind of food would suit New Year's Day?", "元日にはどんな食べ物が合うと思いますか？", ("Would you eat it on another day?", "Would you choose a warm meal or something sweet?"), ("Would you eat it on another day?", "Would you choose a warm meal or something sweet?")),
        reviewed("What's the first thing many people do on New Year's morning?", "元日の朝、多くの人が最初にすることは何ですか？", ("Why do they do it?", "What do you do first on New Year's morning?"), ("What does the action mean to people?", "What do you do first on New Year's morning?")),
        reviewed("Which New Year's tradition is becoming less common?", "だんだん行われなくなっている新年の習慣は何ですか？", ("Why is it fading?", "Which New Year's tradition do young people still enjoy?"), ("What changed in daily life?", "Which New Year's tradition do young people still enjoy?")),
        reviewed("Would you rather spend New Year's Day at home or away?", "元日は家で過ごしたいですか、それとも出かけたいですか？", ("What makes that choice appealing?", "Who would you spend it with?"), ("What would the ideal day look like?", "What could make you choose the other option?")),
        reviewed("Which New Year's custom takes too much time?", "時間がかかりすぎる新年の習慣は何ですか？", ("Why do people keep doing it?", "Which takes more time: cooking, visiting family, or traveling?"), ("Which part should remain?", "Which takes more time: cooking, visiting family, or traveling?")),
        reviewed("What would you most like to ask someone from another country about New Year's Day?", "ほかの国の人に、その国の元日について何をいちばん聞きたいですか？", ("Why does that question interest you?", "What would you compare with Japan?"), ("Which answer might surprise you?", "What would you tell them about Japan in return?")),
    ],
}


HEADINGS = {
    11: {1: ("How many episodes?", "何話まで見る？"), 2: ("A slow story", "ゆっくり進む物語"), 3: ("Friend or app?", "友人かアプリか"), 4: ("Stopping halfway", "途中でやめる理由"), 5: ("One more episode", "もう一話見る？"), 6: ("A good ending", "よい結末"), 7: ("Alone or together?", "一人か誰かと？")},
    12: {0: ("Effort or result?", "努力か結果か"), 1: ("Awkward praise", "気まずい褒め言葉"), 7: ("More everyday praise", "もっと伝えたい褒め言葉")},
    15: {1: ("Hard to resist", "我慢しにくい買い物"), 2: ("Where the money goes", "何にお金を使う？"), 6: ("A changing budget", "変わる予算")},
    16: {0: ("Something new", "試してみたいこと"), 4: ("First-time stories", "初めての体験談")},
    17: {1: ("Unseen effort", "見えない努力"), 4: ("Celebrate a win", "小さな成功を祝う"), 5: ("Private or shared?", "話す？自分だけにする？")},
    19: {2: ("Starting or finishing?", "始める？終わらせる？"), 5: ("Starting right away", "すぐ始めるきっかけ"), 7: ("Restarting", "再開するコツ")},
    20: {4: ("Ready for an emergency", "もしものための持ち物")},
    21: {2: ("Old favorite or new film?", "お気に入りか新しい映画か")},
    22: {2: ("What makes a line stick?", "覚えやすさ"), 4: ("Subtitles", "字幕"), 5: ("Look it up?", "調べる？")},
    24: {2: ("Easier than it sounds", "聞くより歌いやすい曲"), 3: ("Learning a song", "曲の覚え方")},
    26: {1: ("Sweet, salty, fruit, meat", "甘い・塩味・果物・肉"), 3: ("A surprising combination", "意外な組み合わせ"), 7: ("One strange bite", "変わった一口")},
    28: {1: ("The safest gift", "いちばん無難な贈り物"), 2: ("Know the reader", "読む人を知る"), 4: ("An unread book", "読んでいない本"), 5: ("Recommend or give?", "おすすめか贈り物か"), 6: ("A note inside", "本に添える言葉")},
    29: {1: ("Hidden skill", "見えない技術")},
    30: {1: ("Value from a story", "物語が生む価値"), 2: ("Useful or sentimental?", "実用品か思い出の品か"), 3: ("A gift worth keeping", "長く持ちたい贈り物")},
    31: {3: ("What changed your style?", "服装を変えたもの")},
    32: {1: ("Old versus new", "古い物と新しい物"), 3: ("Better with age", "使うほど美しくなる物"), 4: ("Built to last", "長く使える理由"), 5: ("Keep or let go?", "残す？手放す？"), 7: ("Still useful in ten years", "十年後も使う物")},
    33: {3: ("The hardest place to refuse", "断りにくい場所")},
}


EARLY_HEADINGS = {
    2: {2: ("Everyday life", "映画にない日常"), 3: ("Image and reality", "イメージと現実"), 4: ("Positive but unfair", "よくても不公平なイメージ")},
    5: {1: ("Local or famous?", "地元か有名な場所か"), 3: ("Everyday life", "日常が見える場所"), 4: ("The best time", "いちばんよい時間"), 5: ("For a food lover", "食べ物が好きな人へ")},
    6: {4: ("Dictionary trouble", "辞書の訳の問題"), 6: ("A funny mistake", "笑ってしまう翻訳ミス")},
    8: {2: ("New Year's food", "元日の食べ物"), 3: ("The first thing", "最初にすること"), 4: ("A fading tradition", "減っている習慣"), 5: ("Home or away?", "家か外か")},
}


def apply_to(topics: dict[int, dict[str, object]]) -> None:
    """Apply reviewed prompts 2-8 while preserving TOC-owned prompt 1."""
    for topic_no, replacements in REWRITES.items():
        if topic_no not in topics:
            continue
        prompts = topics[topic_no]["prompts"]
        if len(prompts) != 8 or len(replacements) != 7:
            raise ValueError(f"FT{topic_no} prompt inventory changed")
        for prompt_item, replacement in zip(prompts[1:], replacements, strict=True):
            prompt_item.update(replacement)
    for topic_no, replacement in OPENINGS.items():
        if topic_no in topics:
            topics[topic_no]["prompts"][0].update(replacement)
    for topic_no, headings in HEADINGS.items():
        if topic_no not in topics:
            continue
        for prompt_index, (title, title_ja) in headings.items():
            topics[topic_no]["prompts"][prompt_index]["title"] = title
            topics[topic_no]["prompts"][prompt_index]["title_ja"] = title_ja


def apply_early(topics: dict[int, dict[str, object]]) -> None:
    """Apply reviewed tuple-shaped prompts to the narrow FT2-8 generator."""
    for topic_no, replacements in EARLY_REWRITES.items():
        if topic_no not in topics:
            continue
        topic = topics[topic_no]
        opening, warm2, *questions = replacements
        topic["opening"] = (opening["accessible"], opening["ja"])
        topic["opening_full"] = (opening["full"], opening["ja"])
        topic["opening_followups"] = opening["accessible_followups"]
        topic["opening_followups_full"] = opening["full_followups"]
        warm_title, warm_title_ja = topic["warm2"][:2]
        topic["warm2"] = (warm_title, warm_title_ja, warm2["accessible"], warm2["ja"], warm2["accessible_followups"])
        topic["warm2_full"] = (warm_title, warm_title_ja, warm2["full"], warm2["ja"], warm2["full_followups"])
        accessible_questions = []
        full_questions = []
        for old, replacement in zip(topic["questions"], questions, strict=True):
            title, title_ja = old[:2]
            accessible_questions.append((title, title_ja, replacement["accessible"], replacement["ja"], replacement["accessible_followups"]))
            full_questions.append((title, title_ja, replacement["full"], replacement["ja"], replacement["full_followups"]))
        topic["questions"] = accessible_questions
        topic["questions_full"] = full_questions
        for prompt_index, (title, title_ja) in EARLY_HEADINGS.get(topic_no, {}).items():
            if prompt_index == 1:
                topic["warm2"] = (title, title_ja, *topic["warm2"][2:])
                topic["warm2_full"] = (title, title_ja, *topic["warm2_full"][2:])
            elif prompt_index >= 2:
                question_index = prompt_index - 2
                topic["questions"][question_index] = (title, title_ja, *topic["questions"][question_index][2:])
                topic["questions_full"][question_index] = (title, title_ja, *topic["questions_full"][question_index][2:])

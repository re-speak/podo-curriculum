#!/usr/bin/env python3
"""Generate CTX37-48, the projects/deadlines and meetings/decisions courses."""

from __future__ import annotations

import argparse
import contextlib
import pathlib
import re
import sys
from html.parser import HTMLParser

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import generate_contextual_complex_workplace_batch as renderer
import generate_core_course_batch as core
import new_lesson
import vocabulary


ROOT = new_lesson.REPO
TRACK = new_lesson.ENGLISH / "tracks/2-contextual-english"
COURSES = {
    range(37, 43): ("ctx-business-projects-deadlines", "B1", "BUSINESS ENGLISH", "Colleague", "同僚"),
    range(43, 49): ("ctx-business-meetings-decisions", "B2", "BUSINESS ENGLISH", "Colleague", "同僚"),
}


def rows(*items):
    return items


def pattern(*, bridge, meaning, rows_, rule, write, omit_rule=False, omit_reorder=False):
    return renderer.pattern(
        bridge=bridge,
        meaning=meaning,
        rows_=rows_,
        rule=rule,
        write=write,
        omit_rule=omit_rule,
        omit_reorder=omit_reorder,
    )


def live(prompt, prompt_ja, scaffold, scaffold_ja, ask, ask_ja):
    return (prompt, prompt_ja, scaffold, scaffold_ja, ask, ask_ja)


LESSONS = {
    37: dict(
        slug="confirm-priorities-when-everything-seems-urgent", title="Confirm priorities when everything seems urgent",
        ko="모든 일이 급할 때 우선순위 확인하기", ja="すべて急ぎに見えるとき優先順位を確認する",
        role="Manager", scene="Three tasks with the same deadline", scene_ja="同じ締め切りの仕事が三つある場面",
        situation="同じ締め切りの仕事が三つあります。全部できるふりをせず、可能な範囲を伝えて、最初にする仕事を確認します。",
        goal=("Set a realistic limit and get a clear first priority.", "現実的な限界を伝え、最初の優先事項を明確にしましょう。"),
        expressions=(("top priority", "最優先事項"), ("move the deadline", "締め切りを動かす")),
        p1=pattern(
            bridge="まず、できる範囲と難しい範囲を対比して伝えます。",
            meaning=("Use this to commit to a realistic amount without promising everything.", "全部を約束せず、現実的にできる量を示す表現です。"),
            rows_=rows(
                ("{t}I can{/t} finish two by Friday, {t}but probably not{/t} all three.", "金曜日までに二つは{t}終えられますが{/t}、三つ全部は{t}おそらく無理です{/t}。", "I can finish|two by Friday,|but probably not|all three."),
                ("{t}I can{/t} review the report today, {t}but probably not{/t} the slides.", "今日は報告書を{t}確認できますが{/t}、資料までは{t}おそらく無理です{/t}。", "I can review|the report today,|but probably not|the slides."),
                ("{t}I can{/t} call two clients, {t}but probably not{/t} all five.", "顧客二社には{t}電話できますが{/t}、五社全部は{t}おそらく無理です{/t}。", "I can call|two clients,|but probably not|all five."),
                ("{t}I can{/t} fix the urgent issue, {t}but probably not{/t} both issues.", "緊急の問題は{t}直せますが{/t}、両方は{t}おそらく無理です{/t}。", "I can fix|the urgent issue,|but probably not|both issues."),
            ),
            rule=("Put the limit after “but”", "限界は but のあと", "State what you can do first, then the part you probably cannot finish.", "できることを先に、難しい部分をあとに示します。", "I can + realistic amount, but probably not + full amount", "Set a realistic limit", "現実的な限界を示す", ("finish two · not all three", "review the report · not the slides")),
            write=("What can you finish, and what probably has to wait?", "何を終えられ、何を待たせる必要がありますか？"),
        ),
        p2=pattern(
            bridge="次に、迷わず着手できるよう、最初の仕事を一つ確認します。",
            meaning=("Use this to ask which item should receive your attention first.", "どの項目を最初に優先すべきか確認する表現です。"),
            rows_=rows(
                ("{t}Which{/t} task {t}should I do first{/t}?", "{t}どの{/t}仕事を{t}最初にすべきですか{/t}？", "Which task|should I do|first?"),
                ("{t}Which{/t} file {t}should I review first{/t}?", "{t}どの{/t}ファイルを{t}最初に確認すべきですか{/t}？", "Which file|should I review|first?"),
                ("{t}Which{/t} client {t}should I call first{/t}?", "{t}どの{/t}顧客に{t}最初に電話すべきですか{/t}？", "Which client|should I call|first?"),
                ("{t}Which{/t} problem {t}should I fix first{/t}?", "{t}どの{/t}問題を{t}最初に直すべきですか{/t}？", "Which problem|should I fix|first?"),
            ),
            rule=("Put the action before “first”", "行動は first の前", "Name the item after “which” and the action before “first.”", "which のあとに項目、first の前に行動を置きます。", "Which + item + should I + action + first?", "Ask for one priority", "一つの優先事項を確認", ("Which task · should I do · first?", "Which client · should I call · first?")),
            write=("Which task would you ask your manager about first?", "どの仕事を最初にすべきか、上司にどう確認しますか？"),
        ),
        scene_turns=(("other", "I need the client report, the audit notes, and the budget update by Friday.", "金曜日までに顧客報告書、監査メモ、予算更新が必要です。"), ("target", 1, 0), ("other", "Understood. What do you need from me?", "分かりました。私に何を決めてほしいですか？"), ("target", 2, 0), ("other", "Do the client report first. Move the audit to Monday.", "顧客報告書を先にしてください。監査は月曜日に動かしましょう。"), ("me", "Understood. I will update the project plan now.", "分かりました。今、プロジェクト計画を更新します。")),
        receptive=(("all three", "The learner probably cannot finish every task", "学習者は三つすべてを終えられそうにない", "The learner has already finished everything", "学習者はすでに全部終えている"), ("What do you need from me?", "The manager invites the learner to ask for a decision", "上司は学習者に判断事項を尋ねるよう促している", "The manager cancels all three tasks", "上司は三つすべてを中止する"), ("first", "The learner asks for the top priority", "学習者は最優先事項を確認している", "The learner asks for a new manager", "学習者は新しい上司を求めている"), ("Move the audit to Monday.", "The audit gets a later deadline", "監査の締め切りが後ろに動く", "The audit remains due Friday", "監査は金曜日のままである")),
        live=live("Use a real or imaginary set of urgent tasks. Tell me your limit, then ask which task comes first.", "実際または架空の急ぎの仕事を使い、できる範囲を伝えてから最優先を確認してください。", "Real or imaginary: I can ___, but probably not ___. Which ___ should I ___ first?", "実際の仕事でも架空でも、二つの表現を一度ずつ使いましょう。", "If three tasks were due together, which one would you do first?", "三つの仕事の締め切りが同じなら、先生はどれを最初にしますか？"),
        tip=("Choose how certain the limit is", "難しさの確度を選ぶ", "“Probably not” leaves a small possibility; “definitely not” rules it out.", "probably not は少し可能性を残し、definitely not は不可能だとはっきり示します。", ("Some uncertainty", "少し可能性がある", "I can finish two, but probably not all three.", "二つは終えられますが、三つ全部はおそらく無理です。"), ("Certain limit", "確実に無理", "I can finish two, but definitely not all three.", "二つは終えられますが、三つ全部は絶対に無理です。")),
        transfer_title="Prioritising launch work", transfer_ja="公開準備の優先順位を決める", transfer_role="Team Lead",
        transfer_turns=(("other", "The client report, pricing file, and presentation slides all need reviews today.", "顧客報告書、料金ファイル、発表資料はすべて今日中に確認が必要です。"), ("target", 1, 1), ("other", "Then leave the slides until tomorrow morning.", "では、資料は明日の朝まで待たせましょう。"), ("target", 2, 1), ("other", "Review the pricing file first; the designer needs it today.", "料金ファイルを先に確認してください。デザイナーが今日必要です。"), ("me", "All right. I will send that review by noon.", "分かりました。正午までに確認結果を送ります。")),
        vocab=("top priority|最優先事項; move the deadline|締め切りを動かす", "client|顧客|CORE-54; definitely|確実に|CTX-26", "probably not|おそらく無理; urgent|急ぎの", "audit notes|監査メモ; pricing file|料金ファイル"),
    ),
    38: dict(
        slug="clarify-who-owns-an-action", title="Clarify who owns an action", ko="업무 담당자 확인하기", ja="作業の担当者を確認する",
        role="Project Lead", scene="A supplier task with no clear owner", scene_ja="仕入先対応の担当が曖昧な場面",
        situation="会議の終わりに、仕入先への連絡担当が曖昧です。責める口調を避けて確認し、必要なら自分が引き受けます。",
        goal=("Identify the action owner and keep the task from being missed.", "担当者を確認し、仕事が抜け落ちないようにしましょう。"),
        expressions=(("action owner", "作業の担当者"), ("copy me in", "私も宛先に入れる")),
        p1=pattern(bridge="まず、確認のためだと示してから担当者を尋ねます。", meaning=("Use this bounded question to clarify ownership without sounding accusatory.", "責める印象を避けて担当を確認する定型質問です。"), rows_=rows(
            ("{t}Just to clarify, who's contacting{/t} the supplier?", "{t}確認ですが、仕入先に連絡するのは誰ですか{/t}？", "Just to clarify,|who's contacting|the supplier?"),
            ("{t}Just to clarify, who's calling{/t} the client?", "{t}確認ですが、顧客に電話するのは誰ですか{/t}？", "Just to clarify,|who's calling|the client?"),
            ("{t}Just to clarify, who's sending{/t} the invoice?", "{t}確認ですが、請求書を送るのは誰ですか{/t}？", "Just to clarify,|who's sending|the invoice?"),
            ("{t}Just to clarify, who's booking{/t} the room?", "{t}確認ですが、会議室を予約するのは誰ですか{/t}？", "Just to clarify,|who's booking|the room?")), rule=("Keep the ownership question intact", "担当確認の質問は一まとまりで", "This is a bounded workplace question; retrieve it as one polite move.", "職場で使う定型質問なので、一つの丁寧なまとまりとして使います。", "Just to clarify, who's + action?", "Clarify ownership", "担当を確認", ("who's contacting · the supplier", "who's sending · the invoice")), write=("Which task has no clear owner?", "どの仕事の担当者が曖昧ですか？"), omit_rule=True, omit_reorder=True),
        p2=pattern(bridge="担当者がいなければ、自分が引き受ける提案をします。", meaning=("Use this bounded offer when you can take the task if it is still unassigned.", "まだ担当者がいない場合に、自分が引き受けられると伝える定型表現です。"), rows_=rows(
            ("{t}I'm happy to contact them if no one else is doing it{/t}.", "{t}ほかに担当者がいなければ、私が連絡しても構いません{/t}。", "I'm happy to contact them|if no one else|is doing it."),
            ("{t}I'm happy to call them if no one else is doing it{/t}.", "{t}ほかに担当者がいなければ、私が電話しても構いません{/t}。", "I'm happy to call them|if no one else|is doing it."),
            ("{t}I'm happy to send it if no one else is doing it{/t}.", "{t}ほかに担当者がいなければ、私が送っても構いません{/t}。", "I'm happy to send it|if no one else|is doing it."),
            ("{t}I'm happy to book it if no one else is doing it{/t}.", "{t}ほかに担当者がいなければ、私が予約しても構いません{/t}。", "I'm happy to book it|if no one else|is doing it.")), rule=("Keep the conditional offer intact", "条件つきの申し出は一まとまりで", "Offer help only if the action is still unassigned.", "まだ担当者がいない場合にだけ、引き受けると申し出ます。", "I'm happy to + action + if no one else is doing it", "Offer to own the action", "担当を申し出る", ("contact them · if no one else", "send it · if no one else")), write=("Which unassigned task could you take?", "担当者がいないどの仕事を引き受けられますか？"), omit_rule=True, omit_reorder=True),
        scene_turns=(("other", "Your team thinks ours is contacting the supplier, but our team thinks yours is.", "あなたのチームは私たちが仕入先に連絡すると思い、私たちのチームはあなたたちが連絡すると思っています。"), ("target", 1, 0), ("other", "I thought your team was doing it.", "あなたのチームがすると思っていました。"), ("target", 2, 0), ("other", "Thanks. Please copy me in.", "ありがとうございます。私も宛先に入れてください。"), ("me", "I will send the update after this meeting.", "この会議のあとで進捗を送ります。")),
        receptive=(("Your team thinks ours", "The two teams have opposing assumptions about ownership", "二つのチームは担当について反対の思い込みをしている", "Both teams named the same clear owner", "両チームは同じ担当者を明確に決めた"), ("I thought your team was doing it.", "The project lead assumed the learner's team owned it", "リーダーは学習者のチーム担当だと思っていた", "The project lead confirms another named owner", "リーダーは別の担当者を確定した"), ("if no one else is doing it", "The learner's offer depends on the task being unassigned", "申し出は担当者がいない場合に限られる", "The learner refuses the task in every case", "学習者はどの場合も断る"), ("copy me in", "The lead wants to receive the message too", "リーダーもそのメールを受け取りたい", "The lead wants the message deleted", "リーダーはメールを削除してほしい")),
        live=live("Use a real or imaginary unassigned contact task. Clarify the owner, then offer to take it if needed.", "実際または架空の連絡担当が未定の仕事で、担当者を確認し、必要なら引き受けてください。", "Real or imaginary: Just to clarify, who's contacting ___? I'm happy to contact them if no one else is doing it.", "実際の例でも架空でも、連絡担当の確認と条件つきの申し出を使いましょう。", "If a contact task had no owner, which one would you volunteer for?", "連絡担当のいない仕事なら、先生はどれを引き受けますか？"),
        tip=("Choose one message or ongoing updates", "一通か継続的な共有か", "Use “copy me in” for one email; use “keep me posted” for continuing updates.", "一通のメールを共有するなら copy me in、今後も進捗を知らせてもらうなら keep me posted を使います。", ("One email", "一通のメール", "Please copy me in on the email.", "そのメールでは私も宛先に入れてください。"), ("Ongoing updates", "継続的な共有", "Please keep me posted.", "今後も進捗を知らせてください。")),
        transfer_title="Assigning a customer follow-up", transfer_ja="顧客への追加連絡を担当する", transfer_role="Account Lead",
        transfer_turns=(("other", "The client asked for the revised price, but I don't see an owner.", "顧客が修正価格を求めましたが、担当者が見当たりません。"), ("target", 1, 1), ("other", "No one has taken that action yet.", "その仕事はまだ誰も担当していません。"), ("target", 2, 1), ("other", "Great. Call them before four and copy me in on the note.", "助かります。4時までに電話し、メモを私にも共有してください。"), ("me", "I will confirm the price and send you the note.", "価格を確認して、メモを送ります。")),
        vocab=("action owner|作業の担当者; copy me in|私も宛先に入れる; unassigned|担当未定; keep me posted|進捗を知らせる", "client|顧客|CORE-54", "just to clarify|確認ですが; I'm happy to|喜んで〜する", "supplier update|仕入先への進捗; revised price|修正価格"),
    ),
    39: dict(
        slug="raise-a-project-risk-early", title="Raise a project risk early", ko="프로젝트 위험을 일찍 알리기", ja="プロジェクトのリスクを早めに伝える",
        role="Project Sponsor", scene="A status update before a supplier delay", scene_ja="仕入先の遅れが確定する前の進捗報告",
        situation="今は予定どおりですが、仕入先が遅れる可能性があります。問題が起きるまで待たず、現状と主なリスクを分けて伝えます。",
        goal=("Report the current status and surface the main risk before it becomes a problem.", "現在の状況と主なリスクを分け、問題になる前に共有しましょう。"),
        expressions=(("early warning", "早期警告"), ("fallback plan", "代替案")),
        p1=pattern(bridge="まず、現時点では予定どおりだと明確にします。", meaning=("Use this bounded status line to separate today's position from a future risk.", "現在の進捗と将来のリスクを分ける定型の状況報告です。"), rows_=rows(
            ("{t}We're on track at the moment{/t}.", "{t}今のところ予定どおりです{/t}。", "We're on track|at the moment."),
            ("{t}We're on track for this week{/t}.", "{t}今週分は予定どおりです{/t}。", "We're on track|for this week."),
            ("{t}We're on track so far{/t}.", "{t}ここまでは予定どおりです{/t}。", "We're on track|so far."),
            ("{t}We're on track for Friday{/t}.", "{t}金曜日に向けて予定どおりです{/t}。", "We're on track|for Friday.")), rule=("Keep the current status intact", "現在の状況は一まとまりで", "This is a bounded status line; say it before introducing a separate risk.", "定型の状況報告として使い、そのあとで別にリスクを示します。", "We're on track + current time", "State the current position", "現在の状況を示す", ("on track · at the moment", "on track · so far")), write=("What part of a project is currently on track?", "現在予定どおりの部分は何ですか？"), omit_rule=True, omit_reorder=True),
        p2=pattern(bridge="次に、最も大きい不確実性を一つだけ具体的に示します。", meaning=("Use this bounded warning to name the single issue most likely to affect delivery.", "納期に影響しそうな最大の問題を一つ示す定型表現です。"), rows_=rows(
            ("{t}The main risk is that{/t} the supplier may be late.", "{t}主なリスクは{/t}、仕入先が遅れる可能性があることです。", "The main risk is that|the supplier|may be late."),
            ("{t}The main risk is that{/t} the data may be incomplete.", "{t}主なリスクは{/t}、データが不完全な可能性があることです。", "The main risk is that|the data|may be incomplete."),
            ("{t}The main risk is that{/t} approval may take longer.", "{t}主なリスクは{/t}、承認に時間がかかる可能性があることです。", "The main risk is that|approval|may take longer."),
            ("{t}The main risk is that{/t} one test may fail.", "{t}主なリスクは{/t}、一つの試験が失敗する可能性があることです。", "The main risk is that|one test|may fail.")), rule=("Keep the risk frame intact", "リスク提示は一まとまりで", "Name one concrete uncertainty after this bounded warning frame.", "この定型表現のあとに、具体的な不確実性を一つ示します。", "The main risk is that + uncertainty", "Raise one risk", "リスクを一つ示す", ("supplier may be late", "approval may take longer")), write=("What is the main risk in a current or imaginary project?", "実際または架空の案件で、主なリスクは何ですか？"), omit_rule=True, omit_reorder=True),
        scene_turns=(("other", "How is the delivery looking today?", "今日の納品状況はどうですか？"), ("target", 1, 0), ("other", "But you sound worried.", "でも、心配しているようですね。"), ("target", 2, 0), ("other", "Thanks for raising it now. What's the fallback?", "今知らせてくれて助かります。代替案は何ですか？"), ("me", "We can use the backup supplier if the date slips.", "日程が遅れたら、予備の仕入先を使えます。")),
        receptive=(("at the moment", "The project is on schedule now", "案件は現在予定どおりである", "The project has already failed", "案件はすでに失敗した"), ("But you sound worried.", "The sponsor hears a concern behind the status", "スポンサーは状況報告の裏に懸念を感じている", "The sponsor ends the meeting", "スポンサーは会議を終える"), ("may be late", "The delay is a risk, not a confirmed fact", "遅れは確定ではなく可能性である", "The supplier has definitely cancelled", "仕入先は確実に中止した"), ("What's the fallback?", "The sponsor asks for a backup plan", "スポンサーは代替案を尋ねている", "The sponsor asks for last month's invoice", "スポンサーは先月の請求書を尋ねている")),
        live=live("Use a real or imaginary project. State today's status, then raise one possible risk.", "実際または架空の案件で、現在の状況と起こり得るリスクを一つ伝えてください。", "Real or imaginary: We're on track ___. The main risk is that ___.", "実際の案件でも架空でも、現状とリスクの二つを使いましょう。", "On a real or imaginary project, what early warning would you raise?", "実際または架空の案件なら、先生はどんな早期警告を出しますか？"),
        tip=("Use “risk” before it happens", "起きる前なら risk", "A risk may become a problem later; an issue is already affecting the project now.", "risk は今後起こる可能性のある問題、issue はすでに案件へ影響している問題です。", ("Possible later", "今後の可能性", "The main risk is a supplier delay.", "主なリスクは仕入先の遅れです。"), ("Happening now", "すでに発生", "The main issue is missing data.", "現在の主な問題はデータ不足です。")),
        transfer_title="Flagging a data risk", transfer_ja="データのリスクを早めに伝える", transfer_role="Analytics Lead",
        transfer_turns=(("other", "Are we still on track with this week's analysis?", "今週の分析はまだ予定どおりですか？"), ("target", 1, 1), ("other", "What could change that?", "何がその状況を変える可能性がありますか？"), ("target", 2, 1), ("other", "Then check the missing records today and prepare a smaller dataset.", "では今日、不足データを確認し、小さいデータセットも準備してください。"), ("me", "I will report the result and fallback by four.", "4時までに結果と代替案を報告します。")),
        vocab=("early warning|早期警告; fallback plan|代替案; main risk|主なリスク", "on track|予定どおり|CTX-35", "may be|可能性がある; at the moment|今のところ; issue|問題", "backup supplier|予備の仕入先; missing records|不足データ"),
    ),
    40: dict(
        slug="negotiate-a-realistic-deadline", title="Negotiate a realistic deadline", ko="현실적인 마감 협의하기", ja="現実的な締め切りを交渉する",
        role="Manager", scene="A request for analysis sooner than planned", scene_ja="予定より早い分析を求められる場面",
        situation="明日出せる要約と、二日かかる完全な分析を分けて伝えます。条件を確認し、守れる日程に合意します。",
        goal=("Offer a useful interim result and agree on a deadline you can actually meet.", "役立つ中間成果を示し、実際に守れる締め切りに合意しましょう。"),
        expressions=(("full analysis", "完全な分析"), ("realistic timeline", "現実的な日程")),
        p1=pattern(bridge="まず、早く出せるものと時間が必要なものを対比します。", meaning=("Use this to offer an interim result while stating how long the full work needs.", "中間成果を提案し、完全な作業に必要な時間も示す表現です。"), rows_=rows(
            ("{t}I can{/t} send a summary tomorrow, but the full analysis {t}will take{/t} two days.", "明日、要約は{t}送れますが{/t}、完全な分析には二日{t}かかります{/t}。", "I can send|a summary tomorrow,|but the full analysis|will take two days."),
            ("{t}I can{/t} share the outline today, but the final report {t}will take{/t} three days.", "今日、概要は{t}共有できますが{/t}、最終報告書には三日{t}かかります{/t}。", "I can share|the outline today,|but the final report|will take three days."),
            ("{t}I can{/t} send the figures now, but the written review {t}will take{/t} a day.", "今、数値は{t}送れますが{/t}、書面での確認には一日{t}かかります{/t}。", "I can send|the figures now,|but the written review|will take a day."),
            ("{t}I can{/t} give you a draft Friday, but the final version {t}will take{/t} until Monday.", "金曜日に下書きは{t}渡せますが{/t}、最終版は月曜日まで{t}かかります{/t}。", "I can give you|a draft Friday,|but the final version|will take until Monday.")), rule=("Contrast the interim result with the full work", "中間成果と完全版を対比", "Offer the earlier result first; after “but,” state the full item and the time it needs.", "早い成果を先に提案し、but のあとで完全版と必要時間を示します。", "I can + interim result, but + full result + will take + time", "Offer a workable trade-off", "実行可能な代案を示す", ("summary tomorrow · analysis two days", "outline today · report three days")), write=("What could you provide early, and how long would the full work take?", "先に何を出せ、完全な作業にはどれくらいかかりますか？")),
        p2=pattern(bridge="次に、締め切りを守るために必要な条件を明確にします。", meaning=("Use this to confirm a date is achievable only when a visible condition is met.", "明確な条件が満たされる場合に、日程が実現可能だと伝える表現です。"), rows_=rows(
            ("{t}Thursday is realistic{/t} if the data arrives today.", "データが今日届けば、{t}木曜日が現実的です{/t}。", "Thursday is realistic|if the data|arrives today."),
            ("{t}Friday is realistic{/t} if the figures are final tomorrow.", "数値が明日確定すれば、{t}金曜日が現実的です{/t}。", "Friday is realistic|if the figures|are final tomorrow."),
            ("{t}Monday is realistic{/t} if the team approves the draft Friday.", "チームが金曜日に下書きを承認すれば、{t}月曜日が現実的です{/t}。", "Monday is realistic|if the team approves|the draft Friday."),
            ("{t}The end of June is realistic{/t} if the scope stays the same.", "範囲が変わらなければ、{t}6月末が現実的です{/t}。", "The end of June is realistic|if the scope|stays the same.")), rule=("Keep the achievable date tied to its condition", "実現可能な日程と条件を結ぶ", "This bounded frame prevents the date from sounding unconditional.", "定型表現として使い、その日程が無条件ではないことを明確にします。", "date + is realistic if + condition", "Agree conditionally", "条件つきで合意", ("Thursday · if data arrives", "Monday · if draft is approved")), write=("Which deadline is realistic, and what has to happen first?", "どの締め切りなら現実的で、その前に何が必要ですか？"), omit_rule=True, omit_reorder=True),
        scene_turns=(("other", "Could you send the complete analysis tomorrow?", "完全な分析を明日送れますか？"), ("target", 1, 0), ("other", "Could I have the full version by Thursday?", "完全版を木曜日までにもらえますか？"), ("target", 2, 0), ("other", "Agreed. I'll chase the data now.", "合意します。今、データを催促します。"), ("me", "Thanks. I will send tomorrow's summary by noon.", "ありがとうございます。明日の正午までに要約を送ります。")),
        receptive=(("summary tomorrow", "The learner offers an interim result", "学習者は中間成果を提案している", "The learner refuses to send anything", "学習者は何も送らない"), ("two days", "The complete analysis needs more time", "完全な分析にはさらに時間が必要", "The analysis is already complete", "分析はすでに完成している"), ("if the data arrives today", "Thursday depends on receiving data today", "木曜日の日程は今日のデータ到着が条件", "Thursday is guaranteed without data", "データがなくても木曜日は確実"), ("I'll chase the data now.", "The manager takes the action needed for the deadline", "上司は締め切りに必要な行動を取る", "The manager moves the deadline to next month", "上司は締め切りを来月に動かす")),
        live=live("Use a real or imaginary deadline request. Offer an interim result, then name a realistic date and condition.", "実際または架空の締め切り依頼で、中間成果と現実的な日程・条件を伝えてください。", "Real or imaginary: I can ___, but ___ will take ___. ___ is realistic if ___.", "実際の例でも架空でも、二つの表現を一度ずつ使いましょう。", "If someone needed a full report tomorrow, what interim result could you offer?", "完全な報告書を明日求められたら、先生はどんな中間成果を提案しますか？"),
        tip=("Use “realistic” for a date you can defend", "根拠のある日程には realistic", "A realistic date is achievable under the stated conditions; it is not just the date you prefer.", "realistic は示した条件で実現可能な日程で、単なる希望日ではありません。", ("Achievable", "実現可能", "Thursday is realistic if the data arrives.", "データが届けば木曜日が現実的です。"), ("Preference", "希望", "I'd prefer Thursday.", "木曜日が希望です。")),
        transfer_title="Agreeing on a launch review", transfer_ja="公開前レビューの日程に合意する", transfer_role="Product Lead",
        transfer_turns=(("other", "We need the final launch review this afternoon.", "今日の午後に最終公開レビューが必要です。"), ("target", 1, 1), ("other", "When can the complete report be ready?", "完全な報告書はいつ準備できますか？"), ("target", 2, 1), ("other", "I will get the final figures approved tomorrow morning.", "明日の朝、最終数値の承認を取ります。"), ("me", "Then I will deliver the report Friday afternoon.", "では、金曜日の午後に報告書を提出します。")),
        vocab=("full analysis|完全な分析; realistic timeline|現実的な日程; interim result|中間成果", "final version|最終版|CTX-34", "will take|かかる; full report|完全な報告書", "written review|書面での確認; final figures|最終数値"),
    ),
    41: dict(
        slug="deliver-bad-news-with-a-next-step", title="Deliver bad news with a next step", ko="다음 단계와 함께 나쁜 소식 전하기", ja="次の一手とともに悪い知らせを伝える",
        role="Director", scene="A launch that cannot happen on Monday", scene_ja="月曜日に公開できないことを伝える場面",
        situation="公開が間に合わない事実を早めに伝えます。悪い知らせだけで終わらせず、新しい日程と立て直し計画を示します。",
        goal=("State the delay plainly and pair it with a concrete recovery step.", "遅れを明確に伝え、具体的な立て直しの一手を添えましょう。"),
        expressions=(("here's where we are", "現状はこうです"), ("recovery plan", "立て直し計画")),
        p1=pattern(bridge="まず、悪い知らせだと示し、公開できない日を明確にします。", meaning=("Use this bounded line to give difficult schedule news directly but professionally.", "難しい日程の知らせを率直かつ丁寧に伝える定型表現です。"), rows_=rows(
            ("{t}I'm afraid we won't be ready for Monday's launch{/t}.", "{t}残念ですが、月曜日の公開には間に合いません{/t}。", "I'm afraid|we won't be ready|for Monday's launch."),
            ("{t}I'm afraid we won't be ready for Friday's review{/t}.", "{t}残念ですが、金曜日のレビューには間に合いません{/t}。", "I'm afraid|we won't be ready|for Friday's review."),
            ("{t}I'm afraid we won't be ready for tomorrow's demo{/t}.", "{t}残念ですが、明日のデモには間に合いません{/t}。", "I'm afraid|we won't be ready|for tomorrow's demo."),
            ("{t}I'm afraid we won't be ready for the client meeting{/t}.", "{t}残念ですが、顧客会議には間に合いません{/t}。", "I'm afraid|we won't be ready|for the client meeting.")), rule=("Keep the bad-news line intact", "悪い知らせは一まとまりで", "Use this bounded workplace line to name the missed event without hiding it.", "職場の定型表現として、間に合わない予定を曖昧にせず示します。", "I'm afraid we won't be ready for + event", "State the bad news", "悪い知らせを伝える", ("not ready · Monday's launch", "not ready · Friday's review")), write=("Which event might not be ready on time?", "どの予定に間に合わない可能性がありますか？"), omit_rule=True, omit_reorder=True),
        p2=pattern(bridge="次に、新しい日程と、立て直す準備があることを示します。", meaning=("Use this bounded move to give a revised date and signal that a recovery plan is ready.", "新しい日程を示し、立て直し計画も用意していると伝える定型表現です。"), rows_=rows(
            ("{t}We'll need to push it back by a week, and I have a recovery plan{/t}.", "{t}一週間延期する必要がありますが、立て直し計画があります{/t}。", "We'll need to push it back|by a week,|and I have a recovery plan."),
            ("{t}We'll need to push it back by two days, and I have a recovery plan{/t}.", "{t}二日延期する必要がありますが、立て直し計画があります{/t}。", "We'll need to push it back|by two days,|and I have a recovery plan."),
            ("{t}We'll need to push it back until Friday, and I have a recovery plan{/t}.", "{t}金曜日まで延期する必要がありますが、立て直し計画があります{/t}。", "We'll need to push it back|until Friday,|and I have a recovery plan."),
            ("{t}We'll need to push it back to next month, and I have a recovery plan{/t}.", "{t}来月まで延期する必要がありますが、立て直し計画があります{/t}。", "We'll need to push it back|to next month,|and I have a recovery plan.")), rule=("Keep the revised-date move intact", "新しい日程の提示は一まとまりで", "This bounded move pairs the delay with evidence that you are managing it.", "定型表現として、延期と立て直し対応をセットで示します。", "We'll need to push it back + time, and I have a recovery plan", "Give the next step", "次の一手を示す", ("back by a week · recovery plan", "back until Friday · recovery plan")), write=("How far would you move the event?", "予定をどれだけ動かしますか？"), omit_rule=True, omit_reorder=True),
        scene_turns=(("other", "Are we still set for Monday's launch?", "月曜日の公開予定に変更はありませんか？"), ("target", 1, 0), ("other", "How far behind are we?", "どれくらい遅れていますか？"), ("target", 2, 0), ("other", "All right. Talk me through the plan.", "分かりました。計画を説明してください。"), ("me", "Today we will fix the final test and publish a daily update.", "今日は最終テストを修正し、毎日進捗を共有します。")),
        receptive=(("won't be ready", "The Monday launch cannot proceed as planned", "月曜日の公開は予定どおり進められない", "The launch finished early", "公開は早く完了した"), ("How far behind are we?", "The director asks for the size of the delay", "責任者は遅れの長さを尋ねている", "The director asks who booked the room", "責任者は会議室の予約者を尋ねている"), ("push it back by a week", "The proposed new date is one week later", "提案された日程は一週間後", "The launch moves one week earlier", "公開は一週間早まる"), ("Talk me through the plan.", "The director wants the recovery steps explained", "責任者は立て直し手順の説明を求めている", "The director rejects every next step", "責任者はすべての次の行動を拒否する")),
        live=live("Give the bad news and new timing. Then name the recovery action, owner, and deadline.", "悪い知らせと新しい日程を伝え、立て直しの行動・担当者・期限を示してください。", "Real or imaginary: I'm afraid we won't be ready for ___. We'll need to push it back by ___, and I have a recovery plan: ___ will ___ by ___.", "立て直し計画には、行動・担当者・期限を具体的に入れましょう。", "If an important launch slipped, what would your first recovery step be?", "重要な公開が遅れたら、先生の最初の立て直し策は何ですか？"),
        tip=("Pair bad news with an owned next step", "悪い知らせには自分が担う次の一手を", "A recovery plan is useful only when you can explain the action, owner, and timing.", "立て直し計画は、行動・担当・時期を説明できて初めて役立ちます。", ("Actionable", "行動できる", "I'll fix the test today.", "今日テストを修正します。"), ("Too vague", "曖昧", "We'll try harder.", "もっと頑張ります。")),
        transfer_title="Delaying a client review", transfer_ja="顧客レビューを延期する", transfer_role="Client Director",
        transfer_turns=(("other", "Can your team present the final design at tomorrow's demo?", "明日のデモで最終デザインを発表できますか？"), ("target", 1, 2), ("other", "What date can you commit to instead?", "代わりにいつなら約束できますか？"), ("target", 2, 2), ("other", "Friday works if you send me a progress note tomorrow.", "明日進捗メモを送るなら、金曜日で大丈夫です。"), ("me", "Agreed. I will send the note by noon tomorrow.", "合意します。明日の正午までにメモを送ります。")),
        vocab=("here's where we are|現状はこうです; recovery plan|立て直し計画", "push back|後ろへずらす|CTX-12", "I'm afraid|残念ですが; won't be ready|間に合わない", "daily update|毎日の進捗; progress note|進捗メモ"),
    ),
    42: dict(
        slug="close-a-project-discussion-with-actions", title="Close a project discussion with actions", ko="실행 항목으로 프로젝트 논의 마무리하기", ja="実行項目を確認して案件の話し合いを終える",
        role="Project Lead", scene="Closing a project meeting with two owners", scene_ja="二人の担当を確認して会議を終える場面",
        situation="話し合いの最後に、誰が何をいつまでにするかをまとめます。全員が同じ行動と締め切りを持って会議を終えます。",
        goal=("Confirm two action owners and their deadlines before the meeting ends.", "会議が終わる前に、二つの実行項目の担当者と締め切りを確認しましょう。"),
        expressions=(("action items", "実行項目"), ("by close of business", "営業時間終了までに")),
        p1=pattern(bridge="まず、決まった二つの担当を簡潔にまとめます。", meaning=("Use this to recap two people and their separate actions.", "二人とそれぞれの行動をまとめる表現です。"), rows_=rows(
            ("{t}So I'll{/t} update the schedule, and {t}Mia will{/t} contact the client.", "{t}では私が{/t}日程を更新し、{t}ミアが{/t}顧客に連絡します。", "So|I'll update the schedule,|and|Mia will contact the client."),
            ("{t}So I'll{/t} revise the budget, and {t}Ken will{/t} check the figures.", "{t}では私が{/t}予算を修正し、{t}ケンが{/t}数値を確認します。", "So|I'll revise the budget,|and|Ken will check the figures."),
            ("{t}So I'll{/t} write the notes, and {t}Jo will{/t} send the files.", "{t}では私が{/t}メモを書き、{t}ジョーが{/t}ファイルを送ります。", "So|I'll write the notes,|and|Jo will send the files."),
            ("{t}So I'll{/t} call the supplier, and {t}Lee will{/t} update the team.", "{t}では私が{/t}仕入先に電話し、{t}リーが{/t}チームに報告します。", "So|I'll call the supplier,|and|Lee will update the team.")), rule=("Give each action one owner", "各行動に担当者を一人", "State your action first and the other person's action after “and.”", "自分の行動を先に、and のあとにもう一人の行動を示します。", "So + I'll + action, and + person + will + action", "Recap ownership", "担当をまとめる", ("I'll update · Mia will contact", "I'll revise · Ken will check")), write=("Which two actions and owners would you recap?", "どの二つの行動と担当者をまとめますか？")),
        p2=pattern(bridge="次に、それぞれの行動に具体的な締め切りを加えます。", meaning=("Use this to close with a separate deadline for each owned action.", "担当ごとの締め切りを確認して終える表現です。"), rows_=rows(
            ("{t}I'll{/t} send the updated schedule {t}by Wednesday{/t}, and {t}she'll{/t} contact the client {t}by Friday{/t}.", "{t}私が{/t}更新した日程を{t}水曜日までに{/t}送り、{t}彼女が{/t}顧客へ{t}金曜日までに{/t}連絡します。", "I'll send the updated schedule by Wednesday,|and she'll contact the client|by Friday."),
            ("{t}I'll{/t} revise the budget {t}by noon{/t}, and {t}he'll{/t} check the figures {t}by three{/t}.", "{t}私が{/t}予算を{t}正午までに{/t}修正し、{t}彼が{/t}数値を{t}3時までに{/t}確認します。", "I'll revise the budget by noon,|and he'll check the figures|by three."),
            ("{t}I'll{/t} write the notes {t}by tomorrow{/t}, and {t}she'll{/t} send the files {t}by Thursday{/t}.", "{t}私が{/t}メモを{t}明日までに{/t}書き、{t}彼女が{/t}ファイルを{t}木曜日までに{/t}送ります。", "I'll write the notes by tomorrow,|and she'll send the files|by Thursday."),
            ("{t}I'll{/t} call the supplier {t}by four{/t}, and {t}he'll{/t} update the team {t}by five{/t}.", "{t}私が{/t}仕入先に{t}4時までに{/t}電話し、{t}彼が{/t}チームに{t}5時までに{/t}報告します。", "I'll call the supplier by four,|and he'll update the team|by five.")), rule=("Put each deadline after its action", "締め切りは各行動のあと", "Attach the first “by” time to your action and the second to the other person's action.", "一つ目の by を自分の行動、二つ目を相手の行動に結びます。", "I'll + action + by + time, and person will + action + by + time", "Confirm deadlines", "締め切りを確認", ("send · by Wednesday", "contact · by Friday")), write=("What are the two actions, owners, and deadlines?", "二つの行動・担当者・締め切りは何ですか？"), omit_reorder=True),
        scene_turns=(("other", "The schedule and client call still have no owners. You and Mia each thought the other person owned them.", "日程更新と顧客への連絡はまだ担当が決まっていません。あなたとミアはどちらも相手の担当だと思っていました。"), ("target", 1, 0), ("other", "Correct. What are the deadlines?", "そのとおりです。締め切りはいつですか？"), ("target", 2, 0), ("other", "Good. Please put that in the notes.", "分かりました。それを議事録に入れてください。"), ("me", "I will circulate the notes after this meeting.", "この会議のあと、議事録を共有します。")),
        receptive=(("each thought the other person owned them", "Responsibility for both actions was unclear", "二つの行動の担当がどちらも曖昧だった", "Both actions already had confirmed owners", "二つの行動はすでに担当が確定していた"), ("Mia will contact the client", "Mia owns the client contact", "顧客連絡はミアの担当", "The learner owns both actions", "学習者が両方を担当する"), ("by Wednesday", "The schedule has its own deadline", "日程表には個別の締め切りがある", "Wednesday is the meeting date", "水曜日は会議の日である"), ("put that in the notes", "The lead wants the agreement recorded", "リーダーは合意内容の記録を求めている", "The lead asks to delete the actions", "リーダーは行動項目の削除を求めている")),
        live=live("Use a real or imaginary meeting. Recap two owners, then give each action a deadline.", "実際または架空の会議で、二人の担当とそれぞれの締め切りをまとめてください。", "Real or imaginary: So I'll ___, and ___ will ___. I'll ___ by ___, and ___ will ___ by ___.", "実際の会議でも架空でも、担当と締め切りの二つの表現を使いましょう。", "After a meeting, which action would you usually own and by when?", "会議後なら、先生は通常どの行動をいつまでに担当しますか？"),
        tip=("Use “by” for the latest acceptable time", "最終期限には by", "“By Friday” means no later than Friday; it does not mean the work must happen only on Friday.", "by Friday は金曜日までのどこかで、金曜日当日だけという意味ではありません。", ("Deadline", "締め切り", "by Friday", "金曜日までに"), ("Day only", "その日だけ", "on Friday", "金曜日に")),
        transfer_title="Closing a handover discussion", transfer_ja="引き継ぎ会議を行動確認で終える", transfer_role="Team Lead",
        transfer_turns=(("other", "The meeting notes and project files still have no owners. Let's settle that before we finish.", "議事録とプロジェクト資料はまだ担当が決まっていません。終わる前に決めましょう。"), ("target", 1, 2), ("other", "Good. When will each item be ready?", "分かりました。それぞれいつ準備できますか？"), ("target", 2, 2), ("other", "Those dates work. Add them to the shared plan.", "その日程で大丈夫です。共有計画に追加してください。"), ("me", "I will update the plan and send it today.", "計画を更新し、今日送ります。")),
        vocab=("action items|実行項目; by close of business|営業時間終了までに", "client|顧客|CORE-54", "action owner|担当者; circulate|共有する", "meeting notes|議事録; shared plan|共有計画"),
    ),
    43: dict(
        slug="interrupt-to-clarify-a-key-point", title="Interrupt to clarify a key point", ko="핵심을 확인하려고 끼어들기", ja="重要点を確認するために割って入る",
        role="Presenter", scene="Checking a proposed launch date", scene_ja="仕入先の見込みに基づく日程確認",
        situation="会議が次の話題へ進む前に、重要な日程の根拠を確認します。丁寧に割って入り、前提が変われば日程も変わるかを確かめます。",
        goal=("Interrupt politely and expose the assumption behind an important date.", "丁寧に割って入り、重要な日程の前提を明らかにしましょう。"),
        expressions=(("before we move on", "次へ進む前に"), ("underlying assumption", "根底にある前提")),
        p1=pattern(bridge="まず、割って入ることを詫びてから、日程の根拠を尋ねます。", meaning=("Use this bounded question to interrupt for a specific factual basis.", "具体的な根拠を確認するために丁寧に割って入る定型質問です。"), rows_=rows(
            ("{t}Sorry to interrupt, but what is that date based on{/t}?", "{t}お話の途中すみませんが、その日程は何に基づいていますか{/t}？", "Sorry to interrupt,|but what is that date|based on?"),
            ("{t}Sorry to interrupt, but what is that figure based on{/t}?", "{t}お話の途中すみませんが、その数値は何に基づいていますか{/t}？", "Sorry to interrupt,|but what is that figure|based on?"),
            ("{t}Sorry to interrupt, but what is that forecast based on{/t}?", "{t}お話の途中すみませんが、その予測は何に基づいていますか{/t}？", "Sorry to interrupt,|but what is that forecast|based on?"),
            ("{t}Sorry to interrupt, but what is that decision based on{/t}?", "{t}お話の途中すみませんが、その判断は何に基づいていますか{/t}？", "Sorry to interrupt,|but what is that decision|based on?")), rule=("Keep the clarification question intact", "確認の質問は一まとまりで", "This is a bounded meeting move for asking what evidence supports a point.", "会議で、ある点を支える根拠を尋ねる定型表現です。", "Sorry to interrupt, but what is + point + based on?", "Ask for the basis", "根拠を尋ねる", ("date · based on?", "figure · based on?")), write=("Which important date or figure would you ask about?", "どの重要な日程や数値の根拠を尋ねますか？"), omit_rule=True, omit_reorder=True),
        p2=pattern(bridge="次に、その前提が変わった場合の影響を確認します。", meaning=("Use this to check your inference that the stated result is conditional.", "示された結果が条件つきだという理解を確認する表現です。"), rows_=rows(
            ("{t}So it could change{/t} if their estimate changes?", "では、相手の見込みが変われば、{t}それも変わる可能性があるのですね{/t}？", "So it could change|if their estimate|changes?"),
            ("{t}So it could change{/t} if the costs rise?", "では、費用が上がれば、{t}それも変わる可能性があるのですね{/t}？", "So it could change|if the costs|rise?"),
            ("{t}So it could change{/t} if the client results change?", "では、顧客の実績が変われば、{t}それも変わる可能性があるのですね{/t}？", "So it could change|if the client results|change?"),
            ("{t}So it could change{/t} if approval is delayed?", "では、承認が遅れれば、{t}それも変わる可能性があるのですね{/t}？", "So it could change|if approval|is delayed?")), rule=("Put the changing assumption after “if”", "変わる前提は if のあと", "State the possible consequence first and the uncertain assumption after “if.”", "起こり得る結果を先に、不確かな前提を if のあとに置きます。", "So it could change if + assumption changes?", "Test the assumption", "前提を確認", ("could change · if estimate changes", "could change · if approval is delayed")), write=("Which assumption could change the result?", "どの前提が変わると結果も変わりますか？"), omit_reorder=True),
        scene_turns=(("other", "We should be ready to launch on June 12.", "6月12日に公開できる見込みです。"), ("target", 1, 0), ("other", "It's based on the supplier's current estimate.", "仕入先の現在の見込みに基づいています。"), ("target", 2, 0), ("other", "Exactly. It isn't fixed yet.", "そのとおりです。まだ確定ではありません。"), ("me", "Then let's record the date as provisional.", "では、その日程は暫定として記録しましょう。")),
        receptive=(("June 12", "The presenter states a planned launch date", "発表者は公開予定日を示している", "The presenter cancels the launch", "発表者は公開を中止する"), ("based on", "The learner asks for the date's basis", "学習者は日程の根拠を尋ねている", "The learner asks to leave the meeting", "学習者は会議を退出したい"), ("current estimate", "The date relies on a supplier assumption", "日程は仕入先の見込みに依存している", "The date is legally fixed", "日程は法的に確定している"), ("isn't fixed yet", "The date may still change", "日程はまだ変わる可能性がある", "The date cannot change", "日程は変更できない")),
        live=live("Use a real or imaginary meeting claim. Ask what it is based on, then test the assumption behind it.", "実際または架空の会議の主張で、根拠と前提が変わる場合を確認してください。", "Real or imaginary: Sorry to interrupt, but what is ___ based on? So it could change if ___?", "実際の会議でも架空でも、根拠確認と前提確認を使いましょう。", "In a real or imaginary meeting, which claim would you want evidence for?", "実際または架空の会議なら、先生はどの主張の根拠を確認しますか？"),
        tip=("Use “based on” to ask for the source, not the reason", "情報源には based on", "“What is it based on?” asks for evidence or an assumption; “Why?” can invite a broader explanation.", "What is it based on? は根拠や前提、Why? はより広い理由を尋ねます。", ("Evidence", "根拠", "What is the date based on?", "日程は何に基づいていますか？"), ("Broad reason", "広い理由", "Why did you choose that date?", "なぜその日程を選びましたか？")),
        transfer_title="Checking a sales forecast", transfer_ja="売上予測の前提を確認する", transfer_role="Sales Director",
        transfer_turns=(("other", "The forecast assumes sales will rise ten percent next quarter.", "予測では次の四半期に売上が10％増える想定です。"), ("target", 1, 2), ("other", "It uses the results from our three largest clients.", "上位三社の顧客実績を使っています。"), ("target", 2, 2), ("other", "Yes. We will update it after Friday's review.", "はい。金曜日のレビュー後に更新します。"), ("me", "Good. I will label the current forecast as provisional.", "分かりました。現在の予測は暫定と明記します。")),
        vocab=("before we move on|次へ進む前に; underlying assumption|根底にある前提; provisional|暫定の", "supplier|取引先|CORE-82", "sorry to interrupt|お話の途中すみません; based on|基づいている", "sales forecast|売上予測; supporting evidence|裏付けとなる根拠"),
    ),
    44: dict(
        slug="summarise-a-decision-before-moving-on", title="Summarise a decision before moving on", ko="다음으로 넘어가기 전 결정 요약하기", ja="次へ進む前に決定を要約する",
        role="Meeting Chair", scene="Confirming a limited test of option B", scene_ja="選択肢Bの限定テストを確認する場面",
        situation="議題を変える前に、決まった内容を一文でまとめます。自分の理解を確認し、誤った記録を防ぎます。",
        goal=("State the decision in one line and get explicit confirmation before moving on.", "決定を一文でまとめ、次へ進む前に明確な確認を得ましょう。"),
        expressions=(("for the record", "記録のために"), ("before we move on", "次へ進む前に")),
        p1=pattern(bridge="まず、合意した行動を短くまとめます。", meaning=("Use this to state the action the group has just agreed to take.", "グループが合意した行動をまとめる表現です。"), rows_=rows(
            ("{t}So we've agreed to{/t} test option B first.", "では、まず選択肢Bを試すことで{t}合意したのですね{/t}。", "So|we've agreed|to test option B|first."),
            ("{t}So we've agreed to{/t} run one pilot first.", "では、まず一回試験導入することで{t}合意したのですね{/t}。", "So|we've agreed|to run one pilot|first."),
            ("{t}So we've agreed to{/t} use the smaller team first.", "では、まず小さいチームで進めることで{t}合意したのですね{/t}。", "So|we've agreed|to use the smaller team|first."),
            ("{t}So we've agreed to{/t} review the cost Friday.", "では、金曜日に費用を確認することで{t}合意したのですね{/t}。", "So|we've agreed|to review the cost|Friday.")), rule=("Put the agreed action after “to”", "合意した行動は to のあと", "Name the one action the group approved, not every point discussed.", "話し合ったすべてではなく、承認された行動を一つ示します。", "So we've agreed to + action", "Summarise the decision", "決定を要約", ("agreed to · test option B", "agreed to · run one pilot")), write=("What single action did the group agree to?", "グループが合意した一つの行動は何ですか？")),
        p2=pattern(bridge="次に、その理解が正しいかを明確に確認します。", meaning=("Use this to invite a correction before the decision is recorded.", "決定を記録する前に、訂正の機会を作る表現です。"), rows_=rows(
            ("{t}Have I understood{/t} that {t}correctly{/t}?", "そのように{t}理解しましたが{/t}、{t}合っていますか{/t}？", "Have I understood|that|correctly?"),
            ("{t}Have I understood{/t} the scope {t}correctly{/t}?", "範囲をそのように{t}理解しましたが{/t}、{t}合っていますか{/t}？", "Have I understood|the scope|correctly?"),
            ("{t}Have I understood{/t} the timing {t}correctly{/t}?", "日程をそのように{t}理解しましたが{/t}、{t}合っていますか{/t}？", "Have I understood|the timing|correctly?"),
            ("{t}Have I understood{/t} the decision {t}correctly{/t}?", "決定をそのように{t}理解しましたが{/t}、{t}合っていますか{/t}？", "Have I understood|the decision|correctly?")), rule=("Put the point you are checking in the middle", "確認する内容は中央に", "Keep “Have I understood” and “correctly?” around the decision or detail you want checked.", "Have I understood と correctly? の間に、確認したい決定や詳細を置きます。", "Have I understood + point + correctly?", "Invite correction", "訂正を促す", ("understood · the scope · correctly", "understood · the timing · correctly")), write=("Which decision would you confirm before recording it?", "記録する前にどの決定を確認しますか？")),
        scene_turns=(("other", "Let's test option B first.", "まず選択肢Bを試しましょう。"), ("target", 1, 0), ("other", "Yes. Start with the support team only.", "はい。まずサポートチームだけで始めましょう。"), ("target", 2, 0), ("other", "Yes. Please record it that way.", "はい。その内容で記録してください。"), ("me", "I will add the decision and the one-team limit to the notes.", "決定と一チーム限定の条件を議事録に入れます。")),
        receptive=(("test option B first", "The group chooses option B for the first test", "グループは最初のテストに選択肢Bを選んだ", "The group rejects option B", "グループは選択肢Bを却下した"), ("agreed to", "The learner recaps the approved action", "学習者は承認された行動をまとめている", "The learner proposes a new unrelated action", "学習者は無関係な新しい行動を提案する"), ("support team only", "The chair limits the first test to one team", "議長は最初のテストを一チームに限定する", "The chair expands it to all teams", "議長は全チームに広げる"), ("record it that way", "The chair confirms the summary for the notes", "議長はその要約で記録するよう確認する", "The chair asks to erase the decision", "議長は決定を消すよう求める")),
        live=live("Use a real or imaginary meeting decision. Summarise the action, then check that you understood it correctly.", "実際または架空の会議の決定を要約し、理解が正しいか確認してください。", "Real or imaginary: So we've agreed to ___. Have I understood ___ correctly?", "実際の会議でも架空でも、要約と確認の二つを使いましょう。", "Before recording a decision, what detail would you always confirm?", "決定を記録する前に、先生ならどの詳細を必ず確認しますか？"),
        tip=("Use “agreed to” for an action", "行動の合意には agreed to", "“Agreed to test” names an action; “agreed that” normally introduces a full statement.", "agreed to test は行動、agreed that は通常、完全な内容を続けます。", ("Action", "行動", "We agreed to test it.", "試すことで合意しました。"), ("Statement", "内容", "We agreed that it was ready.", "準備できていると合意しました。")),
        transfer_title="Confirming a budget decision", transfer_ja="予算の決定を確認する", transfer_role="Finance Chair",
        transfer_turns=(("other", "We'll run one smaller pilot before any larger rollout.", "大規模展開の前に、小規模な試験導入を一回行います。"), ("target", 1, 1), ("other", "Yes, one pilot before any larger rollout.", "はい、大規模展開の前に一回だけです。"), ("target", 2, 3), ("other", "Correct. Put that in the decision log and schedule a June review.", "そのとおりです。決定記録に入れ、6月のレビューを予定に入れてください。"), ("me", "I will record both the pilot and the review date.", "試験導入とレビュー日程の両方を記録します。")),
        vocab=("for the record|記録のために; decision log|決定記録", "before we move on|次へ進む前に|CTX-43; option|選択肢|CORE-45", "agreed to|合意した; correctly|正しく", "one-team limit|一チーム限定; larger rollout|大規模展開"),
    ),
    45: dict(
        slug="present-a-recommendation-up-front", title="Present a recommendation up front", ko="결론부터 추천안 제시하기", ja="結論から推奨案を示す",
        role="Decision Maker", scene="Choosing among three implementation options", scene_ja="三つの導入案から選ぶ場面",
        situation="比較説明を長く始める前に、推奨案を先に示します。続けて、判断に役立つ理由を一つ述べます。",
        goal=("Lead with one recommendation and support it with a decision-relevant reason.", "一つの推奨案を先に示し、判断に役立つ理由を添えましょう。"),
        expressions=(("bottom line", "結論"), ("recommended option", "推奨案")),
        p1=pattern(bridge="まず、推奨する選択肢を一文で明確にします。", meaning=("Use this bounded line to give the conclusion before the supporting detail.", "詳しい説明の前に結論を示す定型表現です。"), rows_=rows(
            ("{t}I recommend option B{/t}.", "{t}選択肢Bをおすすめします{/t}。", "I recommend|option B."),
            ("{t}I recommend the smaller pilot{/t}.", "{t}小規模な試験導入をおすすめします{/t}。", "I recommend|the smaller pilot."),
            ("{t}I recommend the June launch{/t}.", "{t}6月の公開をおすすめします{/t}。", "I recommend|the June launch."),
            ("{t}I recommend the current supplier{/t}.", "{t}現在の仕入先をおすすめします{/t}。", "I recommend|the current supplier.")), rule=("Keep the recommendation intact", "推奨は一まとまりで", "This bounded line gives one clear choice before you explain why.", "理由を説明する前に、一つの選択肢を明確に示す定型表現です。", "I recommend + option", "Lead with the conclusion", "結論を先に示す", ("recommend · option B", "recommend · the smaller pilot")), write=("Which option would you recommend?", "どの選択肢をおすすめしますか？"), omit_rule=True, omit_reorder=True),
        p2=pattern(bridge="次に、比較できる短い理由を一つ示します。", meaning=("Use a comparative reason that directly supports the choice.", "選択を直接支える比較理由を示す表現です。"), rows_=rows(
            ("It's {t}faster to implement{/t}.", "{t}導入がより速いです{/t}。", "It's faster|to implement."),
            ("It's {t}cheaper to maintain{/t}.", "{t}維持費がより安いです{/t}。", "It's cheaper|to maintain."),
            ("It's {t}easier to explain{/t}.", "{t}説明がより簡単です{/t}。", "It's easier|to explain."),
            ("It's {t}safer to test{/t}.", "{t}試すうえでより安全です{/t}。", "It's safer|to test.")), rule=("Keep the comparative reason together", "比較理由は一まとまりで", "The comparative and its action work as one decision reason here.", "比較語と行動を、判断理由の一まとまりとして使います。", "It's + comparative + to + action", "Support the recommendation", "推奨を支える", ("faster to implement", "cheaper to maintain")), write=("What is one comparative reason for your recommendation?", "推奨案を支える比較理由を一つ挙げると？"), omit_rule=True, omit_reorder=True),
        scene_turns=(("other", "We've reviewed options A, B, and C. Which one should we choose?", "選択肢A、B、Cを検討しました。どれを選ぶべきですか？"), ("target", 1, 0), ("other", "Why B?", "なぜBですか？"), ("target", 2, 0), ("other", "Good. Show us the comparison.", "分かりました。比較を見せてください。"), ("me", "I will show the timing and cost side by side.", "日程と費用を並べて示します。")),
        receptive=(("options A, B, and C", "The managers are considering three options", "管理職は三つの案を検討している", "The managers have already rejected every option", "管理職はすべての案をすでに却下した"), ("option B", "The learner gives one clear recommendation", "学習者は一つの案を明確に推奨する", "The learner avoids choosing", "学習者は選択を避ける"), ("faster to implement", "The reason compares implementation speed", "理由は導入速度を比較している", "The reason compares office locations", "理由はオフィスの場所を比較している"), ("Show us the comparison.", "The decision maker asks for supporting evidence", "意思決定者は比較根拠を求めている", "The decision maker ends the project", "意思決定者は案件を終了する")),
        live=live("Name options A, B, and C. Recommend one and give one comparative reason.", "選択肢A・B・Cを挙げ、一つを推奨し、比較理由を伝えてください。", "Real or imaginary: A = ___; B = ___; C = ___. I recommend ___. It's ___ to ___.", "比較語には easier や more practical などが使えます。", "Of the three options you named, which would you recommend, and why?", "挙げた三つの案なら、先生はどれをなぜおすすめしますか？"),
        tip=("Choose “recommend” or “suggest” by strength", "recommend と suggest の強さ", "“Recommend” marks a clear preferred option; “suggest” offers a lighter possibility.", "recommend は明確な推奨案を示し、suggest はより軽い提案を示します。", ("Clear preference", "明確な推奨", "I recommend option B.", "選択肢Bをおすすめします。"), ("Lighter proposal", "軽い提案", "I suggest a smaller pilot.", "小規模な試験導入を提案します。")),
        transfer_title="Recommending a pilot format", transfer_ja="試験導入の形式を推奨する", transfer_role="Operations Director",
        transfer_turns=(("other", "Should we test with one team or the whole department?", "一チームで試すべきですか、それとも部門全体ですか？"), ("target", 1, 1), ("other", "What makes the smaller pilot better?", "なぜ小規模な試験導入のほうがよいのですか？"), ("target", 2, 3), ("other", "All right. Prepare a two-week test plan.", "分かりました。二週間の試験計画を用意してください。"), ("me", "I will send the plan and success criteria tomorrow.", "明日、計画と成功基準を送ります。")),
        vocab=("bottom line|結論; recommended option|推奨案; recommend|おすすめする; implement|導入する; suggest|提案する", "option|選択肢|CORE-45", "comparative reason|比較理由; up front|先に", "success criteria|成功基準; side by side|並べて"),
    ),
    46: dict(
        slug="answer-a-question-when-you-do-not-know-yet", title="Answer a question when you do not know yet", ko="아직 모르는 질문에 답하기", ja="まだ分からない質問に対応する",
        role="Senior Manager", scene="A meeting question about an unverified figure", scene_ja="未確認の数値を会議で尋ねられる場面",
        situation="手元にない数値を推測で答えません。確認済みではないことを率直に伝え、いつまでに回答するかを約束します。",
        goal=("Protect accuracy and commit to a specific follow-up time.", "正確さを守り、具体的な回答時刻を約束しましょう。"),
        expressions=(("verified figure", "確認済みの数値"), ("follow up in writing", "書面で追って連絡する")),
        p1=pattern(bridge="まず、確認済みの数値が手元にないと明確にします。", meaning=("Use this bounded line to avoid presenting a guess as a confirmed fact.", "推測を確認済みの事実として伝えないための定型表現です。"), rows_=rows(
            ("{t}I don't have the confirmed figure in front of me{/t}.", "{t}確認済みの数値が今、手元にありません{/t}。", "I don't have|the confirmed figure|in front of me."),
            ("{t}I don't have the final cost in front of me{/t}.", "{t}最終費用が今、手元にありません{/t}。", "I don't have|the final cost|in front of me."),
            ("{t}I don't have the exact date in front of me{/t}.", "{t}正確な日付が今、手元にありません{/t}。", "I don't have|the exact date|in front of me."),
            ("{t}I don't have the latest total in front of me{/t}.", "{t}最新の合計が今、手元にありません{/t}。", "I don't have|the latest total|in front of me.")), rule=("Keep the accuracy line intact", "正確さを守る表現は一まとまりで", "Use this bounded line for information you cannot verify during the conversation.", "会話中に確認できない情報について使う定型表現です。", "I don't have + confirmed item + in front of me", "Avoid guessing", "推測を避ける", ("confirmed figure · in front of me", "exact date · in front of me")), write=("Which fact would you refuse to guess about?", "どの事実なら推測で答えませんか？"), omit_rule=True, omit_reorder=True),
        p2=pattern(bridge="次に、確認して回答する具体的な時刻を示します。", meaning=("Use this bounded promise to name both the follow-up action and deadline.", "確認する行動と回答期限の両方を示す定型表現です。"), rows_=rows(
            ("{t}Let me check and get back to you by three{/t}.", "{t}確認して3時までにご連絡します{/t}。", "Let me check|and get back to you|by three."),
            ("{t}Let me check and get back to you by noon{/t}.", "{t}確認して正午までにご連絡します{/t}。", "Let me check|and get back to you|by noon."),
            ("{t}Let me check and get back to you tomorrow{/t}.", "{t}確認して明日ご連絡します{/t}。", "Let me check|and get back to you|tomorrow."),
            ("{t}Let me check and get back to you after the meeting{/t}.", "{t}確認して会議後にご連絡します{/t}。", "Let me check|and get back to you|after the meeting.")), rule=("Keep the follow-up promise intact", "確認と回答の約束は一まとまりで", "This bounded promise combines the check, return message, and deadline.", "確認、回答、期限をまとめた定型表現です。", "Let me check and get back to you by + time", "Commit to follow up", "追って回答を約束", ("check · get back · by three", "check · get back · by noon")), write=("When could you return with a verified answer?", "いつまでに確認済みの回答を返せますか？"), omit_rule=True, omit_reorder=True),
        scene_turns=(("other", "What was the confirmed conversion figure last month?", "先月の確定した成約率はいくつでしたか？"), ("target", 1, 0), ("other", "Can you give us an estimate?", "概算を教えてもらえますか？"), ("target", 2, 0), ("other", "That's fine. Please send it to everyone.", "それで大丈夫です。全員に送ってください。"), ("me", "I will send the verified figure and its source.", "確認済みの数値と情報源を送ります。")),
        receptive=(("confirmed conversion figure", "The manager asks for a verified number", "上司は確認済みの数値を求めている", "The manager asks for a personal opinion", "上司は個人的な意見を求めている"), ("in front of me", "The learner cannot verify the figure during the meeting", "学習者は会議中に数値を確認できない", "The learner knows the figure is zero", "学習者は数値がゼロだと知っている"), ("by three", "The learner promises a specific follow-up time", "学習者は具体的な回答時刻を約束する", "The learner refuses to answer later", "学習者はあとでも答えない"), ("send it to everyone", "The verified answer should be shared with the group", "確認済みの回答を全員に共有する", "The answer should remain private", "回答は非公開にする")),
        live=live("Use a real or imaginary question you cannot verify now. Protect accuracy, then promise a follow-up time.", "実際または架空の今確認できない質問で、正確さを守り、回答時刻を約束してください。", "Real or imaginary: I don't have the confirmed ___ in front of me. Let me check and get back to you by ___.", "実際の例でも架空でも、二つの表現を一度ずつ使いましょう。", "If you did not know an exact figure in a meeting, when would you promise to answer?", "会議で正確な数値が分からなければ、先生はいつまでの回答を約束しますか？"),
        tip=("Do not turn an estimate into a confirmed figure", "概算を確定値にしない", "An estimate is approximate; a confirmed figure has been checked against a reliable source.", "estimate は概算、confirmed figure は信頼できる情報源で確認した数値です。", ("Approximate", "概算", "about 30 percent", "約30％"), ("Verified", "確認済み", "the confirmed figure is 31 percent", "確認済みの数値は31％です")),
        transfer_title="Checking a final project cost", transfer_ja="最終案件費用を確認する", transfer_role="Finance Director",
        transfer_turns=(("other", "What is the final cost after the supplier change?", "仕入先変更後の最終費用はいくらですか？"), ("target", 1, 1), ("other", "When can finance have the verified total?", "財務はいつ確認済みの合計を受け取れますか？"), ("target", 2, 1), ("other", "Noon works. Include the updated invoice.", "正午で大丈夫です。更新済み請求書も入れてください。"), ("me", "I will send both items in one message.", "両方を一通のメッセージで送ります。")),
        vocab=("verified figure|確認済みの数値; follow up in writing|書面で追って連絡する; confirmed figure|確定した数値; get back to you|追って連絡する", "", "estimate|概算; in front of me|手元に", "conversion figure|成約率; reliable source|信頼できる情報源"),
    ),
    47: dict(
        slug="disagree-with-a-senior-colleague-constructively", title="Disagree with a senior colleague constructively", ko="상급자에게 건설적으로 이견 말하기", ja="目上の同僚に建設的に異議を述べる",
        role="Senior Director", scene="A proposal to skip the final test", scene_ja="最終テストを省く提案に異議を述べる場面",
        situation="相手の考えを理解したことを示してから、具体的な懸念を一つ述べます。人ではなく、判断のリスクに焦点を当てます。",
        goal=("Acknowledge the senior colleague's point and identify one specific concern.", "目上の同僚の考えを認め、具体的な懸念を一つ示しましょう。"),
        expressions=(("from my perspective", "私の観点では"), ("specific concern", "具体的な懸念")),
        p1=pattern(bridge="まず、相手の考えを認めてから、自分の懸念へつなぎます。", meaning=("Use this bounded contrast to show you heard the point before disagreeing.", "相手の考えを聞いたことを示してから異議を述べる定型表現です。"), rows_=rows(
            ("{t}I see your point, but{/t} the timing concerns me.", "{t}おっしゃることは分かりますが{/t}、日程が気になります。", "I see your point,|but the timing|concerns me."),
            ("{t}I see your point, but{/t} the cost concerns me.", "{t}おっしゃることは分かりますが{/t}、費用が気になります。", "I see your point,|but the cost|concerns me."),
            ("{t}I see your point, but{/t} the evidence concerns me.", "{t}おっしゃることは分かりますが{/t}、根拠が気になります。", "I see your point,|but the evidence|concerns me."),
            ("{t}I see your point, but{/t} the client impact concerns me.", "{t}おっしゃることは分かりますが{/t}、顧客への影響が気になります。", "I see your point,|but the client impact|concerns me.")), rule=("Keep acknowledgment before concern", "理解を示してから懸念へ", "This bounded opening signals respect before you name the issue.", "定型の冒頭で相手への敬意を示してから、問題点を挙げます。", "I see your point, but + concern", "Disagree constructively", "建設的に異議を述べる", ("see your point · timing concerns me", "see your point · cost concerns me")), write=("Which aspect of a proposal would concern you?", "提案のどの点が気になりますか？"), omit_rule=True, omit_reorder=True),
        p2=pattern(bridge="次に、不安の原因を一つの行動に絞ります。", meaning=("Use this bounded line to identify the exact part of the proposal you cannot support.", "提案の中で賛成できない具体的な部分を示す定型表現です。"), rows_=rows(
            ("{t}The part I'm not comfortable with is{/t} skipping the final test.", "私が{t}不安に思うのは{/t}、最終テストを省く点です。", "The part I'm not comfortable with|is skipping|the final test."),
            ("{t}The part I'm not comfortable with is{/t} reducing the review time.", "私が{t}不安に思うのは{/t}、レビュー時間を短縮する点です。", "The part I'm not comfortable with|is reducing|the review time."),
            ("{t}The part I'm not comfortable with is{/t} using unverified data.", "私が{t}不安に思うのは{/t}、未確認のデータを使う点です。", "The part I'm not comfortable with|is using|unverified data."),
            ("{t}The part I'm not comfortable with is{/t} telling the client later.", "私が{t}不安に思うのは{/t}、顧客への連絡を遅らせる点です。", "The part I'm not comfortable with|is telling|the client later.")), rule=("Keep the specific-concern frame intact", "具体的な懸念の枠は一まとまりで", "Name an action or decision after this bounded frame, not a judgment about the person.", "この定型表現のあとに、人への評価ではなく行動や判断を示します。", "The part I'm not comfortable with is + action", "Focus on the decision", "判断に焦点を当てる", ("not comfortable with · skipping the test", "not comfortable with · using unverified data")), write=("Which specific action would you question?", "どの具体的な行動に疑問を示しますか？"), omit_rule=True, omit_reorder=True),
        scene_turns=(("other", "We can meet the date if we skip the final test.", "最終テストを省けば日程に間に合います。"), ("target", 1, 0), ("other", "What specifically concerns you?", "具体的に何が気になりますか？"), ("target", 2, 0), ("other", "All right. Let's examine that risk.", "分かりました。そのリスクを検討しましょう。"), ("me", "I will show the failure cases from the last release.", "前回の公開で起きた不具合事例を示します。")),
        receptive=(("skip the final test", "The proposed schedule removes a quality step", "提案された日程では品質確認を一つ省く", "The proposal adds another test", "提案はテストを追加する"), ("I see your point", "The learner acknowledges the director's reasoning", "学習者は責任者の考えを認める", "The learner agrees with every detail", "学習者はすべてに賛成する"), ("specifically", "The director asks for the exact concern", "責任者は具体的な懸念を求めている", "The director changes the subject", "責任者は話題を変える"), ("examine that risk", "The concern will be considered", "懸念は検討される", "The concern is dismissed without discussion", "懸念は検討されず退けられる")),
        live=live("Use a real or imaginary proposal from a senior colleague. Acknowledge it, then name one specific concern.", "実際または架空の目上の同僚の提案で、理解を示してから具体的な懸念を一つ述べてください。", "Real or imaginary: I see your point, but ___ concerns me. The part I'm not comfortable with is ___.", "実際の提案でも架空でも、二つの表現を一度ずつ使いましょう。", "If a senior colleague wanted to skip a quality check, what would concern you?", "目上の同僚が品質確認を省こうとしたら、先生は何を懸念しますか？"),
        tip=("Challenge the decision, not the person", "人ではなく判断に異議を", "A specific concern can be examined; calling the other person careless usually makes the discussion defensive.", "具体的な懸念は検討できますが、相手を不用意だと決めつけると防御的な話になりがちです。", ("Decision", "判断", "Skipping the test concerns me.", "テストを省く点が気になります。"), ("Person", "人", "You're being careless.", "あなたは不用意です。")),
        transfer_title="Questioning a late client update", transfer_ja="顧客への連絡遅延に異議を述べる", transfer_role="Department Head",
        transfer_turns=(("other", "Let's wait until Friday before we tell the client about the risk.", "金曜日まで待ってから顧客にリスクを伝えましょう。"), ("target", 1, 3), ("other", "Which part of that plan worries you?", "その計画のどの部分が心配ですか？"), ("target", 2, 3), ("other", "Fair point. Draft an early update for my review.", "もっともです。早めの連絡文を作って、私に確認させてください。"), ("me", "I will send the draft within an hour.", "一時間以内に下書きを送ります。")),
        vocab=("from my perspective|私の観点では; specific concern|具体的な懸念; not comfortable with|〜に不安がある", "timing|タイミング|CORE-85", "I see your point|おっしゃることは分かる; concerns me|気になる", "quality check|品質確認; failure case|不具合事例"),
    ),
    48: dict(
        slug="turn-discussion-into-a-decision", title="Turn discussion into a decision", ko="논의를 결정으로 전환하기", ja="議論を決定につなげる",
        role="Meeting Chair", scene="A funding discussion without enough comparable evidence", scene_ja="比較可能な情報が足りない資金判断の場面",
        situation="話が広がり続ける会議で、今日決める内容を一つに絞ります。情報不足なら、同じ基準で比較する次の一手を提案します。",
        goal=("Define today's decision and create the comparison needed to make it.", "今日決める内容を定め、判断に必要な比較を作りましょう。"),
        expressions=(("decision criteria", "判断基準"), ("come to a decision", "結論を出す")),
        p1=pattern(bridge="まず、今日必要な判断を一文で定義します。", meaning=("Use this bounded line to stop a broad discussion and name the exact decision.", "広がった議論を止め、必要な判断を明確にする定型表現です。"), rows_=rows(
            ("{t}The decision we need today is which option to fund{/t}.", "{t}今日必要な判断は、どの案に資金を出すかです{/t}。", "The decision we need today|is which option|to fund."),
            ("{t}The decision we need today is which pilot to run{/t}.", "{t}今日必要な判断は、どの試験導入を行うかです{/t}。", "The decision we need today|is which pilot|to run."),
            ("{t}The decision we need today is which date to choose{/t}.", "{t}今日必要な判断は、どの日程を選ぶかです{/t}。", "The decision we need today|is which date|to choose."),
            ("{t}The decision we need today is which supplier to use{/t}.", "{t}今日必要な判断は、どの仕入先を使うかです{/t}。", "The decision we need today|is which supplier|to use.")), rule=("Keep the decision frame intact", "判断の定義は一まとまりで", "This bounded frame names one choice the group must make now.", "グループが今決める一つの選択を示す定型表現です。", "The decision we need today is which + option + to + action", "Focus the meeting", "会議の焦点を絞る", ("which option · to fund", "which pilot · to run")), write=("What single decision does a current or imaginary meeting need?", "実際または架空の会議で必要な一つの判断は何ですか？"), omit_rule=True, omit_reorder=True),
        p2=pattern(bridge="情報が足りなければ、判断できる比較方法を提案します。", meaning=("Use this bounded question to propose a practical way to make the options comparable.", "選択肢を比較可能にする実務的な方法を提案する定型質問です。"), rows_=rows(
            ("{t}Would it help if we compared them against the same three criteria{/t}?", "{t}同じ三つの基準で比較すれば、判断しやすくなりますか{/t}？", "Would it help|if we compared them|against the same three criteria?"),
            ("{t}Would it help if we compared them against the same budget{/t}?", "{t}同じ予算で比較すれば、判断しやすくなりますか{/t}？", "Would it help|if we compared them|against the same budget?"),
            ("{t}Would it help if we compared them against the same timeline{/t}?", "{t}同じ日程で比較すれば、判断しやすくなりますか{/t}？", "Would it help|if we compared them|against the same timeline?"),
            ("{t}Would it help if we compared them against the same risks{/t}?", "{t}同じリスク項目で比較すれば、判断しやすくなりますか{/t}？", "Would it help|if we compared them|against the same risks?")), rule=("Keep the comparison proposal intact", "比較提案は一まとまりで", "This bounded question proposes one fair basis for comparing every option.", "すべての案を比較する公平な基準を一つ提案する定型質問です。", "Would it help if we compared them against + same criteria?", "Create comparable evidence", "比較できる根拠を作る", ("compared them · same criteria", "compared them · same budget")), write=("Which common criteria would help the group decide?", "どの共通基準が判断に役立ちますか？"), omit_rule=True, omit_reorder=True),
        scene_turns=(("other", "We've discussed options A, B, and C for forty minutes.", "選択肢A、B、Cについて40分話し合いました。"), ("target", 1, 0), ("other", "I don't think we have enough information.", "判断に十分な情報がないと思います。"), ("target", 2, 0), ("other", "Yes. Then we can decide.", "はい。そうすれば決められます。"), ("me", "I will put cost, timing, and risk into one table.", "費用、日程、リスクを一つの表にまとめます。")),
        receptive=(("forty minutes", "The discussion has continued without a decision", "決定がないまま議論が続いている", "The decision was made forty minutes ago", "40分前に決定した"), ("which option to fund", "The learner defines the exact decision", "学習者は必要な判断を明確にする", "The learner asks to fund every option", "学習者は全案への資金提供を求める"), ("not enough information", "The chair sees an evidence gap", "議長は情報不足を認識している", "The chair has already chosen secretly", "議長はすでに内密に選んだ"), ("Then we can decide.", "A common comparison can unlock the decision", "共通比較によって判断できる", "The comparison will prevent any decision", "比較すると判断できなくなる")),
        live=live("Name three options. Define the decision, then propose one fair comparison.", "三つの案を示し、判断を定義して、公平な比較方法を一つ提案してください。", "Real or imaginary: A = ___; B = ___; C = ___. The decision we need today is ___. Would it help if we compared them against ___?", "三つの案を示してから、判断定義と比較提案を使いましょう。", "If three real or imaginary options were hard to compare, which criteria would you use?", "実際または架空の三案を比べにくいなら、先生はどの基準を使いますか？"),
        tip=("Criteria are standards, not options", "criteria は選択肢ではなく基準", "Options are the things you may choose; criteria are the standards you use to compare them.", "options は選ぶ対象、criteria はそれらを比べる基準です。", ("Things to choose", "選ぶ対象", "options A, B, and C", "選択肢A、B、C"), ("Standards", "比較基準", "cost, timing, and risk", "費用・日程・リスク")),
        transfer_title="Choosing a supplier", transfer_ja="仕入先を選ぶ", transfer_role="Procurement Chair",
        transfer_turns=(("other", "The three suppliers have different prices, dates, and service levels.", "三社は価格、日程、サービス水準が異なります。"), ("target", 1, 3), ("other", "We need a fair way to compare them first.", "まず公平に比較する方法が必要です。"), ("target", 2, 0), ("other", "Yes. Use cost, delivery, and support as the criteria.", "はい。費用、納期、サポートを基準にしてください。"), ("me", "I will complete the comparison before tomorrow's decision meeting.", "明日の意思決定会議までに比較を完成させます。")),
        vocab=("decision criteria|判断基準; come to a decision|結論を出す; fund|資金を出す", "option|選択肢|CORE-45; supplier|取引先|CORE-82", "would it help if|〜すれば役立ちますか; compare|比較する", "service level|サービス水準; evidence gap|根拠不足"),
    ),
}


# Human-reviewed operating copy for the CTX37-48 semantic pass.  These fields
# are kept beside the lesson data so regeneration cannot silently restore
# generic write prompts, unsupported translation, or pattern-production free
# talk.  A checkpoint deliberately has no lexical hints; supported production
# has useful content-word hints while articles and grammar remain learner work.
REVIEWED_COPY_37_48 = {
    37: dict(
        role_ja="上司", transfer_role_ja="チームリーダー",
        live=("When several tasks feel urgent, how do you decide what to do first?", "いくつもの仕事が急ぎに見えるとき、何を最初にするかどう決めますか？", "Your real method and why it works for you", "自分の実際の決め方と、その方法がよい理由", "What about you—how do you decide what comes first?", "先生はどうですか？何を最初にするかどう決めますか？"),
        p1=dict(write_frame="I can ___, but probably not ___", write_script="Use “I can ___, but probably not ___” to tell your manager what you can realistically finish.", write_script_ja="「I can ___, but probably not ___」を使って、現実的に終えられる範囲を上司に伝えましょう。", translate_hints=(("金曜日までに二つ", "two by Friday"), ("今日、報告書", "report today"), ("顧客二社", "two clients"), ("緊急の問題", "urgent issue"))),
        p2=dict(write_frame="Which ___ should I ___ first?", write_script="Use “Which ___ should I ___ first?” to ask your manager for one clear first priority.", write_script_ja="「Which ___ should I ___ first?」を使って、最初に優先する仕事を上司に確認しましょう。", translate_hints=(("仕事", "task"), ("ファイル", "file"), ("顧客", "client"), ("問題", "problem"))),
    ),
    38: dict(
        role_ja="プロジェクト責任者", transfer_role_ja="顧客担当責任者",
        live=("Which kind of work do you prefer to own: contacting people, planning, or checking details?", "人への連絡、計画、細部の確認なら、どの仕事を担当したいですか？", "Your preference and a brief reason", "自分の希望と短い理由", "What about you—which kind of work do you prefer?", "先生はどうですか？どの仕事を担当したいですか？"),
        p1=dict(write_frame="Just to clarify, who's ___?", write_script="Use “Just to clarify, who's ___?” to ask who owns one unclear contact task.", write_script_ja="「Just to clarify, who's ___?」を使って、曖昧な連絡業務の担当者を確認しましょう。", translate_hints=(("仕入先", "supplier"), ("顧客", "client"), ("請求書", "invoice"), ("会議室", "room"))),
        p2=dict(write_frame="I'm happy to ___ if no one else is doing it", write_script="Use “I'm happy to ___ if no one else is doing it” to offer to take an unassigned task.", write_script_ja="「I'm happy to ___ if no one else is doing it」を使って、担当者がいない仕事を引き受けると申し出ましょう。", translate_stage="checkpoint"),
    ),
    39: dict(
        role_ja="プロジェクトスポンサー", transfer_role_ja="分析責任者",
        live=("What makes you trust a project status update?", "どんな進捗報告なら信頼できますか？", "One detail that builds trust and why", "信頼につながる情報を一つと、その理由", "What about you—what makes a status update trustworthy?", "先生はどうですか？どんな進捗報告なら信頼できますか？"),
        p1=dict(write_frame="We're on track ___", write_script="Use “We're on track ___” to give the current project status without overstating it.", write_script_ja="「We're on track ___」を使って、言い過ぎずに現在の進捗を伝えましょう。", translate_stage="checkpoint"),
        p2=dict(write_frame="The main risk is that ___", write_script="Use “The main risk is that ___” to raise one possible problem before it becomes urgent.", write_script_ja="「The main risk is that ___」を使って、深刻になる前に主なリスクを一つ伝えましょう。", translate_hints=(("仕入先", "supplier"), ("データ", "data"), ("承認", "approval"), ("試験", "test"))),
    ),
    40: dict(
        role_ja="上司", transfer_role_ja="製品責任者",
        live=("Would you rather receive a rough answer quickly or a complete answer later, and why?", "早い仮回答と遅い完全な回答なら、どちらがよいですか？なぜですか？", "Your preference and a brief reason", "自分の希望と短い理由", "What about you—which would you rather receive?", "先生はどうですか？どちらを受け取りたいですか？"),
        p1=dict(write_frame="I can ___, but ___ will take ___", write_script="Use “I can ___, but ___ will take ___” to offer an interim result and state how long the full work needs.", write_script_ja="「I can ___, but ___ will take ___」を使って、中間成果を提案し、完全な作業に必要な時間を伝えましょう。", translate_hints=(("要約", "summary"), ("概要", "outline"), ("数値", "figures"), ("下書き", "draft"))),
        p2=dict(write_frame="___ is realistic if ___", write_script="Use “___ is realistic if ___” to propose a workable deadline and the condition it depends on.", write_script_ja="「___ is realistic if ___」を使って、現実的な締め切りと、その条件を伝えましょう。", translate_hints=(("データ", "data"), ("数値", "figures"), ("チーム", "team"), ("範囲", "scope"))),
    ),
    41: dict(
        role_ja="責任者", transfer_role_ja="顧客側の責任者",
        live=("When plans go wrong, do you prefer to hear the bad news immediately or together with a solution?", "計画に問題が起きたら、悪い知らせをすぐ聞きたいですか、それとも解決策と一緒に聞きたいですか？", "Your preference and why", "自分の希望と理由", "What about you—when do you want to hear bad news?", "先生はどうですか？悪い知らせはいつ聞きたいですか？"),
        p1=dict(write_frame="I'm afraid we won't be ready for ___", write_script="Use “I'm afraid we won't be ready for ___” to tell the director which event will be delayed.", write_script_ja="「I'm afraid we won't be ready for ___」を使って、どの予定に間に合わないか責任者に伝えましょう。", translate_stage="checkpoint"),
        p2=dict(write_frame="We'll need to push it back ___, and I have a recovery plan", write_script="Use “We'll need to push it back ___, and I have a recovery plan” to give the new timing and show there is a next step.", write_script_ja="「We'll need to push it back ___, and I have a recovery plan」を使って、新しい日程と立て直し策があることを伝えましょう。", translate_stage="checkpoint"),
    ),
    42: dict(
        role_ja="プロジェクト責任者", transfer_role_ja="チームリーダー",
        live=("What is the most useful thing to receive after a meeting: notes, action items, or deadlines?", "会議後にもらうなら、議事録・行動項目・締め切りのどれが最も役立ちますか？", "Your choice and why it helps", "自分の選択と、役立つ理由", "What about you—which one is most useful?", "先生はどうですか？どれが最も役立ちますか？"),
        p1=dict(write_frame="So I'll ___, and ___ will ___", write_script="Use “So I'll ___, and ___ will ___” to recap two actions and their owners.", write_script_ja="「So I'll ___, and ___ will ___」を使って、二つの行動と担当者をまとめましょう。", translate_hints=((('日程', 'schedule'), ('顧客', 'client')), (('予算', 'budget'), ('数値', 'figures')), (('メモ', 'notes'), ('ファイル', 'files')), (('仕入先', 'supplier'), ('チーム', 'team')))),
        p2=dict(write_frame="I'll ___ by ___, and ___ will ___ by ___", write_script="Use “I'll ___ by ___, and ___ will ___ by ___” to confirm both owners and both deadlines.", write_script_ja="「I'll ___ by ___, and ___ will ___ by ___」を使って、二人の担当と締め切りを確認しましょう。", translate_hints=((('更新した日程', 'updated schedule'), ('顧客', 'client')), (('予算', 'budget'), ('数値', 'figures')), (('メモ', 'notes'), ('ファイル', 'files')), (('仕入先', 'supplier'), ('チーム', 'team')))),
    ),
    43: dict(
        role_ja="発表者", transfer_role_ja="営業責任者",
        live=("In meetings, what makes you question a number or forecast?", "会議で数値や予測を疑うのは、どんなときですか？", "One warning sign and why it matters", "注意する点を一つと、その理由", "What about you—what makes you question a forecast?", "先生はどうですか？どんなときに予測を疑いますか？"),
        p1=dict(write_frame="Sorry to interrupt, but what is ___ based on?", write_script="Use “Sorry to interrupt, but what is ___ based on?” to ask for the evidence behind an important claim.", write_script_ja="「Sorry to interrupt, but what is ___ based on?」を使って、重要な主張の根拠を尋ねましょう。", translate_stage="checkpoint"),
        p2=dict(write_frame="So it could change if ___?", write_script="Use “So it could change if ___?” to check which assumption could change the result.", write_script_ja="「So it could change if ___?」を使って、どの前提が変わると結果も変わるか確認しましょう。", translate_hints=(("見込み", "estimate"), ("費用", "costs"), ("顧客実績", "client results"), ("承認", "approval"))),
    ),
    44: dict(
        role_ja="会議の進行役", transfer_role_ja="財務会議の進行役",
        live=("Have you ever left a meeting with a different understanding from everyone else?", "会議のあと、自分だけ違う理解をしていたことはありますか？", "A real example, or why it has not happened", "実際の例、または起きたことがない理由", "What about you—has that ever happened to you?", "先生はどうですか？そのような経験はありますか？"),
        p1=dict(write_frame="So we've agreed to ___", write_script="Use “So we've agreed to ___” to summarise the action the group decided on.", write_script_ja="「So we've agreed to ___」を使って、グループが決めた行動を要約しましょう。", translate_hints=(("選択肢Bを試す", "test option B"), ("一回試験導入する", "run one pilot"), ("小さいチーム", "smaller team"), ("費用を確認する", "review the cost"))),
        p2=dict(write_frame="Have I understood ___ correctly?", write_script="Use “Have I understood ___ correctly?” to check the decision before you record it.", write_script_ja="「Have I understood ___ correctly?」を使って、記録する前に決定内容を確認しましょう。", translate_stage="checkpoint"),
    ),
    45: dict(
        role_ja="意思決定者", transfer_role_ja="業務責任者",
        live=("When someone recommends an option, which matters more to you: the recommendation or the reason?", "誰かが案をすすめるとき、結論と理由のどちらを重視しますか？", "Your choice and why", "自分の選択と理由", "What about you—which matters more?", "先生はどうですか？どちらを重視しますか？"),
        p1=dict(write_frame="I recommend ___", write_script="Use “I recommend ___” to give the decision maker one clear recommendation.", write_script_ja="「I recommend ___」を使って、意思決定者に一つの案を明確にすすめましょう。", translate_stage="checkpoint"),
        p2=dict(write_frame="It's ___ to ___", write_script="Use “It's ___ to ___” to give one comparative reason for your recommendation.", write_script_ja="「It's ___ to ___」を使って、推奨案を支える比較理由を一つ伝えましょう。", translate_stage="checkpoint"),
    ),
    46: dict(
        role_ja="上級管理職", transfer_role_ja="財務責任者",
        live=("Is it easy for you to say “I don't know” at work? Why or why not?", "仕事で「分かりません」と言うのは簡単ですか？なぜですか？", "Your honest view and reason", "自分の正直な考えと理由", "What about you—is it easy for you?", "先生はどうですか？簡単に言えますか？"),
        p1=dict(write_frame="I don't have ___ in front of me", write_script="Use “I don't have ___ in front of me” to say which fact you cannot verify yet.", write_script_ja="「I don't have ___ in front of me」を使って、今は確認できない情報を伝えましょう。", translate_stage="checkpoint"),
        p2=dict(write_frame="Let me check and get back to you ___", write_script="Use “Let me check and get back to you ___” to promise a specific follow-up time.", write_script_ja="「Let me check and get back to you ___」を使って、確認して回答する時刻を約束しましょう。", translate_stage="checkpoint"),
    ),
    47: dict(
        role_ja="上級責任者", transfer_role_ja="部門責任者",
        live=("Is it harder to disagree with a senior colleague or with a client? Why?", "目上の同僚と顧客なら、どちらに異議を述べるほうが難しいですか？なぜですか？", "Your choice and a real reason", "自分の選択と実際の理由", "What about you—which is harder?", "先生はどうですか？どちらが難しいですか？"),
        p1=dict(write_frame="I see your point, but ___ concerns me", write_script="Use “I see your point, but ___ concerns me” to acknowledge the idea and name one concern.", write_script_ja="「I see your point, but ___ concerns me」を使って、相手の考えを認めたうえで懸念を一つ伝えましょう。", translate_hints=(("日程", "timing"), ("費用", "cost"), ("根拠", "evidence"), ("顧客への影響", "client impact"))),
        p2=dict(write_frame="The part I'm not comfortable with is ___", write_script="Use “The part I'm not comfortable with is ___” to identify the exact action you cannot support.", write_script_ja="「The part I'm not comfortable with is ___」を使って、賛成できない具体的な行動を示しましょう。", translate_hints=(("最終テスト", "final test"), ("レビュー時間", "review time"), ("未確認のデータ", "unverified data"), ("顧客", "client"))),
    ),
    48: dict(
        role_ja="会議の進行役", transfer_role_ja="調達会議の進行役",
        live=("When a group cannot decide, what usually helps most: more information, a deadline, or a vote?", "グループで決められないとき、追加情報・期限・投票のどれが最も役立ちますか？", "Your choice and why it helps", "自分の選択と、役立つ理由", "What about you—which one helps most?", "先生はどうですか？どれが最も役立ちますか？"),
        p1=dict(write_frame="The decision we need today is ___", write_script="Use “The decision we need today is ___” to define the one choice the group must make.", write_script_ja="「The decision we need today is ___」を使って、グループが決める一つの選択を明確にしましょう。", translate_stage="checkpoint"),
        p2=dict(write_frame="Would it help if we compared them against ___?", write_script="Use “Would it help if we compared them against ___?” to propose one fair basis for comparison.", write_script_ja="「Would it help if we compared them against ___?」を使って、公平に比べる基準を一つ提案しましょう。", translate_stage="checkpoint"),
    ),
}


for _number, _copy in REVIEWED_COPY_37_48.items():
    _lesson = LESSONS[_number]
    _lesson["role_ja"] = _copy["role_ja"]
    _lesson["transfer_role_ja"] = _copy["transfer_role_ja"]
    _lesson["live"] = _copy["live"]
    _lesson.pop("live_sequence", None)
    for _part in (1, 2):
        _lesson[f"p{_part}"].update(_copy[f"p{_part}"])

    _owned_english = {
        _entry.split("|")[0].strip().casefold()
        for _category in _lesson["vocab"]
        for _entry in _category.split(";")
        if _entry.strip()
    }
    _support_additions = []
    for _part in (1, 2):
        for _hint_row in _lesson[f"p{_part}"].get("translate_hints", ()):
            if len(_hint_row) == 2 and all(isinstance(_item, str) for _item in _hint_row):
                _hint_row = (_hint_row,)
            for _japanese_hint, _english_hint in _hint_row:
                if _english_hint.casefold() not in _owned_english:
                    _support_additions.append(f"{_english_hint}|{_japanese_hint}")
                    _owned_english.add(_english_hint.casefold())
    if _support_additions:
        _vocab = list(_lesson["vocab"])
        _vocab[2] = "; ".join(filter(None, (_vocab[2], *_support_additions)))
        _lesson["vocab"] = tuple(_vocab)


# The Understand page is tutor-read listening.  Use complete counterpart lines
# from the scene/transfer instead of learner fragments or target answers.
REVIEWED_RECEPTIVE_37_48 = {
    37: (
        ("I need the client report, the audit notes, and the budget update by Friday.", "The manager names three tasks with the same deadline", "上司は同じ締め切りの仕事を三つ挙げている", "The manager has cancelled all three tasks", "上司は三つの仕事をすべて中止した"),
        ("Understood. What do you need from me?", "The manager invites the learner to ask for a decision", "上司は学習者に判断事項を尋ねるよう促している", "The manager refuses to set a priority", "上司は優先順位を決めることを断る"),
        ("Do the client report first.", "The client report is the first priority", "顧客報告書が最優先である", "The audit is the first priority", "監査が最優先である"),
        ("Move the audit to Monday.", "The audit gets a later deadline", "監査の締め切りが後ろに動く", "The audit remains due Friday", "監査は金曜日のままである"),
    ),
    38: (
        ("Your team thinks ours is contacting the supplier, but our team thinks yours is.", "The two teams have different assumptions about ownership", "二つのチームは担当について異なる思い込みをしている", "Both teams named the same clear owner", "両チームは同じ担当者を明確に決めた"),
        ("I thought your team was doing it.", "The project lead assumed the learner's team owned it", "責任者は学習者のチーム担当だと思っていた", "The project lead confirms another named owner", "責任者は別の担当者を確定した"),
        ("No one has taken that action yet.", "The contact task still has no owner", "連絡業務にはまだ担当者がいない", "The contact task is already complete", "連絡業務はすでに完了している"),
        ("Thanks. Please copy me in.", "The lead wants to receive the message too", "責任者もその連絡を受け取りたい", "The lead wants the message deleted", "責任者は連絡を削除してほしい"),
    ),
    39: (
        ("How is the delivery looking today?", "The sponsor asks for the current delivery status", "スポンサーは現在の納品状況を尋ねている", "The sponsor cancels the delivery", "スポンサーは納品を中止する"),
        ("But you sound worried.", "The sponsor hears concern behind the status", "スポンサーは状況報告の裏に懸念を感じている", "The sponsor says there is no risk", "スポンサーはリスクがないと言っている"),
        ("Thanks for raising it now. What's the fallback?", "The sponsor asks for a backup plan", "スポンサーは代替案を尋ねている", "The sponsor asks for last month's invoice", "スポンサーは先月の請求書を尋ねている"),
        ("What could change that?", "The analytics lead asks what could affect the status", "分析責任者は状況が変わる条件を尋ねている", "The analytics lead says the status can never change", "分析責任者は状況が絶対に変わらないと言っている"),
    ),
    40: (
        ("Could you send the complete analysis tomorrow?", "The manager asks for the full analysis tomorrow", "上司は完全な分析を明日求めている", "The manager asks only for an outline next month", "上司は来月の概要だけを求めている"),
        ("Could I have the full version by Thursday?", "The manager proposes Thursday for the full version", "上司は完全版を木曜日までに求めている", "The manager cancels the full version", "上司は完全版を中止する"),
        ("Agreed. I'll chase the data now.", "The manager will follow up on the needed data", "上司は必要なデータを催促する", "The manager will remove the data requirement", "上司はデータの要件をなくす"),
        ("When can the complete report be ready?", "The product lead asks for a realistic completion date", "製品責任者は現実的な完成日を尋ねている", "The product lead asks for a meeting room", "製品責任者は会議室を求めている"),
    ),
    41: (
        ("Are we still set for Monday's launch?", "The director checks whether Monday's launch is still possible", "責任者は月曜日の公開がまだ可能か確認している", "The director says the launch finished", "責任者は公開が完了したと言っている"),
        ("How far behind are we?", "The director asks for the size of the delay", "責任者は遅れの長さを尋ねている", "The director asks who booked the room", "責任者は会議室の予約者を尋ねている"),
        ("All right. Talk me through the plan.", "The director wants the recovery steps explained", "責任者は立て直し手順の説明を求めている", "The director rejects every next step", "責任者はすべての次の行動を拒否する"),
        ("What date can you commit to instead?", "The client director asks for a new reliable date", "顧客側の責任者は代わりに約束できる日を尋ねている", "The client director keeps the original date without discussion", "顧客側の責任者は話し合わず元の日程を維持する"),
    ),
    42: (
        ("The schedule and client call still have no owners. You and Mia each thought the other person owned them.", "Responsibility for both actions is unclear", "二つの行動の担当がどちらも曖昧である", "Both actions already have confirmed owners", "二つの行動はすでに担当が確定している"),
        ("Correct. What are the deadlines?", "The project lead asks when both actions are due", "責任者は二つの行動の締め切りを尋ねている", "The project lead asks to cancel both actions", "責任者は二つの行動の中止を求めている"),
        ("Good. Please put that in the notes.", "The project lead wants the agreement recorded", "責任者は合意内容の記録を求めている", "The project lead asks to delete the actions", "責任者は行動項目の削除を求めている"),
        ("Good. When will each item be ready?", "The team lead asks for a deadline for each item", "チームリーダーは各項目の締め切りを尋ねている", "The team lead says deadlines are unnecessary", "チームリーダーは締め切りが不要だと言っている"),
    ),
    43: (
        ("We should be ready to launch on June 12.", "The presenter states a planned launch date", "発表者は公開予定日を示している", "The presenter cancels the launch", "発表者は公開を中止する"),
        ("It's based on the supplier's current estimate.", "The date relies on the supplier's estimate", "日程は仕入先の見込みに基づいている", "The date is already legally fixed", "日程はすでに法的に確定している"),
        ("Exactly. It isn't fixed yet.", "The launch date may still change", "公開日はまだ変わる可能性がある", "The launch date cannot change", "公開日は変更できない"),
        ("It uses the results from our three largest clients.", "The forecast uses results from three major clients", "予測は主要顧客三社の実績を使っている", "The forecast has no supporting information", "予測には裏付けとなる情報がない"),
    ),
    44: (
        ("Let's test option B first.", "The chair proposes option B for the first test", "進行役は最初のテストに選択肢Bを提案している", "The chair rejects option B", "進行役は選択肢Bを却下する"),
        ("Yes. Start with the support team only.", "The first test is limited to the support team", "最初のテストはサポートチームだけに限定される", "The first test includes every team", "最初のテストには全チームが含まれる"),
        ("Yes. Please record it that way.", "The chair confirms the summary for the notes", "進行役はその要約で記録するよう確認する", "The chair asks to erase the decision", "進行役は決定を消すよう求める"),
        ("Correct. Put that in the decision log and schedule a June review.", "The finance chair wants the decision and review recorded", "財務会議の進行役は決定とレビューの記録を求めている", "The finance chair postpones all documentation", "財務会議の進行役はすべての記録を延期する"),
    ),
    45: (
        ("We've reviewed options A, B, and C. Which one should we choose?", "The decision maker asks for one recommendation", "意思決定者は一つの推奨案を求めている", "The decision maker rejects every option", "意思決定者はすべての案を却下する"),
        ("Why B?", "The decision maker asks for the reason behind option B", "意思決定者は選択肢Bの理由を尋ねている", "The decision maker asks for a new meeting time", "意思決定者は新しい会議時刻を尋ねている"),
        ("Good. Show us the comparison.", "The decision maker asks for supporting evidence", "意思決定者は比較根拠を求めている", "The decision maker ends the project", "意思決定者は案件を終了する"),
        ("What makes the smaller pilot better?", "The operations director asks for a comparative reason", "業務責任者は小規模な試験導入がよい比較理由を尋ねている", "The operations director asks who booked the room", "業務責任者は会議室の予約者を尋ねている"),
    ),
    46: (
        ("What was the confirmed conversion figure last month?", "The senior manager asks for a verified number", "上級管理職は確認済みの数値を求めている", "The senior manager asks for a personal opinion", "上級管理職は個人的な意見を求めている"),
        ("Can you give us an estimate?", "The senior manager asks whether an approximate figure is available", "上級管理職は概算を出せるか尋ねている", "The senior manager asks for a confirmed date", "上級管理職は確定日を求めている"),
        ("That's fine. Please send it to everyone.", "The verified answer should be shared with the group", "確認済みの回答を全員に共有する", "The answer should remain private", "回答は非公開にする"),
        ("When can finance have the verified total?", "The finance director asks for a follow-up time", "財務責任者は確認済み合計の回答時刻を尋ねている", "The finance director asks for an unverified guess", "財務責任者は未確認の推測を求めている"),
    ),
    47: (
        ("We can meet the date if we skip the final test.", "The proposal removes a quality step to meet the date", "提案は日程に間に合わせるため品質確認を省く", "The proposal adds another test", "提案はテストを追加する"),
        ("What specifically concerns you?", "The senior director asks for the exact concern", "上級責任者は具体的な懸念を求めている", "The senior director changes the subject", "上級責任者は話題を変える"),
        ("All right. Let's examine that risk.", "The concern will be considered", "懸念は検討される", "The concern is dismissed without discussion", "懸念は検討されず退けられる"),
        ("Which part of that plan worries you?", "The department head asks which action is concerning", "部門責任者はどの行動が心配か尋ねている", "The department head says the plan cannot be discussed", "部門責任者は計画を話し合えないと言っている"),
    ),
    48: (
        ("We've discussed options A, B, and C for forty minutes.", "The discussion has continued without a decision", "決定がないまま議論が続いている", "The decision was made forty minutes ago", "40分前に決定した"),
        ("I don't think we have enough information.", "The chair sees an evidence gap", "進行役は情報不足を認識している", "The chair has already chosen secretly", "進行役はすでに内密に選んだ"),
        ("Yes. Then we can decide.", "A common comparison can unlock the decision", "共通比較によって判断できる", "The comparison will prevent any decision", "比較すると判断できなくなる"),
        ("We need a fair way to compare them first.", "The procurement chair asks for a fair comparison", "調達会議の進行役は公平な比較を求めている", "The procurement chair says comparison is unnecessary", "調達会議の進行役は比較が不要だと言っている"),
    ),
}

for _number, _receptive in REVIEWED_RECEPTIVE_37_48.items():
    LESSONS[_number]["receptive"] = _receptive


AUTHORITATIVE = {
    number: (lesson["title"], core.strip_marks(lesson["p1"]["rows"][0][0]), core.strip_marks(lesson["p2"]["rows"][0][0]))
    for number, lesson in LESSONS.items()
}

LIVE_FRAME_CONTRACTS = {
    37: ("I can", "but probably not", "Which", "should I"),
    38: ("Just to clarify", "who's", "I'm happy to", "if no one else is doing it"),
    39: ("We're on track", "The main risk is that"),
    40: ("I can", "will take", "is realistic if"),
    41: ("I'm afraid we won't be ready for", "We'll need to push it back", "I have a recovery plan"),
    42: ("So I'll", "and ___ will ___.", "I'll ___ by", "and ___ will ___ by"),
    43: ("Sorry to interrupt", "based on", "So it could change if"),
    44: ("So we've agreed to", "Have I understood", "correctly"),
    45: ("I recommend", "It's", "to"),
    46: ("I don't have the confirmed", "in front of me", "Let me check and get back to you by"),
    47: ("I see your point, but", "concerns me", "The part I'm not comfortable with is"),
    48: ("The decision we need today is", "Would it help if we compared them against"),
}

ENTRY_FLOORS = {**dict.fromkeys(range(37, 43), 59), **dict.fromkeys(range(43, 49), 86)}

# Exact Core owners and bounded-chunk treatment copied from the generated
# briefs.  The guard is deliberately data-driven: a later edit cannot make a
# future Core form look reachable merely by omitting a rule page.
PATTERN_CORE_OWNERS = {
    37: ((56,), (40,)),
    38: ((83,), (57,)),
    39: ((82,), (82,)),
    40: ((56,), (57,)),
    41: ((110,), ()),
    42: ((38,), (38,)),
    43: ((), (83,)),
    44: ((83,), (83,)),
    45: ((), (45, 59)),
    46: ((), (86,)),
    47: ((85,), (85,)),
    48: ((103,), (94,)),
}
BOUNDED_PARTS = {
    (38, 1), (38, 2), (39, 1), (39, 2), (41, 1), (41, 2),
    (43, 1), (45, 1), (46, 1), (48, 1), (48, 2),
}

# These two question frames are already irreducible at three chunks. Every
# other rendered reorder in this batch must expose four honest meaning units.
HONEST_THREE_CHUNK_PARTS = {(37, 2), (44, 2)}

# These are the exact declarations in the currently approved owner decks.
# English text alone is not enough: a changed Japanese gloss is a changed
# metadata entry, not the same cited owner.
VISIBLE_PRIOR_CTX_OWNERS = {
    "definitely|確実に|CTX-26",
    "push back|後ろへずらす|CTX-12",
    "final version|最終版|CTX-34",
    "on track|予定どおり|CTX-35",
    "before we move on|次へ進む前に|CTX-43",
}

# A separable phrasal verb can be visibly taught with its object in the middle.
# Keep that exception explicit so an unrelated metadata-only token cannot pass.
VISIBLE_VOCABULARY_FORMS = {
    (41, "push back"): ("push it back",),
    (43, "supplier"): ("supplier's",),
}


class _VisibleText(HTMLParser):
    """Collect rendered body text without counting metadata or executable text."""

    _SKIPPED = {"head", "script", "style", "template"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in self._SKIPPED:
            self.depth += 1

    def handle_endtag(self, tag):
        if tag in self._SKIPPED:
            self.depth -= 1

    def handle_data(self, data):
        if self.depth == 0:
            self.parts.append(data)


def visible_text(source):
    parser = _VisibleText()
    parser.feed(source)
    return " ".join(parser.parts).casefold()


VISIBLE_TOKEN = re.compile(r"[^\W_]+(?:['’][^\W_]+)*", re.UNICODE)


def visible_tokens(value):
    return tuple(token.replace("’", "'").casefold() for token in VISIBLE_TOKEN.findall(value))


def phrase_is_visible(body, phrase):
    body_tokens = visible_tokens(body)
    phrase_tokens = visible_tokens(phrase)
    if not phrase_tokens:
        return False
    width = len(phrase_tokens)
    return any(body_tokens[index:index + width] == phrase_tokens
               for index in range(len(body_tokens) - width + 1))


def owner_new_pairs(owner_review_id):
    contextual = re.fullmatch(r"CTX-(\d+)", owner_review_id)
    if contextual and int(contextual.group(1)) in LESSONS:
        new_field = LESSONS[int(contextual.group(1))]["vocab"][0]
        return {
            tuple(item.split("|", 1))
            for item in filter(None, new_field.split("; "))
        }

    matches = []
    review_marker = f'<meta name="podo:review-id" content="{owner_review_id}">'
    for path in (new_lesson.ENGLISH / "tracks").rglob("lesson.html"):
        source = path.read_text(encoding="utf-8")
        if review_marker in source:
            matches.append((path, source))
    if len(matches) != 1:
        raise ValueError(f"{owner_review_id}: expected one vocabulary owner deck, found {len(matches)}")
    path, source = matches[0]
    owner = vocabulary.parse(source, source=path)
    return {(item["english"], item["japanese"]) for item in owner["categories"]["new"]}


def validate_rendered_vocabulary(number, source):
    data = vocabulary.parse(source, source=f"CTX-{number}")
    body = visible_text(source)
    for category in ("new", "recycled"):
        for entry in data["categories"][category]:
            english = entry["english"].casefold()
            visible_forms = (english,) + VISIBLE_VOCABULARY_FORMS.get((number, english), ())
            if not any(phrase_is_visible(body, form) for form in visible_forms):
                raise ValueError(
                    f"CTX-{number}: {category} vocabulary is absent from visible deck text: "
                    f"{entry['english']}|{entry['japanese']}"
                )
            if category == "recycled":
                exact = (entry["english"], entry["japanese"])
                if exact not in owner_new_pairs(entry["source"]):
                    raise ValueError(
                        f"CTX-{number}: recycled vocabulary is not an exact English/Japanese "
                        f"row in {entry['source']}: {entry['english']}|{entry['japanese']}"
                    )


@contextlib.contextmanager
def renderer_scope():
    names = ("COURSES", "LESSONS", "AUTHORITATIVE", "LIVE_FRAME_CONTRACTS", "VISIBLE_PRIOR_CTX_OWNERS")
    previous = {name: getattr(renderer, name) for name in names}
    try:
        renderer.COURSES = COURSES
        renderer.LESSONS = LESSONS
        renderer.AUTHORITATIVE = AUTHORITATIVE
        renderer.LIVE_FRAME_CONTRACTS = LIVE_FRAME_CONTRACTS
        renderer.VISIBLE_PRIOR_CTX_OWNERS = VISIBLE_PRIOR_CTX_OWNERS
        yield
    finally:
        for name, value in previous.items():
            setattr(renderer, name, value)


def validate_lesson(number, lesson):
    with renderer_scope():
        renderer.validate_lesson(number, lesson)
    floor = ENTRY_FLOORS[number]
    for part, owners in enumerate(PATTERN_CORE_OWNERS[number], start=1):
        bounded = (number, part) in BOUNDED_PARTS
        if any(owner > floor + 2 for owner in owners) and not bounded:
            raise ValueError(
                f"CTX-{number} p{part}: future Core owner above entry floor must be a bounded chunk"
            )
        pattern_data = lesson[f"p{part}"]
        if bounded and not (pattern_data.get("omit_rule") and pattern_data.get("omit_reorder")):
            raise ValueError(f"CTX-{number} p{part}: bounded chunk cannot unpack rule or reorder")
        if not pattern_data.get("omit_reorder"):
            expected_chunks = 3 if (number, part) in HONEST_THREE_CHUNK_PARTS else 4
            for row_index, row in enumerate(pattern_data["rows"], start=1):
                actual_chunks = len(row[2].split("|"))
                if actual_chunks != expected_chunks:
                    raise ValueError(
                        f"CTX-{number} p{part} row {row_index}: expected "
                        f"{expected_chunks} honest reorder chunks, got {actual_chunks}"
                    )

    for field in lesson["vocab"]:
        for item in filter(None, field.split("; ")):
            owner = re.search(r"\|CTX-(\d+)$", item)
            if not owner:
                continue
            if int(owner.group(1)) >= number:
                raise ValueError(f"CTX-{number}: non-prior Contextual vocabulary owner: {item}")
            if item not in VISIBLE_PRIOR_CTX_OWNERS:
                raise ValueError(f"CTX-{number}: cited Contextual owner is not exact: {item}")


def set_complete_status(source):
    source, count = re.subn(
        r'\n\s*<meta name="podo:proofread-status" content="[^"]+">',
        "",
        source,
    )
    if count == 0:
        raise ValueError("generated source has no proofread-status marker to normalize")
    marker = '<meta name="podo:vocabulary-status" content="reviewed">'
    complete = '<meta name="podo:proofread-status" content="complete">'
    if source.count(marker) != 1:
        raise ValueError("generated source has no unique reviewed vocabulary marker")
    return source.replace(marker, marker + "\n  " + complete, 1)


def build(number, lesson):
    validate_lesson(number, lesson)
    with renderer_scope():
        output, source = renderer.build(number, lesson)
    source = source.replace(
        'data-page-id="lesson-goal" data-act="Travel task"',
        'data-page-id="lesson-goal" data-act="Business task"',
        1,
    )
    source = set_complete_status(source)
    validate_rendered_vocabulary(number, source)
    return output, source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--lesson", type=int, choices=LESSONS)
    args = parser.parse_args()
    selected = LESSONS.items() if args.lesson is None else ((args.lesson, LESSONS[args.lesson]),)
    for number, lesson in selected:
        output, source = build(number, lesson)
        if output.exists() and not args.refresh:
            raise SystemExit(f"refusing to overwrite {output.relative_to(ROOT)}")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(source, encoding="utf-8")
        print(f"wrote {output.relative_to(ROOT)}")
    print(f"{len(LESSONS) if args.lesson is None else 1} Contextual decks generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
